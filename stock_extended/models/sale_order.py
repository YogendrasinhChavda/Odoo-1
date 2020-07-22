"""Sale Order Models."""
# See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class SaleOrder(models.Model):
    """Sale Order Model."""

    _inherit = "sale.order"

    state_id = fields.Many2one(related="partner_id.state_id",
                               string="State", store=True)
