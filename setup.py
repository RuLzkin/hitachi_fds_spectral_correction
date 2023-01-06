# -*- coding: utf-8 -*-
"""
python setup.py build
"""

import sys
from cx_Freeze import setup, Executable

# 依存ファイルをコピーするか否か
copyDependentFiles = False
# コマンドラインを表示しないかどうか
silent = True

# プラットフォームごとの設定。GUIを用いないときはif文ごと削除すると良い
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# パッケージやファイルに関する設定 packagesに関してはなにも記載する必要なし
packages = []
# 必要なパッケージを指定。動作に必須
includes = ["PySide6", "numpy"]
# includes = []
# 不要なパッケージを指定。きちんと設定できると高速起動高速動作
excludes = ["PyQt5", "PySide2", "pandas", "tkinter", "matplotlib", "scipy", "numba"]
# excludes = []
# 一緒にコピーするファイルを指定
incfiles = []

str_ver = "1.1"

# exe にしたい python ファイル
my_exe = Executable(
    script='module_gui_calibration.py',
    base=base,
    targetName="SpectralCorrectionTool_" + str_ver + ".exe"
)

# 設定の有効化。バージョンや名前はここで設定
# （適用されていない気もする）
setup(
    name='F7000_Spectral_Correction',
    version=str_ver,
    options={'build_exe': {
        'include_files': incfiles, 'includes': includes,
        'excludes': excludes, 'packages': packages}
    },
    executables=[my_exe]
)
