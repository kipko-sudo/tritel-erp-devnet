{
    'name': 'Boardroom Booking',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Manage boardroom bookings with approval workflow',
    'description': """
        A module to book boardrooms with approval process and status tracking.
    """,
    'author': 'Victor Kipkorir',
    'depends': ['base', 'mail'],
    # 'depende': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/boardroom_views.xml',
        'views/booking_views.xml',
    ],
    'installable': True,
    'application': True,
    "auto_install": False,
    "sequence": 1,    
}