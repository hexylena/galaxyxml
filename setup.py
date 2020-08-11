from setuptools import setup

with open("README.rst") as fh:
    readme = fh.read()

setup(
    name="galaxyxml",
    version="0.4.10",
    description="Galaxy XML generation library",
    author="Helena Rasche",
    author_email="hxr@hx42.org",
    install_requires=["lxml", "future"],
    long_description=readme,
    long_description_content_type="text/x-rst",
    packages=["galaxyxml", "galaxyxml.tool", "galaxyxml.tool.parameters"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
    ],
    data_files = [("", ["LICENSE.TXT"])]
)
