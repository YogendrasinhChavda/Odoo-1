"""Res Company Model."""

from odoo import api, models


class ResCompany(models.Model):
    """Res Company Model Inherit."""

    _inherit = "res.company"

    @api.multi
    def update_sales_person_in_invoice_lines(self):
        """Method to update sales person reference in invoice lines."""
        """Due to the studio fields that reference is missing need to fix."""
        invoice_obj = self.env['account.invoice']
        cust_invs = invoice_obj.search([])
        print("\n cust_invs ::::::::::", len(cust_invs))
        if cust_invs:
            for cust_inv in cust_invs:
                sales_person = cust_inv.user_id and \
                    cust_inv.user_id.id or False
                if sales_person and cust_inv.invoice_line_ids:
                    cust_inv.invoice_line_ids.write({
                        'x_studio_sales_person': sales_person
                    })
        print("\n DONE ::::::::::")

    @api.multi
    def update_taxes_tags(self):
        """Method to update taxes tags to print Tax report."""
        tax_obj = self.env['account.tax']
        taxes = tax_obj.sudo().search([('company_id', '=', 1)])
        print("\n taxes ::::::::::", len(taxes))
        if taxes:
            for tax in taxes:
                print("\n tax :::::::::::::", tax)
                self._cr.execute(
                    "select account_account_tag_id from \
                        account_tax_account_tag where \
                        account_tax_id=%s" % (tax.id,))
                row = self._cr.fetchall()
                print("\n row :::::::::::::", row)
                tags = []
                if row:
                    tags = [i[0] for i in row if i and len(i) >= 1] or []
                taxes_same = tax_obj.sudo().search([
                    ('company_id', '=', 2),
                    ('name', 'ilike', tax.name)])
                if taxes_same:
                    taxes_same.write({'tag_ids': [(6, 0, tags)]})
        print("\n DONE ::::::::::")
