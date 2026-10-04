import os
import sys

from PySide6.QtWidgets import QApplication


def setup_marker_path():
    if sys.platform.startswith("win"):
        app_data = os.environ.get(
            "APPDATA",
            os.path.expanduser("~"),
        )

        return os.path.join(
            app_data,
            "PravithAI",
            "setup-complete",
        )

    if sys.platform == "darwin":
        return os.path.expanduser(
            "~/Library/Application Support/PravithAI/setup-complete"
        )

    return os.path.expanduser(
        "~/.config/pravithai/setup-complete"
    )


def run_setup_if_needed():
    marker = setup_marker_path()

    if os.path.isfile(marker):
        return True

    from installer.setup_wizard import main as setup_main

    status = setup_main()

    if status != 0:
        return False

    os.makedirs(
        os.path.dirname(marker),
        exist_ok=True,
    )

    with open(marker, "w", encoding="utf-8"):
        pass

    return True


def main():
    if "--setup" in sys.argv:
        from installer.setup_wizard import main as setup_main

        return setup_main()

    if not run_setup_if_needed():
        return 1

    from ui.main_window import MainWindow

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())