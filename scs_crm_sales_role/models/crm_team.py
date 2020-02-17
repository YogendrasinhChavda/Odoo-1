"""CRM Team Model."""

from odoo import fields, models


class CrmTeam(models.Model):
    """CRM Team Model."""

    _inherit = "crm.team"

    levels = fields.Selection([('top_level', 'Top Level'),
                               ('second_level', 'Second Level'),
                               ('third_level', 'Third Level')],
                              string="Levels")
    member_ids = fields.Many2many('res.users', 'crm_team_users_rel',
                                  'crm_team_id', 'user_id',
                                  string='Channel Members')
    parent_id = fields.Many2one('crm.team', string="Parent Team")
    region_team_ids = fields.One2many('crm.team', 'parent_id',
                                      string="Region Teams")
    states_team_ids = fields.One2many('crm.team', 'parent_id',
                                      string="States Teams")

    # @api.onchange('levels')
    # def onchange_levels(self):
    #     """Onchange method to set the """


class CrmLead(models.Model):
    """CRM Lead Model."""

    _inherit = "crm.lead"

    cust_state_id = fields.Many2one("res.country.state",
                                    string='Customer State')
