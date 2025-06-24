from odoo import models , fields,api
from datetime import date

from odoo.exceptions import  UserError


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
    ], string="Contrôle réception",required=True)
    projet_id=fields.Many2one("project.project",string="projet")
    state=fields.Selection([
        ('brouillon','Brouillon'),
        ('recu','reçu')
    ],default='brouillon')

    location_id = fields.Many2one('stock.location', string="Emplacement",required=True)
    ligne_bon_receptions_ids=fields.One2many("module_achat.ligne_bon_reception","bon_reception_id")
    ligne_stock_ids=fields.One2many("module_achat.ligne_stock","bon_reception_id")
    count_ligne_stock=fields.Integer(compute="_compute_count_ligne_stock")
    has_reliquat=fields.Boolean(default=False)

    def valider_bon_reception(self):
        erreur=[]
        qte_recue=self.ligne_bon_receptions_ids.mapped('quantite_recue')
        if sum(qte_recue)==0:
            erreur.append("Veuillez saisir le reste au moin d'un produit")
        for rec in self.ligne_bon_receptions_ids:
            if rec.quantite_recue < 0:
                erreur.append("la quantité recu doit être positive")
            if rec.reste < 0:
                erreur.append("la quantité recu doit être inférieure ou égale a la quantité demandé")

        if len(erreur)!=0:
            # le "\n" est un séparateur entre chaque deux elements par traja3hom une liste
            # la concaténation en rendent le caractère comme un séparateur
            raise UserError("\n".join(erreur))

        self.has_reliquat = True

        self.write({
            'state': 'recu'
        })
        type_mouvement = self.type_operation.id,
        location = self.location_id.id
        for rec in self.ligne_bon_receptions_ids:
            if rec.quantite_recue>0:
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
        for rec in self.ligne_bon_receptions_ids:
            if rec.reste > 0:
                self.has_reliquat = True
                return


    def creer_reliquat(self):
        self.has_reliquat = False
        action = self.env.ref("Module_Achat.action_view_module_achat_bon_reception", raise_if_not_found=False).read()[0]
        action['domain'] = [('bon_commande_id', '=', self.bon_commande_id.id)]
        list=[]
        for rec in self.ligne_bon_receptions_ids:
            # le premier 0 ===> ajouter le deuxième 0
            # le deuxième 0 ==> l'id de l'enregistrement
            if rec.reste > 0:
                list.append((0, 0, {
                    'ref_produit': rec.ref_produit,
                    'produit_id': rec.produit_id.id,
                    'quantite_demandee': rec.reste
                }
                             ))
        type_operation = self.env['stock.picking.type'].search([('name', '=', 'Réceptions')]).id
        self.env['module_achat.bon_reception'].create({
            'date_reception': date.today(),
            'bon_commande_id': self.bon_commande_id.id,
            'fournisseur': self.fournisseur.id,
            'type_operation': type_operation,
            'projet_id': self.projet_id.id,
            "location_id":self.location_id.id,
            "controle_reception":self.controle_reception,
            'ligne_bon_receptions_ids': list,
        })
        return action

    @api.depends("ligne_stock_ids")
    def _compute_count_ligne_stock(self):


       self.count_ligne_stock=len(self.bon_commande_id.bon_reception_ids.mapped("ligne_stock_ids"))
       # parcours chaque bon_reception dans la liste récupère toute les ligne de stock et les fusionnee en un seule record set
       print(self.bon_commande_id.bon_reception_ids.ligne_stock_ids)


    def action_open_stock(self):
        self.ensure_one()
        action=self.env.ref("Module_Achat.action_view_ligne_stock",raise_if_not_found=False).read()[0]
        liste_bon_reception=self.bon_commande_id.bon_reception_ids.mapped("id")
        action['domain'] = [('bon_reception_id', 'in', liste_bon_reception)]

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



