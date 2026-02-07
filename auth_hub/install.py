from auth_hub.api.permissions import create_permissions


def after_install():
    # Create Role and Module Profiles
    create_permissions("Admin")
    create_permissions("System Manager")
