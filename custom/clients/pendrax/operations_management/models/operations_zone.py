from odoo import models, fields, api
from odoo.exceptions import ValidationError

class OperationsZone(models.Model):
    _name = "operation.zone"
    _description = "Zone"
    name = fields.Char(string='Name',
                       required=True,
                       index=True)
    description = fields.Text('Description')
    no_of_guards = fields.Integer('No. of Guards', compute='compute_no_of_guards', store=True)

    @api.multi
    def compute_no_of_guards(self):
        self.ensure_one()
        assignment_obj = self.env['guards.assignment.line']
        self.no_of_guards  = assignment_obj.search_count([('zone_id', '=', self.id), ('status', '=', 'active')])

    @api.multi
    def copy(self):
        """ stop users from making copies
        """
        raise ValidationError('Zones does not support duplication!')

    @api.multi
    def unlink(self):
        for zone in self:
            if zone.no_of_guards>0:
                raise ValidationError(
                    'Cannot delete Zone which has Guards deployments'
                    'state.')
        return super(OperationsZone, self).unlink()