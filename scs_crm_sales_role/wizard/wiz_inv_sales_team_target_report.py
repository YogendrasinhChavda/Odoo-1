"""Wizard Sales Team Target Report TransientModel."""

import xlsxwriter
import os
import base64
from datetime import datetime
from calendar import monthrange
# from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY

from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError
from odoo.tools import ustr  # , DEFAULT_SERVER_DATE_FORMAT as DF


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


class WizSalesTeamTargetReportExported(models.TransientModel):
    """Wizard Sales Team Target Report Exported TransientModel."""

    _name = 'wiz.sales.team.target.report.exported'
    _description = "Wizard Sales Team Target Report Exported"

    file = fields.Binary("Click On Download Link To Download Xlsx File",
                         readonly=True)
    name = fields.Char(string='File Name', size=32)


class WizSalesTeamTargetReport(models.TransientModel):
    """Wizard Sales Team Target Report TransientModel."""

    _name = 'wiz.sales.team.target.report'
    _description = "Wizard Sales Team Target Report"

    @api.model
    def default_get(self, fields=[]):
        """Method to update start and end date."""
        res = super(WizSalesTeamTargetReport, self).default_get(fields)
        curr_year = datetime.today().year
        pre_year = curr_year - 1
        # tot_days = monthrange(curr_dt.year, curr_dt.month)[1]
        st_dt = datetime.today().replace(day=1, month=7, year=pre_year).date()
        # end_dt = datetime.today().replace(day=int(tot_days)).date()
        end_dt = datetime.today().replace(day=30, month=6).date()
        res.update({'date_from': st_dt, 'date_to': end_dt})
        return res

    company_id = fields.Many2one("res.company", string="Company",
                                 default=lambda self: self.env.user and
                                 self.env.user.company_id)
    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')

    @api.onchange('date_from')
    def _onchange_from_date(self):
        """Onchange Method to update end date."""
        from_dt = self.date_from
        if from_dt and self.env.context.get('from_wiz_form_view', False):
            month_days = monthrange(from_dt.year, from_dt.month)
            self.date_to = from_dt.replace(day=int(month_days[1]))

    @api.constrains('date_from')
    def _check_from_date_constrains(self):
        """Method to check From date as First of any month Constrains."""
        for wiz in self:
            if wiz.date_from and wiz.date_from.day != 1:
                raise ValidationError(_("Please, Select Only First Date of \
                    Any Month as 'From Date' !!"))

    @api.constrains('date_from', 'date_to')
    def _check_from_to_date(self):
        for wiz in self:
            if wiz.date_from > wiz.date_to:
                raise ValidationError(_("'From Date' must be less than Or \
                    Equal to 'To Date' !!"))

    @api.multi
    def export_sales_team_target_report(self):
        """Method to generate the Sales Team target report."""
        # sales_team_obj = self.env['crm.team']
        # state_obj = self.env['res.country.state']
        country_obj = self.env['res.country']
        # sale_obj = self.env['sale.order']
        wiz_exported_obj = self.env['wiz.sales.team.target.report.exported']
        trg_team_obj = self.env['sales.billed.invoice.target.team']
        inv_obj = self.env['account.invoice']

        if self.date_from > self.date_to:
            raise Warning(_("To date must be greater than \
                or Equals to from date !!"))

        company = self.company_id and self.company_id.id or False
        # Below is the list of dates month wise.
        dates = [dt for dt in rrule(MONTHLY,
                                    dtstart=self.date_from,
                                    until=self.date_to)]

        file_path = 'YTM Sales Team Report.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/' + file_path)
        worksheet = workbook.add_worksheet("YTM Sales Team Report")

        cell_font_fmt = workbook.add_format({
            'font_name': 'Arial',
        })
        cell_left_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'left',
        })
        cell_center_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'center',
            'bg_color': '#548235',
            'color': '#FFFFFF'
        })
        cell_left_color_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'left',
            'color': '#0070C0'
        })
        cell_right_color_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'right',
            'color': '#0070C0',
            'num_format': '#,##0.00'
        })
        cell_right_bold_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'right',
            'num_format': '#,##0.00',
            'bold': 1,
            'border': 1
        })
        cell_left_bold_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'left',
            'bold': 1,
            'border': 1
        })
        cell_right_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'right',
            'num_format': '#,##0.00'
        })
        cell_bg_fmt = workbook.add_format({
            'font_name': 'Arial',
            'bg_color': '#548235',
            'color': '#FFFFFF'
        })
        cell_bg_cou_actual = workbook.add_format({
            'font_name': 'Arial',
            'bg_color': '#a9d18e',
            'color': '#FFFFFF',
            'num_format': '#,##0.00'
        })
        cell_bg_cou_right_actual = workbook.add_format({
            'font_name': 'Arial',
            'bg_color': '#a9d18e',
            'align': 'right',
            'color': '#FFFFFF',
            'num_format': '#,##0.00'
        })
        cell_right_bold_budget_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'right',
            'num_format': '#,##0.00',
            'color': '#0070C0',
            'bold': 1,
            'border': 1
        })
        cell_left_bold_budget_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'left',
            'bold': 1,
            'border': 1,
            'color': '#0070C0',
        })

        worksheet.set_column(0, 0, 35)
        worksheet.freeze_panes(0, 1)
        worksheet.freeze_panes(5, 1)

        current_date = datetime.now()
        month_str = current_date.strftime('%b')
        year = current_date.year
        head_str = "YTM " + "(" + ustr(month_str) + " " + ustr(year) + " ) "
        head_str += "Sales Report - Acutal  VS Budget  & Comprable Period"
        worksheet.write(0, 0, head_str, cell_font_fmt)
        row = 2
        col = 0
        worksheet.write(row, col, "Sum of Sales  (Net of Tax) Incl freight",
                        cell_font_fmt)
        row += 1
        worksheet.set_row(row, 25)
        worksheet.write(row, col, "Country/State", cell_bg_fmt)
        tot_balance_dict = {}
        # --------------------------TO Print Heading----------------------
        if dates:
            col += 1
            for month_st_dt in dates:
                month_str = month_st_dt.strftime("%B")
                dt_year = month_st_dt.year
                dt_prev_year = dt_year - 1
                worksheet.merge_range(row, col, row, col + 1,
                                      ustr(month_str), cell_center_fmt)
                # below one line is just fill the color for blank cell
                worksheet.set_row(row, 25)
                worksheet.write(row, col + 2, ' ', cell_center_fmt)
                row += 1
                # Below three lines will update years and month heading.
                worksheet.set_column(row, col, 15)
                worksheet.write(row, col, ustr(dt_year), cell_center_fmt)
                worksheet.set_column(row, col + 1, 15)
                worksheet.write(row, col + 1, ustr(dt_prev_year),
                                cell_center_fmt)
                worksheet.set_column(row, col + 2, 15)
                worksheet.set_row(row, 25)
                worksheet.write(row, col + 2, 'Variance', cell_center_fmt)

                if tot_balance_dict.get(month_st_dt, False):
                    tot_balance_dict[month_st_dt].update({
                        'month_str': month_str,
                        'dt_year': ustr(dt_year),
                        'dt_prev_year': ustr(dt_prev_year),
                        # 'dt_year_tot_bal': 0.0,
                        # 'dt_prev_year_tot_bal': 0.0
                    })
                else:
                    tot_balance_dict.update({month_st_dt: {
                        'month_str': month_str,
                        'dt_year': ustr(dt_year),
                        'dt_prev_year': ustr(dt_prev_year),
                        # 'dt_year_tot_bal': 0.0,
                        # 'dt_prev_year_tot_bal': 0.0
                    }})
                row -= 1
                col += 3
            worksheet.set_row(row, 25)
            worksheet.merge_range(row, col, row, col + 1,
                                  ustr('Grand Total (YTM)'),
                                  cell_center_fmt)
            worksheet.write(row, col + 2, ' ', cell_center_fmt)
            worksheet.set_column(row, col, 15)
            fy_year = self.date_to.year
            pre_fy_year = fy_year - 1
            row += 1
            worksheet.write(row, col, 'FY' + ustr(fy_year),
                            cell_center_fmt)
            worksheet.set_column(row, col + 1, 15)
            worksheet.write(row, col + 1, 'FY' + ustr(pre_fy_year),
                            cell_center_fmt)
            worksheet.set_column(row, col + 2, 15)
            worksheet.write(row, col + 2, 'Variance',
                            cell_center_fmt)
            row -= 1

        row += 1
        col = 0
        worksheet.write(row, col, " ", cell_bg_fmt)
        row += 1

        # ------------TO Print Balances Country and team wise----------------
        inv_ids = inv_obj.search([
            ('date_invoice', '>=', self.date_from),
            ('date_invoice', '<=', self.date_to),
            ('type', '=', 'out_invoice'),
            ('company_id', '=', company),
            ('state', 'in', ['open', 'in_payment', 'paid'])])

        # partner_ids = sale_ids.mapped('partner_id')
        # team_ids = sale_ids.mapped('team_id')
        country_ids = inv_ids.mapped('partner_id').mapped('country_id')
        # state_ids = sale_ids.mapped('partner_id').mapped('state_id')
        for country_id in country_obj.search([
                ('id', 'in', country_ids.ids)], order="name"):
            worksheet.set_row(row, 25)
            # worksheet.set_default_row(20)
            row_for_tot_bal = row
            col_for_tot_bal = col
            worksheet.write(row, col,
                            country_id.name + " Actual", cell_bg_cou_actual)
            row += 1
            sale_country_ids = inv_obj.search([
                ('date_invoice', '>=', self.date_from),
                ('date_invoice', '<=', self.date_to),
                ('partner_id.country_id', '=', country_id.id),
                ('type', '=', 'out_invoice'),
                ('company_id', '=', company),
                ('state', 'in', ['open', 'in_payment', 'paid'])])

            sale_team_ids = sale_country_ids.mapped('team_id')
            for team_id in sale_team_ids:
                worksheet.set_row(row, 20)
                worksheet.write(row, col,
                                team_id.name + " Actual", cell_left_fmt)
                # ----------------------------------------------------------
                # Added Budget Team in file.
                row += 1
                worksheet.set_row(row, 20)
                worksheet.write(row, col,
                                team_id.name + " Budget", cell_left_color_fmt)
                row -= 1
                # ----------------------------------------------------------

                row_col = col + 1
                grand_tot_country_team_wise_right = {
                    'grand_total_country_team_wise': 0.0,
                    'pre_grand_total_country_team_wise': 0.0,
                    'grand_tot_budget_country_team_wise': 0.0,
                    'pre_grand_tot_budget_country_team_wise': 0.0
                }
                for month_st_dt in dates:
                    month_days = \
                        monthrange(month_st_dt.year, month_st_dt.month)
                    month_en_dt = month_st_dt
                    month_en_dt = month_en_dt.\
                        replace(day=int(month_days[1]))

                    # month_str = month_st_dt.strftime("%B")
                    dt_year = month_st_dt.year
                    dt_prev_year = dt_year - 1
                    prev_year_month_st_dt = month_st_dt

                    pre_month_days = monthrange(dt_prev_year,
                                                prev_year_month_st_dt.month)
                    prev_year_month_en_dt = month_en_dt

                    prev_year_month_st_dt = prev_year_month_st_dt.\
                        replace(year=int(dt_prev_year))
                    prev_year_month_en_dt = prev_year_month_en_dt.\
                        replace(day=int(pre_month_days[1]),
                                year=int(dt_prev_year))

                    month_en_dt = month_en_dt.strftime("%Y-%m-%d 23:59:59")
                    prev_year_month_en_dt = \
                        prev_year_month_en_dt.strftime("%Y-%m-%d 23:59:59")

                    sale_team_country_wise_ids = inv_obj.search([
                        ('date_invoice', '>=', month_st_dt),
                        ('date_invoice', '<=', month_en_dt),
                        ('partner_id.country_id', '=', country_id.id),
                        ('type', '=', 'out_invoice'),
                        ('team_id', '=', team_id.id),
                        ('company_id', '=', company),
                        ('state', 'in', ['open', 'in_payment', 'paid'])])
                    team_sales_total = \
                        sum(sale_team_country_wise_ids.mapped('amount_total'))

                    sale_trg_budget_ids = trg_team_obj.search([
                        ('date_from', '>=', month_st_dt),
                        ('date_to', '<=', month_en_dt),
                        ('team_id', '=', team_id.id),
                        ('company_id', '=', company)])
                    team_sales_budget_trg_tot = \
                        sum(sale_trg_budget_ids.mapped('sales_team_target'))

                    worksheet.write(row, row_col, round(team_sales_total, 2),
                                    cell_right_fmt)
                    worksheet.write(row + 1, row_col,
                                    round(team_sales_budget_trg_tot, 2),
                                    cell_right_color_fmt)
                    pre_sale_team_country_ids = inv_obj.search([
                        ('date_invoice', '>=', prev_year_month_st_dt),
                        ('date_invoice', '<=', prev_year_month_en_dt),
                        ('partner_id.country_id', '=', country_id.id),
                        ('type', '=', 'out_invoice'),
                        ('team_id', '=', team_id.id),
                        ('company_id', '=', company),
                        ('state', 'in', ['open', 'in_payment', 'paid'])])
                    pre_team_sales_total = \
                        sum(pre_sale_team_country_ids.mapped('amount_total'))

                    pre_sale_trg_budget_ids = trg_team_obj.search([
                        ('date_from', '>=', prev_year_month_st_dt),
                        ('date_to', '<=', prev_year_month_en_dt),
                        ('team_id', '=', team_id.id),
                        ('company_id', '=', company)])
                    pre_team_sales_budget_trg_tot = \
                        sum(pre_sale_trg_budget_ids.
                            mapped('sales_team_target'))

                    row_col += 1
                    worksheet.write(row, row_col,
                                    round(pre_team_sales_total, 2),
                                    cell_right_fmt)
                    worksheet.write(row + 1, row_col,
                                    round(pre_team_sales_budget_trg_tot, 2),
                                    cell_right_color_fmt)
                    variance_per = 0.0
                    if pre_team_sales_total > 0:
                        variance_per = \
                            (team_sales_total - pre_team_sales_total) / \
                            pre_team_sales_total
                        variance_per = round(variance_per, 2)

                    budget_variance_per = 0.0
                    if team_sales_budget_trg_tot > 0:
                        budget_variance_per = \
                            (team_sales_total -
                             team_sales_budget_trg_tot) / \
                            team_sales_budget_trg_tot
                        budget_variance_per = round(budget_variance_per, 2)

                    row_col += 1
                    worksheet.write(row, row_col,
                                    ustr(variance_per) + '%', cell_right_fmt)
                    worksheet.write(row + 1, row_col,
                                    ustr(budget_variance_per) + '%',
                                    cell_right_color_fmt)
                    row_col += 1

                    grand_tot_country_team_wise_right.update({
                        'grand_total_country_team_wise':
                        team_sales_total +
                            grand_tot_country_team_wise_right[
                                'grand_total_country_team_wise'],
                        'pre_grand_total_country_team_wise':
                        pre_team_sales_total +
                            grand_tot_country_team_wise_right[
                                'pre_grand_total_country_team_wise'],

                        'grand_tot_budget_country_team_wise':
                        team_sales_budget_trg_tot +
                        grand_tot_country_team_wise_right[
                            'grand_tot_budget_country_team_wise'],
                        'pre_grand_tot_budget_country_team_wise':
                            pre_team_sales_budget_trg_tot +
                            grand_tot_country_team_wise_right[
                            'pre_grand_tot_budget_country_team_wise'],
                    })

                    if tot_balance_dict.get(month_st_dt, False):
                        if tot_balance_dict[month_st_dt].get(
                                country_id.id, False):
                            tot_balance_dict[month_st_dt][country_id.id].\
                                update({
                                    'dt_year_tot_bal':
                                    tot_balance_dict[month_st_dt]
                                    [country_id.id].
                                        get('dt_year_tot_bal', 0.0) +
                                        team_sales_total,
                                    'dt_prev_year_tot_bal':
                                    tot_balance_dict[month_st_dt]
                                    [country_id.id].
                                        get('dt_prev_year_tot_bal', 0.0) +
                                        pre_team_sales_total,

                                    'team_sales_budget_trg_tot_bal':
                                    tot_balance_dict[month_st_dt]
                                    [country_id.id].get(
                                        'team_sales_budget_trg_tot_bal', 0.0) +
                                        team_sales_budget_trg_tot,

                                    'pre_team_sales_budget_trg_tot_bal':
                                    tot_balance_dict[month_st_dt]
                                    [country_id.id].get(
                                        'pre_team_sales_budget_trg_tot_bal',
                                        0.0) +
                                        pre_team_sales_budget_trg_tot,
                                })
                        else:
                            tot_balance_dict[month_st_dt].update({
                                country_id.id: {
                                    'dt_year_tot_bal': team_sales_total,
                                    'dt_prev_year_tot_bal':
                                    pre_team_sales_total,
                                    'team_sales_budget_trg_tot_bal':
                                    team_sales_budget_trg_tot,
                                    'pre_team_sales_budget_trg_tot_bal':
                                    pre_team_sales_budget_trg_tot
                                }
                            })
                # ------ FY Wise Grand Total Team Wise ----------
                fy_year_tot_grand = \
                    grand_tot_country_team_wise_right[
                        'grand_total_country_team_wise']
                fy_year_tot_budget_grand = \
                    grand_tot_country_team_wise_right[
                        'grand_tot_budget_country_team_wise']
                pre_fy_year_tot_grand = \
                    grand_tot_country_team_wise_right[
                        'pre_grand_total_country_team_wise']
                pre_fy_year_tot_budget_grand = \
                    grand_tot_country_team_wise_right[
                        'pre_grand_tot_budget_country_team_wise']

                grand_variance_per = 0.0
                if pre_fy_year_tot_grand > 0:
                    grand_variance_per = \
                        (fy_year_tot_grand - pre_fy_year_tot_grand) / \
                        pre_fy_year_tot_grand
                    grand_variance_per = round(grand_variance_per, 2)

                grand_budget_variance_per = 0.0
                if fy_year_tot_budget_grand > 0:
                    grand_budget_variance_per = \
                        (fy_year_tot_grand -
                         fy_year_tot_budget_grand) / \
                        fy_year_tot_budget_grand
                    grand_budget_variance_per = \
                        round(grand_budget_variance_per, 2)

                worksheet.write(row, row_col,
                                round(fy_year_tot_grand, 2),
                                cell_right_fmt)
                worksheet.write(row + 1, row_col,
                                round(fy_year_tot_budget_grand, 2),
                                cell_right_color_fmt)
                row_col += 1
                worksheet.write(row, row_col,
                                round(pre_fy_year_tot_grand, 2),
                                cell_right_fmt)
                worksheet.write(row + 1, row_col,
                                round(pre_fy_year_tot_budget_grand, 2),
                                cell_right_color_fmt)
                row_col += 1
                worksheet.write(row, row_col,
                                ustr(grand_variance_per) + '%',
                                cell_right_fmt)
                worksheet.write(row + 1, row_col,
                                ustr(grand_budget_variance_per) + '%',
                                cell_right_color_fmt)

                # We added 2 row plus because added Budget and actual team.
                row += 2
            # ---------------Total for top heading country wise ------------
            grand_tot_country_wise_right = {
                'grand_total_country_wise': 0.0,
                'pre_grand_total_country_wise': 0.0
            }
            for month_st_dt in dates:
                if tot_balance_dict.get(month_st_dt, False) and \
                        tot_balance_dict[month_st_dt].\
                        get(country_id.id, False):
                    sale_tot = \
                        tot_balance_dict[month_st_dt][country_id.id].\
                        get('dt_year_tot_bal', 0.0)
                    pre_sale_tot = \
                        tot_balance_dict[month_st_dt][country_id.id].\
                        get('dt_prev_year_tot_bal', 0.0)

                    grand_tot_country_wise_right.update({
                        'grand_total_country_wise':
                        sale_tot + grand_tot_country_wise_right[
                            'grand_total_country_wise'],
                        'pre_grand_total_country_wise':
                        pre_sale_tot + grand_tot_country_wise_right[
                            'pre_grand_total_country_wise']
                    })

                    sale_budget_tot = \
                        tot_balance_dict[month_st_dt][country_id.id].\
                        get('team_sales_budget_trg_tot_bal', 0.0)
                    pre_sale_budget_tot = \
                        tot_balance_dict[month_st_dt][country_id.id].\
                        get('pre_team_sales_budget_trg_tot_bal', 0.0)

                    worksheet.write(row_for_tot_bal, col_for_tot_bal + 1,
                                    round(sale_tot, 2),
                                    cell_bg_cou_actual)
                    worksheet.write(row_for_tot_bal, col_for_tot_bal + 2,
                                    round(pre_sale_tot, 2),
                                    cell_bg_cou_actual)
                    tot_variance = 0.0
                    if pre_sale_tot > 0:
                        tot_variance = \
                            (sale_tot - pre_sale_tot) / pre_sale_tot
                    worksheet.write(row_for_tot_bal, col_for_tot_bal + 3,
                                    ustr(round(tot_variance, 2)) + '%',
                                    cell_bg_cou_right_actual)

                    if tot_balance_dict[month_st_dt].\
                            get('year_grand_tot_bal', False) and \
                            tot_balance_dict[month_st_dt].\
                            get('pre_year_grand_tot_bal', False):
                        tot_balance_dict[month_st_dt].update({
                            'year_grand_tot_bal': sale_tot +
                            tot_balance_dict[month_st_dt]
                            ['year_grand_tot_bal'],
                            'pre_year_grand_tot_bal': pre_sale_tot +
                            tot_balance_dict[month_st_dt]
                            ['pre_year_grand_tot_bal']
                        })
                    else:
                        tot_balance_dict[month_st_dt].update({
                            'year_grand_tot_bal': sale_tot,
                            'pre_year_grand_tot_bal': pre_sale_tot
                        })

                    if tot_balance_dict[month_st_dt].\
                            get('team_budget_trg_tot_bal', False) and \
                            tot_balance_dict[month_st_dt].\
                            get('pre_team_budget_trg_tot_bal', False):
                        tot_balance_dict[month_st_dt].update({
                            'team_budget_trg_tot_bal': sale_budget_tot +
                            tot_balance_dict[month_st_dt]
                            ['team_budget_trg_tot_bal'],

                            'pre_team_budget_trg_tot_bal':
                            pre_sale_budget_tot +
                            tot_balance_dict[month_st_dt]
                            ['pre_team_budget_trg_tot_bal']
                        })
                    else:
                        tot_balance_dict[month_st_dt].update({
                            'team_budget_trg_tot_bal': sale_budget_tot,
                            'pre_team_budget_trg_tot_bal':
                            pre_sale_budget_tot
                        })

                col_for_tot_bal = col_for_tot_bal + 3
            # --------- Total in Right side FY GRAND Year TOTAL -------------
            fy_year_tot = \
                grand_tot_country_wise_right['grand_total_country_wise']
            pre_fy_year_tot = \
                grand_tot_country_wise_right['pre_grand_total_country_wise']
            worksheet.write(row_for_tot_bal, col_for_tot_bal + 1,
                            round(fy_year_tot, 2),
                            cell_bg_cou_actual)
            worksheet.write(row_for_tot_bal, col_for_tot_bal + 2,
                            round(pre_fy_year_tot, 2),
                            cell_bg_cou_actual)

            fy_year_variance = 0.0
            if pre_fy_year_tot > 0:
                fy_year_variance = \
                    (fy_year_tot - pre_fy_year_tot) / pre_fy_year_tot

            worksheet.write(row_for_tot_bal, col_for_tot_bal + 3,
                            ustr(round(fy_year_variance, 2)) + '%',
                            cell_bg_cou_right_actual)
            # col_for_tot_bal = col_for_tot_bal + 3
        # ----- TO Print Grand Total and Budget Total in bottom --------
        row += 1
        worksheet.write(row, col, "Grand Total", cell_left_bold_fmt)
        row += 1
        worksheet.write(row, col, "Budget Total", cell_left_bold_budget_fmt)
        row -= 1
        col += 1

        grand_tot_fy_wise_right = {
            'grand_total_fy_year_wise': 0.0,
            'pre_grand_total_fy_year_wise': 0.0,
            'grand_budget_total_fy_year_wise': 0.0,
            'pre_grand_budget_total_fy_year_wise': 0.0
        }
        for month_st_dt in dates:
            if tot_balance_dict.get(month_st_dt, False):
                sal_tot = tot_balance_dict[month_st_dt].\
                    get('year_grand_tot_bal', 0.0)
                pre_sal_tot = tot_balance_dict[month_st_dt].\
                    get('pre_year_grand_tot_bal', 0.0)

                sal_budget_trg_tot = tot_balance_dict[month_st_dt].\
                    get('team_budget_trg_tot_bal', 0.0)
                pre_sal_budget_trg_tot = tot_balance_dict[month_st_dt].\
                    get('pre_team_budget_trg_tot_bal', 0.0)

                worksheet.write(row, col, round(sal_tot, 2),
                                cell_right_bold_fmt)
                row += 1
                worksheet.write(row, col, round(sal_budget_trg_tot, 2),
                                cell_right_bold_budget_fmt)
                row -= 1
                col += 1
                worksheet.write(row, col, round(pre_sal_tot, 2),
                                cell_right_bold_fmt)
                row += 1
                worksheet.write(row, col, round(pre_sal_budget_trg_tot, 2),
                                cell_right_bold_budget_fmt)
                row -= 1
                col += 1

                grand_tot_variance = 0.0
                if pre_sal_tot > 0:
                    grand_tot_variance = \
                        (sal_tot - pre_sal_tot) / pre_sal_tot

                worksheet.write(row, col,
                                ustr(round(grand_tot_variance, 2)) + '%',
                                cell_right_bold_fmt)

                row += 1
                worksheet.write(row, col, ' ', cell_right_bold_budget_fmt)
                row -= 1
                col += 1

                # ==================================================
                fy_year_surplus_per = 0.0
                if sal_budget_trg_tot > 0:
                    fy_year_surplus_per = (sal_tot / sal_budget_trg_tot) - 1

                tot_balance_dict.get(month_st_dt, {}).update({
                    'fy_year_surplus_per': fy_year_surplus_per
                })
                # ==================================================

                grand_tot_fy_wise_right.update({
                    'grand_total_fy_year_wise': sal_tot +
                    grand_tot_fy_wise_right['grand_total_fy_year_wise'],
                    'pre_grand_total_fy_year_wise': pre_sal_tot +
                    grand_tot_fy_wise_right['pre_grand_total_fy_year_wise'],
                    'grand_budget_total_fy_year_wise': sal_budget_trg_tot +
                    grand_tot_fy_wise_right['grand_budget_total_fy_year_wise'],
                    'pre_grand_budget_total_fy_year_wise':
                        pre_sal_budget_trg_tot +
                        grand_tot_fy_wise_right[
                        'pre_grand_budget_total_fy_year_wise'],
                })

        # ---------------- Final Last 4 columns Grand totals --------
        fy_year_surplus_per_final_dict = {
            'fy_year_surplus': 0.0
        }
        fy_year_grand_tot_final = \
            grand_tot_fy_wise_right['grand_total_fy_year_wise']
        pre_fy_year_grand_tot_final = \
            grand_tot_fy_wise_right['pre_grand_total_fy_year_wise']
        fy_year_budget_grand_tot_final = \
            grand_tot_fy_wise_right['grand_budget_total_fy_year_wise']
        pre_fy_year_budget_grand_tot_final = \
            grand_tot_fy_wise_right['pre_grand_budget_total_fy_year_wise']

        worksheet.write(row, col, round(fy_year_grand_tot_final, 2),
                        cell_right_bold_fmt)
        row += 1
        worksheet.write(row, col, round(fy_year_budget_grand_tot_final, 2),
                        cell_right_bold_budget_fmt)
        row -= 1
        col += 1
        worksheet.write(row, col, round(pre_fy_year_grand_tot_final, 2),
                        cell_right_bold_fmt)
        row += 1
        worksheet.write(row, col, round(pre_fy_year_budget_grand_tot_final, 2),
                        cell_right_bold_budget_fmt)
        row -= 1
        col += 1

        fy_year_surplus = 0.0
        if fy_year_budget_grand_tot_final > 0.0:
            fy_year_surplus = (fy_year_grand_tot_final /
                               fy_year_budget_grand_tot_final) - 1
        fy_year_surplus_per_final_dict.update({
            'fy_year_surplus': fy_year_surplus
        })

        final_grand_tot_variance = 0.0
        if pre_fy_year_grand_tot_final > 0:
            final_grand_tot_variance = \
                (fy_year_grand_tot_final - pre_fy_year_grand_tot_final) / \
                pre_fy_year_grand_tot_final

        worksheet.write(row, col,
                        ustr(round(final_grand_tot_variance, 2)) + '%',
                        cell_right_bold_fmt)

        row += 1
        worksheet.write(row, col, ' ', cell_right_bold_budget_fmt)

        # ---------------------------------------------------------------

        row += 2
        col = 0

        fy_year = self.date_to.year
        surplus_str = 'Overall FY' + ustr(fy_year) + \
            ' Budgert Deficit or Surplus %'
        worksheet.write(row, col, surplus_str, cell_left_bold_budget_fmt)

        col += 1
        for month_st_dt in dates:
            if tot_balance_dict.get(month_st_dt, False):
                fy_year_surplus_per = \
                    tot_balance_dict[month_st_dt].\
                    get('fy_year_surplus_per', 0.0)
                worksheet.write(row, col,
                                ustr(round(fy_year_surplus_per, 2)) + '%',
                                cell_right_bold_budget_fmt)
                col += 1
                worksheet.write(row, col, ' ', cell_right_bold_budget_fmt)
                col += 1
                worksheet.write(row, col, ' ', cell_right_bold_budget_fmt)
                col += 1
                # worksheet.write(row, col, ' ', cell_right_bold_budget_fmt)
                # col += 1

        fy_year_surplus = fy_year_surplus_per_final_dict['fy_year_surplus']
        fy_year_surplus_msg = ''
        if fy_year_surplus < 0.0:
            fy_year_surplus_msg = \
                ustr(abs(fy_year_surplus)) + '% behind this year budget'
        worksheet.write(row, col,
                        ustr(round(fy_year_surplus, 2)) + '%',
                        cell_right_bold_budget_fmt)
        col += 1
        worksheet.write(row, col, fy_year_surplus_msg,
                        cell_right_bold_budget_fmt)
        col += 1
        worksheet.write(row, col, ' ', cell_right_bold_budget_fmt)

        workbook.close()
        buf = base64.encodestring(open('/tmp/' + file_path, 'rb').read())
        try:
            if buf:
                os.remove(file_path + '.xlsx')
        except OSError:
            pass
        wiz_rec = wiz_exported_obj.create({
            'file': buf,
            'name': file_path
        })
        form_view = self.env.ref(
            'scs_crm_sales_role.wiz_sales_team_target_report_exported_form')
        if wiz_rec and form_view:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': wiz_rec.id,
                'res_model': 'wiz.sales.team.target.report.exported',
                'views': [(form_view.id, 'form')],
                'view_id': form_view.id,
                'target': 'new',
            }
        else:
            return {}
