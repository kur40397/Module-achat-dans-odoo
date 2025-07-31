from odoo import fields,api , models
from odoo.api import readonly
from odoo.exceptions import UserError


class Produit(models.Model):
    _name = "module_achat.produit"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    nom=fields.Char(string="Nom",tracking=True)
    reference=fields.Char(string="Reference",readonly=True,tracking=True)
    categorie=fields.Selection(
        [
            ('equipements_protection_incendie','Équipements de protection incendie'),
            ('Accessoires_consommables','Accessoires & consommables'),
            ('Pieces_rechange','Pièces de rechange'),
            ('Materiaux_test_controle','Matériaux de test & contrôle')
        ]
    ,string="Categorie",required=True,tracking=True)
    norme=fields.Char(string="Norme",required=True,tracking=True)
    unite_mesure=fields.Many2one("uom.uom",string="unite mesure",required=True,tracking=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('valide', 'Valide'),
    ], default="draft",tracking=True)
    prix_fournisseur_ids=fields.One2many("module_achat.prix_fournisseur","prod_id",tracking=True)
    def valider_produit(self):
        # met a jour et enregistre tout de suite a la base
        # par contre self.state = 'valide' sauvegarde dans la mémoire
        self.write({
            'state':'valide',
            'reference':self.env['ir.sequence'].next_by_code('module_achat.produit'),
        })

class PrixFournisseur(models.Model):
    _name = "module_achat.prix_fournisseur"

    reference_fournisseur=fields.Char("reference fournisseur",required=True)
    prod_id=fields.Many2one("module_achat.produit",string="Produit",required=True)
    ref_fournisseur=fields.Many2one("res.partner",string="Fournisseur",required=True)
    prix_unitaire=fields.Float(string="Prix",required=True)
    devise_id =fields.Many2one("res.currency",string="Devise",required=True)

