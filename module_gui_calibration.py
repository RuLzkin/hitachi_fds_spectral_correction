from pathlib import Path
from subprocess import Popen
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QCheckBox,
    QButtonGroup,
    QRadioButton,
    QFrame,
    QFileDialog,
    QMessageBox
)
from PySide6.QtCore import QTranslator, QLocale, QLibraryInfo
from module_fds import loadFDS
from module_calibration import Calibrator

LOCALIZE_JP = False


class VerticalLine(QFrame):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication, parent=None) -> None:
        super().__init__(parent)

        self.calibrator = Calibrator()
        self.app = app
        self.core = CalibratorWidget(self, calibrator=self.calibrator)

        self.initUI()

    def initUI(self):
        self.setCentralWidget(self.core)
        # self.resize(1200, 800)
        self.setWindowTitle("蛍光分光光度計 スペクトル補正ツール")

    def start(self):
        self.show()
        self.app.exec()


class CalibratorWidget(QWidget):
    def __init__(self, parent=None, calibrator: Calibrator = None):
        super().__init__(parent)

        self.calibrator = Calibrator() if calibrator is None else calibrator

        lay_main_message = QVBoxLayout()
        lay_inout_inst = QHBoxLayout()

        lay_inout = self.init_input_output_layout()
        lay_inst = self.init_instrument_layout()

        lay_inout_inst.addLayout(lay_inst)
        lay_inout_inst.addWidget(VerticalLine())
        lay_inout_inst.addLayout(lay_inout)

        self.le_message = QLineEdit("", self)

        lay_main_message.addLayout(lay_inout_inst)
        lay_main_message.addWidget(self.le_message)

        self.setLayout(lay_main_message)

        self.update_start_buttton()

    def init_input_output_layout(self):
        lay_inout = QVBoxLayout()

        self.le_input_filepath = QLineEdit("", self)
        self.le_input_filepath.setPlaceholderText("Input File (*.txt)")
        self.le_input_filepath.setMinimumWidth(200)
        btn_input_filepath = QPushButton("選択", self)
        btn_input_filepath.clicked.connect(self.btn_select_input_clicked)
        lay_input_path = QHBoxLayout()
        lay_input_path.addSpacing(20)
        lay_input_path.addWidget(self.le_input_filepath)
        lay_input_path.addWidget(btn_input_filepath)

        self.le_output_filepath = QLineEdit("", self)
        self.le_output_filepath.setPlaceholderText("Output Directory")
        self.le_output_filepath.setMinimumWidth(300)
        self.le_output_filepath.setEnabled(False)
        self.le_output_filepath.textChanged[str].connect(self.check_output_dir)
        self.btn_output_filepath = QPushButton("選択", self)
        self.btn_output_filepath.clicked.connect(self.btn_select_output_clicked)
        self.btn_output_filepath.setEnabled(False)
        self.check_output_filepath = QCheckBox("入力と同じ", self)
        self.check_output_filepath.setChecked(True)
        self.check_output_filepath.stateChanged.connect(self.update_output_dir)
        lay_output_path = QHBoxLayout()
        lay_output_path.addSpacing(20)
        lay_output_path.addWidget(self.le_output_filepath)
        lay_output_path.addWidget(self.btn_output_filepath)
        lay_output_path.addWidget(self.check_output_filepath)

        self.grp_calib = QButtonGroup(self)
        self.rad_off_to_on = QRadioButton("OFF → ON")
        self.rad_on_to_off = QRadioButton("ON → OFF")
        self.grp_calib.addButton(self.rad_off_to_on, 0)
        self.grp_calib.addButton(self.rad_on_to_off, 1)
        self.check_calib_auto = QCheckBox("自動", self)
        self.check_calib_auto.stateChanged.connect(self.update_correction_mode)
        self.rad_off_to_on.setChecked(True)
        self.check_calib_auto.setChecked(True)

        lay_calib_v = QVBoxLayout()
        lay_calib_v.addWidget(self.rad_off_to_on)
        lay_calib_v.addWidget(self.rad_on_to_off)
        lay_calib_v.addWidget(self.check_calib_auto)
        lay_calib = QHBoxLayout()
        lay_calib.addSpacing(20)
        lay_calib.addLayout(lay_calib_v)

        self.btn_start = QPushButton("補正開始", self)
        self.btn_start.clicked.connect(self.start_calibration)

        self.btn_start.setFixedWidth(300)

        lay_inout.addWidget(QLabel("入力ファイル"))
        lay_inout.addLayout(lay_input_path)
        lay_inout.addWidget(QLabel("出力先"))
        lay_inout.addLayout(lay_output_path)
        lay_inout.addWidget(QLabel("スペクトル補正"))
        lay_inout.addLayout(lay_calib)
        lay_inout.addWidget(self.btn_start)
        lay_inout.addSpacing(20)

        lay_inout.addStretch()
        return lay_inout

    def init_instrument_layout(self):
        lay_inst = QVBoxLayout()

        self.le_ex_short_path = QLineEdit("", self)
        self.le_em_short_path = QLineEdit("", self)
        self.le_ex_long_path = QLineEdit("", self)
        self.le_em_long_path = QLineEdit("", self)

        self.le_ex_short_path.setPlaceholderText("EX Short Instrument File (*.txt)")
        self.le_em_short_path.setPlaceholderText("EM Short Instrument File (*.txt)")
        self.le_ex_long_path.setPlaceholderText("EX Long Instrument File (*.txt)")
        self.le_em_long_path.setPlaceholderText("EM Long Instrument File (*.txt)")

        self.le_ex_short_path.setMinimumWidth(200)
        self.le_em_short_path.setMinimumWidth(200)
        self.le_ex_long_path.setMinimumWidth(200)
        self.le_em_long_path.setMinimumWidth(200)

        self.le_ex_short_path.setMaximumWidth(400)
        self.le_em_short_path.setMaximumWidth(400)
        self.le_ex_long_path.setMaximumWidth(400)
        self.le_em_long_path.setMaximumWidth(400)

        self.check_ex_short = QCheckBox("励起スペクトル（短波長）", self)
        self.check_em_short = QCheckBox("蛍光スペクトル（短波長）", self)
        self.check_ex_long = QCheckBox("励起スペクトル（長波長）", self)
        self.check_em_long = QCheckBox("蛍光スペクトル（長波長）", self)

        self.btn_ex_short_path = QPushButton("選択", self)
        self.btn_em_short_path = QPushButton("選択", self)
        self.btn_ex_long_path = QPushButton("選択", self)
        self.btn_em_long_path = QPushButton("選択", self)

        lay_ex_short_path = QHBoxLayout()
        lay_em_short_path = QHBoxLayout()
        lay_ex_long_path = QHBoxLayout()
        lay_em_long_path = QHBoxLayout()

        self.check_ex_short.stateChanged.connect(self.update_exs_enable)
        self.check_em_short.stateChanged.connect(self.update_ems_enable)
        self.check_ex_long.stateChanged.connect(self.update_exl_enable)
        self.check_em_long.stateChanged.connect(self.update_eml_enable)

        self.check_ex_short.setChecked(True)
        self.check_em_short.setChecked(True)
        self.check_ex_long.setChecked(True)
        self.check_em_long.setChecked(True)

        self.btn_ex_short_path.setFixedWidth(80)
        self.btn_em_short_path.setFixedWidth(80)
        self.btn_ex_long_path.setFixedWidth(80)
        self.btn_em_long_path.setFixedWidth(80)

        self.btn_ex_short_path.clicked.connect(self.btn_select_exs_clicked)
        self.btn_em_short_path.clicked.connect(self.btn_select_ems_clicked)
        self.btn_ex_long_path.clicked.connect(self.btn_select_exl_clicked)
        self.btn_em_long_path.clicked.connect(self.btn_select_eml_clicked)

        lay_ex_short_path.addSpacing(20)
        lay_em_short_path.addSpacing(20)
        lay_ex_long_path.addSpacing(20)
        lay_em_long_path.addSpacing(20)

        lay_ex_short_path.addWidget(self.le_ex_short_path)
        lay_em_short_path.addWidget(self.le_em_short_path)
        lay_ex_long_path.addWidget(self.le_ex_long_path)
        lay_em_long_path.addWidget(self.le_em_long_path)

        lay_ex_short_path.addWidget(self.btn_ex_short_path)
        lay_em_short_path.addWidget(self.btn_em_short_path)
        lay_ex_long_path.addWidget(self.btn_ex_long_path)
        lay_em_long_path.addWidget(self.btn_em_long_path)

        lay_import = QHBoxLayout()
        btn_import = QPushButton("読み込み", self)
        btn_import.setFixedWidth(120)
        btn_import.clicked.connect(self.btn_import_inst)
        self.lbl_inst_status = QLabel("読み込まれていません", self)
        lay_import.addWidget(btn_import)
        lay_import.addWidget(self.lbl_inst_status)

        lay_inst.addWidget(QLabel("装置関数 （チェックを外した箇所は無補正として扱います）"))
        lay_inst.addSpacing(10)
        lay_inst.addWidget(self.check_ex_short)
        lay_inst.addLayout(lay_ex_short_path)
        lay_inst.addWidget(self.check_em_short)
        lay_inst.addLayout(lay_em_short_path)
        lay_inst.addWidget(self.check_ex_long)
        lay_inst.addLayout(lay_ex_long_path)
        lay_inst.addWidget(self.check_em_long)
        lay_inst.addLayout(lay_em_long_path)
        lay_inst.addSpacing(20)
        lay_inst.addLayout(lay_import)
        lay_inst.addSpacing(20)

        lay_inst.addStretch()
        return lay_inst

    def btn_select_input_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, filter="テキストファイル (*.txt)")
        self.le_input_filepath.setText(path)
        self.update_output_dir()
        self.update_correction_mode()

    def btn_select_output_clicked(self):
        path = QFileDialog.getExistingDirectory(self)
        self.le_output_filepath.setText(path)

    def update_output_dir(self):
        _checked = self.check_output_filepath.isChecked()
        self.le_output_filepath.setEnabled(not _checked)
        self.btn_output_filepath.setEnabled(not _checked)
        if not _checked:
            return
        _input_filepath = Path(self.le_input_filepath.text())
        if _input_filepath.is_file():
            _dir = _input_filepath.parent
            self.le_output_filepath.setText(_dir.as_posix())

    def check_output_dir(self, text):
        _path = Path(text)
        if _path.is_dir() and text != "":
            self.calibrator.set_output_dir(text)
        else:
            self.calibrator.set_output_dir(None)
        self.update_start_buttton()

    def update_correction_mode(self):
        _is_auto = self.check_calib_auto.isChecked()
        self.rad_off_to_on.setEnabled(not _is_auto)
        self.rad_on_to_off.setEnabled(not _is_auto)
        if not _is_auto:
            return
        _input_path = self.le_input_filepath.text()
        if _input_path == "":
            return
        if not Path(_input_path).is_file():
            return

        _, _, header = loadFDS(_input_path)
        if header.CorrSpectra:
            self.rad_on_to_off.setChecked(True)
        else:
            self.rad_off_to_on.setChecked(True)

    def update_start_buttton(self):
        _ok_inst, _ok_dir = self.calibrator.is_ready_detail()
        _ready = _ok_inst and _ok_dir
        _outputdir = Path(self.calibrator.output_dir).resolve().as_posix()
        _msg_ready = "補正準備完了" if _ready else "補正準備ができていません"
        _msg_inst = "装置関数：完了" if _ok_inst else "装置関数を入力してください"
        _msg_dir = "出力フォルダ：{0}".format(_outputdir) if _ok_dir else "出力フォルダを指定してください"
        self.btn_start.setEnabled(_ready)
        _color = "green" if _ready else "red"
        self.le_message.setStyleSheet(f"color: {_color}")
        self.le_message.setText(f"{_msg_ready}（{_msg_inst} ／ {_msg_dir}）")

    def start_calibration(self):
        _filepath_input = self.le_input_filepath.text()

        if self.check_calib_auto.isChecked():
            _bool_off_to_on = None
        else:
            _bool_off_to_on = self.grp_calib.checkedId() == 0

        if not Path(_filepath_input).is_file():
            _ = QMessageBox.critical(
                self,
                "指定したファイルが存在しません",
                "指定されたファイルが存在しません\n（アクセス権限による問題の可能性もあります）",
                QMessageBox.Ok)
            return
        try:
            _path_result: Path = self.calibrator.calibrate(_filepath_input, _bool_off_to_on)
            btn_result = QMessageBox.information(
                self,
                "スペクトル補正完了",
                f"スペクトル補正が完了しました。\n出力結果: {_path_result.resolve().as_posix()}",
                QMessageBox.Open, QMessageBox.Ok)
            if btn_result == QMessageBox.Open:
                Popen(["explorer", str(_path_result.resolve().parent)], shell=True)
        except Exception as e:  # noqa
            QMessageBox.critical(
                self,
                "スペクトル補正失敗",
                f"スペクトル補正が失敗しました。\nError: {e}\n\n連続する場合は担当者にご連絡ください。",
                QMessageBox.Ok)
            raise e

    def update_exs_enable(self):
        bool_enable = self.check_ex_short.isChecked()
        self.le_ex_short_path.setEnabled(bool_enable)
        self.btn_ex_short_path.setEnabled(bool_enable)

    def update_ems_enable(self):
        bool_enable = self.check_em_short.isChecked()
        self.le_em_short_path.setEnabled(bool_enable)
        self.btn_em_short_path.setEnabled(bool_enable)

    def update_exl_enable(self):
        bool_enable = self.check_ex_long.isChecked()
        self.le_ex_long_path.setEnabled(bool_enable)
        self.btn_ex_long_path.setEnabled(bool_enable)

    def update_eml_enable(self):
        bool_enable = self.check_em_long.isChecked()
        self.le_em_long_path.setEnabled(bool_enable)
        self.btn_em_long_path.setEnabled(bool_enable)

    def btn_select_exs_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self)
        self.le_ex_short_path.setText(path)

    def btn_select_ems_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self)
        self.le_em_short_path.setText(path)

    def btn_select_exl_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self)
        self.le_ex_long_path.setText(path)

    def btn_select_eml_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self)
        self.le_em_long_path.setText(path)

    def btn_import_inst(self):
        path_exs = self.le_ex_short_path.text() if self.check_ex_short.isChecked() else None
        path_ems = self.le_em_short_path.text() if self.check_em_short.isChecked() else None
        path_exl = self.le_ex_long_path.text() if self.check_ex_long.isChecked() else None
        path_eml = self.le_em_long_path.text() if self.check_em_long.isChecked() else None
        try:
            self.calibrator.set_mat_inst_func(path_exs, path_ems, path_exl, path_eml)
            self.lbl_inst_status.setText("読み込みに成功しました")
        except:  # noqa
            self.lbl_inst_status.setText("読み込みに失敗しました")
            self.calibrator.clear_mat_inst_func()

        self.update_start_buttton()


if __name__ == "__main__":
    app = QApplication()
    if LOCALIZE_JP:
        translator = QTranslator(app)
        locale = QLocale.system().name()
        path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
        translator.load('qt_%s' % locale, path)
        app.installTranslator(translator)
    window = MainWindow(app)
    window.start()
