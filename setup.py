from setuptools import setup, find_packages

setup(
    name="harvester_curator",
    version="0.0.1",
    author="Sarbani Roy, Fangfang Wang",
    author_email="sarbani.roy@simtech.uni-stuttgart.de, fangfang.wang@simtech.uni-stuttgart.de",
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    entry_points={
        'console_scripts': [
            'harvester_curator = harvester_curator.cli:main',
            "harvest=harvester_curator.cli:harvest",
            "curate=harvester_curator.cli:curate",
            "upload=harvester_curator.cli:upload"
        ]},
    install_requires=[
        "cffconvert >= 2.0.0",
        "pydantic >= 2.6.1",
        "PyYAML >= 6.0.1",
        "h5py >= 3.10.0",
        "pyvista >= 0.43.3",
        "vtk >= 9.3.0",
        "python-magic >= 0.4.27",
        "easyDataverse >= 0.4.0"
    ],
    python_requires='>=3.10,<3.13',
    extras_require={
        'dev': [
            "pytest >= 8.2.2",
            "tox >= 3.24.0"
        ]
    }, 
)       