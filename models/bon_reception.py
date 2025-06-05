from odoo import models , fields,api


class bonReception(models.Model):
    _name = "module_achat.bon_reception"
    ref_bon_reception=fields.Char(string="reference bon reception")
    date_reception=fields.Date(string="Date reception")
    bon_commande_id=fields.Many2one("module_achat.bon_commande",string="bon de commande")
    fournisseur=fields.Many2one("res.partner",string="Fournisseur")
    type_operation=fields.Many2one("stock.picking.type",string="Type de réception")
    controle_reception=fields.Selection([
        ('conforme', 'Conforme'),
        ('non_conforme', 'Non conforme'),
        ('partiel', 'Partiellement conforme'),
    ], string="Contrôle réception")
    projet_id=fields.Many2one("project.project",string="projet")
    state=fields.Selection([
        ('brouillon','Brouillon'),
        ('recu','reçu')
    ],default='brouillon')
    ligne_bon_receptions_ids=fields.One2many("module_achat.ligne_bon_reception","bon_reception_id")

    def valider_bon_reception(self):
        self.write({
            'state':'recu'
        })
    def creer_ligne_stock(self):
        pass




class ligneBonReception(models.Model):
    _name = 'module_achat.ligne_bon_reception'
    ref_produit=fields.Integer(string="reference produit")
    produit_id=fields.Many2one("product.product",string="Description")
    quantite_demandee=fields.Float(string="Quantite demandée")
    quantite_recue=fields.Float(string="quantite recue")
    reste=fields.Float(string="Reste",compute='_compute_reste')
    bon_reception_id=fields.Many2one("module_achat.bon_reception")

    @api.depends('quantite_recue')
    def _compute_reste(self):
        for rec in self:
             rec.reste=rec.quantite_demandee-rec.quantite_recue



