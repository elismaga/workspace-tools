import logging
import os
import re
import sys

from workspace.commands.update import update
from workspace.commands.commit import commit
from workspace.scm import repo_check, repo_path
from workspace.utils import log_exception, silent_run, split_doc


log = logging.getLogger(__name__)
new_version = None  # Doesn't work if it is in bump_version

SETUP_FILE = 'setup.py'


def setup_publish_parser(subparsers):
  doc, docs = split_doc(publish.__doc__)
  parser = subparsers.add_parser('publish', description=doc, help=doc)
  group = parser.add_mutually_exclusive_group()
  group.add_argument('--minor', action='store_true', help=docs['minor'])
  group.add_argument('--major', action='store_true', help=docs['major'])
  parser.set_defaults(command=publish)

  return parser


def publish(minor=False, major=False, **kwargs):
  """
  Bumps version in setup.py (defaults to patch), builds a source distribution, and uploads with twine.

  :param bool minor: Perform a minor publish by bumping the minor version
  :param bool major: Perform a major publish by bumping the major version
  """
  repo_check()

  cwd = repo_path()

  silent_run('rm -rf dist/*', shell=True, cwd=cwd)

  update(raises=True)

  new_version = bump_version(minor, major)
  commit(msg='Publish version ' + new_version, push=True)

  log.info('Building source distribution')
  silent_run('python setup.py sdist', cwd=cwd)

  log.info('Uploading')
  silent_run('twine upload dist/*', shell=True, cwd=cwd)


def bump_version(minor=False, major=False):
  """
  Bump the version (defaults to patch) in setup.py

  :param bool minor: Bump the minor version instead of patch.
  :param bool major: Bump the major version instead of patch.
  """
  setup_file = os.path.join(repo_path(), SETUP_FILE)
  if not os.path.exists(setup_file):
    log.error(setup_file + 'does not exist.')
    sys.exit(1)

  def replace_version(match):
    global new_version

    version_parts = match.group(2).split('.')
    i = 0 if major else (1 if minor else 2)

    while len(version_parts) < i + 1:
      version_parts.append(0)

    for j in range(i+1, len(version_parts)):
      version_parts[j] = '0'

    version_parts[i] = str(int(version_parts[i]) + 1)
    new_version = '.'.join(version_parts)

    return 'version=' + match.group(1) + new_version + match.group(1)

  content = re.sub('version\s*=\s*([\'"])(.*)[\'"]', replace_version, open(SETUP_FILE).read())

  with open(setup_file, 'w') as fp:
    fp.write(content)

  if not new_version:
    log.error('Failed to find "version=" in setup.py to bump version')
    sys.exit(1)

  return new_version
