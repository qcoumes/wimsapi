"""Setuptools entry point."""

import codecs
import os


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Software Development :: Libraries :: Python Modules'
]

dirname = os.path.dirname(__file__)
long_description = (
    codecs.open(os.path.join(dirname, 'README.md'), encoding='utf-8').read()
    + '\n\n______\n\n'
    + codecs.open(os.path.join(dirname, 'CHANGES.md'), encoding='utf-8').read()
)

setup(
    name='wimsapi',
    version="0.4.0",
    description='A Python 3 implementation of WIMS adm/raw module.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Coumes Quentin',
    author_email='coumes.quentin@gmail.com',
    url='https://github.com/qcoumes/wimsapi',
    packages=['wimsapi'],
    install_requires=['requests'],
    classifiers=CLASSIFIERS
)
