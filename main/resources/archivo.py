from flask_restful import Resource, current_app
from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
from .. import db
from main.models import ArchivoModel
from main.auth.decorators import role_required


class Archivo(Resource):

    @role_required(roles=["admin"])
    def get(self, id):
        archivo = db.session.query(ArchivoModel).get_or_404(id)
        return archivo.to_json(), 200

    @role_required(roles=["admin"])
    def delete(self, id):
        archivo  = db.session.query(ArchivoModel).get_or_404(id)
        db.session.delete(archivo)
        db.session.commit()
        return {'message': 'Archivo eliminado'}, 204

    @role_required(roles=["admin"])
    def put(self, id):
        try:
            # Retrieve the existing file record from the database
            archivo = ArchivoModel.query.get(id)
            if archivo is None:
                return {'message': 'Archivo no encontrado'}, 404
            
            # Check if a new file is uploaded
            if 'file' in request.files:
                new_file = request.files['file']
                if new_file.filename != '':
                    # Generate a unique filename for the new file
                    filename = str(uuid.uuid4()) + '_' + secure_filename(new_file.filename)
                    
                    # Save the new file to the specified directory
                    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'])
                    if not os.path.exists(upload_dir):
                        os.makedirs(upload_dir)
                    
                    file_path = os.path.join(upload_dir, filename)
                    new_file.save(file_path)
                    
                    # Update the file path and type in the database
                    archivo.archivo_path = file_path
                    archivo.archivo_tipo = new_file.content_type

            # Update other fields of the file record
            archivo.dato_1 = request.form.get('dato_1', archivo.dato_1)
            archivo.dato_2 = request.form.get('dato_2', archivo.dato_2)
            archivo.id_subcategorias = request.form.get('id_subcategorias', archivo.id_subcategorias)
            archivo.fecha_inicio = request.form.get('fecha_inicio', archivo.fecha_inicio)
            archivo.fecha_fin = request.form.get('fecha_fin', archivo.fecha_fin)

            # Commit the changes to the database
            db.session.commit()

            # Return the updated file record in JSON format with status code 200 (OK)
            return archivo.to_json(), 200

        except Exception as e:
            # Rollback the session in case of an error
            db.session.rollback()
            return {'message': 'Error al actualizar el archivo', 'error': str(e)}, 500

class Archivos(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        archivos = db.session.query(ArchivoModel)

        archivos_paginados = archivos.paginate(page=page, per_page=per_page, error_out=False, max_per_page=None)

        return jsonify({
            'archivos': [archivo.to_json() for archivo in archivos_paginados.items],
            'total': archivos_paginados.total,
            'pages': archivos_paginados.pages,
            'page': archivos_paginados.page,
        })

    @role_required(roles=["admin"])
    def post(self):
        try:
            if 'file' not in request.files:
                return {'message': 'No se proporcionó ningún archivo'}, 400
            
            archivo = request.files['file']
            
            if archivo.filename == '':
                return {'message': 'No se seleccionó ningún archivo'}, 400
            
            # Generate a unique filename for the file
            filename = str(uuid.uuid4()) + '_' + secure_filename(archivo.filename)
            
            # Save the file to the specified directory
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'])
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            file_path = os.path.join(upload_dir, filename)
            archivo.save(file_path)
            
            # Create a new instance of ArchivoModel
            nuevo_archivo = ArchivoModel(
                archivo_path=file_path,
                archivo_tipo=archivo.content_type,
                dato_1=request.form.get('dato_1'),
                dato_2=request.form.get('dato_2'),
                id_subcategorias=request.form.get('id_subcategorias'),
                fecha_inicio=request.form.get('fecha_inicio'),
                fecha_fin=request.form.get('fecha_fin')
            )
            
            # Add to session and commit to save to the database
            db.session.add(nuevo_archivo)
            db.session.commit()
            
            # Return the newly created file in JSON format with status code 201 (created)
            return nuevo_archivo.to_json(), 201
        
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error al crear el archivo', 'error': str(e)}, 500