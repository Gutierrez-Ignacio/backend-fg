from flask_restful import Resource
from flask import request, jsonify
from .. import db
from main.models import SubcategoriaModel
from main.auth.decorators import role_required

class Subcategoria(Resource):

    @role_required(roles=["admin"])
    def get(self, id):
        subcategoria  = db.session.query(SubcategoriaModel).get_or_404(id)
        return subcategoria.to_json(), 200

    @role_required(roles=["admin"])
    def delete(self,id):
        subcategoria  = db.session.query(SubcategoriaModel).get_or_404(id)
        db.session.delete(subcategoria)
        db.session.commit()
        return {'message': 'Subcategoria eliminada'}, 204
    
    @role_required(roles=["admin"])
    def put(self, id):
        subcategoria = db.session.query(SubcategoriaModel).get_or_404(id)
        data = request.get_json()

        for key, value in data.items():
            setattr(subcategoria, key, value)

        db.session.add(subcategoria)
        db.session.commit()
        return subcategoria.to_json(), 200
    
class Subcategorias(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        subcategorias = db.session.query(SubcategoriaModel)

        subcategorias_paginadas = subcategorias.paginate(page=page, per_page=per_page, error_out=False, max_per_page=None)

        return jsonify({
            'subcategorias': [subcategoria.to_json() for subcategoria in subcategorias_paginadas.items],
            'total' : subcategorias.total,           
            'pages' : subcategorias.pages,  
            'page' : subcategorias.page,  
        })

    def post(self):
        try:
            new_subcategorias = SubcategoriaModel.from_json(request.get_json())

            db.session.add(new_subcategorias)
            db.session.commit()

            return new_subcategorias.to_json(), 201
        
        except ValueError as ve:
            return {'message': str(ve)}, 400
        
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error al crear la subcategoria', 'error': str(e)}, 500