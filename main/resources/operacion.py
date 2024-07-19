from flask_restful import Resource, current_app
from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
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
            # Check if request contains files
            if 'comprobante' not in request.files or 'imagen1' not in request.files or 'imagen2' not in request.files or 'imagen3' not in request.files:
                return {'message': 'Missing files in request'}, 400
            
            # Get files from request
            comprobante = request.files['comprobante']
            imagen1 = request.files['imagen1']
            imagen2 = request.files['imagen2']
            imagen3 = request.files['imagen3']
            
            # Generate unique filenames for each file
            comprobante_filename = str(uuid.uuid4()) + '_' + secure_filename(comprobante.filename)
            imagen1_filename = str(uuid.uuid4()) + '_' + secure_filename(imagen1.filename)
            imagen2_filename = str(uuid.uuid4()) + '_' + secure_filename(imagen2.filename)
            imagen3_filename = str(uuid.uuid4()) + '_' + secure_filename(imagen3.filename)
            
            # Save files to the specified directory
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'])
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            comprobante_path = os.path.join(upload_dir, comprobante_filename)
            imagen1_path = os.path.join(upload_dir, imagen1_filename)
            imagen2_path = os.path.join(upload_dir, imagen2_filename)
            imagen3_path = os.path.join(upload_dir, imagen3_filename)
            
            comprobante.save(comprobante_path)
            imagen1.save(imagen1_path)
            imagen2.save(imagen2_path)
            imagen3.save(imagen3_path)
            
            # Create a new instance of OperacionModel
            new_operacion = OperacionModel(
                fecha=request.form.get('fecha'),
                tipo=request.form.get('tipo'),
                caracter=request.form.get('caracter'),
                naturaleza=request.form.get('naturaleza'),
                cuit=request.form.get('cuit'),
                razon_social=request.form.get('razon_social'),
                comprobante_path=comprobante_path,
                comprobante_tipo=comprobante.content_type,
                observaciones=request.form.get('observaciones'),
                id_pago=request.form.get('id_pago'),
                id_subcategoria=request.form.get('id_subcategoria'),
                id_usuario=request.form.get('id_usuario'),
                imagen1_path=imagen1_path,
                imagen1_tipo=imagen1.content_type,
                imagen2_path=imagen2_path,
                imagen2_tipo=imagen2.content_type,
                imagen3_path=imagen3_path,
                imagen3_tipo=imagen3.content_type
            )
            
            # Add to session and commit to save to the database
            db.session.add(new_operacion)
            db.session.commit()
            
            # Return the newly created operation in JSON format with status code 201 (created)
            return new_operacion.to_json(), 201
        
        except ValueError as ve:
            return {'message': str(ve)}, 400
        
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error al crear la operacion', 'error': str(e)}, 500