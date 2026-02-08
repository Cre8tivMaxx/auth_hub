import frappe

from auth_hub.api.permissions import create_permissions, ensure_permission_exists

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


@frappe.whitelist(allow_guest=True)
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
	except Exception:
		# TODO: Log the error.
		return False
	return True


@frappe.whitelist(True)
def create_temp_login_link(email: str, expiry: float = 1.5):
	"""create a temp login link for user using his email

	Args:
		email (str): email address of user
		expiry (float, optional): expiry date of the login link in minutes. Defaults to 1.5.

	Returns:
		str: the login end point with key.
		example:

	Note:
		Acessible through <website>/api/method/auth_hub.api.api.create_temp_login_link?email={test@example.com}
	"""
	if not frappe.db.exists("User", email):
		frappe.throw(
			(f"User with email address {email} does not exist"),
			frappe.DoesNotExistError,
		)
	if frappe.get_value("User", email, "name") == "Administrator":
		frappe.throw(
			"You are not permitted to login as Administrator, please use your own email",
			frappe.PermissionError,
		)

	key = frappe.generate_hash()
	frappe.cache.set_value(f"one_time_login_key:{key}", email, expires_in_sec=int(expiry * 60))
	return f"/api/method/frappe.www.login.login_via_key?key={key}"


# TODO: Set the default profile_name form the config doctype
@frappe.whitelist(allow_guest=True)
def assign_permission_to_user(email: str, profile_name="Admin"):
	"""Assign role and moule profile to user.

	Args:
		email (str): the email address for the user.

	Returns:
		bool: True if the user was successfully created, False otherwise.

	Note:
		Accessible through <website>/api/method/auth_hub.api.assign_permission_to_user?email={email}&profile_name={admin or system_manager}
	"""
	if not ensure_signed_up(email):
		frappe.throw(
			(f"User with email address {email} does not exist"),
			frappe.DoesNotExistError,
		)

	if not ensure_permission_exists(profile_name):
		try:
			create_permissions(profile_name)
		except frappe.DoesNotExistError:
			frappe.throw(
				(f"Role or module profiles `{profile_name}` is not exists"),
				frappe.DoesNotExistError,
			)

	try:
		profile_title = frappe.unscrub(profile_name)
		user_updates = {email: {"role_profile_name": profile_title, "module_profile": profile_title}}
		frappe.db.bulk_update("User", user_updates)
	except Exception as e:
		# TODO: Log the error.
		return e
	return True
