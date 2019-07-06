import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PythonMatchingEngine",
    version="0.0.1",
    author="Francisco Merlos and Jesús Sanz",
    description="Realistic market matching engine simulator \
                 for HFT trading strategies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Surbeivol/PythonMatchingEngine",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programmin Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)