"""Sales Billed Invoice Target and Sales Billed Invoice Target Team Model."""

from datetime import datetime
from odoo.tools import date_utils
from odoo import api, fields, models


class SalesBilledInvoiceTargetTeam(models.Model):
    """Sales Billed Invoice Target Team Model."""

    _name = "sales.billed.invoice.target.team"
    _description = "Sales Billed Invoice Target Team"
    _rec_name = 'team_id'

    sales_team_target = fields.Float(string="Sales Team Target")
    time_span = fields.Selection([('monthly', 'Monthly'),
                                  ('quarterly', 'Quarterly'),
                                  ('yearly', 'Yearly')],
                                 string="Time Span",
                                 default="monthly")
    date_from = fields.Date(string="Start Date")
    date_to = fields.Date(string="End Date")
    team_id = fields.Many2one("crm.team", string="Team")
    regions = fields.Selection(related="team_id.regions",
                               string="Regions",
                               store=True)
    sales_ord_trg_achived = fields.Float(
        compute="_get_sales_teams_orders_and_invoice_info",
        store=True,
        string="Sales Order Target Achived")
    billed_inv_trg_achived = fields.Float(
        compute="_get_sales_teams_orders_and_invoice_info",
        store=True,
        string="Billed Invoice Target Achived")
    sale_team_order_ids = fields.Many2many(
        "sale.order",
        "sales_order_team_target_rel",
        "sale_order_team_trg_id", "sale_order_id",
        store=True,
        string="Sale Teams Orders",
        compute='_get_sales_teams_orders_and_invoice_info')
    sale_invoice_ids = fields.Many2many(
        "account.invoice",
        "sales_invoice_team_target_rel",
        "sale_invoice_team_trg_id", "sale_invoice_id",
        store=True,
        string="Sale Teams Invoices",
        compute='_get_sales_teams_orders_and_invoice_info')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'In Progress'),
        ('cancel', 'Cancelled'),
        ('done', 'Done')],
        default="draft", string="Status")

    @api.multi
    def action_open_target(self):
        for team_trg in self:
            team_trg.state = 'open'

    @api.multi
    def action_set_to_draft_target(self):
        for team_trg in self:
            team_trg.state = 'draft'

    @api.multi
    def action_set_to_done(self):
        for team_trg in self:
            team_trg.state = 'done'

    @api.multi
    def action_set_to_cancel(self):
        for team_trg in self:
            team_trg.state = 'cancel'

    @api.multi
    @api.depends('team_id', 'team_id.sale_team_orders_ids',
                 'team_id.sale_team_orders_ids.state',
                 'team_id.sale_team_invoice_ids',
                 'team_id.sale_team_invoice_ids.state',
                 'date_from', 'date_to')
    def _get_sales_teams_orders_and_invoice_info(self):
        sale_obj = self.env['sale.order']
        inv_obj = self.env['account.invoice']
        for sale_team_trg in self:
            sale_team_trg.sale_team_order_ids = [(6, 0, [])]
            sale_team_trg.sale_invoice_ids = [(6, 0, [])]
            team_id = sale_team_trg.team_id and \
                sale_team_trg.team_id.id or False
            if team_id:
                sales = sale_obj.search([
                    ('confirmation_date', '>=', sale_team_trg.date_from),
                    ('confirmation_date', '<=', sale_team_trg.date_to),
                    ('team_id', '=', team_id),
                    ('state', 'in', ['sale', 'done'])])
                sale_team_trg.sale_team_order_ids = [(6, 0, sales.ids)]
                sale_team_trg.sales_ord_trg_achived = \
                    sum([sale.amount_total for sale in sales]) or 0.0

                invoices = inv_obj.search([
                    ('date_invoice', '>=', sale_team_trg.date_from),
                    ('date_invoice', '<=', sale_team_trg.date_to),
                    ('type', '=', 'out_invoice'),
                    ('team_id', '=', team_id),
                    ('state', 'in', ['open', 'in_payment', 'paid'])])
                sale_team_trg.sale_invoice_ids = [(6, 0, invoices.ids)]
                sale_team_trg.billed_inv_trg_achived = \
                    sum([sale_inv.amount_total
                         for sale_inv in invoices]) or 0.0

    @api.multi
    def get_timespan_start_end_dt(self):
        """Method to get the start and end date based on the timespan."""
        curr_dt = datetime.now().date()
        s_date = date_utils.start_of(curr_dt, 'month')
        e_date = date_utils.end_of(curr_dt, 'month')
        if self.time_span:
            if self.time_span == 'monthly':
                s_date = date_utils.start_of(curr_dt, 'month')
                e_date = date_utils.end_of(curr_dt, 'month')
            elif self.time_span == 'quarterly':
                # Pass granularity like year, quarter, month, week, day, hour
                s_date = date_utils.start_of(curr_dt, 'quarter')
                e_date = date_utils.end_of(curr_dt, 'quarter')
            elif self.time_span == 'yearly':
                s_date = date_utils.start_of(curr_dt, 'year')
                e_date = date_utils.end_of(curr_dt, 'year')
        return s_date, e_date

    @api.onchange('time_span')
    def onchange_time_span(self):
        """Onchange timespan to set the start and end date."""
        s_date, e_date = self.get_timespan_start_end_dt()
        if s_date and e_date:
            self.date_from = s_date
            self.date_to = e_date

    # @api.depends('team_id', 'time_span', 'date_from', 'date_to',
    #              'sale_team_order_ids', 'sale_invoice_ids')
    # def compute_sales_billed_team_target(self):
        """Compute method to calculate total achived target for Team."""
        # sale_obj = self.env['sale.order']
        # inv_obj = self.env['account.invoice']
        # for sale_tar_l in self:
        # sale_team_id = sale_tar_l.team_id and \
        #     sale_tar_l.team_id.id or False
        # s_date = sale_tar_l.date_from
        # e_date = sale_tar_l.date_to
        # s_date, e_date = sale_tar_l.get_timespan_start_end_dt()
        # sales = sale_obj.search([('confirmation_date', '>=', s_date),
        #                          ('confirmation_date', '<=', e_date),
        #                          ('team_id', '=', sale_team_id),
        #                          ('state', 'in', ['sale', 'done'])])
        # sale_tar_l.sales_ord_trg_achived = \
        #     sum([sale.amount_total for sale in sales]) or 0.0

        # invoices = inv_obj.search([
        #     ('date_invoice', '>=', s_date),
        #     ('date_invoice', '<=', e_date),
        #     ('type', '=', 'out_invoice'),
        #     ('team_id', '=', sale_team_id),
        #     ('state', 'in', ['open', 'in_payment', 'paid'])])
        # sale_tar_l.billed_inv_trg_achived = \
        #     sum([inv.amount_total for inv in invoices]) or 0.0


