# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Lychee(CargoPackage):
    """Fast, async, stream-based link checker written in Rust."""

    homepage = "https://github.com/lycheeverse/lychee"
    url = "https://github.com/lycheeverse/lychee/archive/refs/tags/lychee-v0.18.0.tar.gz"

    maintainers("alecbcs")

    license("Apache-2.0 OR MIT", checked_by="alecbcs")

    version("0.18.0", sha256="56127481c8684b6f611a22e3940dacb06abf6db6ea24d1af38ccefe91bc09dbe")
    version("0.17.0", sha256="78b006105363ce0e989401124fd8bcb0b60d697db2cb29c71f2cdd7f5179c91c")
    version("0.16.1", sha256="ee61627083c80459e0f6a48c11cd910711c86b744a294b6a00f7072dffa1b04b")
    version("0.16.0", sha256="7ba01e03378868f068a0f3cd29bce8e5dec772e09838c6c2dc53428ce56c77bf")

    depends_on("openssl")

    build_directory = "lychee-bin"

    def setup_build_environment(self, env):
        env.set("OPENSSL_DIR", self.spec["openssl"].prefix)
