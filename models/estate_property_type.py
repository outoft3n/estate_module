from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "A type for property"
    
    name = fields.Char(required=True)
    
    # this means that onc property type have many properties
    property_ids = fields.One2many('estate.property', 'property_type_id', string="Properties")
    
    # DATA CONSTRAINT
    _check_name = models.Constraint('UNIQUE(name)', 'A property type name must be unique')
