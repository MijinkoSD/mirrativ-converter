"""動画を音声に変換するやつ
"""

import ffmpeg
from os import path


def file(filepath: str, outdir: str = "./") -> None:
    output_filename: str = path.splitext(path.basename(filepath))[0]+".mp3"
    output_filepath: str = path.join(outdir, output_filename)
    stream = ffmpeg.input(filepath).output(output_filepath, format="mp3")
    ffmpeg.run(stream)
