# Hitachi-Hightech F7000 Series FDS-File Spectral Correction Tool

日立ハイテクサイエンス社製 F7000 シリーズの測定結果の補正用スクリプト

Python 3.9で開発しています。

## Compile
### CxFreeze
本フォルダでターミナル（コマンドプロンプト）から以下を実行
```sh
python setup.py build
```
コンパイルのオプションは setup.py に記載されています
（パラメータなどはCxFreezeのリファレンスをご参照ください）。

### PyInstaller
本フォルダでターミナル（コマンドプロンプト）から以下を実行
```sh
pyinstaller module_gui_calibration.py.py –noconsole -onefile
```
コンパイルのオプションはspecファイルにも記載されています
（パラメータなどはPyInstallerのリファレンスをご参照ください）。

（-onefileオプションを削除して実行すると、1ファイルではなくなりますが動作が早くなります）


## Update
2023/03/27 Readmeにコンパイル方法を追加
