# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    # Module information
    'name': 'SCS CRM Sales Role',
    'version': '12.0.1.0.0',
    'category': 'crm',
    'sequence': 1,
    'summary': """CRM and Sales Team Role Extended.""",
    'description': """CRM and Sales Team Role Extended.""",

    # Author
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',

    # Dependencies
    'depends': ['crm', 'sale', 'account'],

    # Views
    'data': [
        "security/sales_role_security.xml",
        "security/ir.model.access.csv",
        "views/crm_team_view.xml",
        "views/crm_lead_view.xml",
        "views/sales_billed_invoice_target_view.xml",
        "views/res_company_view.xml",
        "views/res_partner_view.xml",
        "report/sale_invoice_report_view.xml",
        "report/top_most_sale_invoice_report_view.xml",
        "report/top_most_sale_invoice_product_report_view.xml",
        "wizard/wiz_sales_team_target_report_view.xml",
    ],

    # Techical
    'installable': True,
    'auto_install': False
}
