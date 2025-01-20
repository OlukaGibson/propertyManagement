from .extentions import db

class Authentications(db.Model):
    __tablename__ = 'authentications'
    id = db.Column(db.Integer, primary_key=True)
    authType = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, authType):
        self.authType = authType

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), default=None)
    # authAccess = db.Column(db.Integer, db.ForeignKey('authentications.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, default=None)
    password = db.Column(db.String(80), default=None)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

class Devices(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    device_type = db.Column(db.String(100), unique=True, nullable=False)
    field1 = db.Column(db.String(100), default=None)
    field2 = db.Column(db.String(100), default=None)
    field3 = db.Column(db.String(100), default=None)
    field4 = db.Column(db.String(100), default=None)
    field5 = db.Column(db.String(100), default=None)
    field6 = db.Column(db.String(100), default=None)
    field7 = db.Column(db.String(100), default=None)
    field8 = db.Column(db.String(100), default=None)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, device_type, field1, field2, field3, field4, field5, field6, field7, field8):
        self.device_type = device_type
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3
        self.field4 = field4
        self.field5 = field5
        self.field6 = field6
        self.field7 = field7
        self.field8 = field8

class Readings(db.Model):
    __tablename__ = 'metadatavalues'
    id = db.Column(db.Integer, primary_key=True)
    deviceID = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    field1 = db.Column(db.String(100), default=None)
    field2 = db.Column(db.String(100), default=None)
    field3 = db.Column(db.String(100), default=None)
    field4 = db.Column(db.String(100), default=None)
    field5 = db.Column(db.String(100), default=None)
    field6 = db.Column(db.String(100), default=None)
    field7 = db.Column(db.String(100), default=None)
    field8 = db.Column(db.String(100), default=None)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, deviceID, field1, field2, field3, field4, field5, field6, field7, field8):
        self.deviceID = deviceID
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3
        self.field4 = field4
        self.field5 = field5
        self.field6 = field6
        self.field7 = field7
        self.field8 = field8

# class Guests(db.Model):
#     __tablename__ = 'guests'
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(80), nullable=True)
#     last_name = db.Column(db.String(80), nullable=True)
#     email = db.Column(db.String(120), unique=True, nullable=True)
#     phone = db.Column(db.String(80), nullable=True)
#     image = db.Column(db.String(255), nullable=False)
#     created_at = db.Column(db.DateTime, server_default=db.func.now())
#     updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

#     def __init__(self, first_name, last_name, email, phone, image):
#         self.first_name = first_name
#         self.last_name = last_name
#         self.email = email
#         self.phone = phone
#         self.image = image