import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pythonmatchingengine",
    version="0.0.1",
    author="Francisco Merlos and Jesús Sanz",
    author_email='pako_neo@hotmail.com',
    license='MIT License',
    description="Realistic market matching engine simulator \
                 for HFT trading strategies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Surbeivol/PythonMatchingEngine",
    packages=setuptools.find_packages(),
    install_requires=[
        'cycler==0.10.0',
        'kiwisolver==1.1.0',
        'matplotlib==3.1.0',
        'numpy==1.16.4',
        'pandas==0.24.2',
        'pyparsing==2.4.0',
        'python-dateutil==2.8.0',
        'pytz==2019.1',
        'PyYAML==5.1.1',
        'six==1.12.0',
        'tqdm==4.32.2'
    ],
    include_package_data=True,
    classifiers=[
        "Programmin Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

