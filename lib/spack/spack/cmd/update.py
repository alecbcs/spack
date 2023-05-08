# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import argparse
import re
import sys

import llnl.util.tty as tty
from llnl.util.tty.colify import colify
from llnl.util.filesystem import working_dir

import spack.cmd
import spack.util.git
from spack.cmd import spack_is_git_repo

description = "update the spack repository to the latest commit"
section = "system"
level = "short"


def setup_parser(subparser):
    subparser.add_argument("-b", "--branch", help="name of the branch to upate the repository to")


def update(parser, args):
    # make sure that spack is a git repository
    if not spack_is_git_repo():
        tty.die("This spack is not a git clone. Can't use 'spack update'")

    git = spack.util.git.git(required=True)

    # execute git within the spack repository
    with working_dir(spack.paths.prefix):
        checked_out_ref = git("symbolic-ref", "-q", "HEAD", output=str)
        current_branch = checked_out_ref.replace("refs/heads/", "", 1)

        # provide a warning if the user did not specify a branch
        # and spack's repository is not tracking upstream develop
        if args.branch is None:
            upstream_branch = None

            refs = git("for-each-ref", "--format=%(refname)", "refs/heads/", output=str)
            for ref in refs.split():
                branch = ref.replace("refs/heads/", "", 1)
                branch_remote_ref = git("config", f"branch.{branch}.merge", output=str)

                if branch_remote_ref.strip().endswith("develop"):
                    remote = git("config", f"branch.{branch}.remote", output=str).strip()
                    remote_url = git("config", f"remote.{remote}.url", output=str).strip()

                    if remote_url.endswith("spack/spack.git"):
                        upstream_branch = branch
                        break

            if upstream_branch is not None and current_branch != upstream_branch:
                tty.warn("Spack is not tracking upstream develop.")
                tty.warn("Packages may be out of date. To switch to develop run,")
                print()
                print(f"    spack update -b {upstream_branch}")
                print()

        elif args.branch != current_branch:
            git("checkout", args.branch)

        # record commit hash before pull
        old_head = git("rev-parse", "HEAD", output=str).strip()

        # perform a git pull to update the repository
        git("pull", "--rebase", "-n")

        # record commit hash after pull
        new_head = git("rev-parse", "HEAD", output=str).strip()

        # check to see if the repository updated
        if old_head != new_head:
            changed_files = git(
                "diff-tree", "-r", "--name-status", "{old_head}..{new_head}", output=str
            )
            changed_packages = {"Added": [], "Updated": [], "Deleted": []}

            for file in changed_files.split("\n"):
                if file.endswith("package.py"):
                    pkg = re.search(
                        "var/spack/repos/builtin/packages/(.*)/package.py", file
                    ).group(1)
                    if file[0] == "A":
                        changed_packages["Added"].append(pkg)
                    elif file[0] == "M":
                        changed_packages["Updated"].append(pkg)
                    elif file[0] == "D":
                        changed_packages["Deleted"].append(pkg)

            for action in changed_packages.keys():
                if len(changed_packages[action]) > 0:
                    tty.msg(f"{action} %d packages" % len(changed_packages[action]))
                    colify(changed_packages[action], output=sys.stdout)
