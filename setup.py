from setuptools import setup, find_packages

setup(
    name='HandyLib',
    packages='HandyLib',
    url='https://github.com/cwh1te/HandyLib',
    description='A collection of handy Python functions',
    long_description=open('README.md').read(),
    install_requires=open('requirements.txt).readlines(),
    include_package_data=True,
)
