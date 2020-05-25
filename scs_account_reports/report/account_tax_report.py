"""Account Tax Invoice Report."""
# -*- coding: utf-8 -*-

from odoo import models, api


class ReportTaxInvoiceWithPayment(models.AbstractModel):
    """Account Tax Invoice Report."""

    _name = 'report.scs_account_reports.report_tax_invoice_with_payments'
    _description = 'Account Tax Invoice Report with payment lines'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'docs': self.env['account.invoice'].browse(docids),
            'report_type': data.get('report_type') if data else '',
        }
