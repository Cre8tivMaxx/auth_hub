# Copyright (c) 2026, Cre8tiv-maxx and Contributors
# See license.txt

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from auth_hub.api import api

TOKEN = "test-secret-token"


def _req(token: str | None):
	headers = {"X-Auth-Token": token} if token is not None else {}
	return frappe._dict(headers=headers)


class TestTokenValidation(FrappeTestCase):
	"""Every hub endpoint must reject calls without the shared X-Auth-Token."""

	def test_ensure_signed_up_rejects_missing_token(self):
		with (
			patch.object(frappe, "request", _req(None)),
			patch.dict(frappe.conf, {"auth_hub_token": TOKEN}),
		):
			with self.assertRaises(frappe.AuthenticationError):
				api.ensure_signed_up("someone@example.com")

	def test_get_installed_apps_rejects_wrong_token(self):
		with (
			patch.object(frappe, "request", _req("wrong")),
			patch.dict(frappe.conf, {"auth_hub_token": TOKEN}),
		):
			with self.assertRaises(frappe.AuthenticationError):
				api.get_installed_apps()

	def test_get_installed_apps_allows_valid_token(self):
		with (
			patch.object(frappe, "request", _req(TOKEN)),
			patch.dict(frappe.conf, {"auth_hub_token": TOKEN}),
		):
			result = api.get_installed_apps()
		self.assertIsInstance(result, list)


class TestAssignPermissionFailure(FrappeTestCase):
	def setUp(self):
		self.email = "perm-target@example.com"
		if not frappe.db.exists("User", self.email):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": self.email,
					"first_name": "Perm",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)

	def test_save_failure_raises_instead_of_returning_exception(self):
		"""Regression: previously returned the exception object (truthy => silent success)."""
		with (
			patch.object(frappe, "request", _req(TOKEN)),
			patch.dict(frappe.conf, {"auth_hub_token": TOKEN}),
			patch.object(api, "ensure_permission_exists", return_value=True),
			patch.object(frappe, "log_error"),
			patch.object(frappe, "get_doc", side_effect=Exception("save boom")),
		):
			with self.assertRaises(frappe.ValidationError):
				api.assign_permission_to_user(self.email, "Admin")


class TestUpdateUser(FrappeTestCase):
	def setUp(self):
		self.email = "update-target@example.com"
		if not frappe.db.exists("User", self.email):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": self.email,
					"first_name": "Before",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)

	def test_rejects_missing_token(self):
		with (
			patch.object(frappe, "request", _req(None)),
			patch.dict(frappe.conf, {"auth_hub_token": TOKEN}),
		):
			with self.assertRaises(frappe.AuthenticationError):
				api.update_user({"email": self.email, "first_name": "After"})

	def test_unknown_user_raises(self):
		with (
			patch.object(frappe, "request", _req(TOKEN)),
			patch.dict(frappe.conf, {"auth_hub_token": TOKEN}),
		):
			with self.assertRaises(frappe.DoesNotExistError):
				api.update_user({"email": "nobody-here@example.com", "first_name": "X"})

	def test_updates_existing_user(self):
		with (
			patch.object(frappe, "request", _req(TOKEN)),
			patch.dict(frappe.conf, {"auth_hub_token": TOKEN}),
		):
			result = api.update_user({"email": self.email, "first_name": "After"})
		self.assertTrue(result)
		self.assertEqual(frappe.db.get_value("User", self.email, "first_name"), "After")
