"""Account Bank Statement Model."""

from odoo import models, api
# from odoo.tools import ustr, DEFAULT_SERVER_DATE_FORMAT as DF


class AccountBankStatement(models.Model):
    """Account Bank Statement Model."""

    _inherit = "account.bank.statement"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=200):
        """Overridden Name search method to filter unique with date."""
        if args is None:
            args = []
        if self._context.get('bank_st_as_date', False):
            bnk_ids = []
            self.env.cr.execute("SELECT DISTINCT on (date) date,\
                id from account_bank_statement")
            bnk_lst = self.env.cr.fetchall()
            if bnk_lst:
                bnk_ids = [int(i[1]) for i in bnk_lst if len(i) >= 2]
            if bnk_ids:
                args += [('id', 'in', bnk_ids)]
        return super(AccountBankStatement, self).name_search(
            name=name, args=args, operator=operator, limit=limit)

    @api.multi
    def name_get(self):
        """Overridden Name Get method to show the record as date."""
        bnk_st_ctx = self.env.context.get('bank_st_as_date', False)
        res = []
        if bnk_st_ctx:
            for bk_st in self:
                res.append((bk_st.id, bk_st.date))
        else:
            res = super(AccountBankStatement, self).name_get()
        return res
