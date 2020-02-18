# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Inherited General Ledger Report python file."""

from odoo import models, fields, api, _
from odoo.tools.misc import format_date, formatLang
from datetime import datetime, timedelta
from odoo.addons.web.controllers.main import clean_action
from odoo.tools import float_is_zero 


class report_account_general_ledger(models.AbstractModel):
    _inherit = "account.general.ledger"
    _description = "General Ledger Report"
    # _inherit = ["account.general.ledger", "account.report"]

    def _group_by_account_id(self, options, line_id):
        accounts = {}
        results = self._do_query_group_by_account(options, line_id)
        initial_bal_date_to = fields.Date.from_string(
            self.env.context['date_from_aml']) + timedelta(days=-1)
        initial_bal_results = self.with_context(
            date_to=initial_bal_date_to.strftime(
                '%Y-%m-%d'))._do_query_group_by_account(options, line_id)

        context = self.env.context

        last_day_previous_fy = self.env.user.company_id.\
            compute_fiscalyear_dates(fields.Date.from_string(
                self.env.context['date_from_aml']))['date_from'] + \
            timedelta(days=-1)
        unaffected_earnings_per_company = {}
        for cid in context.get('company_ids', []):
            company = self.env['res.company'].browse(cid)
            unaffected_earnings_per_company[company] = \
                self.with_context(date_to=last_day_previous_fy.strftime(
                    '%Y-%m-%d'), date_from=False).\
                _do_query_unaffected_earnings(options, line_id, company)

        unaff_earnings_treated_companies = set()
        unaffected_earnings_type = self.env.ref(
            'account.data_unaffected_earnings')
        for account_id, result in results.items():
            account = self.env['account.account'].browse(account_id)
            accounts[account] = result
            accounts[account]['initial_bal'] = initial_bal_results.get(
                account.id,
                {'balance': 0, 'amount_currency': 0, 'debit': 0, 'credit': 0})
            if account.user_type_id == unaffected_earnings_type and \
                    account.company_id not in unaff_earnings_treated_companies:
                # add the benefit/loss of previous fiscal year to unaffected
                # earnings accounts
                unaffected_earnings_results = unaffected_earnings_per_company[
                    account.company_id]
                for field in ['balance', 'debit', 'credit']:
                    accounts[account]['initial_bal'][
                        field] += unaffected_earnings_results[field]
                    accounts[account][
                        field] += unaffected_earnings_results[field]
                unaff_earnings_treated_companies.add(account.company_id)
            # use query_get + with statement instead of a search in order to
            # work in cash basis too
            aml_ctx = {}
            if context.get('date_from_aml'):
                aml_ctx = {
                    'strict_range': True,
                    'date_from': context['date_from_aml'],
                }
            aml_ids = self.with_context(**aml_ctx).\
                _do_query(options, account_id, group_by_account=False)
            aml_ids = [x[0] for x in aml_ids]

            accounts[account]['total_lines'] = len(aml_ids)
            offset = int(options.get('lines_offset', 0))
            # We Removed Below three lines to Load All Lines At once.
            # if self.MAX_LINES:
            #     stop = offset + self.MAX_LINES
            # else:
            stop = None
            aml_ids = aml_ids[offset:stop]

            accounts[account]['lines'] = self.env[
                'account.move.line'].browse(aml_ids)

        # For each company, if the unaffected earnings account wasn't in the
        # selection yet: add it manually
        user_currency = self.env.user.company_id.currency_id
        for cid in context.get('company_ids', []):
            company = self.env['res.company'].browse(cid)
            if company not in unaff_earnings_treated_companies and \
                    not float_is_zero(
                        unaffected_earnings_per_company[company]['balance'],
                        precision_digits=user_currency.decimal_places):
                unaffected_earnings_account = \
                    self.env['account.account'].search([
                        ('user_type_id', '=', unaffected_earnings_type.id),
                        ('company_id', '=', company.id)
                    ], limit=1)
                if unaffected_earnings_account and \
                        (not line_id or
                         unaffected_earnings_account.id == line_id):
                    accounts[unaffected_earnings_account[0]
                             ] = unaffected_earnings_per_company[company]
                    accounts[unaffected_earnings_account[0]][
                        'initial_bal'] = \
                        unaffected_earnings_per_company[company]
                    accounts[unaffected_earnings_account[0]]['lines'] = []
                    accounts[unaffected_earnings_account[0]]['total_lines'] = 0
        return accounts


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    @api.multi
    def get_html(self, options, line_id=None, additional_context=None):
        '''
        return the html value of report, or html value of unfolded line
        * if line_id is set, the template used will be the line_template
        otherwise it uses the main_template. Reason is for efficiency, when unfolding a line in the report
        we don't want to reload all lines, just get the one we unfolded.
        '''
        # Check the security before updating the context to make sure the options are safe.
        self._check_report_security(options)

        # Prevent inconsistency between options and context.
        self = self.with_context(self._set_context(options))

        templates = self._get_templates()
        report_manager = self._get_report_manager(options)
        report = {'name': self._get_report_name(),
                'summary': report_manager.summary,
                'company_name': self.env.user.company_id.name,}
        lines = self._get_lines(options, line_id=line_id)

        if options.get('hierarchy'):
            lines = self._create_hierarchy(lines)
        footnotes_to_render = []
        if self.env.context.get('print_mode', False):
            # we are in print mode, so compute footnote number and include them in lines values, otherwise, let the js compute the number correctly as
            # we don't know all the visible lines.
            footnotes = dict([(str(f.line), f) for f in report_manager.footnotes_ids])
            number = 0
            for line in lines:
                f = footnotes.get(str(line.get('id')))
                if f:
                    number += 1
                    line['footnote'] = str(number)
                    footnotes_to_render.append({'id': f.id, 'number': number, 'text': f.text})
        rcontext = {'report': report,
                    'lines': {'columns_header': self.get_header(options), 'lines': lines},
                    'options': options,
                    'context': self.env.context,
                    'model': self,
                }
        profit_losse_action = self.env.ref('account_reports.account_financial_report_profitandloss0')
        if profit_losse_action and profit_losse_action.id == self.id:
            rcontext.update({
                'is_total': True
            })
        if additional_context and type(additional_context) == dict:
            rcontext.update(additional_context)
        if self.env.context.get('analytic_account_ids'):
            rcontext['options']['analytic_account_ids'] = [
                {'id': acc.id, 'name': acc.name} for acc in self.env.context['analytic_account_ids']
            ]
        render_template = templates.get('main_template', 'account_reports.main_template')
        if line_id is not None:
            render_template = templates.get('line_template', 'account_reports.line_template')
        html = self.env['ir.ui.view'].render_template(
            render_template,
            values=dict(rcontext),
        )
        if self.env.context.get('print_mode', False):
            for k,v in self._replace_class().items():
                html = html.replace(k, v)
            # append footnote as well
            html = html.replace(b'<div class="js_account_report_footnotes"></div>', self.get_html_footnotes(footnotes_to_render))
        return html

    @api.model
    def get_currency(self, value):
        currency_id = self.env.user.company_id.currency_id
        return formatLang(self.env, value, currency_obj=currency_id)
