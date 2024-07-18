import os
from flask import Flask
from dotenv import load_dotenv
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail

api = Api()
db=SQLAlchemy()
jwt = JWTManager()
mailsender = Mail()

def create_app():
    app = Flask(__name__)
    load_dotenv()

    if not os.path.exists(os.getenv('DATABASE_PATH')+os.getenv('DATABASE_NAME')):
        os.mknod(os.getenv('DATABASE_PATH')+os.getenv('DATABASE_NAME'))

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Database configuration URL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+os.getenv('DATABASE_PATH')+os.getenv('DATABASE_NAME')
    
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')

    db.init_app(app)
    
    # Import resources directory
    import main.resources as resources

    api.add_resource(resources.UsuariosResource,"/usuarios")
    api.add_resource(resources.UsuarioResource, "/usuario/<int:id>")
    api.add_resource(resources.OperacionesResource,"/operaciones")
    api.add_resource(resources.OperacionResource, "/operacion/<id>")
    api.add_resource(resources.ConceptosResource,"/conceptos")
    api.add_resource(resources.ConceptoResource, "/concepto/<id>")
    api.add_resource(resources.CategoriasResource,"/categorias")
    api.add_resource(resources.CategoriaResource, "/categoria/<id>")
    api.add_resource(resources.SubcategoriasResource,"/subcategorias")
    api.add_resource(resources.SubcategoriaResource, "/subcategoria/<id>")
    api.add_resource(resources.PagosResource,"/pagos")
    api.add_resource(resources.PagoResource, "/pago/<id>")
    api.add_resource(resources.ArchivosResource,"/archivos")
    api.add_resource(resources.ArchivoResource, "/archivo/<id>")


    api.init_app(app)

    # JWT configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES'))
    jwt.init_app(app)

    # Registration of authentication routes
    from main.auth import routes
    app.register_blueprint(routes.auth)

    # Flask-Mail configuration for email sending
    app.config['MAIL_HOSTNAME'] = os.getenv('MAIL_HOSTNAME')
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['FLASKY_MAIL_SENDER'] = os.getenv('FLASKY_MAIL_SENDER')
    mailsender.init_app(app)

    return app
