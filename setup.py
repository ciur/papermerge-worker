from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="pmworker",
    version="1.0.0",
    author="Eugen Ciur",
    author_email="eugen@papermerge.com",
    url="https://github.com/ciur/papermerge-worker",
    description=("Papermerge worker - extract OCR text documents"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Proprietary",
    keywords="tesseract documentation tutorial",
    packages=['pmworker'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
