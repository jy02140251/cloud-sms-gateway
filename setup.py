from setuptools import setup, find_packages

setup(
    name="cloud-sms-gateway",
    version="1.2.0",
    author="Wu Xie",
    author_email="jy02140251@gmail.com",
    description="High-performance SMS gateway for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jy02140251/cloud-sms-gateway",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0",
        "pydantic>=2.0",
        "tenacity>=8.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)