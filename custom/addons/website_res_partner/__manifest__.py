# -*- coding: utf-8 -*-
# Part of UES. See LICENSE file for full copyright and licensing details.

{
    'name': 'Menu de solicitudes de usuario',
    'category': 'Website',
    'version': '1.0',
    'summary': 'Formulario de solicitudes de usuario a la plataforma de trabajos de grado',
    'description': """
Contact UES
====================

        """,
    'depends': ['base', 'website_form', 'hr_recruitment','auth_signup'],
    'data': [
        'data/config_data.xml',
        'views/website_res_partner_templates.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
