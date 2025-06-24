from odoo import fields,api , models
from odoo.exceptions import UserError


class Produit(models.Model):
    _inherit = "product.template"
    norme=fields.Char(string="Norme",required=True)
    default_code=fields.Char(required=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('valide', 'Valide'),
    ], default="draft")
    prix_fournisseur_ids=fields.One2many("module_achat.prix_fournisseur","produit_id")
    def valider_produit(self):
        # met a jour et enregistre tout de suite a la base
        # par contre self.state = 'valide' sauvegarde dans la mémoire
        erreur=[]
        if self.weight < 0:
            erreur.append("le poid doit être positive")
        if self.volume <0:
            erreur.append("le volume doit être positive")

        if len(erreur) != 0:
            raise UserError("\n".join(erreur))

        self.write({
            'state':'valide'
        })

class PrixFournisseur(models.Model):
    _name = "module_achat.prix_fournisseur"
    reference_fournisseur=fields.Char("reference fournisseur",required=True)
    produit_id=fields.Many2one("product.template",string="Produit",required=True)
    ref_fournisseur=fields.Many2one("res.partner",string="Fournisseur",required=True)
    prix_unitaire=fields.Float(string="Prix",required=True)
    devise_id =fields.Many2one("res.currency",string="Devise",required=True)

