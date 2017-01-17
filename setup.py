from setuptools import setup


setup(name="galaxyxml",
        version='0.3.1',
        description='Galaxy XML generation library',
        author='Eric Rasche',
        author_email='esr@tamu.edu',
        install_requires=['lxml'],
        packages=["galaxyxml", "galaxyxml.tool", "galaxyxml.tool.parameters"],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Operating System :: OS Independent',
            'Intended Audience :: Developers',
            'Environment :: Console',
            'License :: OSI Approved :: Apache Software License',
            ],
        )
