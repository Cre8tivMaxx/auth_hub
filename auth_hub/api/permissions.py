import frappe

# TODO: Add EXCLUDE to a config file
EXCLUDE = {"Guest", "All", "Administrator", "Employee"}


# TODO -> let this function to be called after_install
# TODO -> create a function `create_system_defaults` and add create_permissions inside it.


@frappe.whitelist(allow_guest=True)
def create_permissions(profile_name=None):
    """Create a role profile and module profile for the given profile name

    Args:
        profile_name: The name of the Role, Module Profiles
        choose from (Admin, System Manager) default is System Manager
    Note:
        Accessible through <website>/api/method/auth_hub.permissions.create_permissions?profile_name={Admin or System Manager}
    """
    profile_name = frappe.scrub(profile_name) if profile_name else ""
    profile_title = frappe.unscrub(profile_name)
    if not profile_name or profile_name == "system_manager":
        create_system_manager_permission(profile_title)

    if profile_name == "admin":
        create_admin_permission(profile_title)


def create_admin_permission(profile):
    # Create Role Profile
    roles = [r for r in frappe.get_all("Role", pluck="name") if r not in EXCLUDE]
    _create_role_profile(profile, roles)

    # Create Module Profile
    block_modules = []  # Allow all modules.
    _create_module_profile(profile, block_modules)


def create_system_manager_permission(profile):
    # Create Role Profile
    roles = ["System Manager", "Desk User"]
    _create_role_profile(profile, roles)

    # Block everything except frappe modules
    block_modules = frappe.get_all(
        "Module Def", filters=[["app_name", "!=", "frappe"]], pluck="name"
    )
    _create_module_profile(profile, block_modules)


# TODO
def create_accounts_permissions(profile):
    pass


# TODO
def crete_purchase_permission(profile):
    pass


def _create_role_profile(role_profile_name: str, roles: list):
    """helper function to create a role profile with the given name and block the given list of modules

    Args:
        role_profile_name (str): Module Profile name (i.e `Admin`)
        roles (list): list of roles to be included i.e ["System Manager", "Sales Manager"]
                refer to `Role` DocType.
    """
    if frappe.db.exists("Role Profile", role_profile_name):
        # TODO: This one may update the role profile
        return

    # Clear existing roles in the profile
    role_profile = frappe.get_doc("Role Profile", role_profile_name)
    role_profile.set("roles", [])
    for role in roles:
        if frappe.db.exists("Role", role):
            role_profile.append("roles", {"role": role})

    role_profile.save(ignore_permissions=True)


def _create_module_profile(module_profile_name: str, block_modules: list):
    """helper function to create a module profile with the given name and block the given list of modules

    Args:
        module_profile_name (str): Module Profile name (i.e `Admin`)
        block_modules (list): modules to be blocked
                if block_modules = ["Accounts", "Buying"] then the module profile will have all permissions except ["Accounts", "Buying"]
    """
    if frappe.db.exists("Module Profile", module_profile_name):
        return
    module_profile = frappe.get_doc("Module Profile", module_profile_name)
    module_profile.set("block_modules", block_modules)
    module_profile.save(ignore_permissions=True)


@frappe.whitelist(allow_guest=True)
def ensure_permission_exists(profile_name="System Manager"):
    """Verify if a Role Profile, and Module profile already exists.

    Args:
    profile_name (str): The profile_name address to check for user existence.

    Returns:
    bool: dict(profile: bool)


    Example:
    >>> ensure_permission_exists("Admin")
    {"Role Profile"}

    Note:
    Accessible through <website>/api/method/auth_hub.permissions.ensure_permission_exists?profile_name={profile_name}
    """
    profile_name = frappe.unscrub(profile_name)
    return {
        "Role Profile": bool(frappe.db.exists("Role Profile", profile_name)),
        "Module Profile": bool(frappe.db.exists("Module Profile", profile_name)),
    }
