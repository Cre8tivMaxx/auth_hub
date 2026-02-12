import frappe
from frappe import _
PROFILES = ["Admin", "System Manager"]
ROLES = ["Admin", "System Manager"]

API_USER_EMAIL = "system_manager@example.com" # Use the same email from after_install

def prevent_role_deletion(doc, method):
    """Prevent deletion of Admin and System Manager roles."""

    if doc.role_name in ROLES:
        frappe.throw(
            _("Role {0} is protected and cannot be deleted.").format(
                doc.role_name),
            frappe.ValidationError
        )


def prevent_profile_deletion(doc, method):
    """Prevent deletion of Admin and System Manager module profiles."""

    if doc.module_profile_name in PROFILES:
        frappe.throw(
            _("Module Profile {0} is protected and cannot be deleted.").format(
                doc.module_profile_name),
            frappe.ValidationError
        )




def prevent_user_modification(doc, method):
    """Prevent modification of the protected API user."""
    if doc.email == API_USER_EMAIL and not doc.is_new():
        frappe.throw(
            _("API User {0} is protected and cannot be modified.").format(
                doc.email),
            frappe.ValidationError
        )


def prevent_user_deletion(doc, method):
    """Prevent deletion of the protected API user."""
    if doc.email == API_USER_EMAIL:
        frappe.throw(
            _("API User {0} is protected and cannot be deleted.").format(
                doc.email),
            frappe.ValidationError
        )
