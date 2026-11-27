#!/usr/bin/env python3
"""Install, upgrade, or remove the standalone Simple Snake desktop application."""

import argparse
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import shutil
import subprocess
import sys
import tempfile


BMFORGE_COMPONENT = {"id": "bmforge.installation", "spec_version": "0.1.3"}

PROJECT_NAME = "SimpleSnake"
DEPLOYMENT_READY = True
COPY_TREES = ("simplesnake", "scripts")
COPY_FILES = ("README.md", "LICENSE", "THIRD_PARTY_NOTICES.md")
# Set to "requirements.txt" for Python applications requiring a production venv.
# Keep None for applications without Python package dependencies.
REQUIREMENTS_FILE = "requirements.txt"
VENV_DIR = ".venv"
# Use the host interpreter, never an activated development checkout venv.
SYSTEM_PYTHON = str(Path(sys._base_executable).resolve())
WINDOWS_RUNTIME_DLLS = ("vcruntime140.dll", "msvcp140.dll", "vcruntime140_1.dll")
WINDOWS_RUNTIME_URL = "https://aka.ms/vc14/vc_redist.x64.exe"
WINDOWS_RUNTIME_PROBE = (
    'from ctypes import WinDLL; from sys import argv; '
    '[WinDLL(name) for name in argv[1:]]'
)
# Adapt to the deployed application's service/client imports when enabling deployment.
RUNTIME_IMPORTS = ("simplesnake.__main__", "simplesnake.interface.MainWindow",
                   "simplesnake.activity.TrainingSession", "PySide6.QtWebEngineWidgets",
                   "PySide6.QtWebChannel", "numpy", "torch")
RUNTIME_PROBE = '''
from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication
from simplesnake.constants.DChart import DChart
from simplesnake.interface.MainWindow import MainWindow
from simplesnake.interface.Localizer import Localizer

app = QApplication([])
window = MainWindow(Localizer("simplesnake/locales").text)
window.show()
loop = QEventLoop()
window.chart.bridge.ready.connect(loop.quit)
window.chart.bridge.failed.connect(loop.quit)
QTimer.singleShot(DChart.READY_TIMEOUT_MS, loop.quit)
loop.exec()
ready, error = window.chart.ready, window.chart.error
window.close()
app.processEvents()
assert ready, error or "The bundled training chart did not render"
'''
MANIFEST = ".installation-manifest.json"
VERSION_MARKER = ".deployment-version"


def relative_path(name: str) -> str:
    # Pure paths inspect path syntax without accessing files on the host system.
    # https://docs.python.org/3/library/pathlib.html#pure-paths
    if not isinstance(name, str):
        raise ValueError("Managed paths must be strings")
    path = PurePosixPath(name)
    if (not name or path.is_absolute() or PureWindowsPath(name).drive
            or '\\' in name or '..' in path.parts or path.as_posix() != name or name == '.'):
        raise ValueError(f"Invalid managed path: {name}")
    if name in (MANIFEST, VERSION_MARKER):
        raise ValueError(f"Reserved bookkeeping path: {name}")
    return name


def reject_symlinks(path: Path) -> None:
    # *path.parents expands the ancestor paths so we check every directory too.
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            raise ValueError(f"Refusing a symbolic link in deployment path: {candidate}")


