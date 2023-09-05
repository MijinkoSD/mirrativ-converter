"""型をまとめているモジュール
"""

from typing import TypedDict


class LiveInfo(TypedDict):
    """ライブ情報の型。
    本来は色々格納されているけれど、現状必要最低限の定義しかしていない。

    Args:
        TypedDict (_type_): _description_
    """
    archive_url_hls: str
    live_id: str


class MovieInfo(TypedDict):
    """動画ファイルの型。

    Args:
        TypedDict (_type_): _description_
    """
    filename: str
    fileurl: str
    movie_length: float
