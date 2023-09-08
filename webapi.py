"""Web API
"""

from os.path import basename, dirname
from logging import getLogger

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, FileResponse, JSONResponse

from mirrativ import download, convert

app = FastAPI()
# app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


def print_log(message: str) -> None:
    """標準出力にメッセージを出力します。

    Args:
        message (str): 出力するメッセージ
    """
    logger = getLogger("uvicorn")
    logger.info(message)


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


@app.get("/archive/{live_id}/m3u8/json")
def get_m3u8_json(live_id: str) -> JSONResponse:
    """playlist.m3u8の内容をJSONで返却します。

    Args:
        live_id (str): ライブID

    Returns:
        JSONResponse: playlist.m3u8をJSON化したレスポンス
    """
    info = download.liveinfo(live_id)
    movie_info = download.get_movie_info(info)

    return JSONResponse(movie_info)


@app.get("/archive/{live_id}/audio/{file_name}")
# pylint: disable-next=invalid-name
def get_audio(live_id: str, file_name: str) -> FileResponse:
    """動画ファイルを音声に変換して返却します。

    Args:
        live_id (str): 動画ID
        file_name (str): 変換する動画ファイルの名前

    Returns:
        FileResponse: 音声ファイルが含まれるレスポンス

    Raises:
        HTTPException: 必要な情報が取得できなかった時
    """
    info = download.liveinfo(live_id)
    archive_url_hls = info["archive_url_hls"]
    if archive_url_hls is None:
        return HTTPException(status_code=400)
    url = "/".join(archive_url_hls.split("/")[0:-1]) + "/" + file_name

    filepath: str = download.movie(url)
    audio_path = convert.file(filepath, dirname(filepath))

    return FileResponse(
        path=audio_path,
        # media_type="audio/mpeg"
        filename=basename(audio_path)
    )
