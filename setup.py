import os
import pathlib
from setuptools import setup, find_packages
import ast

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()


def read_version(fname="open_dubbing/__init__.py"):
    with open(fname, encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return ast.literal_eval(line.split("=")[1].strip())

    raise ValueError("__version__ not found in the file")

def parse_requirements(fname="requirements.txt"):
    with open(HERE / fname, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


setup(
    name="open-dubbing",
    version=read_version(),
    description="AI dubbing system which uses machine learning models to automatically translate and synchronize audio dialogue into different languages.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Softcatala/open-dubbing",
    author="Jordi Mas",
    author_email="jmas@softcatala.org",
    license="Apache Software License 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=parse_requirements(),
    extras_require={
        "dev": ["flake8==7.*", "black==24.*", "pytest==8.*", "isort==5.13"],
        "coqui": ["coqui-tts >= 0.25.1"],
        "openai": ["openai == 1.59.3"],
        "camb": ["requests >= 2.28.0"],
    },
    entry_points={
        "console_scripts": [
            "open-dubbing=open_dubbing.main:main",
        ]
    },
    python_requires='>=3.10'
)
