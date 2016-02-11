# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..compat import compat_HTTPError
from ..utils import (
    ExtractorError,
    determine_ext,
    int_or_none,
    js_to_json,
    strip_jsonp,
    unified_strdate,
    US_RATINGS,
)


class PBSIE(InfoExtractor):
    _STATIONS = (
        (r'(?:video|www|player)\.pbs\.org', 'PBS: Public Broadcasting Service'),  # http://www.pbs.org/
        (r'video\.aptv\.org', 'APT - Alabama Public Television (WBIQ)'),  # http://aptv.org/
        (r'video\.gpb\.org', 'GPB/Georgia Public Broadcasting (WGTV)'),  # http://www.gpb.org/
        (r'video\.mpbonline\.org', 'Mississippi Public Broadcasting (WMPN)'),  # http://www.mpbonline.org
        (r'video\.wnpt\.org', 'Nashville Public Television (WNPT)'),  # http://www.wnpt.org
        (r'video\.wfsu\.org', 'WFSU-TV (WFSU)'),  # http://wfsu.org/
        (r'video\.wsre\.org', 'WSRE (WSRE)'),  # http://www.wsre.org
        (r'video\.wtcitv\.org', 'WTCI (WTCI)'),  # http://www.wtcitv.org
        (r'video\.pba\.org', 'WPBA/Channel 30 (WPBA)'),  # http://pba.org/
        (r'video\.alaskapublic\.org', 'Alaska Public Media (KAKM)'),  # http://alaskapublic.org/kakm
        # (r'kuac\.org', 'KUAC (KUAC)'),  # http://kuac.org/kuac-tv/
        # (r'ktoo\.org', '360 North (KTOO)'),  # http://www.ktoo.org/
        # (r'azpm\.org', 'KUAT 6 (KUAT)'),  # http://www.azpm.org/
        (r'video\.azpbs\.org', 'Arizona PBS (KAET)'),  # http://www.azpbs.org
        (r'portal\.knme\.org', 'KNME-TV/Channel 5 (KNME)'),  # http://www.newmexicopbs.org/
        (r'video\.vegaspbs\.org', 'Vegas PBS (KLVX)'),  # http://vegaspbs.org/
        (r'watch\.aetn\.org', 'AETN/ARKANSAS ETV NETWORK (KETS)'),  # http://www.aetn.org/
        (r'video\.ket\.org', 'KET (WKLE)'),  # http://www.ket.org/
        (r'video\.wkno\.org', 'WKNO/Channel 10 (WKNO)'),  # http://www.wkno.org/
        (r'video\.lpb\.org', 'LPB/LOUISIANA PUBLIC BROADCASTING (WLPB)'),  # http://www.lpb.org/
        (r'videos\.oeta\.tv', 'OETA (KETA)'),  # http://www.oeta.tv
        (r'video\.optv\.org', 'Ozarks Public Television (KOZK)'),  # http://www.optv.org/
        (r'watch\.wsiu\.org', 'WSIU Public Broadcasting (WSIU)'),  # http://www.wsiu.org/
        (r'video\.keet\.org', 'KEET TV (KEET)'),  # http://www.keet.org
        (r'pbs\.kixe\.org', 'KIXE/Channel 9 (KIXE)'),  # http://kixe.org/
        (r'video\.kpbs\.org', 'KPBS San Diego (KPBS)'),  # http://www.kpbs.org/
        (r'video\.kqed\.org', 'KQED (KQED)'),  # http://www.kqed.org
        (r'vids\.kvie\.org', 'KVIE Public Television (KVIE)'),  # http://www.kvie.org
        (r'video\.pbssocal\.org', 'PBS SoCal/KOCE (KOCE)'),  # http://www.pbssocal.org/
        (r'video\.valleypbs\.org', 'ValleyPBS (KVPT)'),  # http://www.valleypbs.org/
        (r'video\.cptv\.org', 'CONNECTICUT PUBLIC TELEVISION (WEDH)'),  # http://cptv.org
        (r'watch\.knpb\.org', 'KNPB Channel 5 (KNPB)'),  # http://www.knpb.org/
        (r'video\.soptv\.org', 'SOPTV (KSYS)'),  # http://www.soptv.org
        # (r'klcs\.org', 'KLCS/Channel 58 (KLCS)'),  # http://www.klcs.org
        # (r'krcb\.org', 'KRCB Television & Radio (KRCB)'),  # http://www.krcb.org
        # (r'kvcr\.org', 'KVCR TV/DT/FM :: Vision for the Future (KVCR)'),  # http://kvcr.org
        (r'video\.rmpbs\.org', 'Rocky Mountain PBS (KRMA)'),  # http://www.rmpbs.org
        (r'video\.kenw\.org', 'KENW-TV3 (KENW)'),  # http://www.kenw.org
        (r'video\.kued\.org', 'KUED Channel 7 (KUED)'),  # http://www.kued.org
        (r'video\.wyomingpbs\.org', 'Wyoming PBS (KCWC)'),  # http://www.wyomingpbs.org
        (r'video\.cpt12\.org', 'Colorado Public Television / KBDI 12 (KBDI)'),  # http://www.cpt12.org/
        (r'video\.kbyueleven\.org', 'KBYU-TV (KBYU)'),  # http://www.kbyutv.org/
        (r'video\.thirteen\.org', 'Thirteen/WNET New York (WNET)'),  # http://www.thirteen.org
        (r'video\.wgbh\.org', 'WGBH/Channel 2 (WGBH)'),  # http://wgbh.org
        (r'video\.wgby\.org', 'WGBY (WGBY)'),  # http://www.wgby.org
        (r'watch\.njtvonline\.org', 'NJTV Public Media NJ (WNJT)'),  # http://www.njtvonline.org/
        # (r'ripbs\.org', 'Rhode Island PBS (WSBE)'),  # http://www.ripbs.org/home/
        (r'watch\.wliw\.org', 'WLIW21 (WLIW)'),  # http://www.wliw.org/
        (r'video\.mpt\.tv', 'mpt/Maryland Public Television (WMPB)'),  # http://www.mpt.org
        (r'watch\.weta\.org', 'WETA Television and Radio (WETA)'),  # http://www.weta.org
        (r'video\.whyy\.org', 'WHYY (WHYY)'),  # http://www.whyy.org
        (r'video\.wlvt\.org', 'PBS 39 (WLVT)'),  # http://www.wlvt.org/
        (r'video\.wvpt\.net', 'WVPT - Your Source for PBS and More! (WVPT)'),  # http://www.wvpt.net
        (r'video\.whut\.org', 'Howard University Television (WHUT)'),  # http://www.whut.org
        (r'video\.wedu\.org', 'WEDU PBS (WEDU)'),  # http://www.wedu.org
        (r'video\.wgcu\.org', 'WGCU Public Media (WGCU)'),  # http://www.wgcu.org/
        # (r'wjct\.org', 'WJCT Public Broadcasting (WJCT)'),  # http://www.wjct.org
        (r'video\.wpbt2\.org', 'WPBT2 (WPBT)'),  # http://www.wpbt2.org
        (r'video\.wucftv\.org', 'WUCF TV (WUCF)'),  # http://wucftv.org
        (r'video\.wuft\.org', 'WUFT/Channel 5 (WUFT)'),  # http://www.wuft.org
        (r'watch\.wxel\.org', 'WXEL/Channel 42 (WXEL)'),  # http://www.wxel.org/home/
        (r'video\.wlrn\.org', 'WLRN/Channel 17 (WLRN)'),  # http://www.wlrn.org/
        (r'video\.wusf\.usf\.edu', 'WUSF Public Broadcasting (WUSF)'),  # http://wusf.org/
        (r'video\.scetv\.org', 'ETV (WRLK)'),  # http://www.scetv.org
        (r'video\.unctv\.org', 'UNC-TV (WUNC)'),  # http://www.unctv.org/
        # (r'pbsguam\.org', 'PBS Guam (KGTF)'),  # http://www.pbsguam.org/
        (r'video\.pbshawaii\.org', 'PBS Hawaii - Oceanic Cable Channel 10 (KHET)'),  # http://www.pbshawaii.org/
        (r'video\.idahoptv\.org', 'Idaho Public Television (KAID)'),  # http://idahoptv.org
        (r'video\.ksps\.org', 'KSPS (KSPS)'),  # http://www.ksps.org/home/
        (r'watch\.opb\.org', 'OPB (KOPB)'),  # http://www.opb.org
        (r'watch\.nwptv\.org', 'KWSU/Channel 10 & KTNW/Channel 31 (KWSU)'),  # http://www.kwsu.org
        (r'video\.will\.illinois\.edu', 'WILL-TV (WILL)'),  # http://will.illinois.edu/
        (r'video\.networkknowledge\.tv', 'Network Knowledge - WSEC/Springfield (WSEC)'),  # http://www.wsec.tv
        (r'video\.wttw\.com', 'WTTW11 (WTTW)'),  # http://www.wttw.com/
        # (r'wtvp\.org', 'WTVP & WTVP.org, Public Media for Central Illinois (WTVP)'),  # http://www.wtvp.org/
        (r'video\.iptv\.org', 'Iowa Public Television/IPTV (KDIN)'),  # http://www.iptv.org/
        (r'video\.ninenet\.org', 'Nine Network (KETC)'),  # http://www.ninenet.org
        (r'video\.wfwa\.org', 'PBS39 Fort Wayne (WFWA)'),  # http://wfwa.org/
        (r'video\.wfyi\.org', 'WFYI Indianapolis (WFYI)'),  # http://www.wfyi.org
        (r'video\.mptv\.org', 'Milwaukee Public Television (WMVS)'),  # http://www.mptv.org
        (r'video\.wnin\.org', 'WNIN (WNIN)'),  # http://www.wnin.org/
        (r'video\.wnit\.org', 'WNIT Public Television (WNIT)'),  # http://www.wnit.org/
        (r'video\.wpt\.org', 'WPT (WPNE)'),  # http://www.wpt.org/
        (r'video\.wvut\.org', 'WVUT/Channel 22 (WVUT)'),  # http://wvut.org/
        (r'video\.weiu\.net', 'WEIU/Channel 51 (WEIU)'),  # http://www.weiu.net
        (r'video\.wqpt\.org', 'WQPT-TV (WQPT)'),  # http://www.wqpt.org
        (r'video\.wycc\.org', 'WYCC PBS Chicago (WYCC)'),  # http://www.wycc.org
        # (r'lakeshorepublicmedia\.org', 'Lakeshore Public Television (WYIN)'),  # http://lakeshorepublicmedia.org/
        (r'video\.wipb\.org', 'WIPB-TV (WIPB)'),  # http://wipb.org
        (r'video\.indianapublicmedia\.org', 'WTIU (WTIU)'),  # http://indianapublicmedia.org/tv/
        (r'watch\.cetconnect\.org', 'CET  (WCET)'),  # http://www.cetconnect.org
        (r'video\.thinktv\.org', 'ThinkTVNetwork (WPTD)'),  # http://www.thinktv.org
        (r'video\.wbgu\.org', 'WBGU-TV (WBGU)'),  # http://wbgu.org
        (r'video\.wgvu\.org', 'WGVU TV (WGVU)'),  # http://www.wgvu.org/
        (r'video\.netnebraska\.org', 'NET1 (KUON)'),  # http://netnebraska.org
        (r'video\.pioneer\.org', 'Pioneer Public Television (KWCM)'),  # http://www.pioneer.org
        (r'watch\.sdpb\.org', 'SDPB Television (KUSD)'),  # http://www.sdpb.org
        (r'video\.tpt\.org', 'TPT (KTCA)'),  # http://www.tpt.org
        (r'watch\.ksmq\.org', 'KSMQ (KSMQ)'),  # http://www.ksmq.org/
        (r'watch\.kpts\.org', 'KPTS/Channel 8 (KPTS)'),  # http://www.kpts.org/
        (r'watch\.ktwu\.org', 'KTWU/Channel 11 (KTWU)'),  # http://ktwu.org
        # (r'shptv\.org', 'Smoky Hills Public Television (KOOD)'),  # http://www.shptv.org
        # (r'kcpt\.org', 'KCPT Kansas City Public Television (KCPT)'),  # http://kcpt.org/
        # (r'blueridgepbs\.org', 'Blue Ridge PBS (WBRA)'),  # http://www.blueridgepbs.org/
        (r'watch\.easttennesseepbs\.org', 'East Tennessee PBS (WSJK)'),  # http://easttennesseepbs.org
        (r'video\.wcte\.tv', 'WCTE-TV (WCTE)'),  # http://www.wcte.org
        (r'video\.wljt\.org', 'WLJT, Channel 11 (WLJT)'),  # http://wljt.org/
        (r'video\.wosu\.org', 'WOSU TV (WOSU)'),  # http://wosu.org/
        (r'video\.woub\.org', 'WOUB/WOUC (WOUB)'),  # http://woub.org/tv/index.php?section=5
        (r'video\.wvpublic\.org', 'WVPB (WVPB)'),  # http://wvpublic.org/
        (r'video\.wkyupbs\.org', 'WKYU-PBS (WKYU)'),  # http://www.wkyupbs.org
        # (r'wyes\.org', 'WYES-TV/New Orleans (WYES)'),  # http://www.wyes.org
        (r'video\.kera\.org', 'KERA 13 (KERA)'),  # http://www.kera.org/
        (r'video\.mpbn\.net', 'MPBN (WCBB)'),  # http://www.mpbn.net/
        (r'video\.mountainlake\.org', 'Mountain Lake PBS (WCFE)'),  # http://www.mountainlake.org/
        (r'video\.nhptv\.org', 'NHPTV (WENH)'),  # http://nhptv.org/
        (r'video\.vpt\.org', 'Vermont PBS (WETK)'),  # http://www.vpt.org
        (r'video\.witf\.org', 'witf (WITF)'),  # http://www.witf.org
        (r'watch\.wqed\.org', 'WQED Multimedia (WQED)'),  # http://www.wqed.org/
        (r'video\.wmht\.org', 'WMHT Educational Telecommunications (WMHT)'),  # http://www.wmht.org/home/
        (r'video\.deltabroadcasting\.org', 'Q-TV (WDCQ)'),  # http://www.deltabroadcasting.org
        (r'video\.dptv\.org', 'WTVS Detroit Public TV (WTVS)'),  # http://www.dptv.org/
        (r'video\.wcmu\.org', 'CMU Public Television (WCMU)'),  # http://www.wcmu.org
        (r'video\.wkar\.org', 'WKAR-TV (WKAR)'),  # http://wkar.org/
        (r'wnmuvideo\.nmu\.edu', 'WNMU-TV Public TV 13 (WNMU)'),  # http://wnmutv.nmu.edu
        (r'video\.wdse\.org', 'WDSE - WRPT (WDSE)'),  # http://www.wdse.org/
        (r'video\.wgte\.org', 'WGTE TV (WGTE)'),  # http://www.wgte.org
        (r'video\.lptv\.org', 'Lakeland Public Television (KAWE)'),  # http://www.lakelandptv.org
        # (r'prairiepublic\.org', 'PRAIRIE PUBLIC (KFME)'),  # http://www.prairiepublic.org/
        (r'video\.kmos\.org', 'KMOS-TV - Channels 6.1, 6.2 and 6.3 (KMOS)'),  # http://www.kmos.org/
        (r'watch\.montanapbs\.org', 'MontanaPBS (KUSM)'),  # http://montanapbs.org
        (r'video\.krwg\.org', 'KRWG/Channel 22 (KRWG)'),  # http://www.krwg.org
        (r'video\.kacvtv\.org', 'KACV (KACV)'),  # http://www.panhandlepbs.org/home/
        (r'video\.kcostv\.org', 'KCOS/Channel 13 (KCOS)'),  # www.kcostv.org
        (r'video\.wcny\.org', 'WCNY/Channel 24 (WCNY)'),  # http://www.wcny.org
        (r'video\.wned\.org', 'WNED (WNED)'),  # http://www.wned.org/
        (r'watch\.wpbstv\.org', 'WPBS (WPBS)'),  # http://www.wpbstv.org
        (r'video\.wskg\.org', 'WSKG Public TV (WSKG)'),  # http://wskg.org
        (r'video\.wxxi\.org', 'WXXI (WXXI)'),  # http://wxxi.org
        (r'video\.wpsu\.org', 'WPSU (WPSU)'),  # http://www.wpsu.org
        # (r'wqln\.org', 'WQLN/Channel 54 (WQLN)'),  # http://www.wqln.org
        (r'on-demand\.wvia\.org', 'WVIA Public Media Studios (WVIA)'),  # http://www.wvia.org/
        (r'video\.wtvi\.org', 'WTVI (WTVI)'),  # http://www.wtvi.org/
        # (r'whro\.org', 'WHRO (WHRO)'),  # http://whro.org
        (r'video\.westernreservepublicmedia\.org', 'Western Reserve PBS (WNEO)'),  # http://www.WesternReservePublicMedia.org/
        (r'video\.ideastream\.org', 'WVIZ/PBS ideastream (WVIZ)'),  # http://www.wviz.org/
        (r'video\.kcts9\.org', 'KCTS 9 (KCTS)'),  # http://kcts9.org/
        (r'video\.basinpbs\.org', 'Basin PBS (KPBT)'),  # http://www.basinpbs.org
        (r'video\.houstonpbs\.org', 'KUHT / Channel 8 (KUHT)'),  # http://www.houstonpublicmedia.org/
        # (r'tamu\.edu', 'KAMU - TV (KAMU)'),  # http://KAMU.tamu.edu
        # (r'kedt\.org', 'KEDT/Channel 16 (KEDT)'),  # http://www.kedt.org
        (r'video\.klrn\.org', 'KLRN (KLRN)'),  # http://www.klrn.org
        (r'video\.klru\.tv', 'KLRU (KLRU)'),  # http://www.klru.org
        # (r'kmbh\.org', 'KMBH-TV (KMBH)'),  # http://www.kmbh.org
        # (r'knct\.org', 'KNCT (KNCT)'),  # http://www.knct.org
        # (r'ktxt\.org', 'KTTZ-TV (KTXT)'),  # http://www.ktxt.org
        (r'video\.wtjx\.org', 'WTJX Channel 12 (WTJX)'),  # http://www.wtjx.org/
        (r'video\.ideastations\.org', 'WCVE PBS (WCVE)'),  # http://ideastations.org/
        (r'video\.kbtc\.org', 'KBTC Public Television (KBTC)'),  # http://kbtc.org
    )

    IE_NAME = 'pbs'
    IE_DESC = 'Public Broadcasting Service (PBS) and member stations: %s' % ', '.join(list(zip(*_STATIONS))[1])

    _VALID_URL = r'''(?x)https?://
        (?:
           # Direct video URL
           (?:%s)/(?:viralplayer|video)/(?P<id>[0-9]+)/? |
           # Article with embedded player (or direct video)
           (?:www\.)?pbs\.org/(?:[^/]+/){2,5}(?P<presumptive_id>[^/]+?)(?:\.html)?/?(?:$|[?\#]) |
           # Player
           (?:video|player)\.pbs\.org/(?:widget/)?partnerplayer/(?P<player_id>[^/]+)/
        )
    ''' % '|'.join(list(zip(*_STATIONS))[0])

    _TESTS = [
        {
            'url': 'http://www.pbs.org/tpt/constitution-usa-peter-sagal/watch/a-more-perfect-union/',
            'md5': 'ce1888486f0908d555a8093cac9a7362',
            'info_dict': {
                'id': '2365006249',
                'ext': 'mp4',
                'title': 'Constitution USA with Peter Sagal - A More Perfect Union',
                'description': 'md5:36f341ae62e251b8f5bd2b754b95a071',
                'duration': 3190,
            },
            'params': {
                'skip_download': True,  # requires ffmpeg
            },
        },
        {
            'url': 'http://www.pbs.org/wgbh/pages/frontline/losing-iraq/',
            'md5': '143c98aa54a346738a3d78f54c925321',
            'info_dict': {
                'id': '2365297690',
                'ext': 'mp4',
                'title': 'FRONTLINE - Losing Iraq',
                'description': 'md5:4d3eaa01f94e61b3e73704735f1196d9',
                'duration': 5050,
            },
            'params': {
                'skip_download': True,  # requires ffmpeg
            }
        },
        {
            'url': 'http://www.pbs.org/newshour/bb/education-jan-june12-cyberschools_02-23/',
            'md5': 'b19856d7f5351b17a5ab1dc6a64be633',
            'info_dict': {
                'id': '2201174722',
                'ext': 'mp4',
                'title': 'PBS NewsHour - Cyber Schools Gain Popularity, but Quality Questions Persist',
                'description': 'md5:95a19f568689d09a166dff9edada3301',
                'duration': 801,
            },
        },
        {
            'url': 'http://www.pbs.org/wnet/gperf/dudamel-conducts-verdi-requiem-hollywood-bowl-full-episode/3374/',
            'md5': 'c62859342be2a0358d6c9eb306595978',
            'info_dict': {
                'id': '2365297708',
                'ext': 'mp4',
                'title': 'Great Performances - Dudamel Conducts Verdi Requiem at the Hollywood Bowl - Full',
                'description': 'md5:657897370e09e2bc6bf0f8d2cd313c6b',
                'duration': 6559,
                'thumbnail': 're:^https?://.*\.jpg$',
            },
            'params': {
                'skip_download': True,  # requires ffmpeg
            },
        },
        {
            'url': 'http://www.pbs.org/wgbh/nova/earth/killer-typhoon.html',
            'md5': '908f3e5473a693b266b84e25e1cf9703',
            'info_dict': {
                'id': '2365160389',
                'display_id': 'killer-typhoon',
                'ext': 'mp4',
                'description': 'md5:c741d14e979fc53228c575894094f157',
                'title': 'NOVA - Killer Typhoon',
                'duration': 3172,
                'thumbnail': 're:^https?://.*\.jpg$',
                'upload_date': '20140122',
                'age_limit': 10,
            },
            'params': {
                'skip_download': True,  # requires ffmpeg
            },
        },
        {
            'url': 'http://www.pbs.org/wgbh/pages/frontline/united-states-of-secrets/',
            'info_dict': {
                'id': 'united-states-of-secrets',
            },
            'playlist_count': 2,
        },
        {
            'url': 'http://www.pbs.org/wgbh/americanexperience/films/death/player/',
            'info_dict': {
                'id': '2276541483',
                'display_id': 'player',
                'ext': 'mp4',
                'title': 'American Experience - Death and the Civil War, Chapter 1',
                'description': 'md5:1b80a74e0380ed2a4fb335026de1600d',
                'duration': 682,
                'thumbnail': 're:^https?://.*\.jpg$',
            },
            'params': {
                'skip_download': True,  # requires ffmpeg
            },
        },
        {
            'url': 'http://www.pbs.org/video/2365245528/',
            'info_dict': {
                'id': '2365245528',
                'display_id': '2365245528',
                'ext': 'mp4',
                'title': 'FRONTLINE - United States of Secrets (Part One)',
                'description': 'md5:55756bd5c551519cc4b7703e373e217e',
                'duration': 6851,
                'thumbnail': 're:^https?://.*\.jpg$',
            },
            'params': {
                'skip_download': True,  # requires ffmpeg
            },
        },
        {
            # Video embedded in iframe containing angle brackets as attribute's value (e.g.
            # "<iframe style='position: absolute;<br />\ntop: 0; left: 0;' ...", see
            # https://github.com/rg3/youtube-dl/issues/7059)
            'url': 'http://www.pbs.org/food/features/a-chefs-life-season-3-episode-5-prickly-business/',
            'info_dict': {
                'id': '2365546844',
                'display_id': 'a-chefs-life-season-3-episode-5-prickly-business',
                'ext': 'mp4',
                'title': "A Chef's Life - Season 3, Ep. 5: Prickly Business",
                'description': 'md5:54033c6baa1f9623607c6e2ed245888b',
                'duration': 1480,
                'thumbnail': 're:^https?://.*\.jpg$',
            },
            'params': {
                'skip_download': True,  # requires ffmpeg
            },
        },
        {
            # Frontline video embedded via flp2012.js
            'url': 'http://www.pbs.org/wgbh/pages/frontline/the-atomic-artists',
            'info_dict': {
                'id': '2070868960',
                'display_id': 'the-atomic-artists',
                'ext': 'mp4',
                'title': 'FRONTLINE - The Atomic Artists',
                'description': 'md5:1a2481e86b32b2e12ec1905dd473e2c1',
                'duration': 723,
                'thumbnail': 're:^https?://.*\.jpg$',
            },
            'params': {
                'skip_download': True,  # requires ffmpeg
            },
        },
        {
            'url': 'http://player.pbs.org/widget/partnerplayer/2365297708/?start=0&end=0&chapterbar=false&endscreen=false&topbar=true',
            'only_matching': True,
        },
        {
            'url': 'http://watch.knpb.org/video/2365616055/',
            'only_matching': True,
        }
    ]
    _ERRORS = {
        101: 'We\'re sorry, but this video is not yet available.',
        403: 'We\'re sorry, but this video is not available in your region due to right restrictions.',
        404: 'We are experiencing technical difficulties that are preventing us from playing the video at this time. Please check back again soon.',
        410: 'This video has expired and is no longer available for online streaming.',
    }

    def _extract_webpage(self, url):
        mobj = re.match(self._VALID_URL, url)

        presumptive_id = mobj.group('presumptive_id')
        display_id = presumptive_id
        if presumptive_id:
            webpage = self._download_webpage(url, display_id)

            upload_date = unified_strdate(self._search_regex(
                r'<input type="hidden" id="air_date_[0-9]+" value="([^"]+)"',
                webpage, 'upload date', default=None))

            # tabbed frontline videos
            tabbed_videos = re.findall(
                r'<div[^>]+class="videotab[^"]*"[^>]+vid="(\d+)"', webpage)
            if tabbed_videos:
                return tabbed_videos, presumptive_id, upload_date

            MEDIA_ID_REGEXES = [
                r"div\s*:\s*'videoembed'\s*,\s*mediaid\s*:\s*'(\d+)'",  # frontline video embed
                r'class="coveplayerid">([^<]+)<',                       # coveplayer
                r'<section[^>]+data-coveid="(\d+)"',                    # coveplayer from http://www.pbs.org/wgbh/frontline/film/real-csi/
                r'<input type="hidden" id="pbs_video_id_[0-9]+" value="([0-9]+)"/>',  # jwplayer
            ]

            media_id = self._search_regex(
                MEDIA_ID_REGEXES, webpage, 'media ID', fatal=False, default=None)
            if media_id:
                return media_id, presumptive_id, upload_date

            # Fronline video embedded via flp
            video_id = self._search_regex(
                r'videoid\s*:\s*"([\d+a-z]{7,})"', webpage, 'videoid', default=None)
            if video_id:
                # pkg_id calculation is reverse engineered from
                # http://www.pbs.org/wgbh/pages/frontline/js/flp2012.js
                prg_id = self._search_regex(
                    r'videoid\s*:\s*"([\d+a-z]{7,})"', webpage, 'videoid')[7:]
                if 'q' in prg_id:
                    prg_id = prg_id.split('q')[1]
                prg_id = int(prg_id, 16)
                getdir = self._download_json(
                    'http://www.pbs.org/wgbh/pages/frontline/.json/getdir/getdir%d.json' % prg_id,
                    presumptive_id, 'Downloading getdir JSON',
                    transform_source=strip_jsonp)
                return getdir['mid'], presumptive_id, upload_date

            for iframe in re.findall(r'(?s)<iframe(.+?)></iframe>', webpage):
                url = self._search_regex(
                    r'src=(["\'])(?P<url>.+?partnerplayer.+?)\1', iframe,
                    'player URL', default=None, group='url')
                if url:
                    break

            mobj = re.match(self._VALID_URL, url)

        player_id = mobj.group('player_id')
        if not display_id:
            display_id = player_id
        if player_id:
            player_page = self._download_webpage(
                url, display_id, note='Downloading player page',
                errnote='Could not download player page')
            video_id = self._search_regex(
                r'<div\s+id="video_([0-9]+)"', player_page, 'video ID')
        else:
            video_id = mobj.group('id')
            display_id = video_id

        return video_id, display_id, None

    def _real_extract(self, url):
        video_id, display_id, upload_date = self._extract_webpage(url)

        if isinstance(video_id, list):
            entries = [self.url_result(
                'http://video.pbs.org/video/%s' % vid_id, 'PBS', vid_id)
                for vid_id in video_id]
            return self.playlist_result(entries, display_id)

        try:
            info = self._download_json(
                'http://player.pbs.org/videoInfo/%s?format=json&type=partner' % video_id,
                display_id, 'Downloading video info JSON')
        except ExtractorError as e:
            if not isinstance(e.cause, compat_HTTPError) or e.cause.code != 404:
                raise
            # videoInfo API may not work for some videos, fallback to portalplayer API
            player = self._download_webpage(
                'http://player.pbs.org/portalplayer/%s' % video_id, display_id)
            info = self._parse_json(
                self._search_regex(
                    r'(?s)PBS\.videoData\s*=\s*({.+?});\n',
                    player, 'video data', default='{}'),
                display_id, transform_source=js_to_json, fatal=False)

        formats = []
        for encoding_name in ('recommended_encoding', 'alternate_encoding'):
            redirect = info.get(encoding_name)
            if not redirect:
                continue
            redirect_url = redirect.get('url')
            if not redirect_url:
                continue

            redirect_info = self._download_json(
                redirect_url + '?format=json', display_id,
                'Downloading %s video url info' % encoding_name)

            if redirect_info['status'] == 'error':
                raise ExtractorError(
                    '%s said: %s' % (
                        self.IE_NAME,
                        self._ERRORS.get(redirect_info['http_code'], redirect_info['message'])),
                    expected=True)

            format_url = redirect_info.get('url')
            if not format_url:
                continue

            if determine_ext(format_url) == 'm3u8':
                formats.extend(self._extract_m3u8_formats(
                    format_url, display_id, 'mp4', preference=1, m3u8_id='hls'))
            else:
                formats.append({
                    'url': format_url,
                    'format_id': redirect.get('eeid'),
                })
        self._sort_formats(formats)

        rating_str = info.get('rating')
        if rating_str is not None:
            rating_str = rating_str.rpartition('-')[2]
        age_limit = US_RATINGS.get(rating_str)

        subtitles = {}
        closed_captions_url = info.get('closed_captions_url')
        if closed_captions_url:
            subtitles['en'] = [{
                'ext': 'ttml',
                'url': closed_captions_url,
            }]

        # info['title'] is often incomplete (e.g. 'Full Episode', 'Episode 5', etc)
        # Try turning it to 'program - title' naming scheme if possible
        alt_title = info.get('program', {}).get('title')
        if alt_title:
            info['title'] = alt_title + ' - ' + re.sub(r'^' + alt_title + '[\s\-:]+', '', info['title'])

        return {
            'id': video_id,
            'display_id': display_id,
            'title': info['title'],
            'description': info.get('description') or info.get('program', {}).get('description'),
            'thumbnail': info.get('image_url'),
            'duration': int_or_none(info.get('duration')),
            'age_limit': age_limit,
            'upload_date': upload_date,
            'formats': formats,
            'subtitles': subtitles,
        }
