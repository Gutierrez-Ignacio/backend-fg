from flask_restful import Resource
from flask import request, jsonify
from .. import db
from main.models import PagoModel
from main.auth.decorators import role_required

class Pago(Resource):

    @role_required(roles=["admin"])
    def get(self, id):
        pago  = db.session.query(PagoModel).get_or_404(id)
        return pago.to_json(), 200

    @role_required(roles=["admin"])
    def delete(self,id):
        categoria  = db.session.query(PagoModel).get_or_404(id)
        db.session.delete(categoria)
        db.session.commit()
        return {'message': 'Pago eliminado'}, 204
    
    @role_required(roles=["admin"])
    def put(self, id):
        categoria = db.session.query(PagoModel).get_or_404(id)
        data = request.get_json()

        for key, value in data.items():
            setattr(categoria, key, value)

        db.session.add(categoria)
        db.session.commit()
        return categoria.to_json(), 200
    
class Pagos(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        pagos = db.session.query(PagoModel)

        pagos_paginados = pagos.paginate(page=page, per_page=per_page, error_out=False, max_per_page=None)

        return jsonify({
            'pagos': [pago.to_json() for pago in pagos_paginados.items],
            'total' : pagos.total,           
            'pages' : pagos.pages,  
            'page' : pagos.page,  
        })

    @role_required(roles=["admin"])
    def post(self):
        try:
            new_pagos = PagoModel.from_json(request.get_json())

            db.session.add(new_pagos)
            db.session.commit()

            return new_pagos.to_json(), 201
        
        except ValueError as ve:
            return {'message': str(ve)}, 400
        
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error al crear el apago', 'error': str(e)}, 500