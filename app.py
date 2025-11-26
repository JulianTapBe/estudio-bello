# ===========================================================
# Estudio Bello - Sistema de Clientes
# Autor: José Julián Tapia Bello
# Descripción: Sistema base con registro, login y panel
# ===========================================================
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message

# -----------------------------------------------------------
# 🔧 CONFIGURACIÓN BÁSICA
# -----------------------------------------------------------

import os

app = Flask(__name__)

# 🔐 SECRET KEY DESDE VARIABLES DE ENTORNO
app.secret_key = os.environ.get("SECRET_KEY", "dev_key")

# 📌 BASE DE DATOS: PostgreSQL en producción, SQLite en local
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Render usa PostgreSQL (psycopg2 requiere este cambio)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # Modo local → SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

db = SQLAlchemy(app)

# 🔧 Crear tablas automáticamente en PRODUCCIÓN
with app.app_context():
    db.create_all()


# Configuración para subida de archivos
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'clientes')
ALLOWED_EXTENSIONS = {'pdf', 'zip', 'mp4'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 📧 CONFIGURACIÓN DE CORREO DESDE VARIABLES DE ENTORNO
app.config['MAIL_SERVER'] = 'smtp-relay.brevo.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = ('Estudio Bello', os.environ.get("MAIL_USERNAME"))

mail = Mail(app)


# -----------------------------------------------------------
# 🔐 CONFIGURACIÓN DEL SISTEMA DE LOGIN
# -----------------------------------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # si no estás logeado, te manda al login

# -----------------------------------------------------------
# 👤 MODELO DE USUARIO
# -----------------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    paquete = db.Column(db.String(100))  # Ejemplo: "Paquete Esencial", "Paquete Ideal"
    contrato = db.Column(db.String(200)) # Ruta del archivo PDF
    fotos = db.Column(db.String(200))    # Ruta carpeta ZIP o enlace de fotos
    video = db.Column(db.String(200))    # Ruta del video
    is_admin = db.Column(db.Boolean, default=False)  # 👈 nuevo campo
    seleccionadas = db.Column(db.String(500))  # Guarda nombres separados por comas


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -----------------------------------------------------------
# 🌐 RUTAS DEL SISTEMA
# -----------------------------------------------------------

# Página principal → redirige al login
from flask import render_template

@app.route('/')
def index():
    return render_template('index.html')

# ------------------ REGISTRO ------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')

        # Evita correos duplicados
        if User.query.filter_by(email=email).first():
            flash("Ese correo ya está registrado.", "error")
            return redirect(url_for('register'))

        nuevo_usuario = User(nombre=nombre, email=email, password=password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Cuenta creada exitosamente. Inicia sesión.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

# ------------------ LOGIN ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')

            if user.is_admin:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('panel'))

        else:
            flash('Correo o contraseña incorrectos', 'danger')

    return render_template('login.html')


# ------------------ PANEL ------------------
@app.route('/panel')
@login_required
def panel():
    # Definir cuántas fotos hay en la carpeta de preselección
    ruta_preseleccion = os.path.join(app.static_folder, 'clientes', current_user.nombre, 'preseleccion')

    if os.path.exists(ruta_preseleccion):
        total_fotos = len([f for f in os.listdir(ruta_preseleccion) if f.endswith('.jpg')])
    else:
        total_fotos = 0

    # Definir límite de fotos según paquete
    limites = {
        "Paquete Esencial": 10,
        "Paquete Ideal": 20,
        "Paquete Premium": 35
    }
    limite_fotos = limites.get(current_user.paquete, 10)  # default 10 si no tiene paquete

    return render_template(
        'panel.html',
        nombre=current_user.nombre,
        email=current_user.email,
        paquete=current_user.paquete,
        contrato=current_user.contrato,
        fotos=current_user.fotos,
        video=current_user.video,
        total_fotos=total_fotos,
        limite_fotos=limite_fotos
    )


# ------------------ LOGOUT ------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for('login'))

# ------------------ ADMINISRADOR ------------------
@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return "Acceso denegado. Solo el administrador puede ver esta página.", 403

    usuarios = User.query.all()
    return render_template('admin.html', usuarios=usuarios)

# ------------------ NOTIFICAR CLIENTE ------------------
@app.route('/admin/notificar/<int:user_id>', methods=['POST'])
@login_required
def enviar_notificacion(user_id):
    if not current_user.is_admin:
        return "Acceso denegado", 403

    usuario = User.query.get_or_404(user_id)

    mensaje = f"""Hola {usuario.nombre},

Tus fotografías y video de {usuario.paquete or 'tu evento'} ya están disponibles para descargar en tu panel de cliente.

📸 Ingresa a tu cuenta en: http://127.0.0.1:5000/login
y descárgalos cuando quieras.

Atentamente,  
Estudio Bello
"""

    enviar_correo(usuario.email, "Tus fotos y video están listos", mensaje)
    flash(f"Notificación enviada a {usuario.email}", "success")
    return redirect(url_for('admin'))


# ------------------ EDITAR CLIENTES ------------------
@app.route('/admin/editar/<int:user_id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(user_id):
    if not current_user.is_admin:
        return "Acceso denegado", 403

    usuario = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # Actualizar campos de texto
        usuario.paquete = request.form['paquete']

        # Subir archivos
        for campo, carpeta in [('contrato', 'contrato'), ('fotos', 'fotos'), ('video', 'video')]:
            file = request.files.get(campo)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                setattr(usuario, campo, filename)

        db.session.commit()
        return redirect(url_for('admin'))

    return render_template('editar_cliente.html', usuario=usuario)

# Función para enviar correos
def enviar_correo(destinatario, asunto, mensaje):
    msg = Message(asunto, recipients=[destinatario])
    msg.body = mensaje
    mail.send(msg)

#------------------GUARDAR SELECCIÓN-------------------------
@app.route('/guardar_seleccion', methods=['POST'])
@login_required
def guardar_seleccion():
    data = request.get_json()
    seleccion = data.get("seleccion", [])

    current_user.seleccionadas = ",".join(map(str, seleccion))
    db.session.commit()

    return {"status": "ok"}


# -----------------------------------------------------------
# 🚀 INICIO DEL SERVIDOR
# -----------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # crea la base de datos automáticamente si no existe
    app.run(debug=True)






