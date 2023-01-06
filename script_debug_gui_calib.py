from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator, QLocale, QLibraryInfo
from module_gui_calibration import MainWindow

app = QApplication()
translator = QTranslator(app)
locale = QLocale.system().name()
path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
translator.load('qt_%s' % locale, path)
print("locale:", locale)
print("path:", path)
app.installTranslator(translator)

window = MainWindow(app)
window.core.check_output_filepath.setChecked(False)
window.core.le_output_filepath.setText("path/to/dir")

window.core.le_input_filepath.setText("path/to/inputfile.TXT")

window.core.le_ex_short_path.setText("path/to/inputfile_exs.TXT")
window.core.le_em_short_path.setText("path/to/inputfile_ems.TXT")
window.core.le_ex_long_path.setText("path/to/inputfile_exl.TXT")
window.core.le_em_long_path.setText("path/to/inputfile_eml.TXT")

window.core.check_ex_long.setChecked(False)
window.core.check_em_long.setChecked(False)
window.core.btn_import_inst()
window.core.update_correction_mode()

window.start()
