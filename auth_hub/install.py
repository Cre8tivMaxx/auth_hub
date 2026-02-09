import frappe
from frappe.utils.password import set_encrypted_password

from auth_hub.api.permissions import create_permissions


def after_install():
	# Create Role and Module Profiles
	create_permissions("Admin")
	create_permissions("System Manager")

	# NOTE this still hardcoded
	# TODO move all variables of email,domain into a config file
	# Create Domain and Email Account
	create_email_account()
	create_email_domain()


def create_email_domain():
	"""
	Creates an Email Domain to be linked with the email account.
	"""
	if frappe.db.exists("Email Domain", "cre8tiv-maxx.com"):
		return

	frappe.get_doc(
		{
			"doctype": "Email Domain",
			"name": "cre8tiv-maxx.com",
			"domain_name": "cre8tiv-maxx.com",
			"email_server": "imap.titan.email",
			"use_imap": 1,
			"use_ssl": 1,
			"use_starttls": 0,
			"incoming_port": "993",
			"attachment_limit": 25,
			"smtp_server": "smtp.titan.email",
			"use_tls": 0,
			"use_ssl_for_outgoing": 1,
			"smtp_port": "465",
			"append_emails_to_sent_folder": 1,
			"sent_folder_name": "Sent",
		}
	).insert(ignore_permissions=True, ignore_if_duplicate=True)


def create_email_account():
	"""
	Set the Email Account Password
	"""
	email = frappe.local.conf.email_account_mail
	password = frappe.local.conf.email_account_password
	if not email or not password:
		# TODO Log a warning to user that email account isn't created
		return
	name = "cre8tiv-maxx Support"
	if frappe.db.exists("Email Account", name) or frappe.db.exists(
		{"doctype": "Email Account", "email_id": email}
	):
		return

	mail = frappe.get_doc(
		{
			"doctype": "Email Account",
			"name": name,
			"email_id": email,
			"email_account_name": "cre8tiv-maxx Support",
			"domain": "cre8tiv-maxx.com",
			"enable_outgoing": 1,
			"default_outgoing": 1,
			"always_use_account_email_id_as_sender": 1,
			"always_use_account_name_as_sender_name": 1,
			"password": password,
		}
	).insert(ignore_permissions=True)
	set_encrypted_password("Email Account", mail.name, password)
