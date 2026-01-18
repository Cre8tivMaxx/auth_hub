### Auth Hub

Single Sign On application, that manages login to provided frappe sites by one click!

### Installation
Make sure you are in your frappe-bench dir.

```bash
cd ~/frappe-bench
bench get-app https://github.com/Cre8tivMaxx/auth_hub --branch develop
bench --site YOUR_SITE_NAME install-app auth_hub
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/auth_hub
pre-commit install
```
