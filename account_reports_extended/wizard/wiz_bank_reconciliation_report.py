"""Wizard Bank Reconcilition Report TransientModel."""

import xlsxwriter
import os
import base64
from datetime import datetime
# from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.tools import ustr
# DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT as DTF

PAY_TYPE = {'outbound': 'Send Money', 'inbound': 'Receive Money',
            'transfer': 'Internal Transfer'}
PARTNER_TYPE = {'customer': 'Customer', 'supplier': 'Vendor'}


def _offset_format_timestamp2(src_tstamp_str, src_format, dst_format,
                              ignore_unparsable_time=True, context=None):
    if not src_tstamp_str:
        return False
    res = src_tstamp_str
    if src_format and dst_format:
        try:
            dt_value = datetime.strptime(src_tstamp_str, src_format)
            if context.get('tz', False):
                try:
                    import pytz
                    src_tz = pytz.timezone('UTC')
                    dst_tz = pytz.timezone(context['tz'])
                    src_dt = src_tz.localize(dt_value, is_dst=True)
                    dt_value = src_dt.astimezone(dst_tz)
                except Exception:
                    pass
            res = dt_value.strftime(dst_format)
        except Exception:
            if not ignore_unparsable_time:
                return False
            pass
    return res


class WizBankReconciliationReportExported(models.TransientModel):
    """Wizard Bank Reconcilition Report Exported TransientModel."""

    _name = 'wiz.bank.reconciliation.report.exported'
    _description = "Wizard Bank Reconcilition Report Exported"

    file = fields.Binary("Click On Download Link To Download Xlsx File",
                         readonly=True)
    name = fields.Char(string='File Name', size=32)


