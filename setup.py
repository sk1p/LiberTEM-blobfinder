import re
import os
import codecs
import subprocess
from setuptools.command.sdist import sdist
from setuptools.command.build_py import build_py
from setuptools import setup


class BakedRevisionBuilderSdist(sdist):
    def make_release_tree(self, base_dir, files):
        if not self.dry_run:
            write_baked_revision(base_dir)
        sdist.make_release_tree(self, base_dir, files)


class BakedRevisionBuilderBuildPy(build_py):
    def run(self):
        if not self.dry_run:
            write_baked_revision(self.build_lib)
        build_py.run(self)


def mkpath(path):
    if not os.path.exists(path):
        os.makedirs(path)


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, *parts), 'r').read()


def remove_rst_roles(txt):
    return re.sub(':(cite|doc):`[^`]+` ?', '', txt)


def get_git_rev():
    # NOTE: this is a copy from src/libertem_blobfinder/versioning.py
    # this is because it is not guaranteed that we can import our own packages
    # from setup.py AFAIK
    try:
        new_cwd = os.path.abspath(os.path.dirname(__file__))
        rev_raw = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=new_cwd)
        return rev_raw.decode("utf8").strip()
    except Exception:
        return "unknown"


def write_baked_revision(base_dir):
    dest_dir = os.path.join(base_dir, 'libertem_blobfinder')
    baked_dest = os.path.join(dest_dir, '_baked_revision.py')
    mkpath(dest_dir)

    with open(baked_dest, "w") as f:
        f.write(r'revision = "%s"' % get_git_rev())


def find_version(*file_paths):
    """
    "stolen" from pip's setup.py
    """
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="libertem-blobfinder",
    version=find_version("src", "libertem_blobfinder", "__version__.py"),
    license='GPL v3',
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=[
        "numpy",
        "scipy",
        "sparse",
        "matplotlib",
        # Pinned due to https://github.com/pydata/sparse/issues/257
        # Ensure compatibility with numpy 1.17
        "numba>=0.46",
        "scikit-image",
        "libertem>=0.3.0"
    ],
    extras_require={
        'pyfftw': 'pyfftw',
    },
    package_dir={"": "src"},
    packages=[
        "libertem_blobfinder",
    ],
    # entry_points={
    #     'console_scripts': [
    #         'libertem-server=libertem.web.cli:main',
    #     ]
    # },
    cmdclass={
        'sdist': BakedRevisionBuilderSdist,
        'build_py': BakedRevisionBuilderBuildPy,
    },
    keywords="electron microscopy",
    description="LiberTEM correlation and refinement library",
    long_description=remove_rst_roles(read("README.rst")),
    long_description_content_type="text/x-rst",
    url="https://libertem.github.io/LiberTEM-blobfinder",
    author_email="libertem-dev@googlegroups.com",
    author="the LiberTEM team",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)