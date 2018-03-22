#!/usr/bin/env python3

from pathlib import Path
import subprocess
import shutil
import sys

project_dir = Path(__file__).resolve().parents[2]

sys.path += [str(project_dir)]

import subdownloader.project

setup_file = project_dir / 'setup.py'

shutil.rmtree(project_dir / 'build')

subprocess.run([sys.executable, str(setup_file), 'clean'], cwd=project_dir, check=True)

subprocess.run([sys.executable, str(setup_file), 'test'], cwd=project_dir, check=True)

subprocess.run([sys.executable, str(setup_file), 'bdist_wheel'], cwd=project_dir, check=True)
subprocess.run([sys.executable, str(setup_file), 'sdist'], cwd=project_dir, check=True)

print()
print('Created distributable files for version {}'.format(subdownloader.project.PROJECT_VERSION_FULL_STR))
print('Upload them to pypi using "twine upload FILES" (after manual inspection)')
print()
