# -*- coding: utf-8 -*-
{
    'name': "Chat Edit/Delete IntegralClass",
    'summary': """The Odoo App provides the feature of editing and deleting an already sent message in Odoo Chat. """,
    'description': """	-Odoo Chat
			-Chat
			-Chat Edit
			-Chat Delete
			-Discussion Edit
			-Discussion Delete
			-Message Edit
			-Message Delete
			-Chat App
			-Odoo Chat App
			-Odoo Chat Edit App
			-Odoo Chat Delete App
			""",
    'author': "Ksolves India Pvt. Ltd.",
    'website': "https://www.ksolves.com/",
    'category': 'Tools',
    'version': '13.0.1.1.1',
    'license': 'LGPL-3',
    'support': 'sales@ksolves.com',
    'live_test_url':'https://www.youtube.com/watch?v=KpU4IcpDR5Y',
    'depends': ['base', 'mail', 'base_setup', 'web',"im_livechat","website_livechat"],
    'data': [
        'security/security.xml',
        'views/ks_assets.xml',
        'views/ks_inherited_res_config.xml',
    ],
    'images': [
        'static/description/main.jpg',
    ],
}
