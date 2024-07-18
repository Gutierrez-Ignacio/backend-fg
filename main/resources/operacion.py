from flask_restful import Resource
from flask import request, jsonify
from .. import db
from sqlalchemy import or_, and_
from main.models import OperacionModel
from main.auth.decorators import role_required

class Operacion(Resource):

    @role_required(roles=["admin"])
    def get(self, id):
        operacion  = db.session.query(OperacionModel).get_or_404(id)
        return operacion.to_json(), 200

    @role_required(roles=["admin"])
    def delete(self,id):
        operacion  = db.session.query(OperacionModel).get_or_404(id)
        db.session.delete(operacion)
        db.session.commit()
        return {'message': 'Operacion eliminada'}, 204
    
    @role_required(roles=["admin"])
    def put(self, id):
        operacion = db.session.query(OperacionModel).get_or_404(id)
        data = request.get_json()

        for key, value in data.items():
            setattr(operacion, key, value)

        db.session.add(operacion)
        db.session.commit()
        return operacion.to_json(), 200
    
class Operaciones(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        search_term = request.args.get('search_term', default='', type=str)

        operaciones = db.session.query(OperacionModel)

        if search_term:
            search_terms = search_term.split(' ')
            if len(search_terms) == 1:
                operaciones = operaciones.filter(and_(
                    OperacionModel.nombre.like(f"%{search_term}%"), 
                ))

        operaciones = operaciones.paginate(page=page, per_page=per_page, error_out=False, max_per_page=None)

        return jsonify({
            'operaciones': [operacion.to_json() for operacion in operaciones.items],
            'total' : operaciones.total,           
            'pages' : operaciones.pages,  
            'page' : operaciones.page,  
        })

    @role_required(roles=["admin"]) 
    def post(self):
        try:
            new_operaciones = OperacionModel.from_json(request.get_json())

            db.session.add(new_operaciones)
            db.session.commit()

            return new_operaciones.to_json(), 201
        
        except ValueError as ve:
            return {'message': str(ve)}, 400
        
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error al crear la operacion', 'error': str(e)}, 500