"""色々とダウンロードを行うやつ
"""

import re
from os import path, makedirs
from typing import Final

from requests import get

from .type import LiveInfo

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
CACHE_DIR: Final[str] = path.join("cache")

# 必要なディレクトリが存在しなければ作成する
makedirs(CACHE_DIR, exist_ok=True)


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


def playlist_urls(live_info: LiveInfo) -> list[str]:
    """動画のURLの一覧を返却します。

    Args:
        live_info (LiveInfo): ライブ情報

    Returns:
        list[str]: URLのlist

    Raises:
        requests.exceptions.Timeout: タイムアウト時
    """
    url: str = live_info["archive_url_hls"]
    url_path: str = "/".join(url.split("/")[0:-1]) + "/"
    res = get(url, headers=HEADERS, timeout=DEFAULT_TIMEOUT)

    splited = res.text.split("\n")
    pattern = re.compile(r"^(?!#).*\.ts$")
    names: list[str] = []
    for line in splited:
        if (pattern.match(line) is None):
            continue
        names.append(line)
    return [url_path + name for name in names]


def movie(url: str) -> str:
    """動画ファイルをダウンロードして保存します。

    Args:
        url (str): 動画ファイルのURL

    Returns:
        str: 保存したファイルの名前

    Raises:
        requests.exceptions.Timeout: タイムアウト時
    """
    filename: str = "_".join(url.split("/")[-2:])
    res = get(url, headers=HEADERS, timeout=DEFAULT_TIMEOUT)

    with open(path.join(CACHE_DIR, filename), mode="wb") as file:
        file.write(res.content)

    return filename
