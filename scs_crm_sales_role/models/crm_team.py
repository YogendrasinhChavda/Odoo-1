"""CRM Team Model."""

from odoo import fields, models, api


class ResUsers(models.Model):
    """Res Users Model."""

    _inherit = "res.users"

    # Below fields added to calculate sales target
    sale_person_orders_ids = fields.One2many('sale.order', 'user_id',
                                             string="Sales Person Orders")
    sale_person_invoice_ids = fields.One2many('account.invoice', 'user_id',
                                              string="Sales Person Invoices")


class ResPartner(models.Model):
    """Res Partner Model."""

    _inherit = "res.partner"

    member_no = fields.Char(string="Member No.")
    # Moved Below fields here from studio custom
    x_studio_plumber_1 = fields.Boolean(string="Plumber")
    x_studio_plumber = fields.Boolean(string="Plumber")


class CrmTeam(models.Model):
    """CRM Team Model."""

    _inherit = "crm.team"

    levels = fields.Selection([('top_level', 'Top Level'),
                               ('second_level', 'Second Level'),
                               ('third_level', 'Third Level')],
                              string="Levels")
    regions = fields.Selection([('eastern', 'Eastern'),
                                ('western', 'Western'),
                                ('northern', 'Northern'),
                                ('southern', 'Southern')],
                               default='northern',
                               string="Regions")
    member_ids = fields.Many2many('res.users', 'crm_team_users_rel',
                                  'crm_team_id', 'user_id',
                                  string='Channel Members')
    parent_id = fields.Many2one('crm.team', string="Parent Team")
    region_team_ids = fields.One2many('crm.team', 'parent_id',
                                      string="Region Teams")
    states_team_ids = fields.One2many('crm.team', 'parent_id',
                                      string="States Teams")
    # Below fields added to calculate sales target
    sale_team_orders_ids = fields.One2many('sale.order', 'team_id',
                                           string="Sales Team Orders")
    sale_team_invoice_ids = fields.One2many('account.invoice', 'team_id',
                                            string="Sales Team Invoices")


class CrmLead(models.Model):
    """CRM Lead Model."""

    _inherit = "crm.lead"

    # cust_state_id = fields.Many2one(related="partner_id.state_id",
    #                                 store=True,
    #                                 string='Customer State')
