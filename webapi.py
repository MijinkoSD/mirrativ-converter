"""Web API
"""

from os.path import basename

from fastapi import FastAPI
from fastapi.responses import Response, FileResponse

from mirrativ import download, convert

app = FastAPI()
# app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.get("/")
def read_root() -> Response:
    """ルートパスのレスポンス。

    Returns:
        Response: 404 Not Found
    """
    return Response(status_code=404)


@app.get("/archive/{live_id}/m3u8")
def get_m3u8(live_id: str) -> FileResponse:
    """playlist.m3u8を返却します。

    Args:
        live_id (str): ライブID

    Returns:
        FileResponse: playlist.m3u8が含まれるレスポンス
    """
    info = download.liveinfo(live_id)
    filepath = download.playlist(info)

    return FileResponse(
        path=filepath,
        media_type="text/plain",
        filename=basename(filepath)
    )


@app.get("/archive/{live_id}/audio/{file_name}")
# pylint: disable-next=invalid-name
def get_audio(live_id: str, file_name: str) -> FileResponse:
    """動画ファイルを音声に変換して返却します。

    Args:
        live_id (str): 動画ID
        file_name (str): ファイル名

    Returns:
        FileResponse: 音声ファイルが含まれるレスポンス
    """
    info = download.liveinfo(live_id)
    url = "/".join(info["archive_url_hls"].split("/")[0:-1]) + file_name

    filepath: str = download.movie(url)
    convert.file(filepath, basename(filepath))

    return FileResponse(
        path=filepath,
        # media_type="audio/mpeg"
        filename=basename(filepath)
    )
