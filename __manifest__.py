{
    'name': 'Module Achat de Olympe industries',
    'version': '1.0',
    'depends': ['base','project'],
    'data': [
        'views/bon_commande_views.xml',
        #'views/bon_reception_views.xml',
        #'views/ligne_stock_views.xml',
        #'views/produit_prix_fournisseurs_views.xml',
        'views/menu_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
