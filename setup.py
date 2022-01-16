from setuptools import setup, find_packages


setup(
    name='dagsim',
    version='1.0.2',
    packages=find_packages(),
    url='https://github.com/uio-bmi/dagsim',
    license='AGPL-3.0 License',
    author='Ghadi S. Al Hajj',
    author_email='ghadia@uio.no',
    description='A framework and specification language for simulating data based on user-defined graphical models',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=['graphviz>=0.16',
                      'numpy>=1.20.2',
                      'pandas>=1.2.4',
                      'python-igraph>=0.9.6',
                      'scikit-learn>=0.24.2',
                      'pyyaml',
                      'ipython>=7.27.0'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'dagsim-quickstart = dagsim.utils.quickstart:main'
        ]
    },
)
