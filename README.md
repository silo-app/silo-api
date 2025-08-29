WARNING: THIS PACKAGE IS CURRENTLY UNDER DEVELOPMENT

![SILO Logo](./src/silo/static/images/SILO_logo_API-dark.png#gh-dark-mode-only)
![SILO Logo](./src/silo/static/images/SILO_logo_API.png#gh-light-mode-only)

SILO is a warehouse software for monitoring parts and stocks of all kinds.

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
$ git clone https://github.com/silo-app/backend.git
$ cd backend/
$ uv sync
$ uv run --env-file .env python3 -m uvicorn main:app --reload --app-dir src/silo
```

## License

This package is licensed under the MIT license.