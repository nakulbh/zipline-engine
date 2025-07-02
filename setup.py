from setuptools import setup, find_packages

setup(
    name="zipline-nse-backtester",
    version="1.0.0",
    description="Professional backtesting engine for NSE stocks using zipline-reloaded",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "zipline-reloaded>=3.0.0",
        "pyfolio-reloaded>=0.9.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "logbook>=1.5.0",
        "click>=7.0",
        "tables>=3.6.0",
        "bcolz>=1.2.0",
        "empyrical-reloaded>=0.5.0",
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'nse-backtest=zipline_nse_backtester.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)