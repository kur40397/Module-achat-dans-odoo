from odoo import models , fields,api
from datetime import date

from odoo.exceptions import UserError


class BonCommande(models.Model):
    _name = "module_achat.bon_commande"
    numero_bon_commande=fields.Char(string="Numero bon commande")
    ref_fournisseur=fields.Many2one("res.partner",string="Fournisseur",required=True)
    code_projet=fields.Many2one("project.project",string="Projet",required=True)
    devise =fields.Many2one("res.currency","Devise",required=True)

    mode_reception =fields.Selection(selection=[
        ("global","Globale"),
        ("partielle","Partielle")
    ],string="Mode réception",default="global",required=True)
    date_bon_commande=fields.Date(string="Date bon commande",required=True)
    date_reception=fields.Date(string="Date réception",required=True)
    state=fields.Selection([
        ('draft','Brouillon'),
        ('valide','Valide'),
    ],default="draft")
    mode_paiement=fields.Selection([
        ("virement_bancaire","Virement bancaire"),
        ("especes","Espèces"),
        ("cheque","Chèque"),
        ("carte_bancaire","Carte bancaire")
    ],string="Mode paiement",copy=False,default="virement_bancaire",required=True)
    condition_de_paiement=fields.Many2one("account.payment.term",string="Condition de paiement",required=True)
    total_ht =fields.Float(string="Total HT",compute="_compute_total",store=True)
    tva=fields.Float(default=0.2)
    total_ttc =fields.Float(string="Total TTC",compute="_compute_total",store=True)
    ligne_bon_commandes_ids=fields.One2many("module_achat.ligne_bon_commande","bon_commande_id")
    count_bon_reception=fields.Integer(compute="_compute_count_bon_reception")
    bon_reception_ids=fields.One2many("module_achat.bon_reception","bon_commande_id")
    has_reliquat=fields.Selection([
        ('true', 'Avec reliquat'),
        ('false', 'Aucun reliquat')
    ],compute="_compute_reliquat",string="État des reliquats",default='false',store=True)
    type_commande = fields.Selection(selection=[
        ("local", "bon de commande local"),
        ("international", "bon de commande international")
    ], default="local",string="Type de commande")
    Incoterm=fields.Many2one("account.incoterms",string="Incoterm",required=True)
    charge_internationales=fields.Float(string="Charge internationales",required=True)
    total_internationales=fields.Float(string="Total international")

    @api.depends("bon_reception_ids")
    def _compute_reliquat(self):
        for rec in self:
          if rec.bon_reception_ids:
              is_cmd_has_reliquat=rec.bon_reception_ids[0]
              if is_cmd_has_reliquat:
                  rec.has_reliquat='true'
              else:
                  rec.has_reliquat = 'false'
          else:
              rec.has_reliquat = 'false'

    def action_imprimer_bon_commande(self):
        pass
    def action_valider_formulaire(self):
       erreur = []
       if  self.date_reception < self.date_bon_commande :
           erreur.append("La date de bon de commande doit être inférieure ou égale à la date de réception")
       if not self.ligne_bon_commandes_ids:
          erreur.append("Veuillez ajouter des lignes de commande")
       else:
           for ligne_cmd in self.ligne_bon_commandes_ids:
             if not ligne_cmd.produit_id or ligne_cmd.quantite == 0 or ligne_cmd.prix_unitaire==0:
               erreur.append("chaque ligne doit avoire une quantité , une quantité et un prix unitaire ")
       if len(erreur) != 0:
           # prend chaque element de la liste et kay7ot binathom had le separateur
           raise UserError("\n".join(erreur))
       self.write(
           {
               "state":"valide"
           }
       )
       ligne_vals=[]
       for rec in self.ligne_bon_commandes_ids:
           # le premier 0 ===> ajouter le deuxième 0
           # le deuxième 0 ==> l'id de l'enregistrement
           ligne_vals.append((0, 0, {
               'ref_produit': rec.ref_prod,
               'produit_id': rec.produit_id.id,
               'quantite_demandee': rec.quantite
           }))
       type_operation = self.env['stock.picking.type'].search([('name', '=', 'Réceptions')]).id
       self.env['module_achat.bon_reception'].create({
           'date_reception': date.today(),
           'bon_commande_id': self.id,
           'fournisseur': self.ref_fournisseur.id,
           'type_operation': type_operation,
           'projet_id': self.code_projet.id,
           'ligne_bon_receptions_ids': ligne_vals,
       })

    @api.depends("ligne_bon_commandes_ids")
    def _compute_total(self):
        for rec in self:
           rec.total_ht=sum(rec.ligne_bon_commandes_ids.mapped("prix_ht"))
           # mapped : sert a récupérer une liste de valeurs a partir d'un
           # ensemble d'enregistrement il suffit juste de préciser le champ
           rec.total_ttc= rec.total_ht*0.2 +rec.total_ht



    def _compute_count_bon_reception(self):
        self.count_bon_reception=len(self.bon_reception_ids)

    def action_open_receptions(self):
        self.ensure_one()
        action=self.env.ref("Module_Achat.action_view_module_achat_bon_reception",raise_if_not_found=False).read()[0]

        action['domain']=[('bon_commande_id', '=', self.id)]


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




