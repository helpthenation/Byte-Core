# -*- coding: utf-8 -*-
from main import *
from .commons import *

_logger = logging.getLogger(__name__)


# List of REST resources in current file:
#   (url prefix)               (method)     (action)
# /api/judiciary.case                GET     - Read all (with optional filters, offset, limit, order)
# /api/judiciary.case/<id>           GET     - Read one
# /api/judiciary.case                POST    - Create one
# /api/judiciary.case/<id>           PUT     - Update one
# /api/judiciary.case/<id>           DELETE  - Delete one
# /api/judiciary.case/<id>/<method>  PUT     - Call method (with optional parameters)


# List of IN/OUT data (json data and HTTP-headers) for each REST resource:

# /api/judiciary.case  GET  - Read all (with optional filters, offset, limit, order)
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
OUT__judiciary_case__read_all__SUCCESS_CODE = 200       # editable
#   JSON:
#       {
#           "count":   XXX,     # number of returned records
#           "results": [
OUT__judiciary_case__read_all__JSON = (                 # editable
    'id',
    'name',
    'uuid',
    'court_type',
    'display_name',
    'date_of_crime',
    'date_of_arrest',
    'arresting_officers',
    'plaintiff_lawyers',
    'defendant_lawyers',
    'description',
    'priority',
    'state',
    'last_state_changed',
    'date_state_trial',
    'date_state_verdict',
    'date_state_sentenced',
    'date_state_appeal',
    'date_state_assign',
    'date_last_state_update',
    'doc_count',
    'plea',
    'has_plead',
    'date_create',
    'date_start',
    'date_end',
    'case_duration',
    'next_court_date',
    'bail_count',
    'ruling',
    'has_parent',
    'parent',
    'plaintiff_represented',
    'defendant_represented',
    'translation_provided',
    'detention',
    'detention_length',
    'active_case',
    'verdict',
    'verdict_text',
    'ruling_text',
    'case_judged_by',
    'jurors',
    'witnesses',
    'data_type',
    'discharged',
    'is_container',
    'is_contained',
    'child_count',
    'spurned_appeal',
    'discharged',
    'spurn_highcourt',
    'last_hash',
    '__last_update',

    # boolean fields with flag
    # 'in_progress',
    ('in_progress', BOOLEAN),

    # many2one fields
    ('defendant_id', MODEL_RES_PARTNER),
    ('court_id', MODEL_SIMPLE_FIELDS),
    ('judge_id', MODEL_SIMPLE_FIELDS),
    ('container_id', MODEL_SIMPLE_FIELDS),
    ('user_id', MODEL_SIMPLE_FIELDS),
    ('create_user_id', MODEL_SIMPLE_FIELDS),

    # many2many one2many fields
    ('category_ids', [MODEL_SIMPLE_FIELDS]),
    ('bail_ids', [MODEL_SIMPLE_FIELDS]),
    ('note_ids', [MODEL_SIMPLE_FIELDS]),
    ('adjournment_ids', [MODEL_SIMPLE_FIELDS]),
    ('attachment_ids', [FILE_LIST_FIELDS]),
    ('description_attachment_ids', [FILE_LIST_FIELDS]),
    ('verdict_attachment_ids', [FILE_LIST_FIELDS]),
    ('ruling_attachment_ids', [FILE_LIST_FIELDS]),
    ('child_ids', [MODEL_SIMPLE_FIELDS]),
)
#           ]
#       }

# /api/judiciary.case/<id>  GET  - Read one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (optional parameter 'search_field' for search object not by 'id' field)
#           {"search_field": "some_field_name"}     # editable
# OUT data:
OUT__judiciary_case__read_one__SUCCESS_CODE = 200       # editable
OUT__judiciary_case__read_one__JSON = (                 # editable
    'id',
    'name',
    'uuid',
    'court_type',
    'display_name',
    'date_of_crime',
    'date_of_arrest',
    'arresting_officers',
    'plaintiff_lawyers',
    'defendant_lawyers',
    'description',
    'priority',
    'state',
    'last_state_changed',
    'date_state_trial',
    'date_state_verdict',
    'date_state_sentenced',
    'date_state_appeal',
    'date_state_assign',
    'date_last_state_update',
    'doc_count',
    'plea',
    'has_plead',
    'date_create',
    'date_start',
    'date_end',
    'case_duration',
    'next_court_date',
    'bail_count',
    'ruling',
    'has_parent',
    'parent',
    'plaintiff_represented',
    'defendant_represented',
    'translation_provided',
    'detention',
    'detention_length',
    'active_case',
    'verdict',
    'verdict_text',
    'ruling_text',
    'case_judged_by',
    'jurors',
    'witnesses',
    'data_type',
    'discharged',
    'is_container',
    'is_contained',
    'child_count',
    'spurned_appeal',
    'discharged',
    'spurn_highcourt',
    'last_hash',

    # boolean fields with flag
    # 'in_progress',
    ('in_progress', BOOLEAN),

    # many2one fields
    ('defendant_id', MODEL_RES_PARTNER),
    ('court_id', ('id', 'name', 'type', 'district')),
    ('judge_id', ('id', 'name', 'official_type')),
    ('user_id', MODEL_SIMPLE_FIELDS),
    ('create_user_id', MODEL_SIMPLE_FIELDS),
    ('container_id', OUT__judiciary_case__read_all__JSON),


    # many2many one2many fields
    ('category_ids', [MODEL_SIMPLE_FIELDS]),
    ('bail_ids', [MODEL_BAIL_DETAIL]),
    ('note_ids', [MODEL_CASE_NOTE]),
    ('adjournment_ids', [MODEL_ADJOURNMENT_FIELDS]),
    ('attachment_ids', [FILE_LIST_FIELDS]),
    ('description_attachment_ids', [FILE_LIST_FIELDS]),
    ('verdict_attachment_ids', [FILE_LIST_FIELDS]),
    ('ruling_attachment_ids', [FILE_LIST_FIELDS]),
    ('child_ids', [OUT__judiciary_case__read_all__JSON]),

)

