import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mapf-branch-and-bound",
    version="0.0.2",
    author="Thom van der Woude",
    author_email="tbvanderwoude@student.tudelft.nl",
    description="A branch-and-bound framework for MAPF solvers that use mapfmclient",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tbvanderwoude/mapf-branch-and-bound/",
    project_urls={
        "Bug Tracker": "https://github.com/tbvanderwoude/mapf-branch-and-bozund/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
)