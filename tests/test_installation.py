import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch
import zipfile

from scripts import install as installer
from simplesnake.constants.DSimpleSnake import DSimpleSnake


ROOT = Path(__file__).resolve().parents[1]


def make_wheel(directory, version):
    """A real, tiny offline dependency to exercise pip and venv isolation."""
    wheel = directory / f'snake_fixture-{version}-py3-none-any.whl'
    info = f'snake_fixture-{version}.dist-info'
    files = {
        'snake_fixture/__init__.py': f'VERSION = "{version}"\n',
        f'{info}/METADATA': f'Metadata-Version: 2.1\nName: snake-fixture\nVersion: {version}\n',
        f'{info}/WHEEL': 'Wheel-Version: 1.0\nGenerator: test\nRoot-Is-Purelib: true\nTag: py3-none-any\n',
    }
    files[f'{info}/RECORD'] = ''.join(f'{name},,\n' for name in [*files, f'{info}/RECORD'])
    # A wheel is a ZIP archive containing package files and installation metadata.
    with zipfile.ZipFile(wheel, 'w') as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return wheel


def real_run(command, **kwargs):
    kwargs.setdefault('capture_output', True)
    kwargs.setdefault('text', True)
    return subprocess.run(command, **kwargs)


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.source = self.base / 'source'
        self.destination = self.base / 'installation with spaces'
        (self.source / 'scripts').mkdir(parents=True)
        (self.source / 'simplesnake/constants').mkdir(parents=True)
        shutil.copyfile(ROOT / 'scripts/check-cmdb.py', self.source / 'scripts/check-cmdb.py')
        constants = (ROOT / 'simplesnake/constants/DSimpleSnake.py').read_text()
        (self.source / 'simplesnake/constants/DSimpleSnake.py').write_text(
            constants.replace(f'"{DSimpleSnake.VERSION}"', '"0.0.0"'))
        (self.source / 'simplesnake/__init__.py').write_text('')
        self.wheel = make_wheel(self.base, '1.0')
        self.requirements = self.source / 'requirements.txt'
        self.requirements.write_text(f'--no-index\n{self.wheel.as_posix()}\n')
        # Swap installer settings for a tiny dependency that pip can install offline.
        self.settings = patch.multiple(installer, COPY_FILES=(),
                                       RUNTIME_IMPORTS=('simplesnake.constants.DSimpleSnake', 'snake_fixture'),
                                       RUNTIME_PROBE='import snake_fixture; assert snake_fixture.VERSION == "1.0"')
        self.settings.start()
        # Cleanups run even if a test fails, restoring settings and removing test files.
        # https://docs.python.org/3/library/unittest.html#unittest.TestCase.addCleanup
        self.addCleanup(self.settings.stop)
        self.addCleanup(self.temporary.cleanup)
        self.installation = installer.Installation(self.source, destination=self.destination, run=real_run)

    def apply(self, action, **kwargs):
        # Capture routine installer output so the test runner stays readable.
        with contextlib.redirect_stdout(io.StringIO()):
            self.installation.apply(action, **kwargs)

    def test_real_offline_install_reinstall_upgrade_and_repeated_uninstall(self):
        self.apply('install', check=True)
        self.assertFalse(self.destination.exists())
        self.apply('install')
        self.apply('install')
        marker = self.destination / installer.VERSION_MARKER
        self.assertEqual(marker.read_text().strip(), '0.0.0')
        data = self.destination / 'user-data.txt'
        data.write_text('keep me')
        self.requirements.write_text(f'--no-index\n{make_wheel(self.base, "2.0").as_posix()}\n')
        constants = self.source / 'simplesnake/constants/DSimpleSnake.py'
        constants.write_text(constants.read_text().replace('"0.0.0"', '"0.0.1"'))
        self.installation = installer.Installation(self.source, destination=self.destination, run=real_run)
        with patch.object(installer, 'RUNTIME_PROBE', 'import snake_fixture; assert snake_fixture.VERSION == "2.0"'):
            self.apply('upgrade')
        self.assertEqual(marker.read_text().strip(), '0.0.1')
        self.assertEqual(data.read_text(), 'keep me')
        # A deployed runtime works with its source checkout unavailable.
        self.source.rename(self.base / 'hidden-source')
        result = real_run([str(self.installation.python_path()), '-I', '-c',
                           'import snake_fixture; print(snake_fixture.VERSION)'],
                          cwd=self.destination, check=True,
                          env=self.installation.python_environment())
        self.assertEqual(result.stdout.strip(), '2.0')
        self.apply('uninstall')
        self.assertFalse(self.installation.python_path().exists())
        self.assertFalse(marker.exists())
        self.assertEqual(data.read_text(), 'keep me')
        self.apply('uninstall')

    def test_failed_pip_or_import_does_not_advance_success_marker(self):
        self.apply('install')
        marker = self.destination / installer.VERSION_MARKER
        before = marker.read_text()
        self.requirements.write_text('--no-index\nno-such-snake-package==9999\n')
        with self.assertRaises(subprocess.CalledProcessError):
            self.apply('upgrade')
        self.assertEqual(marker.read_text(), before)
        self.requirements.write_text(f'--no-index\n{self.wheel.as_posix()}\n')
        with patch.object(installer, 'RUNTIME_IMPORTS', ('missing_snake_import',)):
            with self.assertRaises(subprocess.CalledProcessError):
                self.apply('upgrade')
        self.assertEqual(marker.read_text(), before)
        self.apply('uninstall')

    def test_missing_host_fails_before_mutation_for_check_and_install(self):
        with patch.object(installer, 'SYSTEM_PYTHON', str(self.base / 'missing-python')):
            for check in (True, False):
                with self.assertRaises(ValueError):
                    self.apply('install', check=check)
                self.assertFalse(self.destination.exists())

    def windows_runtime_run(self, command, **kwargs):
        if installer.WINDOWS_RUNTIME_PROBE in command:
            raise subprocess.CalledProcessError(
                1, command, stderr='OSError: msvcp140.dll: [WinError 126]')
        return real_run(command, **kwargs)

    def test_missing_windows_runtime_fails_before_check_or_install_changes_files(self):
        self.installation.run = self.windows_runtime_run
        with patch.object(installer, 'sys', Mock(platform='win32')):
            for check in (True, False):
                with self.subTest(check=check):
                    with self.assertRaises(ValueError) as caught:
                        self.apply('install', check=check)
                    message = str(caught.exception)
                    self.assertIn(installer.WINDOWS_RUNTIME_URL, message)
                    self.assertIn('Restart Windows if', message)
                    self.assertIn('msvcp140.dll', message)
                    self.assertFalse(self.destination.exists())

    def test_missing_windows_runtime_preserves_upgrade_and_allows_uninstall(self):
        self.apply('install')
        before = {path.relative_to(self.destination): path.read_bytes()
                  for path in self.destination.rglob('*') if path.is_file()}
        self.installation.run = self.windows_runtime_run
        with patch.object(installer, 'sys', Mock(platform='win32')):
            for check in (True, False):
                with self.subTest(check=check), self.assertRaises(ValueError) as caught:
                    self.apply('upgrade', check=check)
                self.assertIn(installer.WINDOWS_RUNTIME_URL, str(caught.exception))
            after = {path.relative_to(self.destination): path.read_bytes()
                     for path in self.destination.rglob('*') if path.is_file()}
            self.assertEqual(after, before)
            self.apply('uninstall', check=True)
            self.apply('uninstall')
        self.assertFalse(self.destination.exists())

    def test_loadable_windows_runtime_passes_read_only_preflight(self):
        calls = []

        def run(command, **kwargs):
            if installer.WINDOWS_RUNTIME_PROBE in command:
                calls.append(command)
                return subprocess.CompletedProcess(command, 0, stdout='', stderr='')
            return real_run(command, **kwargs)

        self.installation.run = run
        with patch.object(installer, 'sys', Mock(platform='win32')):
            self.apply('install', check=True)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][-len(installer.WINDOWS_RUNTIME_DLLS):],
                         list(installer.WINDOWS_RUNTIME_DLLS))
        self.assertFalse(self.destination.exists())

    def test_refuses_unowned_destination_and_windows_path_escapes(self):
        self.destination.mkdir()
        (self.destination / 'important.txt').write_text('keep')
        with self.assertRaises(ValueError):
            self.apply('install')
        for value in ('../outside', '/absolute', 'C:/outside', 'C:outside', 'folder\\..\\outside'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                installer.relative_path(value)

    def test_refuses_development_requirements_before_mutation(self):
        self.requirements.write_text('-e /opt/dev/somewhere\n')
        with self.assertRaises(ValueError):
            self.apply('install')
        self.assertFalse(self.destination.exists())

    def test_refuses_unowned_and_broken_virtual_environments(self):
        self.apply('install')
        manifest = self.destination / installer.MANIFEST
        ownership = json.loads(manifest.read_text())
        ownership['venv_owned'] = False
        manifest.write_text(json.dumps(ownership))
        with self.assertRaises(ValueError):
            self.apply('upgrade', check=True)
        ownership['venv_owned'] = True
        manifest.write_text(json.dumps(ownership))
        (self.destination / installer.VENV_DIR / 'pyvenv.cfg').unlink()
        with self.assertRaises(ValueError):
            self.apply('upgrade', check=True)
        self.apply('uninstall')

    def test_failed_first_install_is_uninstallable_without_success_marker(self):
        self.requirements.write_text('--no-index\nno-such-snake-package==9999\n')
        with self.assertRaises(subprocess.CalledProcessError):
            self.apply('install')
        self.assertFalse((self.destination / installer.VERSION_MARKER).exists())
        self.assertTrue((self.destination / installer.MANIFEST).exists())
        self.apply('uninstall')
        self.assertFalse(self.destination.exists())
