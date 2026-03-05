# V1 SSO System — Implementation Plan

## Overview

One admin action from the Frappe desk provisions or removes a user across every registered site automatically.
The React portal (`/home`) lets any logged-in user SSO into any site with one click, pulling site data from the database.

**Architecture:**
- `auth_hub` — installed on every child site (demo, capital, etc.). Exposes user management APIs.
- `auth_consumer` — the admin/portal site. Has a `Site` doctype listing all child sites.

---

## Issues

---

### Issue 1 — [auth_hub] Token validation + disable/enable user endpoints

**File:** `auth_hub/auth_hub/api/api.py`

**Tasks:**
- Add `_validate_token()` helper: reads `X-Auth-Token` request header, compares to `frappe.conf.auth_hub_token`
- Call `_validate_token()` at the top of `create_user`, `create_temp_login_link`, `assign_permission_to_user`
- Fix `@frappe.whitelist(True)` → `@frappe.whitelist(allow_guest=True)` on `create_temp_login_link`
- Add `disable_user(email)` endpoint: sets `User.enabled = 0`, commits
- Add `enable_user(email)` endpoint: sets `User.enabled = 1`, commits

**Operational note:** On each child site set token via:
```bash
bench --site <sitename> set-config auth_hub_token <random-long-string>
```

**Acceptance criteria:**
- Calling any endpoint without `X-Auth-Token` → `AuthenticationError`
- Calling with correct token → normal response
- `disable_user` sets `User.enabled = 0` on child site

---

### Issue 2 — [auth_consumer] Centralised HTTP client (`hub_client.py`)

**New file:** `auth_consumer/auth_consumer/api/hub_client.py`

Replaces raw `requests.post()` calls scattered in `api.py`.

**Every function must:**
1. Read `site_token` via `get_decrypted_password("Site", site_name, "site_token")`
2. Extract base URL from `site_doc.site_url`
3. Send `X-Auth-Token` header on every request
4. Apply a 10-second timeout
5. Log errors to `frappe.log_error` and raise `frappe.ValidationError` on failure

**Functions to implement:**
```python
def call_ensure_signed_up(site_doc, email) -> bool
def call_create_user(site_doc, user_doc) -> bool
def call_assign_permission(site_doc, email, profile_name) -> bool
def call_create_temp_login_link(site_doc, email) -> str   # returns full URL
def call_disable_user(site_doc, email) -> bool
def call_enable_user(site_doc, email) -> bool
def call_get_installed_apps(site_doc) -> list
```

**Acceptance criteria:**
- All auth_hub calls go through this module
- No raw `requests` calls remain in `api.py`
- Failed calls log to Error Log and raise `ValidationError`

---

### Issue 3 — [auth_consumer] Background job workers (`jobs.py`)

**New file:** `auth_consumer/auth_consumer/api/jobs.py`

**Functions:**

```python
def provision_user_all_sites(email: str, profile_name: str = "Admin"):
    """Iterates all enabled Site records, creates user + assigns permission on each."""

def disable_user_all_sites(email: str):
    """Iterates all enabled Site records, disables user on each."""
```

**Behaviour:**
- Per-site errors are logged to `frappe.log_error` but do not abort the whole batch (fail-partial, not fail-all)
- Each function returns a `results` dict: `{ site_name: "ok" | "error" }`

**Acceptance criteria:**
- One failed site does not prevent the others from being processed
- All errors appear in Frappe Error Log

---

### Issue 4 — [auth_consumer] Rewrite API endpoints (`api.py`)

**File:** `auth_consumer/auth_consumer/api/api.py`

**Changes:**

1. Rewrite all functions to use `hub_client` instead of raw `requests`
2. Add `@frappe.whitelist()` to `authenticate_user(site_url, email)` — returns full login URL string
3. Add `add_user_to_all_sites(email, profile_name="Admin")` — `@frappe.whitelist()`, enqueues `jobs.provision_user_all_sites`, returns `{"job_id": job.id}`
4. Add `remove_user_from_all_sites(email)` — `@frappe.whitelist()`, enqueues `jobs.disable_user_all_sites`, returns `{"job_id": job.id}`
5. Add `get_sites()` — `@frappe.whitelist()`, returns:
   ```python
   sites = frappe.get_all("Site", filters={"enabled": 1},
                          fields=["site_name", "site_url", "description"])
   for site in sites:
       site["installed_applications"] = frappe.get_all(
           "Installed Application",
           filters={"parent": site.site_name, "parenttype": "Site"},
           fields=["app_name", "app_version"],
       )
   ```
