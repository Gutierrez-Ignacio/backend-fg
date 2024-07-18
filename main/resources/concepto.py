from flask_restful import Resource
from flask import request, jsonify
from .. import db
from sqlalchemy import or_, and_
from main.models import ConceptoModel
from main.auth.decorators import role_required

class Concepto(Resource):

    @role_required(roles=["admin"])
    def get(self, id):
        concepto  = db.session.query(ConceptoModel).get_or_404(id)
        return concepto.to_json(), 200

    @role_required(roles=["admin"])
    def delete(self,id):
        concepto  = db.session.query(ConceptoModel).get_or_404(id)
        db.session.delete(concepto)
        db.session.commit()
        return {'message': 'Concepto eliminado'}, 204

    @role_required(roles=["admin"])   
    def put(self, id):
        concepto = db.session.query(ConceptoModel).get_or_404(id)
        data = request.get_json().items()

        for key, value in data:
            setattr(concepto, key, value)

        db.session.add(concepto)
        db.session.commit()
        return concepto.to_json(), 200
    
class Conceptos(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        search_term = request.args.get('search_term', default='', type=str)

        conceptos = db.session.query(ConceptoModel)

        if search_term:
            search_terms = search_term.split(' ')
            if len(search_terms) == 1:
                conceptos = conceptos.filter(or_(
                    ConceptoModel.id.like(f"%{search_term}%"),
                    ConceptoModel.nombre.like(f"%{search_term}%"), 
                ))

        conceptos = conceptos.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'conceptos': [concepto.to_json() for concepto in conceptos.items],
            'total': conceptos.total,
            'pages': conceptos.pages,
            'page': conceptos.page,
        })

    @role_required(roles=["admin"])
    def post(self):
        try:
            conceptos = ConceptoModel.from_json(request.get_json())

            db.session.add(conceptos)
            db.session.commit()

            return conceptos.to_json(), 201
        
        except ValueError as ve:
            return {'message': str(ve)}, 400
        
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error al crear el concepto', 'error': str(e)}, 500