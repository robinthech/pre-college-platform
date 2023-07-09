# -*- coding: utf-8 -*-

{
    'name': 'APRENTECH ELEARNING',
    'summary': '''The application to manage signup request from website''',
    'version': '13.0.0.1.0',
    'category': 'Extra Tools',
    'author': 'APRENTECH TECH',
    'author': 'APRENTECH TECH',
    'maintainer': 'APRENTECH TECH',
    'contributors':['Robinson Torres <rtorresh@uni.pe>'],
    'website': 'aprentech.tech',
    'depends': ['base','contacts','website', 'website_slides', 'web','mail','website_slides_survey','website_slides_forum','survey','rating','pragtech_odoo_zoom_meeting_integration','calendar',"im_livechat","website_livechat"],
    'data': [
        'security/security.xml',
        'security/admin.xml',
        'views/cursos.xml',
        'views/contenido.xml',
        'views/foro.xml',
        'views/resenas.xml',
        'views/informes.xml',
        'views/views.xml',
        'views/res_company.xml',

    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'images': ['static/description/poster_image.png'],
}
