from setuptools import find_packages,setup
from typing import List
def get_requirements()->List[str]:
    requirements_list:List[str] = []
    try:
        with open("requirements.txt", "r") as file:
            lines=file.readlines()
            for line in lines:
                requirement=line.strip()
                #ignore empty lines and -e .
                if not requirement or requirement == "-e .":
                    continue
         
                requirements_list.append(requirement)
    except FileNotFoundError:
     print("requirements.txt not found")
       
    return requirements_list



setup(
    name="network_security",
    version="0.0.1",
    author="Tejas Tiwari",
    author_email="[EMAIL_ADDRESS]",
    packages=find_packages(),
    install_requires=get_requirements()
)
