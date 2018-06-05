# -*- coding: utf-8 -*-
from main import *
from .commons import *
import copy;

_logger = logging.getLogger(__name__)


# List of REST resources in current file:
#   (url prefix)               (method)     (action)
# /api/judiciary.adjournment                GET     - Read all (with optional filters, offset, limit, order)
# /api/judiciary.adjournment/<id>           GET     - Read one
# /api/judiciary.adjournment                POST    - Create one
# /api/judiciary.adjournment/<id>           PUT     - Update one
# /api/judiciary.adjournment/<id>           DELETE  - Delete one
# /api/judiciary.adjournment/<id>/<method>  PUT     - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/judiciary.adjournment  GET  - Read all (with optional filters, offset, limit, order)
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
OUT__judiciary_adjournment__read_all__SUCCESS_CODE = 200       # editable
#   JSON:
#       {
#           "count":   XXX,     # number of returned records
#           "results": [
OUT__judiciary_adjournment__read_all__JSON = MODEL_ADJOURNMENT_FIELDS
#           ]
#       }

# /api/judiciary.adjournment/<id>  GET  - Read one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional parameter 'search_field' for search object not by 'id' field)
#           {"search_field": "some_field_name"}     # editable
# OUT data:
OUT__judiciary_adjournment__read_one__SUCCESS_CODE = 200       # editable
OUT__judiciary_adjournment__read_one__JSON = OUT__judiciary_adjournment__read_all__JSON

# /api/judiciary.adjournment  POST  - Create one
# IN data:
#   HEADERS:
#       'access_token'
#   DEFAULTS:
#       (optional default values of fields)
DEFAULTS__judiciary_adjournment__create_one__JSON = {          # editable
            "data_type": "adjournment",
}
#   JSON:
#       (fields and its values of created object;
#        don't forget about model's mandatory fields!)
#           ...                                     # editable
# OUT data:
OUT__judiciary_adjournment__create_one__SUCCESS_CODE = 200     # editable
OUT__judiciary_adjournment__create_one__JSON = (               # editable
    'id',
)

OUT__judiciary_adjournment__update_one__JSON = (               # editable
    'id',
    'last_hash',
)

# /api/judiciary.adjournment/<id>  PUT  - Update one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (fields and new values of updated object)   # editable
#           ...
# OUT data:
OUT__judiciary_adjournment__update_one__SUCCESS_CODE = 200     # editable

# /api/judiciary.adjournment/<id>  DELETE  - Delete one
# IN data:
#   HEADERS:
#       'access_token'
# OUT data:
OUT__judiciary_adjournment__delete_one__SUCCESS_CODE = 200     # editable

# /api/judiciary.adjournment/<id>/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__judiciary_adjournment__call_method__SUCCESS_CODE = 200    # editable


# HTTP controller of REST resources:

class ControllerREST(http.Controller):
    
    # Read all (with optional filters, offset, limit, order):
    @http.route('/api/judiciary.adjournment', methods=['GET'], type='http', auth='none')
    @check_permissions
    def api__judiciary_adjournment__GET(self, filters=None, offset=None, order=None, limit=None):
        return wrap__resource__read_all(
            modelname = 'judiciary.adjournment',
            default_domain = [],
            success_code = OUT__judiciary_adjournment__read_all__SUCCESS_CODE,
            OUT_fields = OUT__judiciary_adjournment__read_all__JSON
        )
    
    # Read one:
    @http.route('/api/judiciary.adjournment/<id>', methods=['GET'], type='http', auth='none')
    @check_permissions
    def api__judiciary_adjournment__id_GET(self, id):
        return wrap__resource__read_one(
            modelname = 'judiciary.adjournment',
            id = id,
            success_code = OUT__judiciary_adjournment__read_one__SUCCESS_CODE,
            OUT_fields = OUT__judiciary_adjournment__read_one__JSON
        )
    
    # Create one:
    @http.route('/api/judiciary.adjournment', methods=['POST'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__judiciary_adjournment__POST(self):
        return wrap__resource__create_one(
            modelname = 'judiciary.adjournment',
            default_vals = DEFAULTS__judiciary_adjournment__create_one__JSON,
            success_code = OUT__judiciary_adjournment__create_one__SUCCESS_CODE,
            OUT_fields = OUT__judiciary_adjournment__create_one__JSON
        )
    
    # Update one:
    @http.route('/api/judiciary.adjournment/<id>', methods=['PUT'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__judiciary_adjournment__id_PUT(self, id):
        return wrap__resource__update_one(
            modelname = 'judiciary.adjournment',
            id = id,
            success_code = OUT__judiciary_adjournment__update_one__SUCCESS_CODE,
            OUT_fields = OUT__judiciary_adjournment__update_one__JSON
        )
    
    # Delete one:
    @http.route('/api/judiciary.adjournment/<id>', methods=['DELETE'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__judiciary_adjournment__id_DELETE(self, id):
        return wrap__resource__delete_one(
            modelname = 'judiciary.adjournment',
            id = id,
            success_code = OUT__judiciary_adjournment__delete_one__SUCCESS_CODE
        )
    
    # Call method (with optional parameters):
    @http.route('/api/judiciary.adjournment/<id>/<method>', methods=['PUT'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__judiciary_adjournment__id__method_PUT(self, id, method):
        return wrap__resource__call_method(
            modelname = 'judiciary.adjournment',
            id = id,
            method = method,
            success_code = OUT__judiciary_adjournment__call_method__SUCCESS_CODE
        )
    
