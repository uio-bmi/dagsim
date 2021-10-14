from setuptools import setup


def import_requirements(filename) -> list:
    with open(filename, 'r') as file:
        requirements = file.read().split("\n")
    return requirements


setup(
    name='dagsim',
    version='0.1',
    packages=['dagsim'],
    url='https://github.com/uio-bmi/dagsim',
    license='AGPL-3.0 License',
    author='Ghadi Al Hajj',
    author_email='ghadia@uio.no.com',
    description='A framework and specification language for simulating data based on graphical models',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=import_requirements(filename="requirements.txt")
)
