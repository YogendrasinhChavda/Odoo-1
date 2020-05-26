
from odoo import api, fields, models
import datetime


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def invoice_line_non_kit(self):
        sale_order_line_obj = self.env['sale.order.line']
        invoice_line_obj = self.env['account.invoice.line']
        inv_rec = self.env['account.invoice'].search(
            [('sale_id', '=', self.origin)], limit=1)
        sale_order = self.env['sale.order'].search(
            [('name', '=', self.origin)], limit=1)
        inv_line = False
        for sale_line in sale_order.order_line:
            if sale_line.product_id and \
                    sale_line.product_id.product_tmpl_id and \
                    not sale_line.product_id.product_tmpl_id.bom_ids:
                account = self.get_account_properties()
                inv_line = invoice_line_obj.create({
                    'name': sale_line.name,
                    'account_id': account and account.id or False,
                    'invoice_id': inv_rec and inv_rec.id or False,
                    'price_unit': sale_line.price_unit,
                    'quantity': sale_line.product_uom_qty,
                    'uom_id': sale_line.product_id and
                    sale_line.product_id.uom_id.id or False,
                    'product_id': sale_line.product_id and
                    sale_line.product_id.id or False,
                })
                order_line_ids = sale_order_line_obj.search([
                    ('order_id', '=', sale_order.id),
                    ('product_id', '=', sale_line.product_id.id)])
                for order_line in order_line_ids:
                    order_line.write({
                        'qty_to_invoice': sale_line.product_uom_qty,
                        'invoice_lines': [(4, inv_line.id, 0)]
                    })
                    tax_ids = []
                    if order_line and order_line_ids[0]:
                        for tax in order_line[0].tax_id:
                            tax_ids.append(tax.id)

                    inv_line.write({
                        'price_unit': order_line[0].price_unit,
                        'discount': order_line[0].discount,
                        'invoice_line_tax_ids': [(6, 0, tax_ids)]
                    })
                    inv_rec.compute_taxes()
        return True

    def get_account_properties(self):
        ir_property_obj = self.env['ir.property']
        account_obj = self.env['account.account']
        account = False
        for pick_line in self.move_lines:
            if pick_line.product_id.property_account_income_id:
                account = pick_line.product_id.\
                    property_account_income_id
            elif pick_line.product_id.categ_id.\
                    property_account_income_categ_id:
                account = pick_line.product_id.categ_id.\
                    property_account_income_categ_id
            else:
                account_search = ir_property_obj.search(
                    [('name', '=', 'property_account_income_categ_id')])
                account = account_search.value_reference
                account = account.split(",")[1]
                account = account_obj.browse(account)
        return account

    def invoice_lines_creation(self):
        invoice_line_obj = self.env['account.invoice.line']
        acc_inv_rec = self.env['account.invoice'].search(
            [('sale_id', '=', self.origin)], limit=1)
        sale_order = self.env['sale.order'].search(
            [('name', '=', self.origin)], limit=1)
        account = self.get_account_properties()
        for inv_lines in acc_inv_rec.invoice_line_ids:
            inv_lines.unlink()
        for sale_line in sale_order.order_line:
            inv_line_id = invoice_line_obj.create({
                'name': sale_line.name,
                'account_id': account and account.id or False,
                'invoice_id': acc_inv_rec and acc_inv_rec.id or False,
                'price_unit': sale_line.price_unit,
                'quantity': sale_line.product_uom_qty,
                'uom_id': sale_line.product_id.uom_id and
                sale_line.product_id.uom_id.id or False,
                'product_id': sale_line.product_id and
                sale_line.product_id.id or False
            })
            sale_line.write({
                'qty_to_invoice': sale_line.qty_delivered,
                'invoice_lines': [(4, inv_line_id.id, 0)]
            })
            tax_ids = []
            if sale_line[0]:
                for tax in sale_line[0].tax_id:
                    tax_ids.append(tax.id)
                    inv_line_id.write({
                        'price_unit': sale_line[0].price_unit,
                        'discount': sale_line[0].discount,
                        'invoice_line_tax_ids': [(6, 0, tax_ids)]
                    })
                    acc_inv_rec.compute_taxes()
        return True

    @api.multi
    def action_done(self):
        if self.sale_id and self.sale_id.carrier_id:
            if not self.env['sale.order.line'].search_count([
                    ('order_id', 'in', self.ids),
                    ('is_delivery', '=', True)]):
                self.sale_id.delivery_rating_success = False
                res = self.sale_id.carrier_id.rate_shipment(self.sale_id)
                if res.get('success', False):
                    self.sale_id.write({
                        'delivery_rating_success': True,
                        'delivery_price': res and res.get('price', 0.0),
                        'delivery_message': res and
                        res.get('warning_message', 0.0),
                    })
                    self.carrier_price = res.get('price', 0.0)
                else:
                    self.sale_id.write({
                        'delivery_rating_success': False,
                        'delivery_price': 0.0,
                        'delivery_message': res and
                        res.get('error_message', 0.0),
                    })
                self._add_delivery_cost_to_so()
                self.sale_id.invoice_shipping_on_delivery = False
        res = super(StockPicking, self).action_done()
        acc_inv_rec = self.env['account.invoice'].search([
            ('sale_id', '=', self.origin)], limit=1)
        sale_order = self.env['sale.order'].search([
            ('name', '=', self.origin)], limit=1)
        inv_line_obj = self.env['account.invoice.line']
        flag = 0
        if sale_order and acc_inv_rec:
            account = self.get_account_properties()
            acc_inv_rec.write({
                'user_id': sale_order.user_id and
                sale_order.user_id.id or False,
                'name': sale_order.client_order_ref,
                'date_invoice': fields.Date.context_today(self)
            })
            for inv_lines in acc_inv_rec.invoice_line_ids:
                inv_lines.unlink()
            for sale_line in sale_order.order_line:
                if sale_line.product_id.product_tmpl_id.bom_ids:
                    invoice_line_id = inv_line_obj.create({
                        'name': sale_line.name,
                        'account_id': account.id,
                        'invoice_id': acc_inv_rec and acc_inv_rec.id,
                        'price_unit': sale_line.price_unit,
                        'quantity': sale_line.product_uom_qty,
                        'uom_id': sale_line.product_id.uom_id.id,
                        'product_id': sale_line.product_id.id})
                    sale_line.write({
                        'qty_to_invoice': sale_line.qty_delivered,
                        'invoice_lines': [(4, invoice_line_id.id, 0)]
                    })
                    tax_ids = []
                    if sale_line[0]:
                        for tax in sale_line[0].tax_id:
                            tax_ids.append(tax.id)
                    invoice_line_id.write({
                        'price_unit': sale_line[0].price_unit,
                        'discount': sale_line[0].discount,
                        'invoice_line_tax_ids': [(6, 0, tax_ids)]
                    })
                    acc_inv_rec.compute_taxes()
                else:
                    flag = 1
            if flag == 1:
                self.invoice_line_non_kit()

            sale_order.write({
                'x_studio_last_invoice_date': datetime.date.today(),
                'x_studio_invoiced': True,
                'x_studio_invoice_amount': acc_inv_rec.amount_total
            })
        return True

    @api.multi
    def do_print_picking_2(self):
        self.write({'x_studio_delivery_printed': True})
        return self.env.ref('stock.action_report_delivery').\
            report_action(self)
