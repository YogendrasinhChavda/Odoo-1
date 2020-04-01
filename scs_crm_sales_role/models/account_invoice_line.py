"""Account Invoice Line Model."""

from odoo import fields, models


class AccountInvoiceLine(models.Model):
    """Account Invoice Line Model."""

    _inherit = "account.invoice.line"

    partner_parent_id = fields.Many2one(related="partner_id.parent_id",
                                        string="Customer Parent Name",
                                        store=True)

    # Moved Below fields here from studio custom
    x_studio_partner_salesperson = \
        fields.Many2one(related="partner_id.user_id",
                        string="Partner Salesperson", store=True)
    # Converted as compute field to fix the sales report issue
    # which is created by odoo studio
    # x_studio_partner_salesperson = \
    #     fields.Many2one(compute="_compute_sales_person",
    #                     string="Sales Person",
    #                     relation="res.users",
    #                     store=True)
    x_studio_sales_person = \
        fields.Many2one(related="sale_line_ids.order_id.user_id",
                        string="Partner Salesperson", store=True)
    x_studio_signed_amount = \
        fields.Monetary(related="price_subtotal_signed",
                        string="Signed Amount", store=True)
    x_studio_invoice_reference_status = fields.Selection(
        related="invoice_id.state",
        string="Invoice Reference Status", store=True)
    x_studio_state = fields.Many2one(
        related="sale_line_ids.order_id.partner_id.state_id",
        store=True,
        string="State")
    x_studio_country = fields.Many2one(
        related="sale_line_ids.order_id.partner_id.country_id",
        store=True,
        string="Country")

    # @api.multi
    # @api.depends('partner_id', 'partner_id.user_id',
    #              'sale_line_ids', 'sale_line_ids.order_id',
    #              'sale_line_ids.order_id.user_id')
    # def _compute_sales_person(self):
    #     """Method to set the Sales Person."""
    #     for inv_line in self:
    #         inv_line.x_studio_partner_salesperson = False
    #         if inv_line.sale_line_ids and \
    #                 inv_line.sale_line_ids[0].order_id and \
    #                 inv_line.sale_line_ids[0].order_id.user_id:
    #             inv_line.x_studio_partner_salesperson = \
    #                 inv_line.sale_line_ids[0].order_id.user_id.id
    #         elif inv_line.partner_id and inv_line.partner_id.user_id:
    #             inv_line.x_studio_partner_salesperson = \
    #                 inv_line.partner_id.user_id.id
    #         elif inv_line.invoice_id and inv_line.invoice_id.partner_id and \
    #                 inv_line.invoice_id.partner_id.user_id:
    #             inv_line.x_studio_partner_salesperson = \
    #                 inv_line.invoice_id.partner_id.user_id.id
