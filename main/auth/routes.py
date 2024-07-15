from flask import request, jsonify, Blueprint
from .. import db
from flask import current_app
from main.models import UsuarioModel
from flask_jwt_extended import jwt_required, create_access_token
from main.mail.functions import sendMail
from datetime import datetime, timedelta
import random
import string
import secrets

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = db.session.query(UsuarioModel).filter(UsuarioModel.email == data.get("email")).first_or_404()

    if usuario.validate_pass(data.get("password")):
        access_token = create_access_token(identity=usuario.to_json())
        return {'access_token': access_token}, 200
    else:
        return 'Contraseña incorrecta', 401



@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    usuario = UsuarioModel.from_json(data)

    # Check if the email already exists
    if db.session.query(UsuarioModel).filter(UsuarioModel.email == usuario.email).scalar() is not None:
        return 'Email duplicado', 409

    try:
        # Generate a random password
        new_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
        usuario.plain_password = new_password

        db.session.add(usuario)
        db.session.commit()

        # Send welcome email
        sendMail([usuario.email], "Bienvenido!", 'register', new_password=new_password, usuario=usuario)
    except Exception as error:
        db.session.rollback()
        return str(error), 409

    return usuario.to_json(), 201


 # Generate a secure random token
def generate_reset_token():
    return secrets.token_urlsafe(16)

@auth.route('/reset-password', methods=['POST'])
def reset_password():
    mail = request.get_json().get("email")

    try:
        usuario = db.session.query(UsuarioModel).filter(UsuarioModel.email == mail).first_or_404()

        # Generate and store the reset token
        reset_token = generate_reset_token()
        usuario.reset_token = reset_token
        usuario.token_expiration = datetime.utcnow() + timedelta(hours=1)  # Set expiration time
        db.session.commit()


        # Send email for password reset
        sendMail([mail], 'Restablecer Contraseña', 'resetpassword', reset_token=reset_token, usuario=usuario)
    except Exception as error:
        print(f"Error: {error}")
        return str(error), 403

    return {'message': 'Correo para restablecer contraseña enviado.'}, 200

@auth.route('/reset-password/confirm', methods=['POST'])
def confirm_reset_password():
    token = request.get_json().get("token")
    new_password = request.get_json().get("new_password")

    usuario = db.session.query(UsuarioModel).filter_by(reset_token=token).first()

    if usuario:
        if usuario.token_expiration > datetime.utcnow():
            usuario.plain_password = new_password
            usuario.reset_token = None 
            usuario.token_expiration = None
            try:
                db.session.commit()
                return jsonify({'message': 'Restablecimiento de contraseña exitoso'}), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({'message': 'Error al guardar la nueva contraseña'}), 500
        else:
            return jsonify({'message': 'Token inválido o expirado'}), 400
    else:
        return jsonify({'message': 'Usuario no encontrado'}), 404

@auth.route('/change-password/<id>', methods=['PUT'])
@jwt_required()
def change_password(id):
    try:
        usuario = UsuarioModel.query.get_or_404(id)
        new_password = request.get_json().get("new_password")

        usuario.plain_password = new_password
        db.session.commit()

        return jsonify({'message': 'Contraseña cambiada exitosamente'}), 201

    except Exception as e:
        print(f"Error al cambiar la contraseña: {e}")
        return jsonify({'message': 'Error al cambiar la contraseña'}), 500