from setuptools import setup, find_packages

setup(
   name = "pyweather",
   version = "1.0",
   description = "Retrieving hourly temperature forecasts",
   author = "Lancelot Lachartre",
   author_email = "lancelotlachartre@gmail.com",
   packages = find_packages(),
   install_requires = [
    "python-dotenv",
    "requests",
    "beautifulsoup4",
    "pendulum"
   ]
)