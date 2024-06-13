from flask import Flask
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
import flask
import os

import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crear el directorio de subidas si no existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route('/')
def index():
    return render_template('index.html')
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    conn = psycopg2.connect(
        host="postgres",
        database="postgres",
        user="postgres",
        password="postgres"
    )
    cur= conn.cursor()

    if request.method == 'POST':
        """--------------- campo para el archivo adjunto --------------"""
        if 'file' not in request.files:
            name_file=''
        file = request.files['file']
        if file.filename == '':
            name_file=file.filename
        if file:
            # Guardar el archivo en el directorio configurado
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            name_file=file.filename
        name = request.form['name']
        email = request.form['email']
        cur.execute("""INSERT INTO test (nombre,correo,file) values ('{0}','{1}','{2}')""".format(name,email,name_file))
        conn.commit()
        return f"Nombre: {name}, Email: {email}, File:{name_file}"
    return redirect(url_for('index'))


#172.23.0.3
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)