# /api/judiciary.case  POST  - Create one
# IN data:
#   HEADERS:
#       'access_token'
#   DEFAULTS:
#       (optional default values of fields)
DEFAULTS__judiciary_case__create_one__JSON = {          # editable
            "data_type": "case",
            #"some_field_2": some_value_2,
            #...
}
#   JSON:
#       (fields and its values of created object;
#        don't forget about model's mandatory fields!)
#           ...                                     # editable
# OUT data:
OUT__judiciary_case__create_one__SUCCESS_CODE = 200     # editable
OUT__judiciary_case__create_one__JSON = (               # editable
    'id',
)

OUT__judiciary_case__update_one__JSON = (               # editable
    'id',
    'last_hash',
)

# /api/judiciary.case/<id>  PUT  - Update one
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (fields and new values of updated object)   # editable
#           ...
# OUT data:
OUT__judiciary_case__update_one__SUCCESS_CODE = 200     # editable

# /api/judiciary.case/<id>  DELETE  - Delete one
# IN data:
#   HEADERS:
#       'access_token'
# OUT data:
OUT__judiciary_case__delete_one__SUCCESS_CODE = 200     # editable

# /api/judiciary.case/<id>/<method>  PUT  - Call method (with optional parameters)
# IN data:
#   HEADERS:
#       'access_token'
#   JSON:
#       (named parameters of method)                # editable
#           ...
# OUT data:
OUT__judiciary_case__call_method__SUCCESS_CODE = 200    # editable


# HTTP controller of REST resources:

class ControllerREST(http.Controller):
    
    # Read all (with optional filters, offset, limit, order):
    @http.route('/api/judiciary.case', methods=['GET'], type='http', auth='none')
    @check_permissions
    def api__judiciary_case__GET(self, filters=None, offset=None, order=None, limit=None, hash=None):
        return wrap__resource__read_all(
            modelname = 'judiciary.case',
            default_domain = [],
            success_code = OUT__judiciary_case__read_all__SUCCESS_CODE,
            OUT_fields = OUT__judiciary_case__read_one__JSON
        )

    # Read one:
    @http.route('/api/judiciary.case/<id>', methods=['GET'], type='http', auth='none')
    @check_permissions
    def api__judiciary_case__id_GET(self, id):
        return wrap__resource__read_one(
            modelname = 'judiciary.case',
            id = id,
            success_code = OUT__judiciary_case__read_one__SUCCESS_CODE,
            OUT_fields = OUT__judiciary_case__read_one__JSON
        )
    
    # Create one:
    @http.route('/api/judiciary.case', methods=['POST'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__judiciary_case__POST(self):
        return wrap__resource__create_one(
            modelname = 'judiciary.case',
            default_vals = DEFAULTS__judiciary_case__create_one__JSON,
            success_code = OUT__judiciary_case__create_one__SUCCESS_CODE,
            OUT_fields = OUT__judiciary_case__create_one__JSON
        )
    
    # Update one:
    @http.route('/api/judiciary.case/<id>', methods=['PUT'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__judiciary_case__id_PUT(self, id):
        return wrap__resource__update_one(
            modelname = 'judiciary.case',
            id = id,
            success_code = OUT__judiciary_case__update_one__SUCCESS_CODE,
            OUT_fields=OUT__judiciary_case__update_one__JSON
        )
    
    # Delete one:
    @http.route('/api/judiciary.case/<id>', methods=['DELETE'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__judiciary_case__id_DELETE(self, id):
        return wrap__resource__delete_one(
            modelname = 'judiciary.case',
            id = id,
            success_code = OUT__judiciary_case__delete_one__SUCCESS_CODE
        )
    
    # Call method (with optional parameters):
    @http.route('/api/judiciary.case/<id>/<method>', methods=['PUT'], type='http', auth='none', csrf=False)
    @check_permissions
    def api__judiciary_case__id__method_PUT(self, id, method):
        return wrap__resource__call_method(
            modelname = 'judiciary.case',
            id = id,
            method = method,
            success_code = OUT__judiciary_case__call_method__SUCCESS_CODE
        )
