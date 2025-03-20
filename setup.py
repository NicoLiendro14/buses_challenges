from setuptools import setup, find_packages

setup(
    name="buses_challenge",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "SQLAlchemy>=2.0.0",
        "pymysql>=1.1.0",
        "python-dotenv>=1.0.0",
        "pytest>=7.4.0"
    ]
) 