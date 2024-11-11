#validate data
from marshmallow import Schema, fields, ValidationError, validates_schema, validate
from marshmallow.validate import Length
from datetime import datetime

class org_schema(Schema):
    'validates organization data'
    name = fields.Str(required=True, validate=Length(min=3, max=100))
    email = fields.Email(required=True)
    totalemployees = fields.Integer(required=True)
    address = fields.Str(required=True, validate=Length(min=5, max=255))
    departments = fields.List(fields.Str(validate=Length(min=2, max=100)), required=False, validate=Length(min=1))
    billing_info = fields.Dict(keys=fields.Str(), values=fields.Str(), required=False)

class auth_schema(Schema):
    '''validates auth schema'''
    role = fields.Str(required=False, validate= lambda x : x in ['admin', 'employee'])
    first_name = fields.Str(required=False, validate=Length(min=2, max=50))
    last_name = fields.Str(required=False, validate=Length(min=2, max=50))
    email = fields.Email(required=False)
    #contact = fields.Str(required=False, validate=Length(min=10, max=15))
    #gender = fields.Str(required=False)
    status = fields.Str(required=False, validate= lambda x : x in ['active', 'leave', 'inactive'])
    department = fields.Str(required=False, validate= lambda x : x in ['ACCOUNTS', 'IT', 'HR'])
    job_title = fields.Str(required=False, validate= lambda x : x in ['hr', 'developer', 'accountant'])
    #nationalId = fields.Int(required=False, validate=Length(max=20))
    joined = fields.Date(required=False)
    password = fields.Str(required=False, validate=Length(min=6, max=16))
    
    
    def __init__(self, activity):
        '''defines the class activity attribute'''
        self.activity = activity
        super().__init__()

    #check specific fields
    @validates_schema
    def validate_role_specific_fields(self, data, **kwargs):
        '''validate fields according to roles and activity'''
        if self.activity == 'login':
            if not all(field for field in data for field in ['password', 'email']):
                raise ValidationError('password/email missing')
        elif self.activity == 'register':
            if not all(field for field in data for field in ['first_name', 'last_name', 'role', 'job_title', 'department']):
                raise ValidationError('first/last name(s) missing')
        #verify email when getting reset code
        elif self.activity == 'get_reset_code':
            if not all(field for field in data for field in ['email']):
                raise ValidationError('Invalid email')
        elif self.activity == 'create_new_password':
            if not all(field for field in data for field in ['password']):
                raise ValidationError('Invalid password format')
        elif self.activity == 'validate_role':
            if not all(field for field in data for field in ['role']):
                raise ValidationError('Invalid role')

class task_schema(Schema):
    '''validates tasks'''
    taskName = fields.Str(required=False, validate=Length(min=5, max=255))
    description = fields.Str(required=False, validate=Length(min=10, max=500))
    #team = fields.List(fields.Str(), required=False, validate=validate.Length(min=1))
    started = fields.DateTime(required=False)
    toEnd = fields.Date(required=False, validate= lambda x : x >= datetime.now().date())
    priority = fields.Str(required=False, validate= validate.OneOf(['high', 'medium', 'low']))
    newStatus = fields.Str(required=False, validate=validate.OneOf(['pending', 'completed']))
    taskId = fields.Str(required=False, validate=Length(max=36, min=36))
    employeeId = fields.Str(required=False, validate=Length(max=36, min=36))

    def __init__(self, activity: str, role='employee'):
        self.activity = activity
        self.role = role
        super().__init__()
    
    @validates_schema
    def validate_fields(self, data, **kwargs):
        '''validate fields based on activity'''
        if self.activity == 'add_new_task':
            if not all(field for field in data for field in ['taskName', 'description', 'started', 'toEnd', 'priority']):
                raise ValidationError('Missing input')
        if self.role == 'admin' and self.activity == 'add_new_task':
            if not all(field for field in data for field in ['employeeId']):
                raise ValidationError('Incorrect payload')
        if self.activity == 'change_status':
            if not all(field for field in data for field in ['newStatus', 'taskId']):
                raise ValidationError('Incorrect payload')
    


