import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(sys.platform == 'win32', 'Requires Windows cmd.exe')
class WindowsLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='snake launcher ')
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / 'extracted source'
        self.local_app_data = self.base / 'local app data'
        self.installed = self.local_app_data / 'Programs' / 'SimpleSnake'
        self.environment = os.environ.copy()
        # Keep these tests independent of any real installation or active venv.
        for name in ('PYTHONHOME', 'PYTHONPATH', 'VIRTUAL_ENV'):
            self.environment.pop(name, None)
        self.environment['LOCALAPPDATA'] = str(self.local_app_data)
        self.launcher(self.source)

    def launcher(self, directory):
        scripts = directory / 'scripts'
        scripts.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'scripts/run.cmd', scripts / 'run.cmd')
        return scripts / 'run.cmd'

    def runtime(self, directory):
        directory.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, '-m', 'venv', '--without-pip',
                        str(directory / '.venv')], check=True,
                       capture_output=True, text=True, env=self.environment)
        package = directory / 'simplesnake'
        package.mkdir()
        (package / '__init__.py').write_text('')
        # Exercise the batch file with a real interpreter and no app dependencies.
        (package / '__main__.py').write_text(
            'import json, os, sys\n'
            'print(json.dumps({"cwd": os.getcwd(), "python": sys.executable, '
            '"args": sys.argv[1:]}))\n'
            'sys.exit(7)\n')

    def run_launcher(self, directory):
        command = self.environment.get('COMSPEC', 'cmd.exe')
        # /s /c strips the outer quotes, preserving the quoted path and argument.
        return subprocess.run(
            f'"{command}" /d /s /c ""{directory / "scripts/run.cmd"}" --example "two words""',
            cwd=self.base, env=self.environment, capture_output=True, text=True,
            timeout=30)

    def assert_runtime(self, result, directory):
        self.assertEqual(result.returncode, 7, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(Path(output['cwd']), directory)
        self.assertEqual(Path(output['python']), directory / '.venv/Scripts/python.exe')
        self.assertEqual(output['args'], ['--example', 'two words'])

    def test_source_launcher_finds_default_installation(self):
        self.runtime(self.installed)
        self.assert_runtime(self.run_launcher(self.source), self.installed)

    def test_local_runtime_takes_precedence_over_default_installation(self):
        self.runtime(self.source)
        self.runtime(self.installed)
        self.assert_runtime(self.run_launcher(self.source), self.source)

    def test_custom_installation_launcher_uses_its_own_runtime(self):
        custom = self.base / 'custom installation'
        self.launcher(custom)
        self.runtime(custom)
        self.assert_runtime(self.run_launcher(custom), custom)

    def test_missing_runtime_explains_install_and_custom_launch(self):
        result = self.run_launcher(self.source)
        self.assertEqual(result.returncode, 1)
        self.assertIn('runtime was not found', result.stderr)
        self.assertIn('install.cmd', result.stderr)
        self.assertIn('custom installation directory', result.stderr)

    def test_incomplete_installation_does_not_launch_another_copy(self):
        self.runtime(self.installed)
        (self.source / '.installation-manifest.json').write_text('{}')
        result = self.run_launcher(self.source)
        self.assertEqual(result.returncode, 1)
        self.assertIn(str(self.source / 'scripts'), result.stderr)
        self.assertIn('runtime was not found', result.stderr)
