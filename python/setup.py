import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
        'cityhash==0.2.3.post9',
        'cryptography'
    ]

setuptools.setup(
    name="pyringcomm",
    version="0.0.5",
    author="Nuclaer (Nuclear_Man_D)",
    author_email="dylanbrophy@gmail.com",
    description="Communication ring for automated systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NuclearManD/RingComms",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    install_requires=requirements,
    setup_requires=requirements
)
