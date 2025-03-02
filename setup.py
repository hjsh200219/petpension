from setuptools import setup, find_packages

setup(
    name="petpension",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "plotly==5.18.0",
        "tenacity>=6.2.0",
        "packaging",
        "streamlit==1.32.0",
        "pandas==2.2.0",
        "numpy==1.26.3",
        "pillow==10.2.0",
        "requests==2.31.0",
        "tqdm==4.66.1",
        "playwright==1.40.0",
        "python-dotenv==1.0.0",
        "beautifulsoup4==4.12.2",
        "lxml==4.9.3",
        "importlib-metadata==6.8.0",
    ],
    python_requires=">=3.8",
) 