import os
import re
import json
import sys

def getProperty(*property_names):
    # Check environment variables first
    for name in property_names:
        value = os.getenv(name)
        if value:
            return value

    # Then check .env file if it exists
    if os.path.exists(".env"):
        with open(".env", "r") as fp:
            env_file = json.load(fp)
        for name in property_names:
            if name in env_file:
                return env_file[name]

    # If none found, exit with error
    print(f"None of the properties {property_names} were found! Exiting...")
    sys.exit(1)

def getMajorMinorPatch(version):
    for major, minor, patch in re.findall(r"(\d+)\.(\d+)\.(\d+)", version):
            major = int(major)
            minor = int(minor)
            patch = int(patch)
            return (major,minor,patch)
    return ("","","")

def read_configurations(name):
    if not os.path.exists(f"configurations/{name}.json"):
        sys.exit(1)
    with open(f"configurations/{name}.json","r") as fp:
        return json.load(fp)
    
def getProductConfiguration(product,version):
    VERSION_MAJOR,VERSION_MINOR,VERSION_PATCH=getMajorMinorPatch(version)

    CONFIGURATIONS=read_configurations("products")

    if product == "horizon":
        if not version:
            version="latest"
            return version,CONFIGURATIONS[product][version]
        else:
            if version not in CONFIGURATIONS[product]:
                return "latest",CONFIGURATIONS[product]["latest"]
            else:
                return version,CONFIGURATIONS[product][version]
    elif product == "meridian":
        if version == "latest":
            version=sorted(CONFIGURATIONS[product].keys())[-1]
        
        if version in CONFIGURATIONS[product]:
             return version,CONFIGURATIONS[product][version]
        elif str(VERSION_MAJOR) in CONFIGURATIONS[product]:
            return VERSION_MAJOR,CONFIGURATIONS[product][str(VERSION_MAJOR)]
        else:
            print(f"Not sure what to do with {version}")
            sys.exit(1)
    else:
        print(f"Not sure how to deal with {product}!")
        sys.exit(1)


def parse_packages(lines):
    result = {}

    # find "Installed Packages"
    STARTING_POSITION=-1
    for i in reversed(range(len(lines))):
        if "Installed Packages" in lines[i]:
            STARTING_POSITION=i+1
            break

    for line in lines[STARTING_POSITION:]:
        if not line.strip():
            continue
        parts = line.split()
        
        if parts[0] == 'ii':
            package = parts[1]
            version = parts[2]
        else:
            package = parts[0]
            version = parts[1]

        if package.endswith('.noarch'):
            package = package[:-7]

        result[package] = version

    return result