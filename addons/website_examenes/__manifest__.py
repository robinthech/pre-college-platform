{
    "name":"Evaluación",
    "depends":["base","website","website_slides"],
    "data":[
        'assets.xml',
        'security/security.xml',
        'security/group_portal.xml',
        'security/group_user.xml',
        'security/group_alumno.xml',
        'templates/evaluaciones.xml',
        'templates/examenes.xml',
        'templates/examen_simulacro.xml',
        'templates/solucionario.xml',
        'templates/clave.xml',
        'views/evaluaciones.xml',
        'views/plantilla.xml',
        'views/respuesta.xml',
        'data/website_data.xml',

    ],
    'qweb': [
        "static/src/xml/xml.xml",
    ],
}