class WizBankReconciliationReport(models.TransientModel):
    """Wizard Bank Reconcilition Report TransientModel."""

    _name = 'wiz.bank.reconciliation.report'
    _description = "Wizard Bank Reconcilition Report"

    date_from = fields.Date(string='Start Date',
                            default=datetime.today().replace(
                                day=1, month=1).date())
    date_to = fields.Date(string='End Date',
                          default=datetime.today().replace(
                              day=31, month=12).date())
    company_id = fields.Many2one("res.company", string="Company",
                                 default=lambda self: self.env.user and
                                 self.env.user.company_id)
    journal_ids = fields.Many2many("account.journal",
                                   "wiz_bank_recon_journal_rel",
                                   "wiz_bankrecon_id", "journal_id",
                                   string="Bank Accounts")

    @api.onchange('company_id')
    def onchange_company_id(self):
        """Onchange company to set journals."""
        journal_obj = self.env['account.journal']
        self.journal_ids = [(6, 0, [])]
        if self.company_id:
            journals = journal_obj.search([
                ('type', '=', 'bank'),
                ('company_id', '=', self.company_id.id)])
            self.journal_ids = [(6, 0, journals.ids)]

    @api.multi
    def export_bank_reconciliation_report(self):
        """Method to export bank reconciliation report."""
        cr, uid, context = self.env.args
        wiz_exported_obj = self.env['wiz.bank.reconciliation.report.exported']
        # sheet Development
        file_path = 'Bank Reconcilition Report.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/' + file_path)
        # num_format = workbook.add_format({'num_format': 'dd/mm/yy'})

        header_cell_fmat = workbook.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'bold': 1,  # 'fg_color': '#96c5f4',
            'align': 'center',
            'border': 1,  # 'valign': 'vcenter'
            'text_wrap': True,
            'bg_color': '#d3d3d3'
        })
        header_cell_l_fmat = workbook.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'bold': 1,  # 'fg_color': '#96c5f4',
            'align': 'left',
            # 'border': 1,  # 'valign': 'vcenter'
            'text_wrap': True
        })
        header_cell_r_fmat = workbook.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'bold': 1,  # 'fg_color': '#96c5f4',
            'align': 'right',
            'border': 1,  # 'valign': 'vcenter'
            'text_wrap': True,
            'bg_color': '#d3d3d3'
        })

        cell_l_fmat = workbook.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'align': 'left',  # 'valign': 'vcenter', 'text_wrap': True
            'text_wrap': True
        })

        cell_r_fmat = workbook.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'align': 'right',  # 'valign': 'vcenter'
            'text_wrap': True
        })

        cell_r_bold_noborder = workbook.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'align': 'right',  # 'valign': 'vcenter'
            'text_wrap': True,
            'bold': 1
        })

        cell_c_fmat = workbook.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'align': 'center',  # 'valign': 'vcenter'
            'text_wrap': True
        })

        cell_c_head_fmat = workbook.add_format({
            'font_name': 'Arial',
            'font_size': 14,
            'align': 'center',
            'bold': True,
            'border': 1,
            'text_wrap': True
        })
        to_date = ''
        from_date = ''
        prev_year_to_date = self.date_to
        prev_year_from_date = self.date_from
        if self.date_from:
            from_date = datetime.strftime(self.date_from, '%d/%m/%Y')
            to_dt = self.date_from
            to_year = self.date_from.year
            prev_year_from_date = \
                to_dt.replace(day=1, month=1, year=to_year - 1)

        if self.date_to:
            to_date = datetime.strftime(self.date_to, '%d/%m/%Y')
            f_dt = self.date_to
            f_year = self.date_to.year
            prev_year_to_date = f_dt.replace(day=31, month=12, year=f_year - 1)

        company_name = self.company_id and self.company_id.name or ''
        for journal in self.journal_ids:
            # print("\n prev_year_from_date :::::::", prev_year_from_date)
            # print("\n prev_year_to_date :::::::::", prev_year_to_date)
            prev_cust_payments = self.env['account.payment'].search([
                ('payment_date', '>=', prev_year_from_date),
                ('payment_date', '<=', prev_year_to_date),
                ('payment_type', '=', 'inbound'),
                ('journal_id', '=', journal.id),
                ('state', 'in', ['reconciled'])],
                order='payment_date')
            tot_prev_cust_payments = sum(prev_cust_payments.mapped('amount'))

            prev_vendor_payments = self.env['account.payment'].search([
                ('payment_date', '>=', prev_year_from_date),
                ('payment_date', '<=', prev_year_to_date),
                ('payment_type', '=', 'outbound'),
                ('journal_id', '=', journal.id),
                ('state', 'in', ['reconciled'])],
                order='payment_date')
            tot_prev_vendor_payments = \
                sum(prev_vendor_payments.mapped('amount'))

            cust_payments = self.env['account.payment'].search([
                ('payment_date', '>=', self.date_from),
                ('payment_date', '<=', self.date_to),
                ('payment_type', '=', 'inbound'),
                ('journal_id', '=', journal.id),
                ('state', 'in', ['reconciled'])],
                order='payment_date')

            vendor_payments = self.env['account.payment'].search([
                ('payment_date', '>=', self.date_from),
                ('payment_date', '<=', self.date_to),
                ('payment_type', '=', 'outbound'),
                ('journal_id', '=', journal.id),
                ('state', 'in', ['reconciled'])],
                order='payment_date')

            # cust_payments = self.env['account.move.line'].search([
            #     ('payment_date', '>=', self.date_from),
            #     ('payment_date', '<=', self.date_to),
            #     ('payment_type', '=', 'inbound'),
            #     ('journal_id', '=', journal.id),
            #     ('state', 'in', ['reconciled'])],
            #     order='payment_date')

            # vendor_payments = self.env['account.move.line'].search([
            #     ('payment_date', '>=', self.date_from),
            #     ('payment_date', '<=', self.date_to),
            #     ('payment_type', '=', 'outbound'),
            #     ('journal_id', '=', journal.id),
            #     ('state', 'in', ['reconciled'])],
            #     order='payment_date')

            worksheet = workbook.add_worksheet(journal.name)

            # worksheet.set_column(0, 4, 20)
            # worksheet.set_column(6, 6, 5)
            worksheet.set_column(0, 0, 5)
            worksheet.set_column(1, 1, 13)
            worksheet.set_column(2, 2, 10)
            worksheet.set_column(3, 3, 20)
            worksheet.set_column(4, 4, 25)
            worksheet.set_column(5, 5, 35)
            worksheet.set_column(6, 6, 15)
            worksheet.set_row(1, 20)
            worksheet.merge_range(
                1, 0, 1, 6, company_name, cell_c_head_fmat)
            worksheet.merge_range(
                2, 0, 2, 6,
                'Reconciliation Details - ' + journal.name, cell_c_head_fmat)
            worksheet.merge_range(
                3, 0, 3, 6,
                'As of ' + ustr(from_date) + ' To ' + ustr(to_date),
                cell_c_head_fmat)
            row = 5
            col = 0
            worksheet.write(row, col, 'ID', header_cell_fmat)
            col += 1
            worksheet.write(row, col, 'Transaction Type', header_cell_fmat)
            col += 1
            worksheet.write(row, col, 'Date', header_cell_fmat)
            col += 1
            worksheet.write(row, col, 'Document Number', header_cell_fmat)
            col += 1
            # worksheet.write(row, col, 'Payment Type', header_cell_fmat)
            # col += 1
            # worksheet.write(row, col, 'Partner Type', header_cell_fmat)
            # col += 1
            worksheet.write(row, col, 'Name', header_cell_fmat)
            col += 1
            worksheet.write(row, col, 'Memo', header_cell_fmat)
            col += 1
            worksheet.write(row, col, 'Balance', header_cell_r_fmat)
            row += 1
            worksheet.merge_range(row, 0, row, 1, 'Reconciled',
                                  header_cell_l_fmat)
            row += 1
            worksheet.merge_range(row, 1, row, 4,
                                  'Cleared Deposits and Other Credits',
                                  header_cell_l_fmat)
            col = 0
            row += 1
            tot_cust_payment = 0.0
            for cust_pay in cust_payments:
                tot_cust_payment = tot_cust_payment + cust_pay.amount or 0.0
                partner = cust_pay.partner_id and \
                    cust_pay.partner_id.name or ''
                # journal = cust_pay.journal_id and \
                #    cust_pay.journal_id.name or ''
                payment_date = ''
                if cust_pay.payment_date:
                    payment_date = \
                        datetime.strftime(cust_pay.payment_date, '%d-%m-%Y')

                worksheet.write(row, col, ' ', cell_c_fmat)
                col += 1
                worksheet.write(row, col, 'Payment', cell_c_fmat)
                col += 1
                worksheet.write(row, col, payment_date, cell_c_fmat)
                col += 1
                worksheet.write(row, col, cust_pay.name or '', cell_l_fmat)
                col += 1
                # worksheet.write(row, col,
                #                 PAY_TYPE.get(cust_pay.payment_type, ''),
                #                 cell_l_fmat)
                # col += 1
                # worksheet.write(row, col,
                #                 PARTNER_TYPE.get(cust_pay.partner_type, ''),
                #                 cell_l_fmat)
                # col += 1
                worksheet.write(row, col, partner, cell_l_fmat)
                col += 1
                worksheet.write(row, col, cust_pay.communication or '',
                                cell_l_fmat)
                col += 1
                worksheet.write(row, col, cust_pay.amount or 0.0, cell_r_fmat)
                col = 0
                row += 1

            row += 1
            worksheet.merge_range(row, 1, row, 4,
                                  'Total - Cleared Deposits and Other Credits',
                                  header_cell_l_fmat)
            worksheet.write(row, 6, tot_cust_payment or 0.0,
                            cell_r_bold_noborder)

            # Start for the Vendor Payments
            # col = 0
            # row += 1
            # worksheet.write(row, col, 'ID', header_cell_fmat)
            # col += 1
            # worksheet.write(row, col, 'Transaction Type', header_cell_fmat)
            # col += 1
            # worksheet.write(row, col, 'Date', header_cell_fmat)
            # col += 1
            # worksheet.write(row, col, 'Document Number', header_cell_fmat)
            # col += 1
            # # worksheet.write(row, col, 'Payment Type', header_cell_fmat)
            # # col += 1
            # # worksheet.write(row, col, 'Partner Type', header_cell_fmat)
            # # col += 1
            # worksheet.write(row, col, 'Name', header_cell_fmat)
            # col += 1
            # worksheet.write(row, col, 'Memo', header_cell_fmat)
            # col += 1
            # worksheet.write(row, col, 'Balance', header_cell_fmat)
            row += 1
            worksheet.merge_range(row, 1, row, 4,
                                  'Cleared Checks and Payments',
                                  header_cell_l_fmat)

            col = 0
            row += 1
            tot_vend_payment = 0.0
            for ven_pay in vendor_payments:
                tot_vend_payment = tot_vend_payment + ven_pay.amount
                partner = ven_pay.partner_id and ven_pay.partner_id.name or ''
                # journal = ven_pay.journal_id and \
                #    ven_pay.journal_id.name or ''
                payment_date = ''
                if ven_pay.payment_date:
                    payment_date = \
                        datetime.strftime(ven_pay.payment_date, '%d-%m-%Y')

                worksheet.write(row, col, ' ', cell_c_fmat)
                col += 1
                worksheet.write(row, col, 'Bill Payment', cell_c_fmat)
                col += 1
                worksheet.write(row, col, payment_date, cell_c_fmat)
                col += 1
                worksheet.write(row, col, ven_pay.name or '', cell_l_fmat)
                col += 1
                # worksheet.write(row, col,
                #                 PAY_TYPE.get(ven_pay.payment_type, ''),
                #                 cell_l_fmat)
                # col += 1
                # worksheet.write(row, col,
                #                 PARTNER_TYPE.get(ven_pay.partner_type, ''),
                #                 cell_l_fmat)
                # col += 1
                worksheet.write(row, col, partner, cell_l_fmat)
                col += 1
                worksheet.write(
                    row, col, ven_pay.communication or '', cell_l_fmat)
                col += 1
                worksheet.write(row, col, ven_pay.amount or '', cell_r_fmat)
                col = 0
                row += 1

            row += 1
            worksheet.merge_range(row, 1, row, 4,
                                  'Total - Cleared Checks and Payments',
                                  header_cell_l_fmat)
            worksheet.write(row, 6, tot_vend_payment or 0.0,
                            cell_r_bold_noborder)
            row += 1
            worksheet.merge_range(row, 0, row, 3,
                                  'Total - Reconciled', header_cell_l_fmat)
            filter_bal = tot_cust_payment + tot_vend_payment
            worksheet.write(row, 6,  filter_bal or 0.0,
                            cell_r_bold_noborder)
            row += 1
            worksheet.merge_range(
                row, 0, row, 3,
                'Last Reconciled Statement Balance - ' +
                ustr(prev_year_to_date),
                header_cell_l_fmat)
            prev_bal = tot_prev_vendor_payments + tot_prev_cust_payments
            worksheet.write(row, 6, prev_bal, cell_r_bold_noborder)
            row += 1
            curr_bal = filter_bal + prev_bal
            worksheet.merge_range(row, 0, row, 3,
                                  'Current Reconciled Balance',
                                  header_cell_l_fmat)
            worksheet.write(row, 6, curr_bal or 0.0, cell_r_bold_noborder)
            row += 1
            worksheet.merge_range(
                row, 0, row, 3,
                'Reconcile Statement Balance - ' + ustr(to_date),
                header_cell_l_fmat)
            worksheet.write(row, 6, curr_bal, cell_r_bold_noborder)
            row += 1
            worksheet.merge_range(
                row, 0, row, 3, 'Difference', header_cell_l_fmat)
            worksheet.write(row, 6, 0.0, cell_r_bold_noborder)
            row += 1
            worksheet.merge_range(row, 0, row, 3, 'Unreconciled',
                                  header_cell_l_fmat)
            worksheet.write(row, 6, 0.0, cell_r_bold_noborder)

        workbook.close()
        buf = base64.encodestring(open('/tmp/' + file_path, 'rb').read())
        try:
            if buf:
                os.remove(file_path + '.xlsx')
        except OSError:
            pass
        wiz_rec = wiz_exported_obj.create({
            'file': buf,
            'name': 'Bank Reconcilition Report.xlsx'
        })
        form_view = self.env.ref(
            'account_reports_extended.wiz_bank_reconcil_rep_exported_form')
        if wiz_rec and form_view:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': wiz_rec.id,
                'res_model': 'wiz.bank.reconciliation.report.exported',
                'views': [(form_view.id, 'form')],
                'view_id': form_view.id,
                'target': 'new',
            }
        else:
            return {}
