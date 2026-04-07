from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "A tag for property"
    _order = "name"
    
    name = fields.Char(required=True)
    color = fields.Integer()
    
    # DATA CONSTRAINT
    _check_name = models.Constraint('UNIQUE(name)', 'A property tag name must be unique')