# -*- coding: utf-8 -*-
{
    'name': 'Modificaciones al Inventario Fisico',
    'version': '1.0',
    'category': 'Cegasa',
    'description': """

        Este modulo agrega el campo costo al Inventario Fisico y este lo lleva al Reporte.
    """,
    'author': 'PonceSoft',
    'website': 'http://poncesoft.blogspot.com',
    'depends': ['base','stock'],
    'update_xml': [
        'stock_view.xml',
        ],
    'installable': True,
    'active': False,
    'certificate' : False,
}