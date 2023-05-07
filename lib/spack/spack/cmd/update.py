# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import argparse

import llnl.util.tty as tty
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

        # perform a git pull to update the repository
        git("pull", "--rebase", "-n")
