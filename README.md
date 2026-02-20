# Mini Order System

A minimal order management microservice (FastAPI) exposing authentication, product and order endpoints.

**Setup Instructions**
    - Clone the repo
    `git clone https://github.com/your-username/mini-order-system.git`
    - Navigate to the repo directory
    `cd mini-order-system`

- **Prerequisites:** Python 3.10+ (recommend 3.10 or 3.11), 'uv', and optionally Docker/Docker Compose.
	
	**Uvicorn (uv) setup**

    **Setup & Run Instructions (Using uv)**

    --Install uv (If Not Installed)
    Windows (PowerShell)
    -- `pip install uv`

    OR (Recommended Method):
    `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex`

    Mac / Linux
    `curl -LsSf https://astral.sh/uv/install.sh | sh`

    - Verify Installation
    `uv --version`

    --Install Dependencies
     Make sure pyproject.toml exists in the root directory, then run:
    `uv sync`

    --Run the Application
    Navigate to the folder where run.py is located and execute:
    `uv run run.py`    

	- Run the app with Uvicorn (development, autoreload):
	  - `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
	- Run Uvicorn in production (multiple workers):
	  - `uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4`
	- Programmatic run (if `run.py` calls `uvicorn.run()`):
	  - `python run.py`  # `run.py` typically calls `uvicorn.run(app, host="0.0.0.0", port=8000)`



**Open API docs**

- **Swagger UI:** open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

    
**Architecture Overview**

- **Project layout:** see `app/` with these main packages:
	- `app/api` — HTTP route definitions (routers for `auth`, `orders`, `products`).
	- `app/core` — security and core config.
	- `app/db` — database initialization and session management.
	- `app/models` — ORM models representing `Order`, `Product`, `User`.
	- `app/schemas` — Pydantic request/response schemas.
	- `app/services` — business logic (e.g., `order_service.py`).
    -  `main.py` — entry point of the api.
    - `run.py` — uvicorn file to start the server.
- **Request flow:** Client -> API router -> service layer -> DB (models) -> response. Authentication is handled at the API layer and enforced via dependencies.

**Assumptions**

- The service is implemented as an ASGI app (FastAPI) and is expected to run under an ASGI server such as Uvicorn or in Docker.
- The default development DB is local and lightweight (suitable for testing). For production, replace with a managed DB (Postgres, MySQL, etc.).
- The codebase uses per-request DB sessions; long-running or heavy background work should be offloaded to a task queue.

**How Concurrency Is Handled**

I used SQLAlchemy’s .with_for_update() inside a database transaction.
This applies SELECT FOR UPDATE, which locks the product row during stock deduction.
If two customers order simultaneously, the second request waits for the first transaction to complete and then reads the updated stock value, preventing overselling.

**Flow of how to handle concurrency is handle** 
If two customers try to order the last product:

- First request locks product row
- Stock deducted inside transaction
- Second request waits
- Second reads updated stock
- If insufficient → order fails

Implemented using:
.with_for_update()

Overselling is prevented.






How to handle api
# Open Swagger
http://127.0.0.1:8000/docs


------------------------------------------------------------
2️⃣ REGISTER USERS
------------------------------------------------------------

# Create Admin
POST /register
{
  "username": "admin1",
  "password": "1234",
  "role": "admin"
}

# Create Customer
POST /register
{
  "username": "customer1",
  "password": "1234",
  "role": "customer"
}


------------------------------------------------------------
3️⃣ LOGIN
------------------------------------------------------------

POST /login
Form Data:
username = admin1
password = 1234

Response:
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}

# Click "Authorize" in Swagger
# Enter:
Bearer JWT_TOKEN


------------------------------------------------------------
4️⃣ CREATE PRODUCT (Admin Only)
------------------------------------------------------------

POST /products
{
  "name": "Laptop",
  "price": 50000,
  "stock_quantity": 5
}

POST /products
{
  "name": "Mouse",
  "price": 500,
  "stock_quantity": 10
}


------------------------------------------------------------
5️⃣ LIST PRODUCTS (Pagination)
------------------------------------------------------------

GET /products?page=1&limit=10


------------------------------------------------------------
6️⃣ LOGIN AS CUSTOMER
------------------------------------------------------------

POST /login
username = customer1
password = 1234

Authorize with new token.


------------------------------------------------------------
7️⃣ PLACE ORDER
------------------------------------------------------------

POST /orders
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}

✔ Stock is reduced
✔ Order status = PENDING


------------------------------------------------------------
8️⃣ LIST ORDERS
------------------------------------------------------------

GET /orders
GET /orders?status=PENDING
GET /orders?page=1&limit=10

✔ Customer sees only their orders
✔ Admin sees all orders


------------------------------------------------------------
9️⃣ CONFIRM ORDER (Admin Only)
------------------------------------------------------------

PATCH /orders/{order_id}/confirm

✔ Status becomes CONFIRMED


------------------------------------------------------------
🔟 CANCEL ORDER
------------------------------------------------------------

PATCH /orders/{order_id}/cancel

✔ Status becomes CANCELLED
✔ Stock restored

