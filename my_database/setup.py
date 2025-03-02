from setuptools import setup, find_packages

setup(
    name="my_database",
    version="0.1",
    packages=find_packages(),
    install_requires=["mysql-connector-python", "python-dotenv"],
    description="A simple database connection package",
    author="kartikey-sapkal",
    author_email="kcsapkal28@gmail.com",
    # url="https://github.com/KartikeySapkal",  # Change as needed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)