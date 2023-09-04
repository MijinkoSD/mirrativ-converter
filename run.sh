#!/usr/bin/env bash

if !(type "python3.11" > /dev/null); then
    echo -e "Python3.11がインストールされていません。\nインストールしてから再度実行してください。";
    exit
fi

if [[ ! -e "./.venv/bin/activate" ]]; then
    python3.11 -m venv .venv
    chmod u+x .venv/bin/activate
fi

source .venv/bin/activate

pip install -U pip
pip install -r ./requirements.txt

# この下で任意のファイルの実行をする
python ./sample/hello.py


# 終了時は自動的にdeactivateされる
