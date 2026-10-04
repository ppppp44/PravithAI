import os
import shutil
import subprocess
import sys
import webbrowser

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from installer.model_downloader import ModelDownloader


FAST_MODEL = "qwen3:1.7b"
VISION_MODEL = "qwen3-vl:4b"

OLLAMA_INSTALL_COMMAND = (
    "curl -fsSL https://ollama.com/install.sh | sh"
)

OLLAMA_DOWNLOAD_URL = "https://ollama.com/download"


# ==========================================================
# OLLAMA INSTALLER
# ==========================================================

class OllamaInstaller(QThread):
    output = Signal(str)
    finished_install = Signal(bool, str)

    def run(self):
        try:
            self.output.emit(
                "Starting Ollama installer..."
            )

            process = subprocess.Popen(
                [
                    "pkexec",
                    "sh",
                    "-c",
                    OLLAMA_INSTALL_COMMAND,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            if process.stdout:
                for line in process.stdout:
                    line = line.strip()

                    if line:
                        self.output.emit(line)

            return_code = process.wait()

            if return_code == 0:
                self.finished_install.emit(
                    True,
                    "Ollama installed successfully.",
                )
            else:
                self.finished_install.emit(
                    False,
                    "Ollama installation was cancelled or failed.",
                )

        except Exception as e:
            self.finished_install.emit(
                False,
                str(e),
            )


# ==========================================================
# SYSTEM CHECKER
# ==========================================================

class SetupChecker(QThread):
    result = Signal(bool, bool, bool)

    def run(self):
        ollama_found = (
            shutil.which("ollama") is not None
        )

        if not ollama_found:
            self.result.emit(
                False,
                False,
                False,
            )
            return

        try:
            output = subprocess.check_output(
                [
                    "ollama",
                    "list",
                ],
                text=True,
                stderr=subprocess.STDOUT,
            )

            fast_found = FAST_MODEL in output
            vision_found = VISION_MODEL in output

            self.result.emit(
                True,
                fast_found,
                vision_found,
            )

        except Exception:
            self.result.emit(
                True,
                False,
                False,
            )


# ==========================================================
# SETUP WIZARD
# ==========================================================

class SetupWizard(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "PravithAI Setup"
        )

        self.setFixedSize(
            600,
            500,
        )

        self.downloader = None
        self.ollama_installer = None
        self.checker = None

        self.ollama_found = False
        self.fast_found = False
        self.vision_found = False

        self.setup_success = False

        self.setStyleSheet(
            """
            QWidget {
                background: #11111b;
                color: #cdd6f4;
                font-family: "JetBrains Mono";
            }

            QLabel#title {
                font-size: 26px;
                font-weight: bold;
                color: #cdd6f4;
            }

            QLabel#subtitle {
                font-size: 13px;
                color: #a6adc8;
            }

            QLabel#status {
                font-size: 14px;
                color: #89b4fa;
            }

            QLabel#models {
                font-size: 13px;
                color: #a6adc8;
            }

            QLabel#download_status {
                font-size: 12px;
                color: #a6adc8;
            }

            QPushButton {
                background: #89b4fa;
                color: #11111b;
                border: none;
                border-radius: 10px;
                padding: 12px 18px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #b4befe;
            }

            QPushButton:disabled {
                background: #45475a;
                color: #6c7086;
            }

            QProgressBar {
                background: #1e1e2e;
                border: none;
                border-radius: 7px;
                height: 16px;
                text-align: center;
            }

            QProgressBar::chunk {
                background: #89b4fa;
                border-radius: 7px;
            }
            """
        )

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            40,
            35,
            40,
            35,
        )

        layout.setSpacing(
            16
        )

        # --------------------------------------------------
        # HEADER
        # --------------------------------------------------

        title = QLabel(
            "PravithAI"
        )

        title.setObjectName(
            "title"
        )

        subtitle = QLabel(
            "Local AI setup wizard"
        )

        subtitle.setObjectName(
            "subtitle"
        )

        # --------------------------------------------------
        # STATUS
        # --------------------------------------------------

        self.status = QLabel(
            "Checking your system..."
        )

        self.status.setObjectName(
            "status"
        )

        self.models = QLabel()

        self.models.setObjectName(
            "models"
        )

        self.download_status = QLabel()

        self.download_status.setObjectName(
            "download_status"
        )

        # --------------------------------------------------
        # PROGRESS
        # --------------------------------------------------

        self.progress = QProgressBar()

        self.progress.setRange(
            0,
            0,
        )

        self.progress.setVisible(
            False
        )

        # --------------------------------------------------
        # BUTTONS
        # --------------------------------------------------

        self.continue_button = QPushButton(
            "Continue"
        )

        self.continue_button.setEnabled(
            False
        )

        self.continue_button.clicked.connect(
            self.continue_setup
        )

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.cancel_button.clicked.connect(
            self.cancel_setup
        )

        # --------------------------------------------------
        # LAYOUT
        # --------------------------------------------------

        layout.addWidget(
            title
        )

        layout.addWidget(
            subtitle
        )

        layout.addSpacing(
            10
        )

        layout.addWidget(
            self.status
        )

        layout.addWidget(
            self.models
        )

        layout.addSpacing(
            10
        )

        layout.addWidget(
            self.download_status
        )

        layout.addWidget(
            self.progress
        )

        layout.addSpacing(
            10
        )

        layout.addWidget(
            self.continue_button
        )

        layout.addWidget(
            self.cancel_button
        )

        # --------------------------------------------------
        # START CHECK
        # --------------------------------------------------

        self.check_system()

    # ======================================================
    # CANCEL
    # ======================================================

    def cancel_setup(self):

        if self.downloader:
            self.downloader.cancel()

        if self.ollama_installer:
            self.ollama_installer.requestInterruption()

        self.setup_success = False

        self.close()

    # ======================================================
    # SYSTEM CHECK
    # ======================================================

    def check_system(self):

        self.status.setText(
            "Checking for Ollama..."
        )

        self.continue_button.setEnabled(
            False
        )

        self.progress.setVisible(
            True
        )

        self.progress.setRange(
            0,
            0,
        )

        self.checker = SetupChecker()

        self.checker.result.connect(
            self.system_checked
        )

        self.checker.start()

    # ======================================================
    # SYSTEM CHECK RESULT
    # ======================================================

    def system_checked(
        self,
        ollama_found,
        fast_found,
        vision_found,
    ):

        self.progress.setVisible(
            False
        )

        self.ollama_found = (
            ollama_found
        )

        self.fast_found = (
            fast_found
        )

        self.vision_found = (
            vision_found
        )

        # --------------------------------------------------
        # OLLAMA MISSING
        # --------------------------------------------------

        if not ollama_found:

            self.status.setText(
                "✗ Ollama was not found"
            )

            self.models.setText(
                "Ollama is required to run PravithAI."
            )

            self.download_status.clear()

            if sys.platform.startswith("linux"):

                self.continue_button.setText(
                    "Install Ollama"
                )

            else:

                self.continue_button.setText(
                    "Get Ollama"
                )

            self.continue_button.setEnabled(
                True
            )

            return

        # --------------------------------------------------
        # OLLAMA FOUND
        # --------------------------------------------------

        self.status.setText(
            "✓ Ollama detected"
        )

        fast_status = (
            "✓ installed"
            if fast_found
            else "⬇ missing"
        )

        vision_status = (
            "✓ installed"
            if vision_found
            else "⬇ missing"
        )

        self.models.setText(
            f"Fast model:   {FAST_MODEL}   {fast_status}\n"
            f"Vision model: {VISION_MODEL}   {vision_status}"
        )

        # --------------------------------------------------
        # EVERYTHING ALREADY INSTALLED
        # --------------------------------------------------

        if (
            fast_found
            and vision_found
        ):

            self.status.setText(
                "✓ PravithAI is ready to use"
            )

            self.continue_button.setText(
                "Finish Setup"
            )

        # --------------------------------------------------
        # SOMETHING MISSING
        # --------------------------------------------------

        else:

            self.continue_button.setText(
                "Download Models"
            )

        self.continue_button.setEnabled(
            True
        )

    # ======================================================
    # CONTINUE
    # ======================================================

    def continue_setup(self):

        # --------------------------------------------------
        # OLLAMA IS MISSING
        # --------------------------------------------------

        if not self.ollama_found:

            if sys.platform.startswith("linux"):
                self.install_ollama_linux()
            else:
                self.install_ollama_external()

            return

        # --------------------------------------------------
        # EVERYTHING EXISTS
        # --------------------------------------------------

        if (
            self.fast_found
            and self.vision_found
        ):

            answer = QMessageBox.information(
                self,
                "Ready!",
                "All PravithAI AI models are already "
                "installed.\n\n"
                "No large download is needed.",
            )

            self.setup_success = True

            self.close()

            return

        # --------------------------------------------------
        # FIND MISSING MODELS
        # --------------------------------------------------

        missing = []

        if not self.fast_found:
            missing.append(
                FAST_MODEL
            )

        if not self.vision_found:
            missing.append(
                VISION_MODEL
            )

        models_text = "\n".join(
            f"• {model}"
            for model in missing
        )

        # --------------------------------------------------
        # CONFIRM DOWNLOAD
        # --------------------------------------------------

        answer = QMessageBox.question(
            self,
            "Download AI Models",
            "PravithAI needs to download several GB "
            "of AI models.\n\n"
            f"{models_text}\n\n"
            "This may use approximately 5 GB of "
            "internet data and disk space.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if (
            answer
            != QMessageBox.StandardButton.Yes
        ):
            return

        self.start_download(
            missing
        )

    # ======================================================
    # INSTALL OLLAMA ON LINUX
    # ======================================================

    def install_ollama_linux(self):

        answer = QMessageBox.question(
            self,
            "Install Ollama",
            "PravithAI needs Ollama to run its "
            "local AI models.\n\n"
            "The official Ollama installer will now "
            "run.\n\n"
            "Linux may ask for administrator "
            "authentication.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if (
            answer
            != QMessageBox.StandardButton.Yes
        ):
            return

        self.continue_button.setEnabled(
            False
        )

        self.cancel_button.setEnabled(
            False
        )

        self.status.setText(
            "Installing Ollama..."
        )

        self.models.setText(
            "Please follow any authentication "
            "prompt from Linux."
        )

        self.download_status.setText(
            "Running official Ollama installer..."
        )

        self.progress.setVisible(
            True
        )

        self.progress.setRange(
            0,
            0,
        )

        self.ollama_installer = (
            OllamaInstaller()
        )

        self.ollama_installer.output.connect(
            self.ollama_install_output
        )

        self.ollama_installer.finished_install.connect(
            self.ollama_install_finished
        )

        self.ollama_installer.start()

    # ======================================================
    # INSTALL OLLAMA ON WINDOWS / MACOS
    # ======================================================

    def install_ollama_external(self):

        system_name = (
            "Windows"
            if sys.platform.startswith("win")
            else "macOS"
        )

        answer = QMessageBox.question(
            self,
            "Install Ollama",
            f"PravithAI needs Ollama to run its "
            f"local AI models.\n\n"
            f"Please install Ollama for {system_name} "
            f"from the official Ollama website.\n\n"
            f"After installation, return to PravithAI "
            f"and click \"Check Again\".\n\n"
            "Open the Ollama download page now?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if (
            answer
            == QMessageBox.StandardButton.Yes
        ):

            try:
                webbrowser.open(
                    OLLAMA_DOWNLOAD_URL
                )

            except Exception:
                pass

        self.continue_button.setText(
            "Check Again"
        )

        self.continue_button.setEnabled(
            True
        )

        self.status.setText(
            "Install Ollama, then check again"
        )

        self.models.setText(
            f"Ollama is required on {system_name}."
        )

        self.download_status.setText(
            OLLAMA_DOWNLOAD_URL
        )

    # ======================================================
    # OLLAMA INSTALL OUTPUT
    # ======================================================

    def ollama_install_output(
        self,
        text,
    ):

        self.download_status.setText(
            text
        )

    # ======================================================
    # OLLAMA INSTALL FINISHED
    # ======================================================

    def ollama_install_finished(
        self,
        success,
        message,
    ):

        self.progress.setVisible(
            False
        )

        if not success:

            self.status.setText(
                "✗ Ollama installation failed"
            )

            self.models.setText(
                message
            )

            self.continue_button.setText(
                "Install Ollama"
            )

            self.continue_button.setEnabled(
                True
            )

            self.cancel_button.setEnabled(
                True
            )

            QMessageBox.critical(
                self,
                "Ollama Installation Failed",
                message,
            )

            return

        self.status.setText(
            "✓ Ollama installed"
        )

        self.models.setText(
            "Checking for PravithAI AI models..."
        )

        self.download_status.clear()

        self.ollama_found = True

        self.continue_button.setText(
            "Checking..."
        )

        self.continue_button.setEnabled(
            False
        )

        self.cancel_button.setEnabled(
            True
        )

        self.check_system()

    # ======================================================
    # DOWNLOAD MODELS
    # ======================================================

    def start_download(
        self,
        missing,
    ):

        self.continue_button.setEnabled(
            False
        )

        self.cancel_button.setEnabled(
            False
        )

        self.progress.setVisible(
            True
        )

        self.progress.setRange(
            0,
            100,
        )

        self.progress.setValue(
            0
        )

        self.status.setText(
            "Downloading AI models..."
        )

        self.download_status.setText(
            "Starting download..."
        )

        self.downloader = ModelDownloader(
            missing
        )

        self.downloader.output.connect(
            self.download_output
        )

        self.downloader.progress.connect(
            self.download_progress
        )

        self.downloader.finished_download.connect(
            self.download_finished
        )

        self.downloader.error.connect(
            self.download_error
        )

        self.downloader.start()

    # ======================================================
    # DOWNLOAD OUTPUT
    # ======================================================

    def download_output(
        self,
        text,
    ):

        self.download_status.setText(
            text
        )

    # ======================================================
    # DOWNLOAD PROGRESS
    # ======================================================

    def download_progress(
        self,
        value,
    ):

        self.progress.setValue(
            value
        )

    # ======================================================
    # DOWNLOAD FINISHED
    # ======================================================

    def download_finished(self):

        self.progress.setValue(
            100
        )

        self.status.setText(
            "✓ AI models installed"
        )

        self.models.setText(
            "Both PravithAI models are ready."
        )

        self.download_status.setText(
            "PravithAI is ready!"
        )

        self.continue_button.setText(
            "Finish Setup"
        )

        self.continue_button.setEnabled(
            True
        )

        self.cancel_button.setEnabled(
            True
        )

        QMessageBox.information(
            self,
            "Setup Complete",
            "The PravithAI AI models have been "
            "installed successfully!\n\n"
            "You're ready to use PravithAI.",
        )

    # ======================================================
    # DOWNLOAD ERROR
    # ======================================================

    def download_error(
        self,
        message,
    ):

        self.status.setText(
            "✗ Download failed"
        )

        self.download_status.setText(
            message
        )

        self.progress.setValue(
            0
        )

        self.continue_button.setText(
            "Try Again"
        )

        self.continue_button.setEnabled(
            True
        )

        self.cancel_button.setEnabled(
            True
        )

        QMessageBox.critical(
            self,
            "Download Failed",
            message,
        )

    # ======================================================
    # CLOSE EVENT
    # ======================================================

    def closeEvent(self, event):

        if self.downloader and self.downloader.isRunning():
            self.downloader.cancel()

        if (
            self.ollama_installer
            and self.ollama_installer.isRunning()
        ):
            self.ollama_installer.requestInterruption()

        event.accept()


# ==========================================================
# MAIN
# ==========================================================

def main():

    app = QApplication(
        sys.argv
    )

    window = SetupWizard()

    window.show()

    app.exec()

    if window.setup_success:
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(
        main()
    )