from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in frappe_vault/__init__.py
from frappe_vault import __version__ as version

setup(
    name="frappe_vault",
    version=version,
    description="A Frappe-based password and secrets management application",
    author="Frappe Vault",
    author_email="hello@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
