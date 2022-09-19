import os
from setuptools import setup, find_packages

import codecs

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="ppulp",
    packages=find_packages(),
    include_package_data=True,
    version="0.1.0",
    license="MIT",
    install_requires=[
        "flopt @ git+ssh://git@github.com/nariaki3551/flopt#egg=flopt",
        "numpy",
        "sympy",
        "matplotlib==3.5.2",
        "pulp",
        "optuna==2.10.1",
        "hyperopt",
        "cvxopt",
        "amplify",
        "pytest",
        "scipy",
        "timeout_decorator",
    ],
    author="nariaki tateiwa",
    author_email="nariaki3551@gmail.com",
    # url="https://ppulp.readthedocs.io/en/latest/index.html",
    description="An extension of PuLP, a linear programming problem modeling tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="optimization LP linear programming modeling",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
