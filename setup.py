from setuptools import setup, find_packages

setup(
    name='Transaction Forwarder',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'aiofiles==25.1.0',
        'annotated-doc==0.0.4',
        'annotated-types==0.7.0',
        'anyio==4.12.1',
        'certifi==2026.1.4',
        'click==8.3.1',
        'colorama==0.4.6',
        'fastapi==0.128.0',
        'h11==0.16.0',
        'httpcore==1.0.9',
        'httpx==0.28.1',
        'idna==3.11',
        'numpy==2.4.0',
        'packaging==25.0',
        'pydantic==2.12.5',
        'pydantic_core==2.41.5',
        'pytz==2025.2',
        'starlette==0.50.0',
        'typing-inspection==0.4.2',
        'typing_extensions==4.15.0',
        'uvicorn==0.40.0',
    ],
    package_data={
        '': ['assets/*.json'],
    },
    entry_points={
        'console_scripts': [
            'my_project = main:main',
        ],
    },
)


# python -m pip install --upgpython -m nuitka --onefile --windows-console-mode=disable --include-data-dir=assets=assets --output-dir=build --remove-output main.py
# python -m nuitka --onefile --windows-console-mode=disable --include-data-dir=assets=assets --output-dir=build --remove-output --lto=yes --mingw64 main.py