from setuptools import setup
from pip.req import parse_requirements
import sys, os

if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist bdist_wheel upload")
    sys.exit()

setup(name="galaxyxml",
        version='0.1.3',
        description='Galaxy XML generation library',
        author='Eric Rasche',
        author_email='rasche.eric@yandex.ru',
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
