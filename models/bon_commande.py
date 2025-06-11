from odoo import models , fields,api
from datetime import date

from odoo.exceptions import UserError


class BonCommande(models.Model):
    _name = "module_achat.bon_commande"
    Numero_bon_commande=fields.Char(string="Numero bon commande")
    ref_fournisseur=fields.Many2one("res.partner",string="Fournisseur")
    code_projet=fields.Many2one("project.project",string="Projet")
    devise =fields.Many2one("res.currency","Devise")
    mode_reception =fields.Selection(selection=[
        ("global","Globale"),
        ("partielle","Partielle")
    ],string="Mode réception")
    date_bon_commande=fields.Date(string="Date bon commande")
    date_reception=fields.Date(string="Date réception")
    state=fields.Selection([
        ('draft','Brouillon'),
        ('valide','Valide'),
    ],default="draft")
    mode_paiement=fields.Selection([
        ("virement_bancaire","Virement bancaire"),
        ("especes","Espèces"),
        ("cheque","Chèque"),
        ("carte_bancaire","Carte bancaire")
    ],string="Mode paiement",copy=False)
    condition_de_paiement=fields.Many2one("account.payment.term",string="Condition de paiement")
    total_ht =fields.Float(string="Total HT",compute="_compute_total")
    tva=fields.Float(default=0.2)
    total_ttc =fields.Float(string="Total TTC",compute="_compute_total")
    ligne_bon_commandes_ids=fields.One2many("module_achat.ligne_bon_commande","bon_commande_id")
    count_bon_reception=fields.Integer(compute="_compute_count_bon_reception")
    bon_reception_ids=fields.One2many("module_achat.bon_reception","bon_commande_id")

    def action_valider_formulaire(self):
       self.write(
           {
               "state":"valide"
           }
       )
    @api.depends("ligne_bon_commandes_ids")
    def _compute_total(self):
        for rec in self:
           rec.total_ht=sum(rec.ligne_bon_commandes_ids.mapped("prix_ht"))
           # mapped : sert a récupérer une liste de valeurs a partir d'un
           # ensemble d'enregistrement il suffit juste de préciser le champ
           if rec.devise.name=='MAD':
              rec.total_ttc= rec.total_ht*0.2 +rec.total_ht
           else:
              rec.total_ttc=rec.total_ht


    def _compute_count_bon_reception(self):
        self.count_bon_reception=len(self.bon_reception_ids)

    def action_open_receptions(self):
        self.ensure_one()
        action=self.env.ref("Module_Achat.action_view_module_achat_bon_reception",raise_if_not_found=False).read()[0]

        action['domain']=[('bon_commande_id', '=', self.id)]
        list=[]
        for rec in self.ligne_bon_commandes_ids:
            # le premier 0 ===> ajouter le deuxième 0
            # le deuxième 0 ==> l'id de l'enregistrement
            list.append((0,0,{
                'ref_produit':rec.ref_prod,
                'produit_id':rec.produit_id.id,
                'quantite_demandee':rec.quantite
            }))
        type_operation=self.env['stock.picking.type'].search([('name','=','Réceptions')]).id
        action['context'] = {
            'default_date_reception': date.today(),
            'default_bon_commande_id': self.id,
            'default_fournisseur': self.ref_fournisseur.id,
            'default_type_operation': type_operation,
            'default_projet_id': self.code_projet.id,
            'default_ligne_bon_receptions_ids': list
        }
        return action








class LigneBonCommande(models.Model):
    _name = "module_achat.ligne_bon_commande"
    ref_prod=fields.Integer(string="Reference produit")
    produit_id=fields.Many2one("product.product",string="Description")
    quantite=fields.Float(string="Quantité")
    unite_mesure=fields.Many2one("uom.uom","unité de mesure")
    prix_unitaire=fields.Float("Prix unitaire")
    prix_ht=fields.Float("Total" ,compute="_compute_total")
    bon_commande_id=fields.Many2one("module_achat.bon_commande")

    @api.depends("prix_unitaire","quantite")
    def _compute_total(self):
        for rec in self:
            rec.prix_ht=rec.prix_unitaire*rec.quantite




