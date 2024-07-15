from .. import db
import re
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String, nullable=False)
    apellido = db.Column(db.String ,nullable=False)
    email = db.Column(db.String, unique=True, index=True, nullable=False)
    password = db.Column(db.String, nullable=True)
    rol = db.Column(db.String, nullable=True, default="admin")

    operaciones = db.relationship("Operacion", back_populates="usuarios")

    @db.validates('email')
    def validate_email(self, key, value):
        email_pattern = re.compile(r'^[a-zA-Z0-9_\-\.~]{2,}@[a-zA-Z0-9_\-\.~]{2,}\.[a-zA-Z]{2,4}$')
        if not email_pattern.match(value):
            raise ValueError("Invalid EMAIL format. It should be a valid email address.")
        return value
    

    @property
    def plain_password(self):
        raise AttributeError('password cant be read')
    
    @plain_password.setter
    def plain_password(self, password):
        self.password = generate_password_hash(password)
        
    def validate_pass(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return '<Usuario: %r %r %r %r %r>'% (self.id, self.nombre, self.apellido, self.email, self.rol)
    
    
    def to_json(self):
        usuario_json = {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'email': self.email,
            'rol': self.rol
        }
        return usuario_json

    def to_json_short(self):
        usuario_json = {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'rol': self.rol
        }
        return usuario_json

    @staticmethod
    def from_json(usuario_json):
        id = usuario_json.get('id')
        nombre = usuario_json.get('nombre')
        apellido = usuario_json.get('apellido')
        email = usuario_json.get('email')
        password = usuario_json.get('password')
        rol = usuario_json.get('rol')
        return Usuario(
                    id=id,
                    nombre=nombre,
                    apellido=apellido,     
                    email=email,
                    plain_password=password,
                    rol=rol
                    )