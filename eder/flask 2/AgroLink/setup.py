from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="agrolink",
    version="0.1.0",
    author="Seu Nome",
    author_email="seu.email@exemplo.com",
    description="Sistema de Gerenciamento Agrícola",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/AgroLink",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Flask",
        "Intended Audience :: Agriculture",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "agrolink=main:app",
        ],
    },
) 