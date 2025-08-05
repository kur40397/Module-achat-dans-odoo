from odoo import models , fields,api
from datetime import date

from odoo.api import readonly
from odoo.exceptions import  UserError


class bonReception(models.Model):
    _name = "module_achat.bon_reception"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    ref_bon_reception=fields.Char(string="reference bon reception",readonly=True)
    date_reception=fields.Date(string="Date reception",tracking=True)
    bon_commande_id=fields.Many2one("module_achat.bon_commande",string="bon de commande",tracking=True)
    fournisseur=fields.Many2one("res.partner",string="Fournisseur",tracking=True)

    controle_reception=fields.Selection([
        ('conforme', 'Conforme'),
        ('non_conforme', 'Non conforme'),
        ('partiel', 'Partiellement conforme'),
    ], string="Contrôle réception",required=True,default="conforme",tracking=True)
    projet_id=fields.Many2one("project.project",string="projet",tracking=True)
    state=fields.Selection([
        ('brouillon','Brouillon'),
        ('recu','reçu')
    ],default='brouillon',tracking=True)

    location_id = fields.Many2one('stock.location', string="Emplacement",tracking=True)
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


        self.write({
            'state': 'recu'
        })
        reste=sum(self.ligne_bon_receptions_ids.mapped('reste'))
        if self.bon_commande_id.politique_reception=='reliquat' and reste == 0 :
            self.write({
                'has_reliquat':True
            })

        self.ref_bon_reception=self.env['ir.sequence'].next_by_code('module_achat.bon_reception')

        location = self.location_id.id
        for rec in self.ligne_bon_receptions_ids:
            if rec.quantite_recue>0:
                self.env['module_achat.ligne_stock'].create(
                  {
                    "ref_ligne_Stock":self.env['ir.sequence'].next_by_code('module_achat.ligne_stock'),
                    'produit_id': rec.produit_id.id,
                    'bon_reception_id': self.id,
                    'quantite': rec.quantite_recue,
                    'mouvement': 'entree',
                    'location_id': location,
                    'date': date.today(),
                    'state':'valide',
                    'origin':'reception'
                  }
                )

    def creer_un_reliquat(self):
        pass

    @api.depends("ligne_stock_ids")
    def _compute_count_ligne_stock(self):


       self.count_ligne_stock=len(self.bon_commande_id.bon_reception_ids.mapped("ligne_stock_ids"))
       # parcours chaque bon_reception dans la liste récupère toute les ligne de stock et les fusionnee en un seule record set


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



