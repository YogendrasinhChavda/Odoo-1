# -*- coding: utf-8 -*-
"""Inherited For Res Partner."""

from odoo import fields, models


class ResPartner(models.Model):
    """Inherited For Res Partner."""

    _inherit = "res.partner"

    x_studio_branch = fields.Char(string="Branch")
