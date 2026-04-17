import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QTextEdit, QPushButton
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

class InstallThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, venv_python, req_file, marker_file):
        super().__init__()
        self.venv_python = venv_python
        self.req_file = req_file
        self.marker_file = marker_file

    def run_cmd(self, cmd_list):
        creationflags = 0
        if os.name == 'nt' and hasattr(subprocess, 'CREATE_NO_WINDOW'):
            creationflags = getattr(subprocess, 'CREATE_NO_WINDOW')
            
        process = subprocess.Popen(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=creationflags
        )
        if process.stdout is not None:
            for line in process.stdout:
                self.progress_signal.emit(line.strip())
        process.wait()
        return process.returncode

    def run(self):
        self.progress_signal.emit("تحديث مدير الحزم (pip)...")
        self.run_cmd([self.venv_python, "-m", "pip", "install", "--upgrade", "pip"])

        self.progress_signal.emit("\n\nتحميل مكتبة PyTorch ودعم الـ GPU (CUDA 12.1)...")
        self.progress_signal.emit("ملاحظة: حجم المكتبة كبير وقد يستغرق التحميل بعض الوقت.\n")
        cmd_torch = [
            self.venv_python, "-m", "pip", "install", "torch", "torchvision", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/cu121"
        ]
        self.run_cmd(cmd_torch)

        if os.path.exists(self.req_file):
            self.progress_signal.emit("\n\nتثبيت باقي المكتبات المطلوبة...")
            self.run_cmd([self.venv_python, "-m", "pip", "install", "-r", self.req_file])

        # Write marker
        try:
            with open(self.marker_file, 'w') as f:
                f.write("done")
        except:
            pass

        self.progress_signal.emit("\n\nاكتمل الإعداد المحلي بنجاح! سيتم إطلاق التطبيق الآن...")
        self.finished_signal.emit(True)


class SetupUI(QWidget):
    def __init__(self, venv_python, req_file, marker_file):
        super().__init__()
        self.venv_python = venv_python
        self.req_file = req_file
        self.marker_file = marker_file
        self.init_ui()
        self.start_install()

    def init_ui(self):
        self.setWindowTitle("إعداد مستلزمات AxoLexis المسبقة")
        self.setFixedSize(600, 400)
        self.setStyleSheet("background-color: #1a1b26; color: #a9b1d6;")

        layout = QVBoxLayout(self)

        self.title_label = QLabel("يتم الآن إعداد بيئة AxoLexis لأول مرة...")
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #16161e; color: #7aa2f7; font-family: Consolas;")
        layout.addWidget(self.log_output)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Indeterminate
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #7aa2f7; border-radius: 5px; text-align: center; } QProgressBar::chunk { background-color: #7aa2f7; }")
        layout.addWidget(self.progress_bar)
        
        self.start_btn = QPushButton("بدء التطبيق")
        self.start_btn.setStyleSheet("QPushButton { background-color: #3d59a1; border-radius: 5px; padding: 8px; font-weight: bold; } QPushButton:disabled { background-color: #16161e; color: #565f89; }")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.close)
        layout.addWidget(self.start_btn)

    def start_install(self):
        self.thread = InstallThread(self.venv_python, self.req_file, self.marker_file)
        self.thread.progress_signal.connect(self.append_log)
        self.thread.finished_signal.connect(self.on_finish)
        self.thread.start()

    def append_log(self, text):
        if text.strip():
            self.log_output.append(text)
            # scroll to bottom
            sb = self.log_output.verticalScrollBar()
            sb.setValue(sb.maximum())

    def on_finish(self, success):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.start_btn.setEnabled(True)
        self.title_label.setText("اكتمل الإعداد!")
        self.start_btn.setText("إغلاق وبدء AxoLexis")

def run_setup_ui(venv_python, req_file, marker_file):
    app = QApplication(sys.argv)
    window = SetupUI(venv_python, req_file, marker_file)
    window.show()
    app.exec()

if __name__ == "__main__":
    if len(sys.argv) >= 4:
        run_setup_ui(sys.argv[1], sys.argv[2], sys.argv[3])
