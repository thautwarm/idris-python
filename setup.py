from setuptools import setup, find_packages
from datetime import datetime
from pathlib import Path

with Path('README.rst').open() as readme:
    readme = readme.read()

setup(
    name='idris-python',
    version="0.25",
    keywords="Idris, Dependent Types, Type Safety, Compiler",
    # keywords of your project that separated by comma ","
    description=
    "Loader for a kind of Idris IR.",  # a conceise introduction of your project
    long_description=readme,
    license='bsd3',
    url='https://github.com/thautwarm/idris-python',
    author='thautwarm',
    author_email='twshere@outlook.com',
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "idris-python=idris_python.cli:idris_python_run",
            "run-cam=idris_python.cli:cam_run"
        ]
    },
    # above option specifies commands to be installed,
    # e.g: entry_points={"console_scripts": ["yapypy=yapypy.cmd.compiler"]}
    install_requires=['wisepy2', 'toml'],
    platforms="any",
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    zip_safe=False,
)
