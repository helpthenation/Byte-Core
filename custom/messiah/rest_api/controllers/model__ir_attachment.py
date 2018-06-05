# -*- coding: utf-8 -*-
from main import *
from .commons import *
import copy;

_logger = logging.getLogger(__name__)


# List of REST resources in current file:
#   (url prefix)               (method)     (action)
# /api/ir.attachment                GET     - Read all (with optional filters, offset, limit, order)
# /api/ir.attachment/<id>           GET     - Read one
# /api/ir.attachment                POST    - Create one
# /api/ir.attachment/<id>           PUT     - Update one
# /api/ir.attachment/<id>           DELETE  - Delete one
# /api/ir.attachment/<id>/<method>  PUT     - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/ir.attachment  GET  - Read all (with optional filters, offset, limit, order)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional filters (Odoo domain), offset, limit, order)
#           {                                       # editable
#               "filters": "[('some_field_1', '=', some_value_1), ('some_field_2', '!=', some_value_2), ...]",
#               "offset":  XXX,
#               "limit":   XXX,
#               "order":   "list_of_fields"  # default 'name asc'
#           }
# OUT data:
OUT__ir_attachment__read_all__SUCCESS_CODE = 200       # editable
#   JSON:
#       {
#           "count":   XXX,     # number of returned records
#           "results": [
OUT__ir_attachment__read_all__JSON = FILE_LIST_FIELDS
#           ]
#       }

# /api/ir.attachment/<id>  GET  - Read one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional parameter 'search_field' for search object not by 'id' field)
#           {"search_field": "some_field_name"}     # editable
# OUT data:
OUT__ir_attachment__read_one__SUCCESS_CODE = 200       # editable
OUT__ir_attachment__read_one__JSON = (
    'id',
    'name',
    'file_size',
    'file_type',
    'res_model',
    'res_id',
    'datas_fname',
    'sequence',
    'type',
    'checksum',
    'datas',
)

# /api/ir.attachment  POST  - Create one
# IN data:
#   HEADERS:
#       'access_token'
#   DEFAULTS:
#       (optional default values of fields)
DEFAULTS__ir_attachment__create_one__JSON = {          # editable
}
#   JSON:
#       (fields and its values of created object;
#        don't forget about model's mandatory fields!)
#           ...                                     # editable
# OUT data:
OUT__ir_attachment__create_one__SUCCESS_CODE = 200     # editable
OUT__ir_attachment__create_one__JSON = (               # editable
    'id',
)

# /api/ir.attachment/<id>  PUT  - Update one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (fields and new values of updated object)   # editable
#           ...
# OUT data:
OUT__ir_attachment__update_one__SUCCESS_CODE = 200     # editable

# /api/ir.attachment/<id>  DELETE  - Delete one
# IN data:
#   HEADERS:
#       'access_token'
# OUT data:
OUT__ir_attachment__delete_one__SUCCESS_CODE = 200     # editable

# /api/ir.attachment/<id>/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__ir_attachment__call_method__SUCCESS_CODE = 200    # editable


# HTTP controller of REST resources:

class ControllerREST(http.Controller):
    
    # Read all (with optional filters, offset, limit, order):
    @http.route('/api/ir.attachment', methods=['GET'], type='http', auth='none')
    @check_permissions
    def api__ir_attachment__GET(self, filters=None, offset=None, order=None, limit=None):
        return wrap__resource__read_all(
            modelname = 'ir.attachment',
            default_domain = [],
            success_code = OUT__ir_attachment__read_all__SUCCESS_CODE,
            OUT_fields = OUT__ir_attachment__read_all__JSON
        )
    
    # Read one:
    @http.route('/api/ir.attachment/<id>', methods=['GET'], type='http', auth='none')
    @check_permissions
    def api__ir_attachment__id_GET(self, id):
        return wrap__resource__read_one(
            modelname = 'ir.attachment',
            id = id,
            success_code = OUT__ir_attachment__read_one__SUCCESS_CODE,
            OUT_fields = OUT__ir_attachment__read_one__JSON
        )
    
    # Create one:
    @http.route('/api/ir.attachment', methods=['POST'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__ir_attachment__POST(self):
        return wrap__resource__create_one(
            modelname = 'ir.attachment',
            default_vals = DEFAULTS__ir_attachment__create_one__JSON,
            success_code = OUT__ir_attachment__create_one__SUCCESS_CODE,
            OUT_fields = OUT__ir_attachment__create_one__JSON
        )
    
    # Update one:
    @http.route('/api/ir.attachment/<id>', methods=['PUT'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__ir_attachment__id_PUT(self, id):
        return wrap__resource__update_one(
            modelname = 'ir.attachment',
            id = id,
            success_code = OUT__ir_attachment__update_one__SUCCESS_CODE
        )
    
    # Delete one:
    @http.route('/api/ir.attachment/<id>', methods=['DELETE'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__ir_attachment__id_DELETE(self, id):
        return wrap__resource__delete_one(
            modelname = 'ir.attachment',
            id = id,
            success_code = OUT__ir_attachment__delete_one__SUCCESS_CODE
        )
    
    # Call method (with optional parameters):
    @http.route('/api/ir.attachment/<id>/<method>', methods=['PUT'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__ir_attachment__id__method_PUT(self, id, method):
        return wrap__resource__call_method(
            modelname = 'ir.attachment',
            id = id,
            method = method,
            success_code = OUT__ir_attachment__call_method__SUCCESS_CODE
        )
    
