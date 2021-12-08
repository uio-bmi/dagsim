from setuptools import setup, find_packages


def import_requirements(filename) -> list:
    with open(filename, 'r') as file:
        requirements = file.read().split("\n")
    return requirements


setup(
    name='dagsim',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/uio-bmi/dagsim',
    license='AGPL-3.0 License',
    author='Ghadi Al Hajj',
    author_email='ghadia@uio.no.com',
    description='A framework and specification language for simulating data based on user-defined graphical models',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=import_requirements(filename="requirements.txt"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
)
