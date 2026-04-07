{
    'name': 'Real Estate',
    'version': '1.0',
    'description': 'An assess management tool',
    'author': 'yay',
    'license': 'LGPL-3',
    'depends': [
        'base_setup'
    ],
    'data': [
        'security/ir.model.access.csv',
        
        # ต้องใส่ view ก่อน menu เพราะ data load แบบ sequentialy
        'views/estate_property_offer_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        # add loaded all the above before this main view bc there's action depended on the above views
        'views/estate_property_views.xml',
        
        'views/estate_menus.xml',
        
        ],
    'auto_install': True,
    'application': True,
}