from odoo import models , fields,api
from datetime import date

from odoo.exceptions import ValidationError


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
    location_id = fields.Many2one('stock.location', string="Emplacement")
    ligne_bon_receptions_ids=fields.One2many("module_achat.ligne_bon_reception","bon_reception_id")
    ligne_stock_ids=fields.One2many("module_achat.ligne_stock","bon_reception_id")
    count_ligne_stock=fields.Integer(computer="_compute_count_ligne_stock")
    has_reliquat=fields.Boolean(default=False)
    has_reliquat_xml=fields.Char(default="false")







    def valider_bon_reception(self):
        self.write({
            'state':'recu'
        })
        for rec in self.ligne_bon_receptions_ids:
            if rec.quantite_recue > 0:
                self.has_reliquat = True
                self.has_reliquat_xml='true'
                return





    def _compute_count_ligne_stock(self):
       self.count_ligne_stock=len(self.ligne_stock_ids)

    def action_open_stock(self):
        self.ensure_one()
        action=self.env.ref("Module_Achat.action_view_ligne_stock",raise_if_not_found=False).read()[0]
        action['domain'] = [('bon_reception_id', '=', self.id)]
        type_mouvement = self.type_operation.id,
        location = self.location_id.id
        for rec in self.ligne_bon_receptions_ids:
            self.env['module_achat.ligne_stock'].create(
                {
                    'produit_id': rec.produit_id.id,
                    'bon_reception_id': self.id,
                    'quantite': rec.quantite_recue,
                    'type_mouvement': type_mouvement,
                    'location_id': location,
                    'date': date.today()
                }
            )
        return action



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



