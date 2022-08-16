""" Setup file for module """
from setuptools import setup

with open('README.md', encoding='utf8') as f:
    long_description = f.read()

with open('requirements.txt', encoding='utf8') as f:
    requirements = f.readlines()

setup(
    name='tgfp-nfl',
    version='2.0.0',
    packages=['tgfp_nfl'],
    python_requires='>=3.10.*',
    url='https://github.com/johnsturgeon/tgfp-nfl',
    license='MIT',
    author='John Sturgeon',
    author_email='john.sturgeon@me.com',
    install_requires=requirements,
    description='Python extraction of NFL scores schedule data from abstracted data source',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
