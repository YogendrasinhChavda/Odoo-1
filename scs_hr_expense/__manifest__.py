# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    # Module information
    'name': 'SCS Expense',
    'version': '12.0.1.0.0',
    'category': 'hr',
    'sequence': 1,
    'summary': """HR Expenses Extended.""",
    'description': """HR Expenses Extended.""",

    # Author
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',

    # Dependencies
    'depends': ['hr_expense'],

    # Views
    'data': [
        'views/hr_expense_view.xml',
    ],

    # Techical
    'installable': True,
    'auto_install': False
}
