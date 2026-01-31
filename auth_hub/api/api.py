import frappe


@frappe.whitelist(allow_guest=True)
def ping():
	"""
	Ping the site to make sure the APIs works.
	Returns:
		bool: "pong"
	Endpoint:
		GET <website>/api/method/auth_hub.api.ping
	Example:
		>>> ping()
		"pong"

	Accessible through <website>/api/method/auth_hub.api.ping
	"""
	return "pong"


@frappe.whitelist(allow_guest=True)
def ensure_signed_up(email):
	"""
	    Verify if a user is already signed up in the system.
	    Args:
	            email (str): The email address to check for user existence.
	    Returns:
	            bool: True if a user with the given email exists, False otherwise.
	    Endpoint:
	            GET <website>/api/method/auth_hub.api.ensure_signed_up?email={email}
	    Example:
	            >>> ensure_signed_up("user@example.com")
	            True
	Accessible through <website>/api/method/auth_hub.api.ensure_signed_up?email={email}
	"""
	return bool(frappe.db.exists("User", email))


# @frappe.whitelist(all)
