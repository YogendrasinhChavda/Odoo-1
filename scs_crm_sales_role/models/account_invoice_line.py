"""Account Invoice Line Model."""

from odoo import fields, models


class AccountInvoiceLine(models.Model):
    """Account Invoice Line Model."""

    _inherit = "account.invoice.line"

    partner_parent_id = fields.Many2one(related="partner_id.parent_id",
                                        string="Customer Parent Name",
                                        store=True)
    team_id = fields.Many2one(related="invoice_id.team_id",
                              string="Sales Team",
                              store=True)

    # Moved Below fields here from studio custom
    x_studio_partner_salesperson = fields.Many2one(
        related="invoice_id.partner_id.user_id",
        string="Partner Salesperson", store=True)

    # x_studio_customer_name = fields.Char(
    #     related="sale_line_ids.order_id.partner_id.display_name",
    #     string="Customer Name")
    x_studio_customer_name = fields.Char(
        related="invoice_id.partner_id.name",
        string="Customer Name",
        store=True)

    x_studio_sales_person = \
        fields.Many2one(
            # related="sale_line_ids.order_id.user_id",
            related="invoice_id.user_id",
            string="Salesperson", store=True)
    x_studio_signed_amount = \
        fields.Monetary(related="price_subtotal_signed",
                        string="Signed Amount", store=True)
    x_studio_invoice_reference_status = fields.Selection(
        related="invoice_id.state",
        string="Invoice Reference Status", store=True)
    x_studio_state = fields.Many2one(
        # related="sale_line_ids.order_id.partner_id.state_id",
        related="invoice_id.partner_id.state_id",
        store=True,
        string="State")
    x_studio_country = fields.Many2one(
        # related="sale_line_ids.order_id.partner_id.country_id",
        related="invoice_id.partner_id.country_id",
        store=True,
        string="Country")
