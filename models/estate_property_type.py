from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "A type for property"
    
    name = fields.Char(required=True)
    
    # DATA CONSTRAINT
    _check_name = models.Constraint('UNIQUE(name)', 'A property type name must be unique')