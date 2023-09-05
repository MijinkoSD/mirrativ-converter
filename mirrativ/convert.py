"""動画を音声に変換するやつ
"""

from os import path

import ffmpeg


def file(filepath: str, outdir: str = "./") -> None:
    """ファイルをmp3に変換します。

    Args:
        filepath (str): ファイルパス
        outdir (str, optional): 出力先ディレクトリ。 既定で"./"。
    """

    output_filename: str = path.splitext(path.basename(filepath))[0]+".mp3"
    output_filepath: str = path.join(outdir, output_filename)

    if path.isfile(output_filepath):
        # ファイルが既に存在していた場合は変換しない
        return

    stream = ffmpeg.input(filepath).output(output_filepath, format="mp3")
    ffmpeg.run(stream)
