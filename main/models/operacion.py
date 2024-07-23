from .. import db
import re 

class Operacion(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.String(10), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)
    caracter = db.Column(db.String(10), nullable=False)
    naturaleza = db.Column(db.String(10), nullable=False)
    cuit = db.Column(db.Integer, nullable=False)
    razon_social = db.Column(db.String(255), nullable=False)
    comprobante_path = db.Column(db.String(255), nullable=True)
    comprobante_tipo = db.Column(db.String(10), nullable=True)
    observaciones = db.Column(db.String(255), nullable=False)

    id_pago = db.Column(db.Integer, db.ForeignKey("pago.id"), nullable=False)
    pagos = db.relationship("Pago", back_populates="operaciones", uselist=False, single_parent=True)
    
    id_subcategoria = db.Column(db.Integer, db.ForeignKey("subcategoria.id"), nullable=False)
    subcategorias = db.relationship("Subcategoria", back_populates="operaciones", uselist=False, single_parent=True)
    
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    usuarios = db.relationship("Usuario", back_populates="operaciones", uselist=False, single_parent=True)


    imagen1_path = db.Column(db.String(255), nullable=True)
    imagen1_tipo = db.Column(db.String(10), nullable=True)
    imagen2_path = db.Column(db.String(255), nullable=True)
    imagen2_tipo = db.Column(db.String(10), nullable=True)
    imagen3_path = db.Column(db.String(255), nullable=True)
    imagen3_tipo = db.Column(db.String(10), nullable=True)
    
    

    @db.validates('cuit')
    def validate_cuit(self, key, value):
        cuit_pattern = re.compile(r'^\d{11}$')
        if not cuit_pattern.match(str(value)):
            raise ValueError("Invalid CUIT format. It should be in the format 'XXXXXXXXXXX'.")
        return value

    
    @db.validates('fecha')
    def validate_fecha(self, key, value):
        fecha_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not fecha_pattern.match(value):
            raise ValueError("Invalid FECHA format. It should be in the format '%Y-%m-%d'.")
        return value

    

    def __repr__(self):
        return '<Operacion: %r %r %r %r %r %r %r %r %r %r>'% (self.id, self.fecha, self.tipo, self.caracter, self.naturaleza, self.id_subcategoria, self.cuit, self.razon_social, self.observaciones)
    
    def to_json(self):
        operacion_json = {
            'id': self.id,
            'fecha': str(self.fecha),
            'tipo': self.tipo,
            'caracter': self.caracter,
            'naturaleza': self.naturaleza,
            'cuit': self.cuit,
            'razon_social': self.razon_social,
            'comprobante_path': self.comprobante_path,
            'comprobante_tipo': self.comprobante_tipo,
            'observaciones': self.observaciones,
            'id_pago': self.id_pago,
            'id_subcategoria': self.id_subcategoria,
            'id_usuario': self.id_usuario,
            'imagen1_path': self.imagen1_path,
            'imagen1_tipo': self.imagen1_tipo,
            'imagen2_path': self.imagen2_path,
            'imagen2_tipo': self.imagen2_tipo,
            'imagen3_path': self.imagen3_path,
            'imagen3_tipo': self.imagen3_tipo,
        }
        return operacion_json

    @staticmethod
    def from_json(operacion_json):
        id = operacion_json.get('id')
        fecha = operacion_json.get('fecha')
        tipo = operacion_json.get('tipo')
        caracter = operacion_json.get('caracter')
        naturaleza = operacion_json.get('naturaleza')
        cuit = operacion_json.get('cuit')
        razon_social = operacion_json.get('razon_social')
        comprobante_path = operacion_json.get('comprobante_path')
        comprobante_tipo = operacion_json.get('comprobante_tipo')
        observaciones = operacion_json.get('observaciones')
        id_pago = operacion_json.get('id_pago')
        id_subcategoria = operacion_json.get('id_subcategoria')
        id_usuario = operacion_json.get('id_usuario')
        imagen1_path = operacion_json.get('imagen1_path')
        imagen1_tipo = operacion_json.get('imagen1_tipo')
        imagen2_path = operacion_json.get('imagen2_path')
        imagen2_tipo = operacion_json.get('imagen2_tipo')
        imagen3_path = operacion_json.get('imagen3_path')
        imagen3_tipo = operacion_json.get('imagen3_tipo')
        return Operacion(
                    id = id,
                    fecha = fecha,
                    tipo = tipo,
                    caracter = caracter,
                    naturaleza = naturaleza,
                    id_subcategoria = id_subcategoria,
                    cuit = cuit,
                    razon_social = razon_social,
                    comprobante_path = comprobante_path,
                    comprobante_tipo = comprobante_tipo,
                    observaciones = observaciones,
                    id_usuario = id_usuario,
                    id_pago  = id_pago, 
                    imagen1_path = imagen1_path,
                    imagen1_tipo = imagen1_tipo,
                    imagen2_path = imagen2_path,
                    imagen2_tipo = imagen2_tipo,
                    imagen3_path = imagen3_path,
                    imagen3_tipo = imagen3_tipo
                    )