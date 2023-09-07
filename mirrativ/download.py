"""色々とダウンロードを行うやつ
"""

import re
from os import path, makedirs
from os.path import isfile, abspath
from typing import Final

from requests import get

from .common import CACHE_BASE_DIR
from .type import LiveInfo, MovieInfo

LIVEINFO_BASE_URL: Final[str] = "https://www.mirrativ.com/api/live/live"
HEADERS: Final[dict[str, str]] = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ja",
    "Cache-Control": "no-cache",
    "Origin": "https://www.mirrativ.com",
    "Referer": "https://www.mirrativ.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/116.0.0.0 Safari/537.36",
}
DEFAULT_TIMEOUT: Final[tuple[float, float]] = (3.0, 7.5)

# 必要なディレクトリが存在しなければ作成する
makedirs(CACHE_BASE_DIR, exist_ok=True)


def liveinfo(live_id: str) -> LiveInfo:
    """ライブ情報を取得します。

    Args:
        live_id (str): ライブID

    Returns:
        LiveInfo: ライブ情報

    Raises:
        requests.exceptions.Timeout: タイムアウト時
    """
    params = {"live_id": live_id}
    res = get(LIVEINFO_BASE_URL, params=params,
              headers=HEADERS, timeout=DEFAULT_TIMEOUT)
    data: LiveInfo = res.json()
    return data


def playlist(live_info: LiveInfo) -> str:
    """動画ファイルの情報を取得してキャッシュに保存します。

    Args:
        live_info (LiveInfo): ライブ情報

    Returns:
        str: 保存したファイルのパス

    Raises:
        requests.exceptions.Timeout: タイムアウト時
    """
    url: str = live_info["archive_url_hls"]
    res = get(url, headers=HEADERS, timeout=DEFAULT_TIMEOUT)

    filedir: str = path.join(CACHE_BASE_DIR, live_info["live_id"])
    makedirs(filedir, exist_ok=True)
    filepath: str = path.join(filedir, "playlist.m3u8")
    with open(filepath, mode="wt", encoding="utf-8") as file:
        file.write(res.text)

    return abspath(filepath)


def get_movie_info(live_info: LiveInfo) -> list[MovieInfo]:
    """動画情報の一覧を返却します。

    Args:
        live_info (LiveInfo): ライブ情報

    Returns:
        list[MovieInfo]: 動画情報の一覧
    """
    url_path: str = "/".join(
        live_info["archive_url_hls"].split("/")[0:-1]
    ) + "/"

    filedir: str = path.join(CACHE_BASE_DIR, live_info["live_id"])
    makedirs(filedir, exist_ok=True)
    filepath: str = path.join(filedir, "playlist.m3u8")
    if not isfile(filepath):
        # ファイルがなければダウンロードしてくる
        playlist(live_info)
        if not isfile(filepath):
            # エラーが一般的すぎると言われたけれど、めんどくさいので握り潰す
            # pylint: disable-next=broad-exception-raised
            raise Exception("原因不明")

    lines = []
    with open(filepath, mode="rt", encoding="utf-8") as file:
        lines = file.read().split("\n")

    pattern_extinf = re.compile(r"^#EXTINF:(.*),$")
    pattern_filename = re.compile(r"^(?!#).*\.ts$")
    info: list[MovieInfo] = []
    for line in lines:
        match_extinf = pattern_extinf.match(line)
        if match_extinf is not None:
            # #EXTINFが見つかった場合
            length = float(match_extinf.groups()[0])
            info.append({
                "movie_length": length,
                # 仮で値を入れておく
                "filename": "",
                "fileurl": "",
            })

        elif pattern_filename.match(line) is not None:
            # ファイル名が見つかった場合
            if len(info) <= 0:
                continue
            info[-1]["filename"] = line
            info[-1]["fileurl"] = url_path + line

    return info


def movie(url: str) -> str:
    """動画ファイルをダウンロードして保存します。

    Args:
        url (str): 動画ファイルのURL

    Returns:
        str: 保存したファイルの絶対パス

    Raises:
        requests.exceptions.Timeout: タイムアウト時
    """
    [live_id, movie_name] = url.split("/")[-2:]
    cache_dir = path.join(CACHE_BASE_DIR, live_id)
    filename: str = movie_name
    filepath = path.join(cache_dir, filename)
    if isfile(filepath):
        # 既にダウンロード済みであれば何もしない
        return abspath(filepath)

    res = get(url, headers=HEADERS, timeout=DEFAULT_TIMEOUT)
    makedirs(cache_dir, exist_ok=True)

    with open(filepath, mode="wb") as file:
        file.write(res.content)

    return abspath(filepath)
