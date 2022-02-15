# coding: utf-8
from .common import InfoExtractor


class VideocampusSachsenIE(InfoExtractor):
    _VALID_URL = r'https?://videocampus\.sachsen\.de/(?:(?:m/(?P<tmp_id>[0-9a-f]+))|(?:(?P<c>category/)?video/(?P<display_id>[A-Za-z0-9-]+)/(?P<id>[0-9a-f]{32}))(?(c)/[0-9]+))'

    _TESTS = [
        {
            'url': 'https://videocampus.sachsen.de/m/e0d6c8ce6e394c188f1342f1ab7c50ed6fc4490b808699801def5cb2e46d76ca7367f622a9f516c542ffb805b24d6b643bd7c81f385acaac4c59081b87a2767b',
            'info_dict': {
                'id': 'e6b9349905c1628631f175712250f2a1',
                'title': 'Konstruktiver Entwicklungsprozess Vorlesung 7',
                'ext': 'mp4',
            },
        },
        {
            'url': 'https://videocampus.sachsen.de/video/Was-ist-selbstgesteuertes-Lernen/fc99c527e4205b121cb7c74433469262',
            'info_dict': {
                'id': 'fc99c527e4205b121cb7c74433469262',
                'title': 'Was ist selbstgesteuertes Lernen?',
                'ext': 'mp4',
            },
        },
        {
            'url': 'https://videocampus.sachsen.de/category/video/Tutorial-zur-Nutzung-von-Adobe-Connect-aus-Veranstalter-Sicht/09d4ed029002eb1bdda610f1103dd54c/100',
            'info_dict': {
                'id': '09d4ed029002eb1bdda610f1103dd54c',
                'title': 'Tutorial zur Nutzung von Adobe Connect aus Veranstalter-Sicht',
                'ext': 'mp4',
            },
        },
    ]

    def _real_extract(self, url):
        video_id, tmp_id, display_id = self._match_valid_url(url).group(
            'id', 'tmp_id', 'display_id')

        webpage = self._download_webpage(url, tmp_id)

        if tmp_id is not None:
            video_id = self._html_search_regex(
                r'src="https?://videocampus\.sachsen\.de/media/embed\?key=([0-9a-f]+)&',
                webpage,
                'video_id')

        title = self._html_search_regex(
            (
                '<h1>([^<]+)</h1>',
                '<meta[^>]+name=(["\'])title\1[^>]+content=\1(?P<a>(?:(?!\1).)+)\1[^>]*/>',
            ),
            webpage,
            'title')

        medium_url = f'https://videocampus.sachsen.de/media/hlsMedium/key/{video_id}/format/auto/ext/mp4/learning/0/path/m3u8'

        formats, subs = self._extract_m3u8_formats_and_subtitles(
            medium_url, video_id, 'mp4', 'm3u8_native', m3u8_id='hls')
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'formats': formats,
        }


class VideocampusSachsenEmbedIE(InfoExtractor):
    _VALID_URL = r'https?://videocampus.sachsen.de/media/embed\?key=(?P<id>[0-9a-f]+)'

    _TESTS = [
        {
            'url': 'https://videocampus.sachsen.de/media/embed?key=fc99c527e4205b121cb7c74433469262',
            'info_dict': {
                'id': 'fc99c527e4205b121cb7c74433469262',
                'title': 'Was ist selbstgesteuertes Lernen?',
                'ext': 'mp4',
            },
        }
    ]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)
        title = self._html_search_regex('<img[^>]*title="([^"<]+)"', webpage, 'title')

        medium_url = f'https://videocampus.sachsen.de/media/hlsMedium/key/{video_id}/format/auto/ext/mp4/learning/0/path/m3u8'

        formats, subs = self._extract_m3u8_formats_and_subtitles(
            medium_url, video_id, 'mp4', 'm3u8_native', m3u8_id='hls')
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'formats': formats,
        }
