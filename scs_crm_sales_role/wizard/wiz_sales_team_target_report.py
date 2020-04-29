"""Wizard Sales Team Target Report TransientModel."""

import xlsxwriter
import os
import base64
from datetime import datetime
# from calendar import monthrange
# from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import Warning
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

    @api.multi
    def export_sales_team_target_report(self):
        """Method to generate the Sales Team target report."""
        sales_team_obj = self.env['crm.team']
        country_obj = self.env['res.country']
        state_obj = self.env['res.country.state']
        sale_obj = self.env['sale.order']
        wiz_exported_obj = self.env['wiz.sales.team.target.report.exported']

        if self.date_from > self.date_to:
            raise Warning(_("To date must be greater than \
                or Equals to from date !!"))

        file_path = 'YTM Sales Team Report.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/' + file_path)
        worksheet = workbook.add_worksheet("YTM Sales Team Report")

        cell_font_fmt = workbook.add_format({
            'font_name': 'Arial',
        })
        # cell_center_fmt = workbook.add_format({
        #     'font_name': 'Arial',
        #     'align': 'center',
        # })
        cell_left_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'left',
        })
        cell_left_color_fmt = workbook.add_format({
            'font_name': 'Arial',
            'align': 'left',
            'color': '#0070C0'
        })
        cell_bg_fmt = workbook.add_format({
            'font_name': 'Arial',
            'bg_color': '#548235'
        })
        cell_bg_fmt1 = workbook.add_format({
            'font_name': 'Arial',
            'bg_color': '#a9d18e'
        })

        worksheet.set_column(0, 0, 35)
        worksheet.freeze_panes(0, 1)

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
        worksheet.write(row, col, "Country/State", cell_bg_fmt)
        row += 1
        worksheet.write(row, col, " ", cell_bg_fmt)
        row += 1

        # ---------------------------------------------------------------
        sale_ids = sale_obj.search([
            ('confirmation_date', '>=', self.date_from),
            ('confirmation_date', '<=', self.date_to),
            ('state', 'in', ['sale', 'done'])])

        print("\n sale_ids::::::1::::::::", sale_ids)
        partner_ids = sale_ids.mapped('partner_id')
        # team_ids = sale_ids.mapped('team_id')
        country_ids = sale_ids.mapped('partner_id').mapped('country_id')
        state_ids = sale_ids.mapped('partner_id').mapped('state_id')
        print("\n partner_ids::::::2::::::::", partner_ids)
        print("\n country_ids::::::3::::::::", country_ids)
        print("\n state_ids::::::4::::::::", state_ids)
        for country_id in country_obj.search([
                ('id', 'in', country_ids.ids)], order="name"):
            worksheet.write(row, col,
                            country_id.name + " Actual", cell_bg_fmt1)
            row += 1
            sale_country_ids = sale_obj.search([
                ('confirmation_date', '>=', self.date_from),
                ('confirmation_date', '<=', self.date_to),
                ('partner_id.country_id', '=', country_id.id),
                ('state', 'in', ['sale', 'done'])])
            # sales_team_obj.search([('')])
            sale_team_ids = sale_country_ids.mapped('team_id')
            for team_id in sale_team_ids:
                worksheet.write(row, col,
                                team_id.name + " Actual", cell_left_fmt)
                row += 1
                worksheet.write(row, col,
                                team_id.name + " Budget", cell_left_color_fmt)
                row += 1
        # ---------------------------------------------------------------

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
