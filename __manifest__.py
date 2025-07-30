{
    'name': 'Module Achat de Olympe industries',
    'version': '1.0',
    'depends': ['base','project','mail'],
    # Déclare les vues indépendantes en premier, et les vues qui en dépendent ensuite.
    'data': [
        'views/produit_prix_fournisseurs_views.xml',
        'views/bon_commande_views.xml',
        'views/bon_reception_views.xml',
        'views/ligne_stock_views.xml',
        'data/sequence.xml',
        'views/menu_view.xml',
        'security/ir.model.access.csv',
    ],
    # le module est prêt a être installer
    'installable': True,
    # apparaitre comme une vrai app dans le menu de odoo
    'application': True,
}
