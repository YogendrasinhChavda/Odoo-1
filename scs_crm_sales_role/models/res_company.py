"""Res Company Model."""

from odoo import api, models


class ResCompany(models.Model):
    """Res Company Model Inherit."""

    _inherit = "res.company"

    @api.multi
    def remove_date_end_from_pricelistitem(self):
        """Method to remove date end from price list item."""
        self.env.cr.execute("update product_pricelist_item set \
            date_end=null")

    @api.multi
    def update_sales_team_in_quote_sales_order(self):
        """Method to set sales team in Quotation/Sale Orders."""
        sale_obj = self.env['sale.order']
        sales_ords = sale_obj.search([
            ('partner_id', '!=', False),
            ('team_id', '=', False)])
        for sale_ord in sales_ords:
            if sale_ord.partner_id.team_id:
                sale_ord.write({
                    'team_id': sale_ord.partner_id.team_id.id or False
                })
            elif sale_ord.partner_id.parent_id and \
                    sale_ord.partner_id.parent_id.team_id:
                sale_ord.write({
                    'team_id':
                    sale_ord.partner_id.parent_id.team_id.id or False
                })

    @api.multi
    def update_sales_team_in_account_invoice(self):
        """Method to set sales team in Sales Invoices."""
        invoice_obj = self.env['account.invoice']
        sales_invoices = invoice_obj.search([
            ('partner_id', '!=', False),
            ('team_id', '=', False),
            ('type', 'in', ['out_invoice', 'out_refund'])])
        for sale_inv in sales_invoices:
            if sale_inv.partner_id:
                if sale_inv.partner_id.team_id:
                    sale_inv.write({
                        'team_id': sale_inv.partner_id.team_id.id or False
                    })
                elif sale_inv.partner_id.parent_id and \
                        sale_inv.partner_id.parent_id.team_id:
                    sale_inv.write({
                        'team_id':
                        sale_inv.partner_id.parent_id.team_id.id or False
                    })

    @api.multi
    def update_sales_person_in_quote_sales_order(self):
        """Method to update sales person reference in sale order."""
        """Due to the studio fields that reference is missing need to fix."""
        sale_obj = self.env['sale.order']
        sales_ords = sale_obj.search([
            ('partner_id', '!=', False),
            ('user_id', '=', False)])
        for sale_ord in sales_ords:
            if sale_ord.partner_id.user_id:
                sale_ord.write({
                    'user_id': sale_ord.partner_id.user_id.id or False
                })
            elif sale_ord.partner_id.parent_id and \
                    sale_ord.partner_id.parent_id.user_id:
                sale_ord.write({
                    'user_id':
                    sale_ord.partner_id.parent_id.user_id.id or False
                })

    @api.multi
    def update_sales_person_in_account_invoice(self):
        """Method to update sales person reference in account invoice."""
        """Due to the studio fields that reference is missing need to fix."""
        invoice_obj = self.env['account.invoice']
        cust_invs = invoice_obj.search([
            ('partner_id', '!=', False),
            ('user_id', '=', False),
            ('type', 'in', ['out_invoice', 'out_refund'])])
        for cust_inv in cust_invs:
            if cust_inv.partner_id.user_id:
                cust_inv.write({
                    'user_id': cust_inv.partner_id.user_id.id or False
                })
            elif cust_inv.partner_id.parent_id and \
                    cust_inv.partner_id.parent_id.user_id:
                cust_inv.write({
                    'user_id':
                    cust_inv.partner_id.parent_id.user_id.id or False
                })

    @api.multi
    def update_sales_person_in_account_invoice_lines(self):
        """Method to update sales person reference in account invoice lines."""
        """Due to the studio fields that reference is missing need to fix."""
        inv_line_obj = self.env['account.invoice.line']
        inv_lines = inv_line_obj.search([
            ('x_studio_sales_person', '=', False),
            ('invoice_id', '!=', False),
            ('invoice_id.user_id', '!=', False)])
        for inv_line in inv_lines:
            inv_line.write({
                'x_studio_sales_person': inv_line.invoice_id.user_id.id
            })

    # @api.multi
    # def update_taxes_tags(self):
    #     """Method to update taxes tags to print Tax report."""
    #     tax_obj = self.env['account.tax']
    #     taxes = tax_obj.sudo().search([('company_id', '=', 1)])
    #     if taxes:
    #         for tax in taxes:
    #             self._cr.execute(
    #                 "select account_account_tag_id from \
    #                     account_tax_account_tag where \
    #                     account_tax_id=%s" % (tax.id,))
    #             row = self._cr.fetchall()
    #             tags = []
    #             if row:
    #                 tags = [i[0] for i in row if i and len(i) >= 1] or []
    #             taxes_same = tax_obj.sudo().search([
    #                 ('company_id', '=', 2),
    #                 ('name', 'ilike', tax.name)])
    #             if taxes_same:
    #                 taxes_same.write({'tag_ids': [(6, 0, tags)]})
