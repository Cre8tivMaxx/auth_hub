import frappe

from auth_hub.api.permissions import create_permissions, ensure_permission_exists

# TODO: Setup a logger that log errors, messages inside (logs/auth_hub.error.log, logs/auth_hub.log)


def _validate_token():
	"""Validate the X-Auth-Token request header against site config.

	Reads `auth_hub_token` from site_config.json (frappe.conf) and compares
	it to the incoming X-Auth-Token header.

	Raises:
		frappe.AuthenticationError: if the token is missing or does not match.

	Note:
		Set the token on each child site with:
		    bench --site <sitename> set-config auth_hub_token <random-long-string>
	"""
	token = frappe.request.headers.get("X-Auth-Token")
	expected = frappe.conf.get("auth_hub_token")
	if not token or not expected or token != expected:
		frappe.throw("Invalid or missing X-Auth-Token", frappe.AuthenticationError)


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
	_validate_token()
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
	_validate_token()
	try:
		frappe.get_doc(user).insert(ignore_permissions=True)
	except Exception:
		frappe.log_error(title="auth_hub.create_user")
		frappe.throw("Could not create user on hub site", frappe.ValidationError)
	return True


@frappe.whitelist(allow_guest=True)
def update_user(user: dict):
	"""Update an existing user on this site with a replicated profile.

	Args:
		user (dict): dict of user's data, typically from
			`frappe.get_doc("User", email).as_dict()` on the consumer side.
			Must carry an "email" (or "name") identifying an existing user.

	Returns:
		bool: True if the user was successfully updated.

	Note:
		Accessible through <website>/api/method/auth_hub.api.api.update_user
	"""
	_validate_token()
	email = user.get("email") or user.get("name")
	if not email or not frappe.db.exists("User", email):
		frappe.throw(
			f"User with email address {email} does not exist",
			frappe.DoesNotExistError,
		)
	try:
		doc = frappe.get_doc("User", email)
		doc.update(user)
		doc.save(ignore_permissions=True)
	except Exception:
		frappe.log_error(title=f"auth_hub.update_user [{email}]")
		frappe.throw("Could not update user on hub site", frappe.ValidationError)
	return True


@frappe.whitelist(allow_guest=True)
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
	_validate_token()
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
		profile_name: The name of the Role, Module Profiles

	Returns:
		bool: True if the user was successfully created, False otherwise.

	Note:
		Accessible through <website>/api/method/auth_hub.api.assign_permission_to_user?email={email}&profile_name={admin or system_manager}
	"""
	_validate_token()
	if not ensure_signed_up(email):
		frappe.throw(
			(f"User with email address {email} does not exist"),
			frappe.DoesNotExistError,
		)

	# Normalize: "cre8tiv_maxx_team" → "Cre8tiv Maxx Team", "Admin" → "Admin"
	profile_title = frappe.unscrub(frappe.scrub(profile_name))

	role_profile_exists = bool(frappe.db.exists("Role Profile", profile_title))

	if not role_profile_exists:
		if frappe.scrub(profile_name) in ("admin", "system_manager"):
			# Built-in profile — create it if missing
			create_permissions(profile_name)
		else:
			# Custom profile — must already exist on this site
			frappe.log_error(
				title=f"auth_hub.assign_permission_to_user: Role Profile '{profile_title}' not found on this site"
			)
			frappe.throw(
				f"Role Profile `{profile_title}` does not exist on this site. Create it first.",
				frappe.DoesNotExistError,
			)

	try:
		doc = frappe.get_doc("User", email)
		doc.set("role_profile_name", profile_title)
		# Only set module_profile if one with this name exists — avoid LinkValidationError
		if frappe.db.exists("Module Profile", profile_title):
			doc.set("module_profile", profile_title)
		doc.save(ignore_permissions=True)

	except Exception:
		frappe.log_error(title=f"auth_hub.assign_permission_to_user [{email}]")
		frappe.throw(
			f"Could not assign profile `{profile_title}` to {email}",
			frappe.ValidationError,
		)
	return True


@frappe.whitelist(allow_guest=True)
def disable_user(email: str):
	"""Disable a user account on this site.

	Args:
		email (str): The email address of the user to disable.

	Returns:
		bool: True if the user was successfully disabled.

	Note:
		Accessible through <website>/api/method/auth_hub.api.api.disable_user
	"""
	_validate_token()
	if not frappe.db.exists("User", email):
		frappe.throw(f"User with email address {email} does not exist", frappe.DoesNotExistError)

	frappe.db.set_value("User", email, "enabled", 0)
	frappe.db.commit()
	return True


@frappe.whitelist(allow_guest=True)
def enable_user(email: str):
	"""Enable a user account on this site.

	Args:
		email (str): The email address of the user to enable.

	Returns:
		bool: True if the user was successfully enabled.

	Note:
		Accessible through <website>/api/method/auth_hub.api.api.enable_user
	"""
	_validate_token()
	if not frappe.db.exists("User", email):
		frappe.throw(f"User with email address {email} does not exist", frappe.DoesNotExistError)

	frappe.db.set_value("User", email, "enabled", 1)
	frappe.db.commit()
	return True


@frappe.whitelist(allow_guest=True)
def get_installed_apps():
	"""Returns a list of installed apps

	Example:
	>>> get_installed_apps()
	[
	    {
	        "app_name": "frappe",
	        "app_version": "14.0.0"
	    }
	]

	Returns:
	    list: list of installed apps

	Note:
	    Accessible through <website>/api/method/auth_hub.api.get_installed_apps

	"""
	_validate_token()
	apps = frappe.get_all("Installed Application", fields=["app_name", "app_version"])

	return apps
