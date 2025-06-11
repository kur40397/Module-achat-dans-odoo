from odoo import models , fields,api

# la class de base des modèle de odoo
class ligneStock(models.Model):
    _name="module_achat.ligne_stock"
    ref_ligne_Stock=fields.Char("reference ligne de stock")
    produit_id=fields.Many2one("product.product",string="Produit")
    location_id = fields.Many2one('stock.location', string="Emplacement")
    type_mouvement=fields.Many2one("stock.picking.type",string="Type de mouvement")
    quantite=fields.Integer("Quantite")
    date=fields.Date("Date")
    bon_reception_id = fields.Many2one("module_achat.bon_reception", "bon de reception")

