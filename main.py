import sys

from PySide6.QtWidgets import QApplication


def main():
    if "--setup" in sys.argv:
        from installer.setup_wizard import main as setup_main

        return setup_main()

    from ui.main_window import MainWindow

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())