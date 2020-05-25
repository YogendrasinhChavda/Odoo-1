# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    # Module information
    'name': 'SCS Account Reports',
    'version': '12.0.1.0.0',
    'category': 'Invoicing Management',
    'sequence': 1,
    'summary': """Accounting Reports and Enhancement.""",
    'description': """
        Accounting Reports and Enhancement.
    """,

    # Author
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',

    # Dependencies
    'depends': ['account'],

    # Views
    'data': [
        'report/report_invoice.xml',
        'report/report_tax_invoice.xml',
        'views/account_report.xml',
    ],

    # Techical
    'installable': True,
    'auto_install': False
}