class Installation:
    def __init__(self, checkout: Path, *, destination: Path | None = None,
                 run=None) -> None:
        self.checkout = checkout.resolve()
        self.run = run or subprocess.run
        self.version_file = f"{PROJECT_NAME.lower()}/constants/D{PROJECT_NAME}.py"
        # Load the checker by filename: its hyphen is not valid in a normal import.
        # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
        spec = importlib.util.spec_from_file_location('cmdb_checker', self.checkout / 'scripts/check-cmdb.py')
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        self.metadata = checker.validate((self.checkout / self.version_file).read_text(),
                                         PROJECT_NAME, self.version_file)
        default = (Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData/Local'))
                   / 'Programs' / PROJECT_NAME) if os.name == 'nt' else Path(self.metadata['BASE_DIR'])
        self.destination = Path(destination if destination is not None else default).absolute()
        reject_symlinks(self.destination)
        if (self.checkout.is_relative_to(self.destination)
                or self.destination.is_relative_to(self.checkout)):
            raise ValueError("Run deployment from a separate checkout outside the installation")

    def installed_files(self) -> list[str] | None:
        # The manifest lists files we own; None means no installation was found.
        manifest = self.destination / MANIFEST
        reject_symlinks(manifest)
        if not manifest.exists():
            if self.destination.exists():
                raise ValueError("Installation directory exists without an ownership manifest; inspect it before proceeding")
            return None
        data = json.loads(manifest.read_text())
        if (not isinstance(data, dict) or data.get('project') != PROJECT_NAME
                or not isinstance(data.get('files'), list)):
            raise ValueError("Installation ownership manifest does not match this project")
        if type(data.get('venv_owned', False)) is not bool:
            raise ValueError("Installation manifest has invalid virtual environment ownership")
        names = [relative_path(name) for name in data['files']]
        if (len(names) != len(set(names))
                or self.version_file not in names and not (not names and data.get('removed') is True)):
            raise ValueError("Installation ownership manifest has invalid files")
        for name in [*names, VERSION_MARKER]:
            path = self.destination / name
            reject_symlinks(path)
            if path.exists() and not path.is_file():
                raise ValueError(f"Managed file is no longer a regular file: {path}")
        return names

    def source_files(self) -> list[str]:
        names = {relative_path(name) for name in COPY_FILES}
        if REQUIREMENTS_FILE is not None:
            names.add(relative_path(REQUIREMENTS_FILE))
        for name in COPY_TREES:
            folder = self.checkout / relative_path(name)
            reject_symlinks(folder)
            if not folder.is_dir():
                raise ValueError(f"Missing source directory: {name}")
            # rglob walks nested folders; generated caches are not deployment sources.
            for path in folder.rglob('*'):
                if '__pycache__' in path.parts or VENV_DIR in path.parts or path.suffix in ('.pyc', '.pyo'):
                    continue
                reject_symlinks(path)
                if path.is_file():
                    names.add(relative_path(path.relative_to(self.checkout).as_posix()))
        if self.version_file not in names:
            raise ValueError("Deployment must include readable CMDB constants")
        for name in names:
            source = self.checkout / name
            reject_symlinks(source)
            if not source.is_file():
                raise ValueError(f"Missing source file: {name}")
            target = self.destination / name
            reject_symlinks(target)
            if target.exists() and not target.is_file():
                raise ValueError(f"Managed file target is not a regular file: {target}")
        return sorted(names)

    def plan(self, action: str) -> tuple[list[str] | None, list[str]]:
        if not DEPLOYMENT_READY:
            raise ValueError("Deployment is not configured: implement provisioning, lifecycle, and health checks before enabling it")
        previous = self.installed_files()
        if action == 'upgrade' and not previous:
            raise ValueError("No installation found; run install.sh first")
        current = [] if action == 'uninstall' else self.source_files()
        if previous is not None:
            for name in set(current) - set(previous):
                if (self.destination / name).exists():
                    raise ValueError(f"New managed file would overwrite an unowned file: {name}")
        self.preflight_python(action)
        return previous, current

    def venv_owned(self) -> bool:
        manifest = self.destination / MANIFEST
        return manifest.is_file() and json.loads(manifest.read_text()).get('venv_owned') is True

    def python_path(self) -> Path:
        return self.destination / VENV_DIR / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')

    @staticmethod
    def python_environment() -> dict[str, str]:
        # Copy before removing variables so the installer's own environment is unchanged.
        environment = os.environ.copy()
        for variable in ('PYTHONPATH', 'PYTHONHOME', 'VIRTUAL_ENV',
                         'PIP_TARGET', 'PIP_PREFIX', 'PIP_USER'):
            environment.pop(variable, None)
        environment['PYTHONNOUSERSITE'] = '1'
        return environment

    def preflight_python(self, action: str) -> None:
        venv = self.destination / VENV_DIR
        reject_symlinks(venv)
        if venv.exists() and not venv.is_dir():
            raise ValueError(f'Virtual environment path is not a directory: {venv}')
        if action == 'uninstall' or REQUIREMENTS_FILE is None:
            return
        requirements = self.checkout / relative_path(REQUIREMENTS_FILE)
        if not requirements.is_file():
            raise ValueError(f'Missing Python dependency manifest: {REQUIREMENTS_FILE}')
        for entry in requirements.read_text().splitlines():
            entry = entry.strip()
            if (entry.startswith(('-e ', '--editable')) or '/opt/dev/' in entry):
                raise ValueError('Production Python dependencies must not use editable or /opt/dev installs')
        if venv.exists():
            if not self.venv_owned():
                raise ValueError(f'Refusing an unowned virtual environment: {venv}')
            configuration = venv / 'pyvenv.cfg'
            binary = self.python_path()
            reject_symlinks(configuration)
            reject_symlinks(binary.parent)
            if (not configuration.is_file() or not binary.is_file()
                    or '/opt/dev/' in configuration.read_text()
                    or '/opt/dev/' in str(binary.resolve())):
                raise ValueError(f'Production virtual environment is incomplete or references /opt/dev: {venv}')
        host_python = Path(SYSTEM_PYTHON)
        if (not host_python.is_absolute() or '/opt/dev/' in SYSTEM_PYTHON
                or host_python.is_relative_to(self.destination)
                or host_python.is_relative_to(self.checkout)
                or host_python.resolve().is_relative_to(self.checkout)
                or host_python.resolve().is_relative_to(self.destination)
                or '/opt/dev/' in str(host_python.resolve())
                or (host_python.parent.parent / 'pyvenv.cfg').exists()):
            raise ValueError('SYSTEM_PYTHON must be a host interpreter outside development and deployed environments')
        if shutil.which(SYSTEM_PYTHON) is None:
            raise ValueError(f'Missing host Python interpreter: {SYSTEM_PYTHON}')
        # Arguments are separate list items; check=True raises on a failed command.
        # https://docs.python.org/3/library/subprocess.html#subprocess.run
        self.run([SYSTEM_PYTHON, '-B', '-c', 'import venv, ensurepip'],
                 check=True, env=self.python_environment(), capture_output=True,
                 text=True, timeout=30)
        if sys.platform == 'win32':
            # Probe the same C++ runtime DLLs that PyTorch's Windows loader needs.
            # https://docs.pytorch.org/docs/stable/notes/windows.html#installation
            try:
                self.run([SYSTEM_PYTHON, '-B', '-c', WINDOWS_RUNTIME_PROBE,
                          *WINDOWS_RUNTIME_DLLS], check=True,
                         env=self.python_environment(), capture_output=True,
                         text=True, timeout=30)
            except subprocess.CalledProcessError as error:
                raise ValueError(
                    'The Microsoft Visual C++ x64 runtime could not be loaded. '
                    f'Install or repair the latest redistributable: {WINDOWS_RUNTIME_URL}\n'
                    'Restart Windows if its installer requests it, then rerun the same '
                    'Simple Snake install or upgrade command. No application files were changed.\n'
                    f'{error.stderr or error}'
                ) from error

    def prepare_python(self) -> None:
        if REQUIREMENTS_FILE is None:
            return
        venv = self.destination / VENV_DIR
        python = self.python_path()
        environment = self.python_environment()
        if not venv.exists():
            # A virtual environment keeps deployed dependencies separate from the host.
            # https://docs.python.org/3/library/venv.html
            self.run([SYSTEM_PYTHON, '-m', 'venv', str(venv)],
                     check=True, env=environment, timeout=120)
        self.run([str(python), '-m', 'pip', 'install', '--upgrade',
                  '-r', str(self.destination / REQUIREMENTS_FILE)],
                 check=True, cwd=self.destination, env=environment, timeout=300)
        self.run([str(python), '-m', 'pip', 'check'],
                 check=True, cwd=self.destination, env=environment, timeout=30)
        if RUNTIME_IMPORTS:
            # Imports run from deployed files, without a checkout or PYTHONPATH.
            self.run([str(python), '-B', '-c',
                      'from importlib import import_module; from sys import argv; '
                      '[import_module(name) for name in argv[1:]]',
                      *RUNTIME_IMPORTS],
                     check=True, cwd=self.destination, env=environment, timeout=30)
        if RUNTIME_PROBE:
            probe_environment = environment.copy()
            probe_environment['QT_QPA_PLATFORM'] = 'offscreen'
            probe_environment.setdefault('QT_QUICK_BACKEND', 'software')
            probe_environment.setdefault('QTWEBENGINE_CHROMIUM_FLAGS', '--disable-gpu')
            self.run([str(python), '-B', '-c', RUNTIME_PROBE], check=True,
                     cwd=self.destination, env=probe_environment, timeout=60)

    def atomic_write(self, path: Path, content: bytes, mode: int = 0o644) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        for directory in (path.parent, *path.parent.parents):
            if directory == self.destination.parent:
                break
            directory.chmod(0o755)
        # Create beside the target so replace() can rename on the same filesystem.
        # mkstemp returns an open file descriptor and its path.
        # https://docs.python.org/3/library/tempfile.html#tempfile.mkstemp
        descriptor, name = tempfile.mkstemp(prefix='.bmforge-install-', dir=path.parent)
        temporary = Path(name)
        try:
            # fdopen wraps that descriptor in a stream; with closes it after writing.
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(content)
            temporary.chmod(mode)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)

    def remove_files(self, names: list[str]) -> None:
        for name in names:
            path = self.destination / name
            path.unlink(missing_ok=True)
            for directory in path.parents:
                if directory == self.destination:
                    break
                try:
                    # rmdir removes only empty folders, preserving any unowned content.
                    directory.rmdir()
                except OSError:
                    break

    def apply(self, action: str, *, check: bool = False) -> None:
        # Validate the whole plan before creating, replacing, or removing files.
        previous, names = self.plan(action)
        if check:
            print(f"{action}: checks passed for {self.destination}; no files changed.")
            return
        if action == 'uninstall':
            if previous is not None:
                self.remove_files(previous)
                venv = self.destination / VENV_DIR
                reject_symlinks(venv)
                if venv.is_dir() and self.venv_owned():
                    shutil.rmtree(venv)
                (self.destination / VERSION_MARKER).unlink(missing_ok=True)
                (self.destination / MANIFEST).unlink()
                try:
                    self.destination.rmdir()
                except OSError:
                    # Remember that retained state belongs to this project so
                    # repeated removal or reinstallation can recognize it.
                    removed = {'project': PROJECT_NAME, 'files': [], 'removed': True}
                    self.atomic_write(self.destination / MANIFEST, (json.dumps(removed, indent=2) + '\n').encode())
            print(f"Removed managed {PROJECT_NAME} files; unowned files and persistent data are retained.")
            return
        self.destination.mkdir(parents=True, exist_ok=True)
        self.destination.chmod(0o755)
        # Keep ownership information for partial copies so a retry or uninstall can
        # account for new files. Advance the successful-version marker only last.
        owned = sorted(set(previous or ()) | set(names))
        previous_venv = self.venv_owned() if previous is not None else False
        ownership = {'project': PROJECT_NAME, 'files': owned,
                     'venv_owned': REQUIREMENTS_FILE is not None or previous_venv}
        self.atomic_write(self.destination / MANIFEST, (json.dumps(ownership, indent=2) + '\n').encode())
        # Existing managed files may change before success; this is not rollback.
        for name in names:
            source = self.checkout / name
            # Octal permission bits preserve executability for copied launch scripts.
            mode = 0o755 if source.stat().st_mode & 0o111 else 0o644
            self.atomic_write(self.destination / name, source.read_bytes(), mode)
        self.prepare_python()
        # Set subtraction identifies files owned by the old release but absent now.
        self.remove_files(sorted(set(previous or ()) - set(names)))
        ownership['files'] = names
        self.atomic_write(self.destination / MANIFEST, (json.dumps(ownership, indent=2) + '\n').encode())
        self.atomic_write(self.destination / VERSION_MARKER, (self.metadata['VERSION'] + '\n').encode())
        print(f"{action}: {PROJECT_NAME} {self.metadata['VERSION']} deployed to {self.destination}.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('install', 'upgrade', 'uninstall'))
    parser.add_argument('--check', action='store_true', help='Validate the operation without changing files')
    parser.add_argument('--destination', type=Path, help='Installation directory (Linux default: /opt/prod/simplesnake; Windows: LocalAppData/Programs/SimpleSnake)')
    args = parser.parse_args()
    try:
        Installation(Path(__file__).resolve().parents[1], destination=args.destination).apply(args.action, check=args.check)
    except (OSError, ValueError, TypeError, SyntaxError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Deployment failed: {error}\n")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
