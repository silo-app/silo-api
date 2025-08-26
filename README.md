WARNING: THIS PACKAGE IS CURRENTLY UNDER DEVELOPMENT

# System for Inventory and Logistics Optimization (SILO)

SILO is a warehouse software for monitoring parts and stocks of all kinds.

- [System for Inventory and Logistics Optimization (SILO)](#system-for-inventory-and-logistics-optimization-silo)
  - [Features \& Use-Cases](#features--use-cases)
  - [Demo](#demo)
  - [Installation](#installation)
  - [Configuration options](#configuration-options)
    - [Example configuration](#example-configuration)
  - [API documentation](#api-documentation)
  - [Development instance](#development-instance)
  - [License](#license)


## Features & Use-Cases

* Simple stock management through ease of use
* Quickly find items
* Simple and effective inventory monitoring
* Authentication via LDAP/barcode scanner
  * Group & role management to restrict entire parts pools
  * Manufacturers can get access to "their" spare parts

## Demo


## Installation

```
python3 -m pip install silo-api
```

## Configuration options

### Example configuration

```json
{
    ...
    "secret_key": "<YOUR_SECRET_KEY>"
}
```

## API documentation

You can access the API documentation on `/docs`.

## Development instance

```
git clone https://github.com/silo-app/backend.git
```

## License

This package is licensed under the MIT license.