from .. import db
import re

class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    monto_total = db.Column(db.String, nullable=False)
    metodo_de_pago = db.Column(db.String, nullable=False)

    operaciones = db.relationship("Operacion", uselist=False, back_populates="pagos", single_parent=True)

    @db.validates('monto_total')
    def validate_email(self, key, value):
        monto_total_pattern = re.compile(r'^\d+(\.\d+)?$')
        if not monto_total_pattern.match(value):
            raise ValueError("Invalid MONTO TOTAL format. It should be a valid amount.")
        return value
    
    def __repr__(self):
        return '<Concepto: %r %r %r>'% (self.id, self.monto_total, self.metodo_de_pago)
    
    def to_json(self):
        concepto_json = {
            'id': self.id,
            'monto_total': self.monto_total,
            'metodo_de_pago': self.metodo_de_pago,
        }
        return concepto_json

    @staticmethod
    def from_json(concepto_json):
        id = concepto_json.get('id')
        monto_total = concepto_json.get('monto_total')
        metodo_de_pago = concepto_json.get('metodo_de_pago')
        return Pago(
                    id=id,
                    monto_total=monto_total,
                    metodo_de_pago=metodo_de_pago
        )