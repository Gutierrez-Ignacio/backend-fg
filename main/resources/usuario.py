from flask_restful import Resource
from flask import request, jsonify
from .. import db
from sqlalchemy import or_, and_
from main.models import UsuarioModel

class Usuario(Resource):

    def get(self, id):
        usuario = db.session.query(UsuarioModel).get_or_404(id)
        return usuario.to_json(), 200

    def delete(self,id):
        usuario = db.session.query(UsuarioModel).get_or_404(id)
        db.session.delete(usuario)
        db.session.commit()
        return {'message': 'Usuario eliminado'}, 204
    
    def put(self, id):
        usuario = db.session.query(UsuarioModel).get_or_404(id)
        data = request.get_json()

        for key, value in data.items():
            if key == 'password':
                usuario.plain_password = value
            else:
                setattr(usuario, key, value)

        db.session.commit()
        return usuario.to_json(), 200
    

class Usuarios(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        usuarios = db.session.query(UsuarioModel)

        if request.args.get('search_term'):
            search_term = request.args.get('search_term')
            search_terms = search_term.split(' ')

            if len(search_terms) == 1:
                usuarios = usuarios.filter(or_(
                    UsuarioModel.id.like(f"%{search_term}%"),
                    UsuarioModel.nombre.like(f"%{search_term}%"),
                    UsuarioModel.apellido.like(f"%{search_term}%"),
                    UsuarioModel.email.like(f"%{search_term}%")
                ))
            elif len(search_terms) == 2:
                usuarios = usuarios.filter(and_(
                    UsuarioModel.nombre.like(f"%{search_terms[0]}%"),
                    UsuarioModel.apellido.like(f"%{search_terms[1]}%")
                ))

        usuarios = usuarios.paginate(page=page, per_page=per_page, error_out=False, max_per_page=100)

        return jsonify({
            'usuarios': [usuario.to_json() for usuario in usuarios.items],
            'total': usuarios.total,
            'pages': usuarios.pages,
            'page': usuarios.page,
        })

    def post(self):
        try:
            new_usuario = UsuarioModel.from_json(request.get_json())
            
            db.session.add(new_usuario)
            db.session.commit()

            return new_usuario.to_json(), 201
        
        except ValueError as ve:
            return {'message': str(ve)}, 400
        
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error al crear el usuario', 'error': str(e)}, 500