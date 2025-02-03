from setuptools import setup, find_packages

setup(
    name="app",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi==0.103.2",
        "uvicorn==0.23.2",
        "sqlalchemy==1.4.41",
        "pydantic==2.4.2",
        "pydantic-settings==2.0.3",
        "alembic==1.12.0",
    ],
) 