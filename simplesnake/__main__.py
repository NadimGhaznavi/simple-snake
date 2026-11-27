import argparse
from pathlib import Path
import sys

from simplesnake.constants.DSimpleSnake import DSimpleSnake
from simplesnake.constants.DText import DText
from simplesnake.interface.Localizer import Localizer


def main():
    # __file__ locates bundled translations independently of the working directory.
    # Path joins: https://docs.python.org/3/library/pathlib.html#operators
    localizer = Localizer(Path(__file__).parent / "locales")
    parser = argparse.ArgumentParser(description=localizer.text(DText.CLI_DESCRIPTION))
    parser.add_argument("--language", default=DSimpleSnake.DEFAULT_LOCALE,
                        help=localizer.text(DText.CLI_LANGUAGE))
    parser.add_argument("--version", action="version", version=DSimpleSnake.VERSION,
                        help=localizer.text(DText.CLI_VERSION))
    # Convert command-line options into attributes such as args.language.
    # https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.parse_args
    args = parser.parse_args()
    locale = localizer.select(explicit=args.language)

    # Help/version need neither a display nor the heavyweight UI/ML imports.
    from PySide6.QtWidgets import QApplication
    import torch
    from simplesnake.constants.DTraining import DTraining
    from simplesnake.interface.MainWindow import MainWindow

    torch.set_num_threads(DTraining.CPU_THREADS)
    app = QApplication(sys.argv[:1])
    app.setApplicationName(DSimpleSnake.APPLICATION_ID)
    app.setOrganizationName(DSimpleSnake.ORGANIZATION)
    app.setApplicationVersion(DSimpleSnake.VERSION)

    def text(key, **values):
        # This nested function remembers locale; **values forwards named placeholders.
        # https://docs.python.org/3/tutorial/controlflow.html#unpacking-argument-lists
        return localizer.text(key, locale=locale, **values)

    window = MainWindow(text)
    app.aboutToQuit.connect(window._stop_training)
    window.show()
    # Qt's event loop waits for input and dispatches callbacks until the app closes.
    return app.exec()


if __name__ == "__main__":
    # Run on direct execution (including python -m simplesnake), not on import.
    # https://docs.python.org/3/library/__main__.html
    raise SystemExit(main())
