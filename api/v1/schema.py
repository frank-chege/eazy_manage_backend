#validate data
from marshmallow import Schema, fields, ValidationError, validates_schema, validate
from marshmallow.validate import Length
from datetime import datetime

class auth_schema(Schema):
    '''validates auth schema'''
    role = fields.Str(required=False, validate= lambda x : x in ['admin', 'employee'])
    firstName = fields.Str(required=False, validate=Length(min=2, max=50))
    lastName = fields.Str(required=False, validate=Length(min=2, max=50))
    email = fields.Email(required=True)
    #contact = fields.Str(required=False, validate=Length(min=10, max=15))
    #gender = fields.Str(required=False)
    status = fields.Str(required=False, validate= lambda x : x in ['active', 'leave', 'inactive'])
    dep = fields.Str(required=False, validate= lambda x : x in ['ACCOUNTS', 'IT', 'HR'])
    jobTitle = fields.Str(required=False, validate= lambda x : x in ['hr', 'developer', 'accountant'])
    #nationalId = fields.Int(required=False, validate=Length(max=20))
    joined = fields.Date(required=False)
    password = fields.Str(required=False, validate=Length(min=6, max=16))
    auth_code = fields.Int(required=False, validate=Length(min=6, max=6))
    reset_action = fields.Str(required=False, validate= lambda x : x in ['get_reset_code', 'reset_pwd'])
    
    
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
            if not all(field for field in data for field in ['firstName', 'lastName', 'role', 'jobTitle', 'department']):
                raise ValidationError('first/last name(s) missing')
        elif self.activity == 'get_reset_code':
            if not all(field for field in data for field in ['email']):
                raise ValidationError('Invalid email')
        elif self.activity == 'reset_action':
            if not all(field for field in data for field in ['reset_action']):
                raise ValidationError('Invalid reset action')
        elif self.activity == 'reset_pwd':
            if not all(field for field in data for field in ['auth_code', 'email', 'password']):
                raise ValidationError('Invalid code')
        elif self.activity == 'auth_status':
            if not all(field for field in data for field in ['role']):
                raise ValidationError('Invalid role')

class task_schema(Schema):
    '''validates tasks'''
    task_name = fields.Str(required=True, validate=Length(min=5, max=255))
    description = fields.Str(required=True, validate=Length(min=10, max=500))
    team = fields.List(fields.Str(), required=True, validate=validate.Length(min=1))
    started = fields.DateTime(required=True, validate= lambda x : x >= datetime.now())
    to_end = fields.DateTime(required=True, validate= lambda x : x >= datetime.now())
    priority = fields.Str(required=True, validate= validate.OneOf(['high', 'medium', 'low']))
    


