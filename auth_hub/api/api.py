import frappe

# TODO: Setup a logger that log errors, messages inside (logs/auth_hub.error.log, logs/auth_hub.log)


@frappe.whitelist(allow_guest=True)
def ping():
    """Ping the site to make sure the APIs works.

    Example:
        >>> ping()
        "pong"

    Returns:
        str: "pong"

    Note:
        Accessible through <website>/api/method/auth_hub.api.ping
    """
    return "pong"


@frappe.whitelist(allow_guest=True)
def ensure_signed_up(email):
    """Verify if a user is already signed up in the system.

    Args:
        email (str): The email address to check for user existence.

    Returns:
        bool: True if a user with the given email exists, False otherwise.

    Example:
        >>> ensure_signed_up("user@example.com")
        True

    Note:
        Accessible through <website>/api/method/auth_hub.api.ensure_signed_up?email={email}
    """
    return bool(frappe.db.exists("User", email))


def create_user(user: dict):
    """Create a new user on the system.

    Args:
        user (dict): dict of user's data, this should be injected from
            `frappe.get_doc("User", user_email).as_dict()`.

    Returns:
        bool: True if the user was successfully created, False otherwise.

    Note:
        Accessible through <website>/api/method/auth_hub.api.create_user?user={user}
    """
    try:
        frappe.get_doc(user).insert(ignore_permissions=True)
    except Exception as e:
        # TODO: Log the error.
        return False
    return True
