from setuptools import setup, find_packages

setup(
    name="pyOS",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # List your production dependencies here
    ],
    extras_require={
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "coverage>=5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "pyos=pyOS:main",
        ],
    },
)
