# Release Verification 
The purpose of this script is to help verify the latest version of our products can be installed on the supported operating systems.

# Usage

1. Install the required libraries
```python
pip install -r requirements.txt
```

2. (Required for testing Meridian) Create a `.env` file 
```json
cat << EOF > .env
{
    "MERIDIAN_USERNAME":"REPLACE_ME",
    "MERIDIAN_PASSWORD":"REPLACE_ME"
}
EOF
```

3. Execute the script
```bash

# Testing latest Meridian
$ python3 main.py -p meridian

# Testing Meridian 2023
$ python3 main.py -p meridian -v 2023 

# Testing Horizon
$ python3 main.py -p horizon
```

```bash
$ python3 main.py -h
usage: Release Tester [-h] [--version VERSION] --product PRODUCT

options:
  -h, --help            show this help message and exit
  --version VERSION, -v VERSION
                        Release version (e.g., 30.0.2 or 2024.0.1)
  --product PRODUCT, -p PRODUCT
                        Product line (e.g., horizon or meridian)
```