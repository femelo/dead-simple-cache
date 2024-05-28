#!/usr/bin/env python3
import os

from setuptools import setup

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def required(requirements_file):
    """ Read requirements file and remove comments and empty lines. """
    with open(os.path.join(BASEDIR, requirements_file), 'r') as f:
        requirements = f.read().splitlines()
        return [pkg for pkg in requirements
                if pkg.strip() and not pkg.startswith("#")]


with open("README.md", "r") as f:
    long_description = f.read()


def get_version():
    """ Find the version of the package"""
    version = None
    version_file = os.path.join(BASEDIR, 'dead_simple_cache', 'version.py')
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if alpha and int(alpha) > 0:
        version += f"a{alpha}"
    return version


setup(
    name='dead-simple-cache',
    version=get_version(),
    description='A dead simple caching lib',
    url='https://github.com/femelo/dead-simple-cache',
    author='Flávio De Melo',
    author_email='flavio.eler@gmail.com',
    license='Apache 2.0',
    packages=['dead_simple_cache'],
    zip_safe=True,
    keywords='caching',
    install_requires=required("requirements.txt"),
    long_description=long_description,
    long_description_content_type='text/markdown'
)
