from setuptools import setup

requirements = [x.strip() for x in open('requirements.txt', 'r').readlines()]

setup(name="galaxyxml",
        version='0.1',
        description='Galaxy XML generation library',
        author='Eric Rasche',
        author_email='rasche.eric@yandex.ru',
        license='GPL3',
        install_requires=requirements,
        packages=["galaxyxml", "galaxyxml.tool", "galaxyxml.tool.parameters"],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Operating System :: OS Independent',
            'Intended Audience :: Developers',
            'Environment :: Console',
            ],
        )
