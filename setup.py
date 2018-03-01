from setuptools import setup


setup(name="galaxyxml",
        version='0.4.5',
        description='Galaxy XML generation library',
        author='E. Rasche',
        author_email='hxr@hx42.org',
        install_requires=['lxml', 'future'],
        packages=["galaxyxml", "galaxyxml.tool", "galaxyxml.tool.parameters"],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Operating System :: OS Independent',
            'Intended Audience :: Developers',
            'Environment :: Console',
            'License :: OSI Approved :: Apache Software License',
            ],
        )
