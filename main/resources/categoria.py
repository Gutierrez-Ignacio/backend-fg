from flask_restful import Resource
from flask import request, jsonify
from .. import db
from main.models import CategoriaModel
from main.auth.decorators import role_required

class Categoria(Resource):

    @role_required(roles=["admin"])
    def get(self, id):
        categoria  = db.session.query(CategoriaModel).get_or_404(id)
        return categoria.to_json(), 200

    @role_required(roles=["admin"])
    def delete(self,id):
        categoria  = db.session.query(CategoriaModel).get_or_404(id)
        db.session.delete(categoria)
        db.session.commit()
        return {'message': 'Categoria eliminada'}, 204
    
    @role_required(roles=["admin"])
    def put(self, id):
        categoria = db.session.query(CategoriaModel).get_or_404(id)
        data = request.get_json()
        
        for key, value in data:
            setattr(categoria, key, value)

        db.session.add(categoria)
        db.session.commit()
        return categoria.to_json(), 200
    
class Categorias(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        categorias_query = db.session.query(CategoriaModel)

        categorias_paginadas = categorias_query.paginate(page=page, per_page=per_page, error_out=False, max_per_page=None)

        response = {
            'categorias': [categoria.to_json() for categoria in categorias_paginadas.items],
            'total': categorias_paginadas.total,
            'pages': categorias_paginadas.pages,
            'page': categorias_paginadas.page,
        }
        return jsonify(response)

    @role_required(roles=["admin"])
    def post(self):
        try:
            new_categorias = CategoriaModel.from_json(request.get_json())

            db.session.add(new_categorias)
            db.session.commit()

            return new_categorias.to_json(), 201
        
        except ValueError as ve:
            return {'message': str(ve)}, 400
        
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error al crear la categoria', 'error': str(e)}, 500