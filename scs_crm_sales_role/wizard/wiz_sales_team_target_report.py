"""Wizard Sales Team Target Report TransientModel."""

import xlsxwriter
import os
import base64
from datetime import datetime
from calendar import monthrange
# from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
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
        curr_dt = datetime.today()
        tot_days = monthrange(curr_dt.year, curr_dt.month)[1]
        st_dt = datetime.today().replace(day=1).date()
        end_dt = datetime.today().replace(day=int(tot_days)).date()
        res.update({'date_from': st_dt, 'date_to': end_dt})
        return res

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    company_id = fields.Many2one("res.company", string="Company",
                                 default=lambda self: self.env.user and
                                 self.env.user.company_id)
