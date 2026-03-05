# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Overview

**Auth Hub** is the SSO central hub Frappe app. It lives on a dedicated SSO site and exposes API endpoints that other sites (running **Auth Consumer**) call to authenticate users. Together they implement one-click cross-site login.

**Auth Consumer** (`/home/frappe/frappe-bench/apps/auth_consumer`) is installed on each child/client Frappe site. It calls Auth Hub's APIs via HTTP `requests` to check user existence, replicate users, assign permissions, and generate temporary login links.

## SSO Flow

```
Consumer site (auth_consumer) → Auth Hub site (auth_hub)
  1. ensure_signed_up(email)         → check if user exists
  2. create_user(user_dict)          → replicate user if not exists
  3. assign_permission_to_user()     → set role/module profile
  4. create_temp_login_link(email)   → Redis-cached key, expiry 1.5 min
     → returns /api/method/frappe.www.login.login_via_key?key=...
```

The `authenticate_user()` function in `auth_consumer/api/api.py` orchestrates the full flow.

## Common Commands

```bash
# Install apps on a site
bench --site {site_name} install-app auth_hub
bench --site {site_name} install-app auth_consumer

# Development server
bench start

# Linting (Python)
ruff check auth_hub/
ruff format auth_hub/

# Pre-commit (runs ruff, prettier, eslint)
pre-commit install   # one-time setup
pre-commit run --all-files

# Run tests
bench --site {site_name} run-tests --app auth_hub
bench --site {site_name} run-tests --app auth_consumer

# Run a single test
bench --site {site_name} run-tests --app auth_hub --module auth_hub.auth_hub.doctype.site.test_site
```

## Key File Locations

### auth_hub
| File | Purpose |
|------|---------|
| `auth_hub/api/api.py` | Whitelisted API endpoints exposed to consumers |
| `auth_hub/api/permissions.py` | Role Profile / Module Profile creation logic |
| `auth_hub/install.py` | `after_install` and `after_app_install` hooks |
| `auth_hub/www/home.html` | Portal page shell (loads auth_consumer's React bundle) |
| `auth_hub/www/home.py` | Jinja context for the portal (static placeholder data) |
| `auth_hub/hooks.py` | `after_install`, `after_app_install` registrations |

### auth_consumer
| File | Purpose |
|------|---------|
| `auth_consumer/api/api.py` | HTTP client functions calling auth_hub endpoints |
| `auth_consumer/www/home.py` | SPA page controller; provides boot data + CSRF token |
| `auth_consumer/hooks.py` | SPA route rules (`/home`, `/home/<path>`) |
| `auth_consumer/auth_consumer/doctype/site/site.py` | `Site` doctype (stub, not yet implemented) |

## Architecture Notes

- **Permissions system**: Two profiles (`Admin`, `System Manager`) are created on `after_install`. `Admin` gets all roles/modules; `System Manager` gets only Frappe core modules. When a new app is installed (`after_app_install`), permissions are refreshed via `update_existed_permissions()`.

- **Email account config**: `create_email_account()` reads `email_account_mail` and `email_account_password` from `frappe.local.conf` (i.e., `site_config.json`). These must be set manually — installation silently skips email setup if missing.

- **API endpoint naming**: Auth Hub endpoints are at `auth_hub.api.api.*` (note the double `api`). This is intentional — the module is `auth_hub/api/api.py`. Consumer hardcodes these paths as constants at the top of `auth_consumer/api/api.py`.

- **Frontend (auth_consumer)**: The React SPA lives in `home/` inside auth_consumer, built with Vite. The compiled bundle is served as Frappe public assets. The `home.html` page injects `window.csrf_token` from the server.

- **Bruno API collection**: `Auth Hub Requests/` directory contains `.bru` files for manual API testing against `demo.cre8tiv-maxx.com`.

## Known TODOs in the Codebase

- Logger setup (`logs/auth_hub.error.log`) — not yet implemented
- Config doctype for hardcoded values (email, domain, `EXCLUDE` set, `TEMP_LOGIN_LINK` paths)
- `create_accounts_permissions()` and `crete_purchase_permission()` — stubs
- `Site` doctype — empty controller, not yet connected to SSO flow

## Code Style

- Python: tabs for indentation, `ruff` with `line-length = 110`, `target-version = "py310"`
- Quotes: double quotes (`ruff.format.quote-style = "double"`)
- JS/CSS: prettier + eslint via pre-commit
