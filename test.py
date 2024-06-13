from flask import Flask
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
import flask
import os

app = Flask(__name__)

# Configuración para subida de archivos
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="postgres"
    )
    cur= conn.cursor()

    if request.method == 'POST':
        """--------------- campo para el archivo adjunto --------------"""
        file = request.files['file']
        print(file)
        # file = request.files['file']
        # file = request.files['file']
        # Aquí puedes hacer algo con los datos, como guardarlos en una base de datos
        name = request.form['name']
        email = request.form['email']
        cur.execute("""INSERT INTO test (nombre,correo) values ('{0}','{1}')""".format(name,email))
        conn.commit()
        return f"Nombre: {name}, Email: {email}, file: {file}"
    return redirect(url_for('index'))


app.run()