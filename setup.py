from distutils.core import setup

setup(
    name='PETRARCH',
    entry_points={
        'console_scripts': ['petrarch = petrarch.petrarch:main']},
    version='0.01a',
    author='Philip Schrodt',
    author_email='schrodt@psu.edu',
    packages=['PETRARCH'],
    url='eventdata.psu.edu',
    license='LICENSE.txt',
    description='PETRARCH parser for event data',
    long_description=open('README.md').read())
