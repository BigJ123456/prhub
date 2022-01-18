# coding: utf-8
from __future__ import unicode_literals

import json

from ..compat import compat_str
from ..utils import (
    clean_html,
    determine_ext,
    ExtractorError,
    dict_get,
    int_or_none,
    merge_dicts,
    parse_age_limit,
    parse_iso8601,
    str_or_none,
    try_get,
    url_or_none,
)

from .common import InfoExtractor


class ERTFlixBaseIE(InfoExtractor):
    _VALID_URL = r'ertflix:(?P<id>[\w-]+)'
    _TESTS = [{
        'url': 'ertflix:monogramma-praxitelis-tzanoylinos',
        'md5': '5b9c2cd171f09126167e4082fc1dd0ef',
        'info_dict': {
            'id': 'monogramma-praxitelis-tzanoylinos',
            'ext': 'mp4',
            'title': 'md5:ef0b439902963d56c43ac83c3f41dd0e',
        },
    },
    ]

    def _call_api(
        self, video_id, method='Player/AcquireContent', api_version=1,
        param_headers=None, data=None, headers=None, **params):
        platform_codename = {'platformCodename': 'www'}
        headers_as_param = {"X-Api-Date-Format": "iso", "X-Api-Camel-Case": False}
        headers_as_param.update(param_headers or {})
        headers = headers or {}
        if data:
            headers["Content-Type"] = headers_as_param["Content-Type"] = \
                "application/json;charset=utf-8"
            data = json.dumps(merge_dicts(platform_codename, data)).encode('utf-8')
        query = merge_dicts(
            {} if data else platform_codename,
            {'$headers': json.dumps(headers_as_param)},
            params)
        response = self._download_json(
            'https://api.app.ertflix.gr/v%s/%s' % (str(api_version), method),
            video_id, fatal=False, query=query, data=data, headers=headers)
        if try_get(response, lambda x: x['Result']['Success']) is True:
            return response

    def _extract_formats(self, video_id, allow_none=True):
        media_info = self._call_api(video_id, codename=video_id)
        formats = []
        for media_file in try_get(media_info, lambda x: x['MediaFiles'], list) or []:
            for media in try_get(media_file, lambda x: x['Formats'], list) or []:
                fmt_url = url_or_none(try_get(media, lambda x: x['Url']))
                if not fmt_url:
                    continue
                ext = determine_ext(fmt_url)
                if ext == 'm3u8':
                    formats.extend(self._extract_m3u8_formats(fmt_url, video_id, m3u8_id='hls', ext='mp4', entry_protocol='m3u8_native', fatal=False))
                elif ext == 'mpd':
                    formats.extend(self._extract_mpd_formats(fmt_url, video_id, mpd_id='dash', fatal=False))
                else:
                    formats.append({
                        'url': fmt_url,
                        'format_id': str_or_none(media.get('Id')),
                    })

        if formats or not allow_none:
            self._sort_formats(formats)
        return formats

    def _real_extract(self, url):
        video_id = self._match_id(url)

        formats = self._extract_formats(video_id)

        if formats:
            return {
                'id': video_id,
                'formats': formats,
                'title': self._generic_title(url),
            }


class ERTFlixIE(ERTFlixBaseIE):
    _VALID_URL = r'https?://www\.ertflix\.gr/(?:series|vod)/(?P<id>[a-z]{3}\.\d+)'
    _TESTS = [{
        'url': 'https://www.ertflix.gr/vod/vod.173258-aoratoi-ergates',
        'md5': '388f47a70e1935c8dabe454e871446bb',
        'info_dict': {
            'id': 'aoratoi-ergates',
            'ext': 'mp4',
            'title': 'md5:c1433d598fbba0211b0069021517f8b4',
            'description': 'md5:8cc02e5cdb31058c8f6e0423db813770',
            'thumbnail': r're:https?://.+\.jpg',
        },
    }, {
        'url': 'https://www.ertflix.gr/series/ser.3448-monogramma',
        'info_dict': {
            'id': 'ser.3448',
            'age_limit': 8,
            'description': 'Η εκπομπή σαράντα ετών που σημάδεψε τον πολιτισμό μας.',
            'title': 'Μονόγραμμα',
        },
        'playlist_mincount': 64,
    },
    ]

    def _extract_episode(self, episode):
        codename = try_get(episode, lambda x: x['Codename'], compat_str)
        title = episode.get('Title')
        description = clean_html(dict_get(episode, ('Description', 'ShortDescription', 'TinyDescription', )))
        if description:
            description = description.strip('\r') # CRLF spotted in response for extended description
        if not codename or not title or not episode.get('HasPlayableStream', True):
            return
        for _t in try_get(episode, lambda x: x['Images'], list) or [episode.get('Image', {})]:
            if _t.get('IsMain'):
                thumbnail = url_or_none(_t.get('Url'))
                break
        else:
            thumbnail = None
        return {
            '_type': 'url_transparent',
            'thumbnail': thumbnail,
            'id': codename,
            'episode_id': episode.get('Id'),
            'title': title,
            'alt_title': episode.get('Subtitle'),
            'description': description,
            'timestamp': parse_iso8601(episode.get('PublishDate')),
            'duration': episode.get('DurationSeconds'),
            'age_limit': self._parse_age_rating(episode),
            'url': 'ertflix:%s' % (codename, ),
        }

    @staticmethod
    def _parse_age_rating(info_dict):
        return parse_age_limit(
            info_dict.get('AgeRating')
            or (info_dict.get('IsAdultContent') and 18)
            or (info_dict.get('IsKidsContent') and 0))

    def _extract_series(self, video_id):
        media_info = self._call_api(video_id, method='Tile/GetSeriesDetails', id=video_id)

        series = try_get(media_info, lambda x: x['Series'], dict) or {}
        series_info = {
            'age_limit': self._parse_age_rating(series),
            'title': series.get('Title'),
            'description': dict_get(series, ('ShortDescription', 'TinyDescription', )),
        }

        def gen_episode(m_info):
            for episode_group in try_get(m_info, lambda x: x['EpisodeGroups'], list) or []:
                episodes = try_get(episode_group, lambda x: x['Episodes'], list)
                if not episodes:
                    continue
                season_info = {
                    'season': episode_group.get('Title'),
                    'season_number': int_or_none(episode_group.get('SeasonNumber')),
                }
                try:
                    episodes = [(int(ep['EpisodeNumber']), ep) for ep in episodes]
                    episodes.sort()
                except (KeyError, ValueError):
                    episodes = enumerate(episodes, 1)
                for n, episode in episodes:
                    info = self._extract_episode(episode)
                    if info is None:
                        continue
                    info['episode_number'] = n
                    info.update(season_info)
                    yield info

        result = self.playlist_result(list(gen_episode(media_info)), playlist_id=video_id)
        result.update(series_info)
        return result

    def _real_extract(self, url):
        video_id = self._match_id(url)
        if video_id.startswith('ser'):
            return self._extract_series(video_id)

        tiles_response = self._call_api(
            video_id, method="Tile/GetTiles", api_version=2,
            data={"RequestedTiles": [{"Id": video_id}]})
        tiles = try_get(tiles_response, lambda x: x['Tiles'], list) or []
        try:
            ep_info = next(tile for tile in tiles if tile['Id'] == video_id)
        except StopIteration:
            raise ExtractorError('No matching video found', video_id=video_id)
        return self._extract_episode(ep_info)
