import io

from ._helper import InstanceStoreMixin, select_proxy
from .common import (
    Features,
    Request,
    Response,
    register_preference,
    register_rh,
)
from .exceptions import (
    CertificateVerifyError,
    HTTPError,
    IncompleteRead,
    ProxyError,
    SSLError,
    TransportError,
)
from .impersonate import ImpersonateRequestHandler
from ..dependencies import curl_cffi
from ..utils import int_or_none

if curl_cffi is None:
    raise ImportError('curl_cffi is not installed')

import curl_cffi.requests
from curl_cffi.const import CurlECode, CurlOpt


class CurlCFFIResponseReader(io.IOBase):
    def __init__(self, response: curl_cffi.requests.Response):
        self._response = response
        self._buffer = b''
        self._eof = False

    def readable(self):
        return True

    def read(self, size=None):
        try:
            while not self._eof and (size is None or len(self._buffer) < size):
                chunk = next(self._response.iter_content(), None)
                if chunk is None:
                    self._eof = True
                    break
                self._buffer += chunk

            if size is None:
                data = self._buffer
                self._buffer = b''
            else:
                data = self._buffer[:size]
                self._buffer = self._buffer[size:]

            # "free" the curl instance if the response is fully read.
            # curl_cffi doesn't do this automatically and only allows one open response per thread
            if self._eof and len(self._buffer) == 0:
                self.close()
            return data
        except Exception:
            self.close()
            raise

    def close(self):
        self._response.close()
        super().close()


class CurlCFFIResponseAdapter(Response):
    def __init__(self, response: curl_cffi.requests.Response):
        super().__init__(
            fp=CurlCFFIResponseReader(response),
            headers=response.headers,
            url=response.url,
            status=response.status_code)


@register_rh
class CurlCFFIRH(ImpersonateRequestHandler, InstanceStoreMixin):
    RH_NAME = 'curl_cffi'
    _SUPPORTED_URL_SCHEMES = ('http', 'https')
    _SUPPORTED_FEATURES = (Features.NO_PROXY, Features.ALL_PROXY)
    _SUPPORTED_PROXY_SCHEMES = ('http', 'https', 'socks4', 'socks4a', 'socks5', 'socks5h')
    _SUPPORTED_IMPERSONATE_TARGETS = curl_cffi.requests.BrowserType._member_names_

    def _create_instance(self, cookiejar=None):
        return curl_cffi.requests.Session(cookies=cookiejar)

    def _check_extensions(self, extensions):
        super()._check_extensions(extensions)
        extensions.pop('impersonate', None)
        extensions.pop('cookiejar', None)
        extensions.pop('timeout', None)

    def _send(self, request: Request):
        max_redirects_exceeded = False
        cookiejar = request.extensions.get('cookiejar') or self.cookiejar
        session: curl_cffi.requests.Session = self._get_instance(
            cookiejar=cookiejar if 'cookie' not in request.headers else None)

        if self.verbose:
            session.curl.setopt(CurlOpt.VERBOSE, 1)

        proxies = (request.proxies or self.proxies).copy()
        if 'no' in proxies:
            session.curl.setopt(CurlOpt.NOPROXY, proxies['no'].encode())
            proxies.pop('no', None)

        # curl doesn't support per protocol proxies, so we select the one that matches the request protocol
        proxy = select_proxy(request.url, proxies=proxies)
        if proxy:
            session.curl.setopt(CurlOpt.PROXY, proxy.encode())
            if proxy.startswith('https'):
                # enable HTTP CONNECT for https urls
                session.curl.setopt(CurlOpt.HTTPPROXYTUNNEL, 1)

        headers = self._get_impersonate_headers(request)

        if self._client_cert:
            session.curl.setopt(CurlOpt.SSLCERT, self._client_cert['client_certificate'].encode())
            client_certificate_key = self._client_cert.get('client_certificate_key')
            client_certificate_password = self._client_cert.get('client_certificate_password')
            if client_certificate_key:
                session.curl.setopt(CurlOpt.SSLKEY, client_certificate_key.encode())
            if client_certificate_password:
                session.curl.setopt(CurlOpt.KEYPASSWD, client_certificate_password.encode())
        try:
            curl_response = session.request(
                method=request.method,
                url=request.url,
                headers=headers,
                data=request.data,
                verify=self.verify,
                max_redirects=5,
                timeout=request.extensions.get('timeout') or self.timeout,
                impersonate=self._get_impersonate_target(request),
                interface=self.source_address,
                stream=True
            )
        except curl_cffi.requests.errors.RequestsError as e:
            if e.code == CurlECode.PEER_FAILED_VERIFICATION:
                raise CertificateVerifyError(cause=e) from e

            elif e.code == CurlECode.SSL_CONNECT_ERROR:
                raise SSLError(cause=e) from e

            elif e.code == CurlECode.TOO_MANY_REDIRECTS:
                max_redirects_exceeded = True
                curl_response = e.response

            elif e.code == CurlECode.PARTIAL_FILE:
                partial = e.response.content
                content_length = int_or_none(e.response.headers.get('Content-Length'))
                raise IncompleteRead(
                    partial=len(partial),
                    expected=content_length - len(partial) if content_length is not None else None,
                    cause=e) from e
            elif e.code == CurlECode.PROXY:
                raise ProxyError(cause=e) from e
            else:
                raise TransportError(cause=e) from e

        response = CurlCFFIResponseAdapter(curl_response)

        if not 200 <= response.status < 300:
            raise HTTPError(response, redirect_loop=max_redirects_exceeded)

        return response


@register_preference(CurlCFFIRH)
def curl_cffi_preference(rh, request):
    return -100
