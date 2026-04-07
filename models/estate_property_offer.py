from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "An offer for property"
    _order = "price desc"
    
    price = fields.Float()
    status = fields.Selection(copy=False, selection=[('accepted', 'Accepted'), ('refused', 'Refused')])
    partner_id = fields.Many2one('res.partner', required=True, string="Partner")
    property_id = fields.Many2one('estate.property', required=True)
    
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_deadline", inverse="_inverse_deadline")
    
    property_type_id = fields.Many2one(
        'estate.property.type',
        related='property_id.property_type_id',
        store=True
    )
    
    # DATA CONSTRAINT
    _check_price = models.Constraint('CHECK(price > 0)', 'An offer price must be strictly positive')
    
    @api.depends("validity", "create_date")
    def _compute_deadline(self):
        for record in self:
            # fields.Datetime.now() is a fallback to prevent error in case that there is no create date record
            create_date = record.create_date or fields.Datetime.now()
            # timedalta(days=record.validity) is for transforming days in Interger form to Date form 
            record.date_deadline = create_date.date() + timedelta(days=record.validity)
    
    def _inverse_deadline(self):
        for record in self:
            create_date = record.create_date or fields.Datetime.now()
            # convert deadline back to validity (number of days from create_date)
            record.validity = (record.date_deadline - create_date.date()).days
            
    def action_accept_offer(self):
        for record in self:
            property = record.property_id
            
            # this is for checking whether this property has already got an accepted offer
            accepted_offer = property.offer_ids.filtered(lambda o: o.status == 'accepted') # a shorten function to check if the status if accepted or nah
            if accepted_offer:
                raise UserError("Only one offer can be accepted per property")
            
            # this is the changing part
            record.status = 'accepted'
            property.partner_id = record.partner_id
            property.selling_price = record.price
            
        return True
    
    def action_refuse_offer(self):
        for record in self:
            record.status = 'refused'
        return True
    