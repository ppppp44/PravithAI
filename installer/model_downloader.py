import re
import subprocess

from PySide6.QtCore import QThread, Signal


class ModelDownloader(QThread):
    output = Signal(str)
    progress = Signal(int)
    finished_download = Signal()
    error = Signal(str)

    def __init__(self, models):
        super().__init__()

        self.models = models
        self.cancel_requested = False

    def run(self):
        try:
            total_models = len(self.models)

            if total_models == 0:
                self.progress.emit(100)
                self.finished_download.emit()
                return

            for index, model in enumerate(self.models):

                if self.cancel_requested:
                    return

                self.output.emit(
                    f"Downloading {model}..."
                )

                process = subprocess.Popen(
                    [
                        "ollama",
                        "pull",
                        model,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )

                if process.stdout:
                    for line in process.stdout:
                        if self.cancel_requested:
                            process.terminate()
                            return

                        line = line.strip()

                        if not line:
                            continue

                        self.output.emit(line)

                        model_progress = (
                            self.parse_progress(line)
                        )

                        if model_progress is not None:
                            overall_progress = int(
                                (
                                    index * 100
                                    + model_progress
                                )
                                / total_models
                            )

                            self.progress.emit(
                                overall_progress
                            )

                return_code = process.wait()

                if return_code != 0:
                    self.error.emit(
                        f"Failed to download {model}."
                    )
                    return

                overall_progress = int(
                    ((index + 1) * 100)
                    / total_models
                )

                self.progress.emit(
                    overall_progress
                )

            self.progress.emit(100)

            self.output.emit(
                "All models downloaded successfully."
            )

            self.finished_download.emit()

        except Exception as e:
            self.error.emit(
                str(e)
            )

    @staticmethod
    def parse_progress(line):
        matches = re.findall(
            r"(\d+)%\s*$",
            line,
        )

        if not matches:
            return None

        percentage = int(
            matches[-1]
        )

        return max(
            0,
            min(
                100,
                percentage,
            ),
        )

    def cancel(self):
        self.cancel_requested = True