from odoo import fields,api , models

class Produit(models.Model):
    _inherit = "product.template"
    norme=fields.Char(string="Norme")
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('valide', 'Valide'),
    ], default="draft")
    prix_fournisseur_ids=fields.One2many("module_achat.prix_fournisseur","produit_id")
    def valider_produit(self):
        # met a jour et enregistre tout de suite a la base
        # par contre self.state = 'valide' sauvegarde dans la mémoire
        self.write({
            'state':'valide'
        })

class PrixFournisseur(models.Model):
    _name = "module_achat.prix_fournisseur"
    produit_id=fields.Many2one("product.template")
    ref_fournisseur=fields.Many2one("res.partner",string="Fournisseur")
    prix_unitaire=fields.Float(string="Prix")
    devise_id =fields.Many2one("res.currency",string="Devise")
