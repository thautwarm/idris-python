from setuptools import setup, find_packages
from datetime import datetime
from pathlib import Path

with Path('README.md').open() as readme:
    readme = readme.read()

setup(
    name='idris-python',
    version="0.1",
    keywords="Idris, Dependent Types, Type Safety, Compiler",
    # keywords of your project that separated by comma ","
    description=
    "Loader for a kind of Idris IR.",  # a conceise introduction of your project
    long_description=readme,
    long_description_content_type="text/markdown",
    license='bsd3',
    url='https://github.com/thautwarm/idris-python',
    author='thautwarm',
    author_email='twshere@outlook.com',
    packages=find_packages(),
    entry_points={"console_scripts": []},
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