6. Add `sync_site_installed_apps(site_name)` — `@frappe.whitelist()`, calls `hub_client.call_get_installed_apps()` and saves to Site child table

**Bugs to fix:**
- `TEMP_LOGIN_LINK` constant missing leading `/`
- `expiry_date` kwarg → `expiry`
- `ensure_signed_up` checks `r.status_code` before calling `.json()`
- `assign_permission_to_user` has unreachable return after try/except

**Acceptance criteria:**
- React portal can call `get_sites()` and receive real data
- `authenticate_user` returns a valid one-time login URL
- Bulk provisioning/removal enqueues background jobs

---

### Issue 5 — [auth_consumer] Desk integration — custom buttons on User and Site doctypes

**New file:** `auth_consumer/auth_consumer/public/js/user.js`

Custom buttons on the `User` doctype form (skip for `Administrator` and `Guest`):

- **"Add to All Sites"** (under "Auth Hub" group): prompts for Role Profile (`Admin` / `System Manager`), calls `add_user_to_all_sites`
- **"Remove from All Sites"** (under "Auth Hub" group): shows confirm dialog, calls `remove_user_from_all_sites`

**New file:** `auth_consumer/auth_consumer/public/js/site.js`

- **"Sync Installed Apps"** button on the `Site` doctype form: calls `sync_site_installed_apps`

**File:** `auth_consumer/auth_consumer/hooks.py`

Register assets:
```python
doctype_js = {
    "User": "public/js/user.js",
    "Site": "public/js/site.js",
}
```

**Acceptance criteria:**
- "Auth Hub" button group appears on User form
- Clicking "Add to All Sites" enqueues the background job and shows a green alert
- Clicking "Remove from All Sites" shows confirm dialog then enqueues the job
- "Sync Installed Apps" button updates the Site child table

---

### Issue 6 — [auth_consumer] Fix `www/home.py` — real data + login guard

**File:** `auth_consumer/auth_consumer/www/home.py`

- Add login redirect: if `frappe.session.user == "Guest"` → redirect to `/login`
- Replace hardcoded `context.sites` with real data from `Site` doctype
- Populate `context.boot` from Frappe session

**Acceptance criteria:**
- Unauthenticated users are redirected to `/login`
- `context.sites` reflects real Site records

---

### Issue 7 — [auth_consumer] React frontend — real auth, real data, real SSO

**Files in** `auth_consumer/home/src/`

| File | Change |
|------|--------|
| `Context/AuthContext.jsx` | Replace mock login with `useFrappeAuth` from `frappe-react-sdk`. Expose `currentUser` (email). Fetch User doc with `useFrappeGetDoc`. |
| `Pages/Home.jsx` | Replace `fetch("/api/method/auth_consumer.www.home.get_context")` with `frappe.call` to `auth_consumer.auth_consumer.api.api.get_sites`. Map to `{ site_name, site_url, description, installed_applications }`. |
| `Components/AppCard.jsx` | Replace `<a href={site.login}>` with button that calls `authenticate_user` and opens returned URL in new tab. Pass `window.csrf_token` in `X-Frappe-CSRF-Token` header. |
| `Pages/Profile.jsx` | Replace `localStorage.setItem` with `useFrappeUpdateDoc("User", currentUser, {...})`. Pre-populate form from `useFrappeGetDoc("User", currentUser)`. |
| `Components/Layout.jsx` | Add redirect guard: if `isAuthenticated === false` and loading is done, redirect to `/login`. |

After changes, rebuild:
```bash
cd apps/auth_consumer/home && npm run build
bench --site <sitename> build --app auth_consumer
```

**Acceptance criteria:**
- Portal shows real site cards from the database
- Clicking Login on a site card opens a new tab and auto-logs into that site
- Profile edits persist after page reload (stored in Frappe, not localStorage)
- Unauthenticated users are redirected to `/login`

---

## Out of Scope (V1)

- Config doctype for hardcoded values (email domain, EXCLUDE set)
- Per-site role override after initial provisioning
- Real-time job progress
- Audit log / provisioning history
- Invitation email to new users

---

## Dependency Order

```
Issue 1 (auth_hub token + endpoints)
  └── Issue 2 (hub_client — needs token header)
        └── Issue 3 (jobs — needs hub_client)
              └── Issue 4 (api.py — needs jobs + hub_client)
                    ├── Issue 5 (desk buttons — needs api endpoints)
                    ├── Issue 6 (home.py — parallel, no code dep)
                    └── Issue 7 (React — needs get_sites + authenticate_user)
```

Issues 1–2 can be done in parallel. Issues 3–4 depend on Issue 2. Issues 5–7 depend on Issue 4.
