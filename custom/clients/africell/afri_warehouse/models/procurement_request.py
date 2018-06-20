from odoo import models, fields, api
import datetime


class ProcurementRequest(models.Model):
    _name = 'warehouse.procurement.request'
    _rec_name = 'reference'
    reference = fields.Char(string='Reference',
                            default=lambda obj: obj.env['ir.sequence'].next_by_code('warehouse.procurement.request'),
                            index=True,
                            readonly=True)
    date = fields.Date(string='Date',
                       default=datetime.date.today(),
                       readonly=True)
    warehouse_request_id = fields.Many2one(comodel_name='warehouse.request',
                                           string='Warehouse Request')
    product_request_lines = fields.One2many(comodel_name='warehouse.procurement.request.line',
                                            inverse_name='procurement_request_id',
                                            required=True)

    @api.model
    def create(self, vals):
        res = super(ProcurementRequest, self).create(vals)
        res.warehouse_request_id.procurement_request_id = res
        return res
