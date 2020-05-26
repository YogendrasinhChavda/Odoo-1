"""Stock models."""
# -*- coding: utf-8 -*-
from odoo import api, fields, models


class StockPicking(models.Model):
    """Stock Picking Model."""

    _inherit = 'stock.picking'

    internal_reference = fields.Char(string='Internal Reference')

    @api.multi
    def write(self, vals):
        if len(self) == 1 and self.state == 'assigned' and \
                not vals.get('internal_reference', False):
            for move in self.move_ids_without_package:
                if move.product_tmpl_id and \
                        move.product_tmpl_id.bom_count or \
                        not self.internal_reference:
                    # self.internal_reference = \
                    #     move.product_tmpl_id.default_code
                    vals.update({
                        'internal_reference':
                        move.product_tmpl_id.default_code or ''
                    })
        return super(StockPicking, self).write(vals)


class AccountMove(models.Model):
    """Account Move Model."""

    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        """Override method to update refrence when manual inventory adjust."""
        acc_move = super(AccountMove, self).create(vals)
        if acc_move and not acc_move.ref:
            if acc_move.stock_move_id and \
                acc_move.stock_move_id.inventory_id and \
                    acc_move.stock_move_id.inventory_id.name:
                acc_move.write({
                    'ref': 'INV:' + acc_move.stock_move_id.inventory_id.name
                })
            elif acc_move.stock_move_id and acc_move.stock_move_id.reference:
                acc_move.write({
                    'ref': acc_move.stock_move_id.reference
                })
        return acc_move
