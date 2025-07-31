from odoo import models , fields,api
from datetime import date

from odoo.api import readonly


# la class de base des modèle de odoo
class ligneStock(models.Model):
    _name="module_achat.ligne_stock"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    ref_ligne_Stock=fields.Char("reference ligne de stock",readonly=True)
    produit_id=fields.Many2one("product.product",string="Produit",tracking=True)
    location_id = fields.Many2one('stock.location', string="Emplacement",tracking=True)
    mouvement=fields.Selection(
        [
            ('entree','Entree'),
            ('sortie','Sortie'),
        ],tracking=True
    )
    quantite=fields.Integer("Quantite",tracking=True)
    date=fields.Date("Date",tracking=True)
    origin=fields.Selection(
        [
            ("reception","automatique par réception"),
            ("manuelle","saisie manuelle par l’utilisateur"),

        ]
    ,string="L'origin du mouvement",default="manuelle",readonly=True,tracking=True)
    bon_reception_id = fields.Many2one("module_achat.bon_reception", "bon de reception")
    state=fields.Selection(
        [
            ("draft", "brouillon"),
            ("valide","valide"),
        ],default="draft",tracking=True
    )

    def action_valider_ligne_stock(self):
        self.write({
            'state':'valide'
        })
        self.env["module_achat.ligne_stock"].create(
            {
                'ref_ligne_Stock':self.env['ir.sequence'].next_by_code('module_achat.ligne_stock'),
                'produit_id': self.produit_id.id,
                'bon_reception_id': None,
                'quantite': self.quantite,
                'mouvement': self.mouvement,
                'location_id': self.location_id.id,
                'date': date.today(),

            }
        )

