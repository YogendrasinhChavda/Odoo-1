# -*- coding: utf-8 -*-


{
    'name': 'Custom Auto Custom_Au_in(Shipment/Delivery)',
    'version': '12.0.0.0',
    'category': 'Accounting',
    'summary': 'This apps automatically create invoice from Picking when picking(Shipment/Delivery) get done',
    'description': """ This apps Custom_Au_in automatically create invoice from Picking when picking(Shipment/Delivery) get done
""",
    'depends': ['sale','purchase','stock','Au_In12'],
    'data': [
        'report/custom_report.xml',
        'report/custom_stock_picking_report.xml',
        'views/stock_picking.xml',
        ],
    'demo': [],
    'js': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
