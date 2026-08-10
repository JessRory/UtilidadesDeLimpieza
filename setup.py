from setuptools import setup, find_packages

setup(
    name="CleanUtils", 
    author= "Jesús Riera Llarena",
    author_email= "josuroera1974@gmail.com",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "dateparser",
        "rapidfuzz",
    ],
)
