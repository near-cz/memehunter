# Dashboard MVP

The first dashboard is a static, responsive frontend at `apps/dashboard/index.html`.

## Run locally

Open `apps/dashboard/index.html` in a browser. No build step is required.

## Current behavior

- Shows service connection states as not configured.
- Starts with zero opportunities and no fabricated market metrics.
- Provides basic opportunity filters for the future API-backed list.
- Explicitly indicates read-only mode; no transaction or launch controls are exposed.

## Next integration

The dashboard should consume a read-only API endpoint such as `GET /api/v1/opportunities` and a health endpoint such as `GET /api/v1/health`. It must never receive wallet private keys or sign transactions. API authentication, CORS allow-listing, rate limits, and server-side validation are required before remote deployment.
