import os.path
from setuptools import setup


cwd = os.path.abspath(os.path.dirname(__file__))


# Metadata
about = {}
with open(os.path.join(cwd, 'rq_exporter', '__version__.py'), 'r') as f:
    exec(f.read(), about)

# Description
with open('README.md', 'r') as f:
    long_description = f.read()

# Requirements
requirements = []
with open(os.path.join(cwd, 'requirements.txt'), 'r') as f:
    requirements = [l.strip() for l in f.readlines()]


setup(
    name = 'rq-exporter',
    url = about['__url__'],
    license = about['__license__'],
    version = about['__version__'],
    author = about['__author__'],
    author_email = about['__author_email__'],
    description = about['__description__'],
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    install_requires = requirements,
    packages = ['rq_exporter'],
    classifiers = [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Monitoring'
    ],
    python_requires='>=3.6',
    entry_points = {
        'console_scripts': ['rq-exporter = rq_exporter.__main__:main']
    }
)
