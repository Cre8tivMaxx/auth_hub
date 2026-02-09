import frappe

@frappe.whitelist(allow_guest=True)
def get_context():
    return {
        "sites": ["Capital", "demo", "majd", "ERP16 site" ,"Other Site"],
        "status": ["Enabled", "Disabled"],
        "installed_apps": ["ERPnext", "CRM", "HRMs", "Lms", "Education", "Payments"],
        "Description": "It will be always a short description like two lines maximum",
        "login": "https://demo-capital.cre8tiv-maxx.com/"
    }