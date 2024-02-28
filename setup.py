from setuptools import setup, find_packages

setup(
    name="harvester_curator",
    version="0.0.1",
    author="Sarbani Roy, Fangfang Wang",
    author_email="sarbani.roy@simtech.uni-stuttgart.de, fangfang.wang@simtech.uni-stuttgart.de",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'harvester_curator = harvester_curator.cli:main'
        ]},
    install_requires=[
        "cffconvert == 2.0.0",
        "pydantic",
        "PyYAML == 6.0.1",
        "h5py == 3.10.0",
        "pyvista == 0.43.3",
        "vtk == 9.3.0",
        "python-magic == 0.4.27",
        "easyDataverse @ git+https://github.com/gdcc/easyDataverse.git@flexible-connect"
    ]
)       