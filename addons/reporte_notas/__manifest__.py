{
    "name":"Reporte de Notas",
    "depends":["base","website","website_slides","website_examenes","website_examenes_user"],
    "data":[
        'assets.xml',
        'security/security.xml',
        'templates/reporte_alumno.xml',
        'templates/views.xml',
        'data/website_data.xml',

    ],
    "qweb":[
        'reporte_notas/static/src/xml/reporte_class_ponde_700.xml',
        'reporte_notas/static/src/xml/reporte_asistencia_20.xml',

    ],
}
