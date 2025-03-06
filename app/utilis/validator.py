from marshmallow import Schema, fields, validate, ValidationError

class UserRegistrationSchema(Schema):
    username = fields.Str(
        required=True, 
        validate=[
            validate.Length(min=3, max=50, 
            error='Username must be between 3 and 50 characters')
        ]
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, error='Password must be at least 8 characters'),
            validate.Regexp(
                r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
                error='Password must include letters, numbers, and special characters'
            )
        ]
    )

def validate_user_registration(data):
    schema = UserRegistrationSchema()
    try:
        schema.load(data)
    except ValidationError as err:
        return err.messages
    return None
    