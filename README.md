# Inventory Management API

A small Flask service and command-line client for managing retail inventory. The
service provides CRUD operations for products and can enrich records with product
data from [Open Food Facts](https://world.openfoodfacts.org/). The application uses
an in-memory store by design, making it easy to run locally and test without a
database.

## Features

- JSON REST API for creating, reading, updating, and deleting inventory items
- Product lookup and name search through Open Food Facts
- Enrichment of stored products without changing local price or stock data
- CLI for everyday inventory operations and API access
- Consistent JSON errors for invalid input, missing resources, and upstream failures
- Offline test suite with external HTTP calls mocked

## Requirements

- Python 3.9 or newer
- Network access only for live Open Food Facts lookups

## Quick start

```bash
git clone <repository-url>
cd inventory
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
```

Start the API:

```bash
python app.py
```

The development server listens on `http://127.0.0.1:5000`. In another terminal,
with the environment activated, run:

```bash
python cli.py list
```

Set `INVENTORY_API_URL` when the API is running at another address:

```bash
INVENTORY_API_URL=http://localhost:8000 python cli.py list
```

## API

All successful responses are JSON. New items receive an integer `id`; IDs are not
reused after deletion. The service starts with three sample products on every
restart.

### Item schema

| Field | Type | Notes |
| --- | --- | --- |
| `id` | integer | Assigned by the service |
| `barcode` | string | Optional product barcode |
| `product_name` | string | Required when creating an item |
| `brands` | string | Optional brand name |
| `ingredients_text` | string | Optional ingredient list |
| `price` | number | Must be greater than or equal to `0`; defaults to `0` |
| `stock` | integer | Must be greater than or equal to `0`; defaults to `0` |

Unknown fields are rejected. `PATCH` accepts any non-empty subset of editable
fields.

### Endpoints

| Method | Path | Description | Success |
| --- | --- | --- | --- |
| `GET` | `/inventory` | List all items | `200` |
| `GET` | `/inventory/<id>` | Get one item | `200` |
| `POST` | `/inventory` | Create an item | `201` |
| `PATCH` | `/inventory/<id>` | Partially update an item | `200` |
| `DELETE` | `/inventory/<id>` | Delete an item | `200` |
| `GET` | `/lookup/barcode/<barcode>` | Look up a barcode | `200` |
| `GET` | `/lookup/search?name=<text>` | Search by product name | `200` |
| `POST` | `/inventory/<id>/enrich` | Import external product details | `200` |

Errors use the form `{"error": "message"}`. Typical status codes are `400` for
invalid input, `404` for missing items/products, `405` for unsupported methods, and
`502` when Open Food Facts is unavailable.

Create and update an item with curl:

```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H 'Content-Type: application/json' \
  -d '{"product_name":"Maize Flour","price":2.20,"stock":30}'

curl -X PATCH http://127.0.0.1:5000/inventory/4 \
  -H 'Content-Type: application/json' \
  -d '{"stock":25}'
```

## CLI

```bash
python cli.py list
python cli.py view 3
python cli.py add "Maize Flour" --price 2.2 --stock 30 --barcode 6001234567890 --brand Jogoo
python cli.py update 4 --price 2.5 --stock 20
python cli.py delete 4
python cli.py find --barcode 3017624010701
python cli.py find --name "oat milk"
python cli.py enrich 2
python cli.py import 3017624010701 --price 6 --stock 10
```

CLI failures are written as `Error: ...` to stderr and return exit code `1`.

## Project structure

```text
app.py                  Flask application entry point
cli.py                  CLI entry point
inventory_api/          API application, domain logic, validation, and storage
inventory_cli/          API client, argument parsing, and output formatting
tests/                  Unit and integration tests
docs/                   Postman collection and manual API test guide
```

Routes are deliberately thin: validation owns request rules, `InventoryStore`
owns persistence, services coordinate domain actions, and `off_client` is the only
module that talks to Open Food Facts. Replacing the in-memory store can therefore
be done without changing the route or CLI layers.

## Development

Run the test suite from the repository root:

```bash
pytest
```

Tests do not call Open Food Facts; `requests` calls are mocked for deterministic,
offline execution. A ready-to-import Postman collection is available at
`docs/inventory_api_postman_collection.json`, with usage notes in
`docs/POSTMAN_GUIDE.md`.

## Configuration and limitations

- `INVENTORY_API_URL` changes the CLI's API base URL; it defaults to
  `http://127.0.0.1:5000`.
- The API runs in Flask debug mode when started with `python app.py`; use a
  production WSGI server and persistent database for deployment.
- Inventory data is reset whenever the process restarts.
- Open Food Facts requests use a custom `User-Agent` and a bounded timeout.