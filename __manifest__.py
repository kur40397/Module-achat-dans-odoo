{
    'name': 'Module Achat de Olympe industries',
    'version': '1.0',
    'depends': ['base','project','mail'],
    # Déclare les vues indépendantes en premier, et les vues qui en dépendent ensuite.
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/produit_prix_fournisseurs_views.xml',
        'views/bon_commande_views.xml',
        'views/report_bon_commande.xml',
        'views/bon_reception_views.xml',
        'views/ligne_stock_views.xml',
        'reports/report.xml',
        'views/menu_view.xml',
    ],
    # le module est prêt a être installer
    'installable': True,
    # apparaitre comme une vrai app dans le menu de odoo
    'application': True,
}
