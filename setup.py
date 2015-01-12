from setuptools import setup
from pip.req import parse_requirements

setup(name="galaxyxml",
        version='0.1.1',
        description='Galaxy XML generation library',
        author='Eric Rasche',
        author_email='rasche.eric@yandex.ru',
        license='GPL3',
        install_requires=['lxml'],
        packages=["galaxyxml", "galaxyxml.tool", "galaxyxml.tool.parameters"],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Operating System :: OS Independent',
            'Intended Audience :: Developers',
            'Environment :: Console',
            ],
        )
