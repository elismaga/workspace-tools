import logging
import os
import sys

from tabulate import tabulate

from workspace.commands import AbstractCommand
from workspace.commands.helpers import expand_product_groups
from workspace.scm import product_name, is_git_repo, current_branch, product_path
from workspace.utils import background_processes, run, run_in_background

log = logging.getLogger(__name__)


class Wait(AbstractCommand):
  """
    Wait for an event to be completed and optionally start background/waiting tasks.

    If no argument is passed, then show running background/waiting tasks.
    Any extra arguments passed to wait will be run in the background. I.e. ws wait sleep 10

    :param int review: Wait for 'Ship It' from review board.
                       This is blocking, and so can be used to chain commands in command prompt.
                       i.e.: ws wait -r && ws push (equivalent of ws wait -p)
    :param bool publish: Wait for a new version to be published.
                         This is blocking, and so can be used to chain commands in command prompt.
    :param int interval: Minutes to wait between each check.
                         Defaults to 5 minutes.
    :param push: Wait for review and push. Implies --review, however it is non-blocking / runs in background.
    :param bump_in: Wait for publish and bump it in the given products/product groups.
                    Implies --publish, however it is non-blocking / runs in the background.
    :param list extra_args: Arbitrary commands to run in background.
  """
  def __init__(self, *args, **kwargs):
    #: Run wait in background if possible
    self.in_background = False

    super(Wait, self).__init__(*args, **kwargs)

    if self.push:
      self.review = True

    if self.bump_in:
      self.publish = True

    #: Save the branch as it could change while waiting
    self.branch = is_git_repo() and current_branch()

  @classmethod
  def arguments(cls):
    _, docs = cls.docs()
    return ([
        cls.make_args('-r', '--review', action='store_true', help=docs['review']),
        cls.make_args('-P', '--publish', action='store_true', help=docs['publish']),
        cls.make_args('-i', '--interval', type=int, default=5, help=docs['interval'])
      ],
      [
        cls.make_args('-p', '--push', action='store_true', help=docs['push']),
        cls.make_args('-bi', '--bump-in', metavar='PRODUCT', nargs='*', help=docs['bump_in']),
      ])

  def run(self):
    if self.extra_args:
      run_in_background(' '.join(self.extra_args))
      run(self.extra_args, shell=True)
      sys.exit(0)

    if not (self.review or self.publish):
      processes = background_processes()
      if processes:
        print tabulate(processes, headers=['PID', 'Task'])
      sys.exit(0)

    if self.push:
      self.commander.run('push', branch=self.branch)

    if self.bump_in:
      name = product_name()
      for product in expand_product_groups(self.bump_in):
        path = product_path(product)
        if os.path.exists(path):
          if not os.fork():  # child
            os.chdir(path)
            self.commander.run('bump', test=True, push=True, names=[name])

    raise NotImplementedError('Not implemented. Please implement Wait.run() in a subclass.')
