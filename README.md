## motivation
suumoに掲載されている安い賃貸物件を、日本全国から一括で取得したい。

## env
python 3.8.2

## 実行手順
1. モジュールのインストール（`python3 main.py`を実行してみて、エラー出たモジュールを`pip install {module name}`すればOK）
2. `python3 main.py`

## 実行後
1. 生成されたcsvファイルをGoogle Driveにアップロードする
2. それをスプレッドシートとして開く
3. C列の先頭に付与されてしまう`'`を削除する
4. 行1までを固定する

## tips
- [VScode上でimportの警告が消えない場合](https://startlab.jp/learning-python/vscode-settings/)
