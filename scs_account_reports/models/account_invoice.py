"""Account Invoice Model."""

from odoo import models, api


class AccountInvoice(models.Model):
    """Account Invoice Model."""

    _inherit = "account.invoice"

    @api.model
    def get_invoice_bill_bank_details(self):
        """Method to print the bank details in invoice Q-web report."""
        self.ensure_one()
        invoice_bank_detals = {'bank_name': '', 'bsb': '', 'acc_number': ''}
        company = self.company_id and self.company_id
        bank = False
        if not company:
            company = self.env.user.company_id
        if self.partner_bank_id:
            bank = self.partner_bank_id
        else:
            if company:
                bank = self._get_partner_bank_id(company.id)
        if bank:
            invoice_bank_detals.update({
                'bank_name': bank.bank_id and bank.bank_id.name or '',
                'bsb': bank.aba_bsb or '',
                'acc_number': bank.acc_number or ''
            })
        return invoice_bank_detals
