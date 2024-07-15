from .. import db
import re

class Archivo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    id_subcategorias = db.Column(db.Integer, db.ForeignKey("subcategoria.id"), nullable=False) 
    subcategorias = db.relationship("Subcategoria", back_populates="archivos", uselist=False, single_parent=True)

    archivo_path = db.Column(db.String(255), nullable=True)
    archivo_tipo = db.Column(db.String(10), nullable=True)
    dato_1 = db.Column(db.String, nullable=True)
    dato_2 = db.Column(db.String, nullable=True)
    fecha_inicio = db.Column(db.String(10), nullable=True)
    fecha_fin = db.Column(db.String(10), nullable=True)

    @db.validates('fecha_inicio')
    def validate_fecha_inicio(self, key, value):
        fecha_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not fecha_pattern.match(value):
            raise ValueError("Invalid FECHA format. It should be in the format '%Y-%m-%d'.")
        return value

    @db.validates('fecha_fin')
    def validate_fecha_fin(self, key, value):
        fecha_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not fecha_pattern.match(value):
            raise ValueError("Invalid FECHA format. It should be in the format '%Y-%m-%d'.")
        return value

    def __repr__(self):
        return '<Archivo: %r %r %r %r %r %r %r>' % (
            self.id, self.archivo, self.id_subcategoria,
            self.dato_1, self.dato_2, self.fecha_inicio, self.fecha_fin
        )

    def to_json(self):
        archivo_json = {
            'id': self.id,
            'archivo_path': self.archivo_path,
            'archivo_tipo': self.archivo_tipo,
            'id_subcategoria': self.id_subcategoria,
            'dato_1': self.dato_1,
            'dato_2': self.dato_2,
            'fecha_inicio': self.fecha_inicio,
            'fecha_fin': self.fecha_fin,
        }
        return archivo_json

    @staticmethod
    def from_json(archivo_json):
        id = archivo_json.get('id')
        archivo_path = archivo_json.get('archivo_path')
        archivo_tipo = archivo_json.get('archivo_tipo')
        id_subcategoria = archivo_json.get('id_subcategoria')
        dato_1 = archivo_json.get('dato_1')
        dato_2 = archivo_json.get('dato_2')
        fecha_inicio = archivo_json.get('fecha_inicio')
        fecha_fin = archivo_json.get('fecha_fin')
        return Archivo(
            id=id,
            archivo_path=archivo_path,
            archivo_tipo=archivo_tipo,
            id_subcategoria=id_subcategoria,
            dato_1=dato_1,
            dato_2=dato_2,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
