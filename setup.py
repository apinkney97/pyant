from setuptools import find_packages, setup

setup(
    name="ant",
    packages=find_packages(),
    entry_points={"console_scripts": ["pyant=ant.main:main"]},
)
