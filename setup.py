from setuptools import setup, find_packages

setup(
    name="telegram_forwarder",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot==20.7",
        "python-dotenv==1.0.0",
    ],
    python_requires=">=3.7",
) 