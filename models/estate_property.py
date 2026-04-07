from odoo import models, fields, api
from odoo.exceptions import UserError,ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero
from datetime import timedelta

class EstateProperty(models.Model):
    _name = "estate.property" # this will be used as a table name in DB
    _description = "This table stored owned assess"
    _order = "id desc"
    
    name = fields.Char(required=True, index=True, string="Title") # using index=True created a DB index called "estate_property__name_index"
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(default=lambda self: fields.Date.today() + timedelta(days=90), string="Available From", copy=False)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False, default=0)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Boolean()
    garage = fields.Integer()
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')]
    ) # this is stored as a VARCHAR() in DB
    
    active = fields.Boolean(default=False) # this is a reserved field, if false then record is invisible in most search and listing
    
    state = fields.Selection(
        selection=[('new', 'New'), ('offer', 'Offer'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('cancel', 'Cancel')],
        required=True,
        copy=False,
        default="new",
        string="Status"
    )
    
    property_type_id = fields.Many2one('estate.property.type', string="Property Type")
    user_id = fields.Many2one('res.users', string="Salesman", default=lambda self: self.env.user) # odoo will find the current user with magic of ORM 'self.env.user' will be translated as 'self.env.user.id'
    partner_id = fields.Many2one('res.partner', string="Buyer", copy=False)
    tag_ids = fields.Many2many('estate.property.tag')
    offer_ids = fields.One2many('estate.property.offer', 'property_id')
    
    total_area = fields.Float(compute="_compute_total_area")
    
    best_price = fields.Float(compute="_compute_best_price", string="Best Offer")
    
    
    # DATA CONSTRAINT
    _check_expected_price = models.Constraint('CHECK(expected_price > 0)', 'A property expected price must be strictly positive')
    _check_selling_price = models.Constraint('CHECK(selling_price >= 0)', 'A property selling price must be positive')
    
    @api.constrains("selling_price", "expected_price")
    def _check_selling_price_percent(self):
        for record in self:
            # skipping if the selling price is still zerogit remote -v
            if float_is_zero(self.selling_price, precision_rounding=0.01):
                continue
            
            min_price = record.expected_price * 0.9
            
            if float_compare(self.selling_price, min_price, precision_rounding=0.01) < 0:
                raise ValidationError('Selling price cannot be lower than 90% of expected price')
            
    # COMPUTED FIELDS METHODS
    @api.depends("living_area", "garden_area") # to specify that this method is depended on living_area and garden_area field
    def _compute_total_area(self):
        for record in self: # this is done in a loop since some record from self might have more than one, so we loop for best practice
            record.total_area = record.living_area + record.garden_area
        
    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped("price") # mapped is used to pull every `price` record from offer
            record.best_price = max(prices) if prices else 0.0 # added error prevention logic in case if there's no offer record
            
    # ONCHANGES METHODS
    # this is for defining that this onchange method will depend on the changes of field 'garden'
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None
    
    # OBJECT TYPE
    def action_sold_property(self):
        for record in self:
            if record.state == 'cancel':
                raise UserError('Canceled property cannot be sold') # this is used to raise an error, kind of a logical validation
            if record.state != 'cancel':
                record.state = 'sold'
        return True
    
    def action_cancel_property(self):
        for record in self:
            if record.state == 'sold':
                raise UserError('Sold property cannot be canceled')
            if record.state != 'sold':
                record.state = 'cancel'
        return True
    
    # INHERITANCES
    def unlink(self):
        for record in self:
            if record.state not in ('new', 'cancel'):
                raise UserError("You cannot delete a property unless it is New or Cancel")
            record.offer_ids.unlink()
        return super().unlink()