# Cart Service

FastAPI microservice for managing shopping carts in the scalable ecommerce project.

## Setup

- Create and activate a virtual environment.
- Install dependencies with `pip install -e .` or `pip install -r requirements.txt` if present.
- Export `DATABASE_URL` for production databases; defaults to `sqlite:///./test.db`.
- Launch with `uvicorn app.main:app --reload` (update import path if entrypoint differs).

## Database

- Tables: `carts` (one per user) and `cart_items` (line items with quantity and unit price).
- ORM migrations are manual; metadata auto-creates tables at startup when using SQLite.

## API Summary

- `POST /carts` create a cart with optional seed items.
- `GET /carts/{user_id}` fetch a user cart.
- `POST /carts/{user_id}/items` add or increment product quantity (auto-creates cart).
- `PATCH /carts/status/{user_id}` update cart status.
- `PATCH /carts/{user_id}/items/{product_id}` set quantity or unit price.
- `PUT /carts/{user_id}/items` replace the entire item list.
- `DELETE /carts/{user_id}/items/{product_id}` remove a single item.
- `DELETE /carts/{user_id}/items` clear all items.
- `DELETE /carts/{user_id}` delete the cart.

## Sample Requests

Set `BASE_URL` to your server host, e.g. `http://localhost:8002`.

Create cart

```
curl -X POST "$BASE_URL/carts" \
	-H "Content-Type: application/json" \
	-d '{
				"user_id": 1,
				"status": "PENDING",
				"items": [
					{"product_id": 101, "quantity": 2, "unit_price": 1999}
				]
			}'
```

Add item

```
curl -X POST "$BASE_URL/carts/1/items" \
	-H "Content-Type: application/json" \
	-d '{"product_id": 102, "quantity": 1, "unit_price": 4999}'
```

Update status

```
curl -X PATCH "$BASE_URL/carts/status/1" \
	-H "Content-Type: application/json" \
	-d '{"status": "CHECKOUT"}'
```

Remove item

```
curl -X DELETE "$BASE_URL/carts/1/items/102"
```

## Error Examples

- `GET /carts/9999` -> 404 when cart is absent.
- `PATCH /carts/status/1` with `{}` -> 400 for empty payload.
- `PATCH /carts/1/items/9999` -> 404 when item not found.

## Testing

- Use `pytest` for unit tests once implemented.
- Exercise endpoints via `curl` or an API client to confirm expected responses.
