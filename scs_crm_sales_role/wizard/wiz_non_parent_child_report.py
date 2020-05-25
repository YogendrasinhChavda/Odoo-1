"""Wizard Non-Parent Child Report Exported TransientModel."""

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


class WizNonParentChildReportExported(models.TransientModel):
    """Wizard Non-Parent Child Report Exported TransientModel."""

    _name = 'wiz.non.parent.child.report.exported'
    _description = "Wizard Non-Parent Child Report Exported"

    file = fields.Binary("Click On Download Link To Download Xlsx File",
                         readonly=True)
    name = fields.Char(string='File Name', size=32)


class WizNonParentChildReport(models.TransientModel):
    """Wizard Non-Parent Child Report TransientModel."""

    _name = 'wiz.non.parent.child.report'
    _description = "Wizard Sales Team Target Report"

    @api.model
    def default_get(self, fields=[]):
        """Method to update start and end date."""
        res = super(WizNonParentChildReport, self).default_get(fields)
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
        # country_obj = self.env['res.country']
        sale_obj = self.env['sale.order']
        partner_obj = self.env['res.partner']
        wiz_exported_obj = self.env['wiz.non.parent.child.report.exported']
        # trg_team_obj = self.env['sales.billed.invoice.target.team']
        # inv_obj = self.env['account.invoice']

        if self.date_from > self.date_to:
            raise Warning(_("To date must be greater than \
                or Equals to from date !!"))

        company = self.company_id and self.company_id.id or False
        # Below is the list of dates month wise.
        dates = [dt for dt in rrule(MONTHLY,
                                    dtstart=self.date_from,
                                    until=self.date_to)]
        plumber_ids = partner_obj.search([
            ('company_id', '=', company),
            ('member_no', '!=', False)
            # ('x_studio_plumber', '=', True),
        ])

        file_path = 'Non-Parent And Child Report.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/' + file_path)
        worksheet = workbook.add_worksheet("Non-Parent And Child Report")

        cell_center_head_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'center',
            'bg_color': 'gray',
            'color': '#FFFFFF'
        })

        cell_center_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'center',
            'bg_color': 'white',
            'color': '#003366',
            'font_size': 20,
            'border': 2,
        })

        cell_center_num_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'center',
            'bg_color': '#2F5597',
            'color': '#FFFFFF',
            'num_format': '#,##0.00'
        })

        cell_right_num_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'right',
            'bg_color': 'gray',
            'color': '#FFFFFF',
            'num_format': '#,##0.00'
        })

        # cell_center_left_head_fmt = workbook.add_format({
        #     'font_name': 'Arial',
        #     'align': 'left',
        #     'bg_color': 'gray',
        #     'color': '#FFFFFF'
        # })
        cell_center_mem_id_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'center',
            'bg_color': 'ffcc99',
            'color': 'black'
        })
        cell_center_left_mem_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'left',
            'bg_color': 'white',
            'color': 'black',
            'border': 1
        })
        cell_center_bal_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'center',
            'bg_color': 'ffeb9c',
            'color': 'black',
            'num_format': '#,##0.00'
        })
        cell_left_tot_bal_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'left',
            'bg_color': '#DAE3F3',
            'color': 'black'
        })

        cell_right_bal_blue_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'right',
            'bg_color': '#2F5597',
            'color': 'white',
            'num_format': '#,##0.00'
        })

        worksheet.set_column(1, 1, 35)

        worksheet.set_row(1, 25)
        worksheet.merge_range(1, 2, 1, 5,
                              'Plumbing Plus Supplier Purchase Figures',
                              cell_center_fmt)
        curr_dt = datetime.now().date().strftime("%d-%m-%Y")
        worksheet.write(3, 5, "Print Date:", cell_center_left_mem_fmt)
        worksheet.write(3, 6, curr_dt, cell_center_left_mem_fmt)

        worksheet.freeze_panes(0, 2)
        worksheet.freeze_panes(5, 2)
        row = 5
        col = 0
        # worksheet.set_column(row, col, 15)
        worksheet.write(row, col, 'MemID', cell_center_head_fmt)
        col += 1
        # worksheet.set_column(1, 1, 35)
        worksheet.write(row, col, 'MEMBER', cell_center_head_fmt)
        col += 1

        if dates:
            for month_st_dt in dates:
                month_str = month_st_dt.strftime("%b")
                year_str = month_st_dt.strftime("%y")
                month_year_str = month_str + '-' + ustr(year_str)
                # dt_year = month_st_dt.year
                # dt_prev_year = dt_year - 1
                worksheet.set_column(col, col, 15)
                worksheet.write(row, col, month_year_str,
                                cell_center_head_fmt)
                col += 1
            worksheet.set_column(col, col, 15)
            worksheet.write(row, col, 'YTD Total',
                            cell_center_head_fmt)
            # col += 1
            # worksheet.set_column(col, col, 15)
            # worksheet.write(row, col, 'MEMBER %',
            #                 cell_center_head_fmt)
            # col += 1
            # worksheet.set_column(col, col, 15)
            # worksheet.write(row, col, 'Region',
            #                 cell_center_head_fmt)
            # col += 1
            # worksheet.set_column(col, col, 15)
            # worksheet.write(row, col, 'ABN',
            #                 cell_center_head_fmt)

        row += 1
        col = 0
        final_ytd_tot = 0.0
        final_totals_dict = {}
        for plumber in plumber_ids:
            worksheet.write(row, col, plumber.member_no or ' ',
                            cell_center_mem_id_fmt)
            col += 1
            worksheet.write(row, col, plumber.name or '',
                            cell_center_left_mem_fmt)
            col += 1

            plumber_tot = 0.0
            if dates:
                for month_st_dt in dates:
                    month_days = monthrange(month_st_dt.year,
                                            month_st_dt.month)
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

                    sale_ids = sale_obj.search([
                        ('company_id', '=', company),
                        ('partner_id', '=', plumber.id),
                        ('confirmation_date', '>=', month_st_dt),
                        ('confirmation_date', '<=', month_en_dt),
                        # ('date_order', '>=', month_st_dt),
                        # ('date_order', '<=', month_en_dt),
                    ])
                    sale_tot = sum(sale_ids.mapped('amount_total'))
                    worksheet.write(row, col, sale_tot,
                                    cell_center_bal_fmt)

                    if final_totals_dict and \
                            month_st_dt in final_totals_dict.keys():
                        amt = final_totals_dict[month_st_dt] + sale_tot
                        final_totals_dict.update({
                            month_st_dt: amt
                        })
                    else:
                        final_totals_dict.update({month_st_dt: sale_tot})
                    plumber_tot += sale_tot
                    col += 1
            # YTD Total
            worksheet.write(row, col, plumber_tot,
                            cell_right_bal_blue_fmt)
            final_ytd_tot += plumber_tot
            row += 1
            col = 0
        col = 1
        if final_totals_dict:
            worksheet.write(row, col, 'Total:', cell_left_tot_bal_fmt)
        col += 1
        if dates and final_totals_dict:
            for month_st_dt in dates:
                worksheet.write(row, col, final_totals_dict[month_st_dt],
                                cell_center_num_fmt)
                col += 1
        # YTD Total FINAL
        if final_totals_dict:
            worksheet.write(row, col, final_ytd_tot, cell_right_num_fmt)

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
            'scs_crm_sales_role.wiz_non_parent_child_report_exported_form')
        if wiz_rec and form_view:
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': wiz_rec.id,
                'res_model': 'wiz.non.parent.child.report.exported',
                'views': [(form_view.id, 'form')],
                'view_id': form_view.id,
                'target': 'new',
            }
        else:
            return {}
