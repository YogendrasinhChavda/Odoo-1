"""Res Company Model."""

from odoo import api, models


class ResCompany(models.Model):
    """Res Company Model Inherit."""

    _inherit = "res.company"

    @api.multi
    def update_sales_team_in_quote_sales_order(self):
        """Method to set sales team in Quotation/Sale Orders."""
        sale_obj = self.env['sale.order']
        sales_ords = sale_obj.search([('partner_id', '!=', False)])
        print("\n sales_ords ::::::::::", sales_ords, len(sales_ords))
        for sale_ord in sales_ords:
            if sale_ord.partner_id and sale_ord.partner_id.team_id:
                sale_ord.write({
                    'team_id': sale_ord.partner_id.team_id.id or False
                })
        print("\n DONE ::::SALES ORDERS:::SALES TEAM UPDATE:::")

    @api.multi
    def update_sales_team_in_account_invoice(self):
        """Method to set sales team in Quotation/Sale Orders."""
        sale_obj = self.env['sale.order']
        sales_invoices = sale_obj.search([
            ('partner_id', '!=', False),
            ('type', 'in', ['out_invoice', 'out_refund'])])
        print("\n sales_invoices :::::::", sales_invoices, len(sales_invoices))
        for sale_inv in sales_invoices:
            if sale_inv.partner_id and sale_inv.partner_id.team_id:
                sale_inv.write({
                    'team_id': sale_inv.partner_id.team_id.id or False
                })
        print("\n DONE ::::SALES Invoices:::SALES TEAM UPDATE:::")

    @api.multi
    def update_sales_person_in_invoice_lines(self):
        """Method to update sales person reference in invoice lines."""
        """Due to the studio fields that reference is missing need to fix."""
        invoice_obj = self.env['account.invoice']
        cust_invs = invoice_obj.search([
            ('user_id', '=', False),
            ('type', 'in', ['out_invoice', 'out_refund'])])
        print("\n cust_invs ::::::::::", cust_invs, len(cust_invs))
        for cust_inv in cust_invs:
            sales_person = cust_inv.partner_id and \
                cust_inv.partner_id.user_id and \
                cust_inv.partner_id.user_id.id or False
            if sales_person:
                cust_inv.write({
                    'user_id': sales_person
                })
        print("\n DONE ::::LINES::::::")

    # @api.multi
    # def update_taxes_tags(self):
    #     """Method to update taxes tags to print Tax report."""
    #     tax_obj = self.env['account.tax']
    #     taxes = tax_obj.sudo().search([('company_id', '=', 1)])
    #     print("\n taxes ::::::::::", len(taxes))
    #     if taxes:
    #         for tax in taxes:
    #             print("\n tax :::::::::::::", tax)
    #             self._cr.execute(
    #                 "select account_account_tag_id from \
    #                     account_tax_account_tag where \
    #                     account_tax_id=%s" % (tax.id,))
    #             row = self._cr.fetchall()
    #             print("\n row :::::::::::::", row)
    #             tags = []
    #             if row:
    #                 tags = [i[0] for i in row if i and len(i) >= 1] or []
    #             taxes_same = tax_obj.sudo().search([
    #                 ('company_id', '=', 2),
    #                 ('name', 'ilike', tax.name)])
    #             if taxes_same:
    #                 taxes_same.write({'tag_ids': [(6, 0, tags)]})
    #     print("\n DONE ::::TAXES::::::")
