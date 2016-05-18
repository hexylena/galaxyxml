from setuptools import setup
from pip.req import parse_requirements
import sys, os

if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist bdist_wheel upload; git push")
    sys.exit()

setup(name="galaxyxml",
        version='0.2.1',
        description='Galaxy XML generation library',
        author='Eric Rasche',
        author_email='esr@tamu.edu',
        install_requires=['lxml'],
        packages=["galaxyxml", "galaxyxml.tool", "galaxyxml.tool.parameters"],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Operating System :: OS Independent',
            'Intended Audience :: Developers',
            'Environment :: Console',
            'License :: OSI Approved :: Apache Software License',
            ],
        )
