CASE_LIST_FIELDS = ('id', 'name', 'state')

FILE_LIST_FIELDS = ('id', 'name', 'file_size', 'file_type', 'res_model', 'res_id', 'sequence')

MODEL_SIMPLE_FIELDS = ('id', 'name')

MODEL_BAIL_DETAIL = (                 # editable
    'id',
    'name',
    'date',
    'next_hearing_date',
    'state',
    'decision',
    'note',

    # many2one fields
    ('adjournment_id', MODEL_SIMPLE_FIELDS),
    ('case_id', CASE_LIST_FIELDS),


    ('attachment_ids', [
        FILE_LIST_FIELDS
    ]),
)

MODEL_CASE_NOTE = (
    'id',
    'name',
    'summary',
    'description',
    'date_create',
    'date_edit',
    'is_public',

    # many2one fields
    ('case_id', CASE_LIST_FIELDS),


    ('attachment_ids', [
        FILE_LIST_FIELDS
    ]),
)

MODEL_ADJOURNMENT_RESULT_FIELDS = ('id', 'name', 'default_reason')


MODEL_ADJOURNMENT_FIELDS = (
    'id',
    'name',
    'is_done',
    'state',
    'note',
    'data_type',

    # many2one fields
    ('reason_id', MODEL_ADJOURNMENT_RESULT_FIELDS),
    ('case_id', CASE_LIST_FIELDS),
)

MODEL_RES_PARTNER = ('id', 'name', 'street', 'street2', 'city', 'phone', 'gender', 'birthdate', 'district',
                      'id_type', 'id_number')

MODEL_RES_USERS = ('id', 'name', 'login', 'email', 'judiciary_role')

BOOLEAN = "BOOLEAN"
