from itertools import count

from odoo import models , fields,api
from datetime import date

from odoo.exceptions import UserError

# la création du bon de commande

class BonCommande(models.Model):
    _name = "module_achat.bon_commande"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # mail.thread : pour les messages et suivre les notification & tracker les modification
    # mail.activity.mixin : planifier les tâches
    numero_bon_commande=fields.Char(string="Numero bon commande",readonly=True)
    ref_fournisseur=fields.Many2one("res.partner",string="Fournisseur",required=True,tracking=True)
    code_projet=fields.Many2one("project.project",string="Projet",required=True,tracking=True)
    devise =fields.Many2one("res.currency","Devise",required=True,tracking=True)
    date_bon_commande=fields.Date(string="Date bon commande",required=True,tracking=True)
    date_reception=fields.Date(string="Date réception",required=True,tracking=True)
    state=fields.Selection([
        ('draft','Brouillon'),
        ('valide','Valide'),
    ],default="draft",tracking=True)
    mode_paiement=fields.Selection([
        ("virement_bancaire","Virement bancaire"),
        ("especes","Espèces"),
        ("cheque","Chèque"),
        ("carte_bancaire","Carte bancaire")
    ],string="Mode paiement",copy=False,default="virement_bancaire",tracking=True)

    politique_reception = fields.Selection(
        [
            ('reliquat', 'Accepter reliquat'),
            ('sans_reliquat', 'Refuser reliquat')
        ],string="Politique de reception",default="reliquat",tracking=True)

    condition_de_paiement=fields.Many2one("account.payment.term",string="Condition de paiement",required=True,tracking=True)
    total_ht =fields.Float(string="Total HT",compute="_compute_total",store=True,tracking=True)
    tva=fields.Float(default=0.2)
    total_ttc =fields.Float(string="Total TTC",compute="_compute_total",store=True,tracking=True)
    ligne_bon_commandes_ids=fields.One2many("module_achat.ligne_bon_commande","bon_commande_id")
    count_reception=fields.Integer(string="bon de reception",compute="_compute_count_reception",store=True)
    bon_reception_ids=fields.One2many("module_achat.bon_reception","bon_commande_id")

    def action_imprimer_bon_commande(self):
        action = self.env.ref("Module_Achat.action_bon_commande_report", raise_if_not_found=False).read()[0]
        return action
    @api.depends("bon_reception_ids")
    def _compute_count_reception(self):
        self.count_reception=len(self.bon_reception_ids)

    #  methode qui s'active lorsque tu t'appuit sur le bouton valider
    def action_valider_formulaire(self):
       erreur = []
       if  self.date_reception < self.date_bon_commande :
           erreur.append("La date de bon de commande doit être inférieure ou égale à la date de réception")
       if not self.ligne_bon_commandes_ids:
          erreur.append("Veuillez ajouter des lignes de commande")
       else:
           for ligne_cmd in self.ligne_bon_commandes_ids:
             if not ligne_cmd.produit_id or ligne_cmd.quantite == 0 or ligne_cmd.prix_unitaire==0:
               erreur.append("Chaque ligne de commande doit contenir un produit, une quantité non nulle et un prix unitaire ")
       if len(erreur) != 0:
           # prend chaque element de la liste et kay7ot binathom had le separateur
           raise UserError("\n".join(erreur))
       self.write(
           {
               "state":"valide"
           }
       )
       # on appel la sequence ici
       self.numero_bon_commande=self.env['ir.sequence'].next_by_code('module_achat.bon_commande')
       ligne_vals=[]
       # ajouter des bon de receptions
       for rec in self.ligne_bon_commandes_ids:
           # le premier 0 ===> ajouter le bon de commande
           # le deuxième 0 ==> l'id de l'enregistrement
           ligne_vals.append((0, 0, {
               'ref_produit': rec.ref_prod,
               'produit_id': rec.produit_id.id,
               'quantite_demandee': rec.quantite
           }))
       self.env['module_achat.bon_reception'].create({
           'date_reception': date.today(),
           'bon_commande_id': self.id,
           'fournisseur': self.ref_fournisseur.id,
           'projet_id': self.code_projet.id,
           'ligne_bon_receptions_ids': ligne_vals,
       })
    # le calcul du total ht et total ttc
    @api.depends("ligne_bon_commandes_ids")
    def _compute_total(self):
        self.total_ht =sum(self.ligne_bon_commandes_ids.mapped("prix_ht"))

        self.total_ttc= self.total_ht*0.2 +self.total_ht


    # action pour ouvrir le bon de reception
    def action_open_receptions(self):
        self.ensure_one()
        action=self.env.ref("Module_Achat.action_view_module_achat_bon_reception",raise_if_not_found=False).read()[0]

        action['domain']=[('bon_commande_id', '=', self.id)]
        # le type de vue affiché dépend de la politique de réception choisie
        if self.politique_reception == 'sans_reliquat':
            # on force l'action a afficher une vue précise
            # ID pour récuperer l'id de cette vue dans la base de données Odoo
            # external id : l'id de la vue dans les fichier xml
            # 'form' type de formulaire a afficher
           action['views']=[(self.env.ref('Module_Achat.view_form_module_achat_bon_reception').id, 'form')]

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

    @api.depends("prix_unitaire")
    def _compute_total(self):
        for rec in self:
            rec.prix_ht=rec.prix_unitaire*rec.quantite




