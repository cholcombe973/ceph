# Largely taken from
# https://blog.kevin-brown.com/programming/2014/09/24/combining-autotools-and-setuptools.html
import os, sys, os.path

from setuptools.command.egg_info import egg_info
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext


def get_version():
    try:
        for line in open(os.path.join(os.path.dirname(__file__), "..", "ceph_ver.h")):
            if "CEPH_GIT_NICE_VER" in line:
                return line.split()[2][1:-1]
        else:
            return "0"
    except IOError:
        return "0"

class EggInfoCommand(egg_info):
    def finalize_options(self):
        egg_info.finalize_options(self)
        if "build" in self.distribution.command_obj:
            build_command = self.distribution.command_obj["build"]
            self.egg_base = build_command.build_base
            self.egg_info = os.path.join(self.egg_base, os.path.basename(self.egg_info))

# Disable cythonification if we're not really building anything
if (len(sys.argv) >= 2 and
    any(i in sys.argv[1:] for i in ('--help', 'clean', 'egg_info', '--version')
    )):
    def cythonize(x, **kwargs):
        return x

setup(
    name = 'cephfs',
    version = get_version(),
    description = "Python libraries for the Ceph libcephfs library",
    long_description = (
        "This package contains Python libraries for interacting with Ceph's "
        "cephfs library."),
    ext_modules = cythonize([
        Extension("cephfs",
            ["cephfs.pyx"],
            libraries=["cephfs"],
            )
    ], build_dir=os.environ.get("CYTHON_BUILD_DIR", None), include_path=[
        os.path.join(os.path.dirname(__file__), "..", "rados")]
    ),
    cmdclass={
        "build_ext": build_ext,
        "egg_info": EggInfoCommand,
    },
)
