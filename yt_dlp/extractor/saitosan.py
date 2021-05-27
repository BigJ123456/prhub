# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor


class SaitosanIE(InfoExtractor):
    IE_NAME = 'Saitosan'
    _VALID_URL = r'https?://(?:www\.)?saitosan\.net/bview.html\?id=(?P<id>[0-9]+)'
    _TESTS = [{
        'url': 'http://www.saitosan.net/bview.html?id=10031846',
        'info_dict': {
            'id': '10031846',
            'ext': 'mp4',
            'title': '井下原 和弥',
            'uploader': '井下原 和弥',
            'thumbnail': 'http://111.171.196.85:8088/921f916f-7f55-4c97-b92e-5d9d0fef8f5f/thumb',
            'is_live': True,
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
        'skip': 'Broadcasts are ephemeral',
    },
        {
        'url': 'http://www.saitosan.net/bview.html?id=10031795',
        'info_dict': {
            'id': '10031795',
            'ext': 'mp4',
            'title': '橋本',
            'uploader': '橋本',
            'thumbnail': 'http://111.171.196.85:8088/1a3933e1-a01a-483b-8931-af15f37f8082/thumb',
            'is_live': True,
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
        'skip': 'Broadcasts are ephemeral',
    }]

    def _real_extract(self, url):
        b_id = self._match_id(url)

        def format_socket_response_as_json(data):
            return self._parse_json(data[data.find('{'):data.rfind('}') + 1], b_id)

        base = 'http://hankachi.saitosan-api.net:8002/socket.io/?transport=polling&EIO=3'
        sid = format_socket_response_as_json(self._download_webpage(base, b_id, note='Opening socket')).get('sid')
        base += "&sid=" + sid

        self._download_webpage(base, b_id, note="Polling socket")
        payload = '420["room_start_join",{"room_id":"' + str(b_id) + '"}]'
        payload = str(len(payload)) + ":" + payload

        self._download_webpage(base, b_id, data=payload, note='Polling socket with payload')
        should_continue = format_socket_response_as_json(self._download_webpage(base, b_id, note="Polling socket")).get('ok')
        if not should_continue:
            # The socket does not give any specific error messages.
            raise ExtractorError(
                'The socket reported that the broadcast could not be joined. Maybe it's offline or the URL is incorrect',
                expected=True, video_id=b_id)

        self._download_webpage(base, b_id, data='26:421["room_finish_join",{}]', note="Polling socket")
        b_data = format_socket_response_as_json(self._download_webpage(base, b_id, note='Getting broadcast metadata from socket'))

        self._download_webpage(base, b_id, data="1:1", note="Closing socket")

        title = b_data.get('name')
        uploader = b_data.get('broadcast_user')
        uploader_name = uploader.get('name')  # same as title

        m3u8_url = b_data.get('url')
        thumbnail = m3u8_url.replace('av.m3u8', 'thumb')
        formats = self._extract_m3u8_formats(m3u8_url, b_id, 'mp4', live=True)

        return {
            'id': b_id,
            'title': title,
            'formats': formats,
            'thumbnail': thumbnail,
            'uploader': uploader_name,
            'is_live': True
        }