class SalesBilledInvoiceTarget(models.Model):
    """Sales Billed Invoice Target Model."""

    _name = "sales.billed.invoice.target"
    _description = "Sales Billed Invoice Target Person"
    _rec_name = 'sales_user_id'

    sales_user_id = fields.Many2one("res.users", string="Sales Person")
    sales_user_ids = fields.Many2many("res.users",
                                      "sales_bill_user_target_rel",
                                      "sale_target_id", "sal_user_id",
                                      string="Sales Persons")
    sales_person_target = fields.Float(string="Sales Person Target")
    time_span = fields.Selection([('monthly', 'Monthly'),
                                  ('quarterly', 'Quarterly'),
                                  ('yearly', 'Yearly')],
                                 string="Time Span",
                                 default="monthly")
    date_from = fields.Date(string="Start Date")
    date_to = fields.Date(string="End Date")
    team_id = fields.Many2one("crm.team", string="Team")
    regions = fields.Selection(related="team_id.regions",
                               string="Regions",
                               store=True)
    sales_ord_trg_achived = fields.Float(
        compute="_get_sales_persons_orders_and_invoice_info",
        store=True,
        string="Sales Order Target Achived")
    billed_inv_trg_achived = fields.Float(
        compute="_get_sales_persons_orders_and_invoice_info",
        store=True,
        string="Billed Invoice Target Achived")
    sale_person_order_ids = fields.Many2many(
        "sale.order",
        "sales_ord_person_target_rel",
        "sale_ord_person_trg_id", "sale_order_id",
        string="Sale Teams Orders",
        store=True,
        compute='_get_sales_persons_orders_and_invoice_info')
    sale_invoice_ids = fields.Many2many(
        "account.invoice",
        "sales_invoice_person_target_rel",
        "sale_invoice_person_trg_id", "sale_invoice_id",
        string="Sale Teams Invoices",
        store=True,
        compute='_get_sales_persons_orders_and_invoice_info')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'In Progress'),
        ('cancel', 'Cancelled'),
        ('done', 'Done')],
        default="draft", string="Status")

    @api.multi
    def action_open_target(self):
        for team_trg in self:
            team_trg.state = 'open'

    @api.multi
    def action_set_to_draft_target(self):
        for team_trg in self:
            team_trg.state = 'draft'

    @api.multi
    def action_set_to_done(self):
        for team_trg in self:
            team_trg.state = 'done'

    @api.multi
    def action_set_to_cancel(self):
        for team_trg in self:
            team_trg.state = 'cancel'

    @api.multi
    def get_timespan_start_end_dt(self):
        """Method to get the start and end date based on the timespan."""
        curr_dt = datetime.now().date()
        s_date = date_utils.start_of(curr_dt, 'month')
        e_date = date_utils.end_of(curr_dt, 'month')
        if self.time_span:
            if self.time_span == 'monthly':
                s_date = date_utils.start_of(curr_dt, 'month')
                e_date = date_utils.end_of(curr_dt, 'month')
            elif self.time_span == 'quarterly':
                # Pass granularity like year, quarter, month, week, day, hour
                s_date = date_utils.start_of(curr_dt, 'quarter')
                e_date = date_utils.end_of(curr_dt, 'quarter')
            elif self.time_span == 'yearly':
                s_date = date_utils.start_of(curr_dt, 'year')
                e_date = date_utils.end_of(curr_dt, 'year')
        return s_date, e_date

    @api.onchange('time_span')
    def onchange_time_span(self):
        """Onchange timespan to set the start and end date."""
        s_date, e_date = self.get_timespan_start_end_dt()
        if s_date and e_date:
            self.date_from = s_date
            self.date_to = e_date

    @api.multi
    @api.depends('team_id', 'sales_user_id',
                 'sales_user_id.sale_person_orders_ids',
                 'sales_user_id.sale_person_orders_ids.state',
                 'sales_user_id.sale_person_orders_ids.user_id',
                 'sales_user_id.sale_person_invoice_ids',
                 'sales_user_id.sale_person_invoice_ids.state',
                 'sales_user_id.sale_person_invoice_ids.user_id',
                 'date_from', 'date_to')
    def _get_sales_persons_orders_and_invoice_info(self):
        sale_obj = self.env['sale.order']
        inv_obj = self.env['account.invoice']
        for sale_person_trg in self:
            sale_person_trg.sale_person_order_ids = [(6, 0, [])]
            sale_person_trg.sale_invoice_ids = [(6, 0, [])]
            sale_person = sale_person_trg.sales_user_id and \
                sale_person_trg.sales_user_id.id or False
            team_id = sale_person_trg.team_id and \
                sale_person_trg.team_id.id or False
            if team_id:
                sales = sale_obj.search([
                    ('confirmation_date', '>=', sale_person_trg.date_from),
                    ('confirmation_date', '<=', sale_person_trg.date_to),
                    ('user_id', '=', sale_person),
                    ('team_id', '=', team_id),
                    ('state', 'in', ['sale', 'done'])])
                sale_person_trg.sale_person_order_ids = [(6, 0, sales.ids)]
                sale_person_trg.sales_ord_trg_achived = \
                    sum([sale.amount_total for sale in sales]) or 0.0

                invoices = inv_obj.search([
                    ('date_invoice', '>=', sale_person_trg.date_from),
                    ('date_invoice', '<=', sale_person_trg.date_to),
                    ('type', '=', 'out_invoice'),
                    ('user_id', '=', sale_person),
                    ('team_id', '=', team_id),
                    ('state', 'in', ['open', 'in_payment', 'paid'])])
                sale_person_trg.sale_invoice_ids = [(6, 0, invoices.ids)]
                sale_person_trg.billed_inv_trg_achived = \
                    sum([sale_inv.amount_total
                         for sale_inv in invoices]) or 0.0

    # @api.depends('team_id', 'sales_user_id',
    #              'time_span')
    # def compute_sales_billed_target(self):
    #     """Compute method to calculate total achived target for Person."""
    #     sale_obj = self.env['sale.order']
    #     inv_obj = self.env['account.invoice']
    #     for sale_tar_l in self:
    #         sale_person = sale_tar_l.sales_user_id and \
    #             sale_tar_l.sales_user_id.id or False
    #         s_date = sale_tar_l.date_from
    #         e_date = sale_tar_l.date_to
    #         # s_date, e_date = sale_tar_l.get_timespan_start_end_dt()
    #         sales = sale_obj.search([('confirmation_date', '>=', s_date),
    #                                  ('confirmation_date', '<=', e_date),
    #                                  ('user_id', '=', sale_person),
    #                                  ('state', 'in', ['sale', 'done'])])
    #         sale_tar_l.sales_ord_trg_achived = \
    #             sum([sale.amount_total for sale in sales]) or 0.0

    #         invoices = inv_obj.search([
    #             ('date_invoice', '>=', s_date),
    #             ('date_invoice', '<=', e_date),
    #             ('type', '=', 'out_invoice'),
    #             ('user_id', '=', sale_person),
    #             ('state', 'in', ['open', 'in_payment', 'paid'])])
    #         sale_tar_l.billed_inv_trg_achived = \
    #             sum([inv.amount_total for inv in invoices]) or 0.0

    # @api.onchange('time_span')
    # def onchange_sales_user_id(self):
    #     """Onchange Method to set start and end date."""
    #     datetime.now()
    #     if self.time_span == 'monthly':
    #     elif self.time_span == 'quarterly':
    #     elif self.time_span == 'yearly':

    @api.onchange('team_id')
    def onchange_sales_user_id(self):
        """Onchange Method to filter sales person."""
        sales_persons = self.env['res.users'].search([
            ('active', '=', True)]).ids
        sales_persons_lst = []
        self.sales_user_id = False
        if self.team_id:
            if self.team_id.user_id:
                sales_persons_lst.append(self.team_id.user_id.id)
            if self.team_id.member_ids:
                sales_persons_lst.extend(self.team_id.member_ids.ids)
            if sales_persons_lst:
                sales_persons = list(set(sales_persons_lst))
        if sales_persons:
            self.sales_user_ids = [(6, 0, sales_persons)]
