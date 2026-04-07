from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "A type for property"
    _order = "sequence,name"
    
    name = fields.Char(required=True)
    sequence = fields.Integer()
    
    # this means that onc property type have many properties
    property_ids = fields.One2many('estate.property', 'property_type_id', string="Properties")
    
    offer_ids = fields.One2many(
        'estate.property.offer',
        'property_type_id',
        string="Offers"
    )

    offer_count = fields.Integer(
        compute='_compute_offer_count',
        string="Offer Count"
    )
    
    # DATA CONSTRAINT
    _check_name = models.Constraint('UNIQUE(name)', 'A property type name must be unique')


    # COMPUTATIONAL FIELDS
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)