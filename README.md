# Freshmart

**Live demo:** https://freshmart-j97h.onrender.com

**Okwuii's Grocery Store (OGS)**: a grocery delivery demo. A Python (FastAPI) app that renders its own pages (Jinja2 + HTMX), with TypeScript for the cart and checkout, in one repository.

```
Freshmart/
├── apps/
│   ├── api/        Python FastAPI backend (accounts, orders, staff inbox)
│   └── web/        TypeScript source (src/), CSS, HTMX and the compiled bundle (static/)
├── docs/           Architecture, API reference, deployment, security
├── scripts/        Small helpers (secrets, cleanup)
├── .github/        CI workflow and pull request template
├── Makefile        One-command setup, dev, test, lint
└── render.yaml     Render Blueprint (API + Postgres)
```

## Quick start

You need Python 3.11 or newer, and Node 20+ only if you change the TypeScript.

```bash
make setup     # create apps/api/.venv, install Python and TypeScript dependencies
make dev       # http://localhost:4000 (API and storefront together)
make test      # run the test suite
make lint      # check Python style and type-check the TypeScript (make format to fix)
make build-web # recompile TypeScript after editing apps/web/src (commit the result)
```

Run `make help` for the full list. With no `DATABASE_URL` set, data is kept in a local JSON file (`apps/api/data/db.json`). Set `DATABASE_URL` to use Postgres.

## What is real and what is simulated

| Real | Simulated or optional |
| --- | --- |
| Accounts with hashed passwords and httpOnly session cookies | Card, bank transfer and USSD payments (no money moves) |
| Orders saved server-side with prices recalculated from the server catalog, and a staff-only inbox behind a staff key | The new-order SMS reaches the shop's phone only once an SMS gateway is configured; until then it stays in the staff feed |

To make payments real, integrate Paystack or Flutterwave.

SMS is already wired to the API. Set `SMS_PROVIDER`, `SMS_API_KEY`, `SMS_SENDER_ID` and `STORE_PHONE` and every new order is texted to the shop's phone through Termii or Africa's Talking; leave them unset and the message is only collected in the staff feed, as before. The gateway is called server-side, never from the browser.

## Documentation

- [Architecture](docs/architecture.md): how the pieces fit together
- [API reference](docs/api.md): every endpoint
- [Deployment](docs/deployment.md): Render setup and environment variables
- [Security notes](docs/security.md): what is protected and known limits
- [Orders, tracking and cancellation](docs/orders.md): statuses, cancel, tracking
- [Contributing](CONTRIBUTING.md): workflow and conventions

## License

See [LICENSE](LICENSE).
