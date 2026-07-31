"""Field metadata API — provides dynamic field discovery for list view controls."""

import frappe
from frappe import _
from frappe.model import no_value_fields

from frappe_vault.utils.constants import SENSITIVE_FIELDS

ALLOWED_FILTER_FIELDTYPES = [
    "Check",
    "Data",
    "Float",
    "Int",
    "Currency",
    "Dynamic Link",
    "Link",
    "Long Text",
    "Select",
    "Small Text",
    "Text Editor",
    "Text",
    "Date",
    "Datetime",
]

STANDARD_FILTERABLE_FIELDS = [
    {"fieldname": "name", "fieldtype": "Link", "label": "Name", "options": "Vault Secret"},
    {"fieldname": "owner", "fieldtype": "Link", "label": "Created By", "options": "User"},
    {"fieldname": "modified_by", "fieldtype": "Link", "label": "Last Updated By", "options": "User"},
    {"fieldname": "_user_tags", "fieldtype": "Data", "label": "Tags"},
    {"fieldname": "_liked_by", "fieldtype": "Data", "label": "Like"},
    {"fieldname": "_comments", "fieldtype": "Text", "label": "Comments"},
    {"fieldname": "creation", "fieldtype": "Datetime", "label": "Created On"},
    {"fieldname": "modified", "fieldtype": "Datetime", "label": "Last Updated On"},
]

STANDARD_SORT_FIELDS = [
    {"label": "Name", "fieldname": "name"},
    {"label": "Created On", "fieldname": "creation"},
    {"label": "Last Modified", "fieldname": "modified"},
    {"label": "Modified By", "fieldname": "modified_by"},
    {"label": "Owner", "fieldname": "owner"},
]


@frappe.whitelist()
def get_filterable_fields(doctype="Vault Secret"):
    """Return fields that can be used as list filters, read from DocType meta.

    Excludes sensitive fields (passwords, keys) and layout-only fields.
    Includes standard fields like name, owner, creation, modified.
    """
    meta = frappe.get_meta(doctype)

    fields = []
    for field in STANDARD_FILTERABLE_FIELDS + meta.fields:
        fd = field if isinstance(field, dict) else field.as_dict()
        fieldname = fd.get("fieldname")
        fieldtype = fd.get("fieldtype")
        label = fd.get("label")

        if not fieldname or not fieldtype or not label:
            continue
        if fieldtype not in ALLOWED_FILTER_FIELDTYPES:
            continue
        if fieldname in SENSITIVE_FIELDS:
            continue

        fields.append({
            "fieldname": fieldname,
            "fieldtype": fieldtype,
            "label": _(label),
            "value": fieldname,
            "name": fieldname,
            "options": fd.get("options", ""),
        })

    return fields


@frappe.whitelist()
def get_sort_options(doctype="Vault Secret"):
    """Return fields available for sorting, read from DocType meta.

    Excludes layout-only fields (Section Break, Column Break, etc.)
    and sensitive fields. Includes standard sort fields.
    """
    meta = frappe.get_meta(doctype)

    fields = []
    for field in meta.fields:
        fd = field if isinstance(field, dict) else field.as_dict()
        fieldname = fd.get("fieldname")
        fieldtype = fd.get("fieldtype")
        label = fd.get("label")

        if not fieldname or not label:
            continue
        if fieldtype in no_value_fields:
            continue
        if fieldname in SENSITIVE_FIELDS:
            continue

        fields.append({
            "label": _(label),
            "value": fieldname,
            "fieldname": fieldname,
        })

    for sf in STANDARD_SORT_FIELDS:
        fields.append({
            "label": _(sf["label"]),
            "value": sf["fieldname"],
            "fieldname": sf["fieldname"],
        })

    return fields
