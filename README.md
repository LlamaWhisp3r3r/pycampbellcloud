# pycampbellcloud

**_pycampbellcloud_** is a Python client library designed to provide a clean, object-oriented interface to the Campbell Cloud REST API. It abstracts away HTTP requests and authentication details, allowing you to easily access, manipulate, and manage monitoring data from Campbell Cloud in a Pythonic way.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)

## Features

- Easy-to-use object-oriented interface
- Simplified authentication and session management
- Access to all endpoints of the Campbell Cloud API
- Support for data retrieval, manipulation, and management
- Comprehensive error handling
- Thorough documentation

## Installation

You can install `pycampbellcloud` using pip:

```bash
pip install pycampbellcloud
```

## Usage

Here's a quick example of how to use `pycampbellcloud`:
```python
from pycampbellcloud import CampbellCloud

# Initialize the client
client = CampbellCloud('your_organization_id', 'your_username', 'your_password')

# Fetch a list of assets for your organization
assets = client.list_assets()

# print the list of assets
print(assets)
```

## API Reference

For detailed information on the available methods and classes, please refer to the [API documentation](https://us-west-2.campbell-cloud.com/api/v1/docs/).
