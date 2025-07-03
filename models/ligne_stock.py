from odoo import models , fields,api
from datetime import date

# la class de base des modèle de odoo
class ligneStock(models.Model):
    _name="module_achat.ligne_stock"
    ref_ligne_Stock=fields.Char("reference ligne de stock")
    produit_id=fields.Many2one("product.product",string="Produit")
    location_id = fields.Many2one('stock.location', string="Emplacement")
    mouvement=fields.Selection(
        [
            ('entree','Entree'),
            ('sortie','Sortie'),
        ]
    )
    quantite=fields.Integer("Quantite")
    date=fields.Date("Date")
    origin=fields.Selection(
        [
            ("reception","automatique par réception"),
            ("manuelle","saisie manuelle par l’utilisateur"),

        ]
    ,string="L'origin du mouvement",default="manuelle",readonly=True)
    bon_reception_id = fields.Many2one("module_achat.bon_reception", "bon de reception")
    state=fields.Selection(
        [
            ("draft", "brouillon"),
            ("valide","valide"),
        ],default="draft"
    )

    def action_valider_ligne_stock(self):
        self.write({
            'state':'valide'
        })
        self.env["module_achat.ligne_stock"].create(
            {
                'produit_id': self.produit_id.id,
                'bon_reception_id': None,
                'quantite': self.quantite,
                'mouvement': self.mouvement,
                'location_id': self.location_id.id,
                'date': date.today(),

            }
        )
