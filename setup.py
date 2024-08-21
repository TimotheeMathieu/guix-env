from setuptools import find_packages
from distutils.core import setup
import os

ver_file = os.path.join("guix_env", "_version.py")
with open(ver_file) as f:
    exec(f.read())

packages = ['guix_env']

setup(
    name='guix-env',
    version=__version__,
    license="MIT",
    packages=packages,
    include_package_data=True,
    install_requires=[
        'Click', "jinja2"
    ],
    entry_points={
        'console_scripts': [
            'guix-env = guix_env.cli:guix_env',
        ],
    },
)
