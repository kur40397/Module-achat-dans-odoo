from odoo import models , fields,api

class BonCommande(models.Model):
    _name = "module_achat.bon_commande"
    Numero_bon_commande=fields.Char(string="Numero bon commande")
    ref_fournisseur=fields.Many2one("res.partner",string="Fournisseur")
    code_projet=fields.Many2many("project.project",string="Projet")
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
    ],string="Mode paiement")
    condition_de_paiement=fields.Many2one("account.payment.term",string="Condition de paiement")
    total_ht =fields.Float(string="Total HT")
    total_ttc =fields.Float(string="Total TTC")

