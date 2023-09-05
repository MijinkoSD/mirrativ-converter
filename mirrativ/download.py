"""色々とダウンロードを行うやつ
"""

import re
from os import path, makedirs
from typing import Final

from requests import get

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
CACHE_BASE_DIR: Final[str] = path.join("cache")

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


def playlist(live_info: LiveInfo) -> None:
    """動画ファイルの情報を取得してキャッシュに保存します。

    Args:
        live_info (LiveInfo): ライブ情報

    Returns:
        list[str]: URLのlist

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


def get_urls(live_info: LiveInfo) -> list[MovieInfo]:
    """動画のURLの一覧を返却します。

    Args:
        live_info (LiveInfo): _description_

    Returns:
        list[str]: _description_
    """
    url_path: str = "/".join(
        live_info["archive_url_hls"].split("/")[0:-1]
    ) + "/"

    filedir: str = path.join(CACHE_BASE_DIR, live_info["live_id"])
    makedirs(filedir, exist_ok=True)
    filepath: str = path.join(filedir, "playlist.m3u8")

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
        str: 保存したファイルの名前

    Raises:
        requests.exceptions.Timeout: タイムアウト時
    """
    [live_id, movie_name] = url.split("/")[-2:]
    filename: str = movie_name
    res = get(url, headers=HEADERS, timeout=DEFAULT_TIMEOUT)
    cache_dir = path.join(CACHE_BASE_DIR, live_id)
    makedirs(cache_dir, exist_ok=True)

    with open(path.join(cache_dir, filename), mode="wb") as file:
        file.write(res.content)

    return filename
