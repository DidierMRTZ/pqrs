import pyodbc
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import msal
from dotenv import load_dotenv
import os
import requests

"""------------- Crear conecxion con base datos ODBC --------------"""
# Load enviroment variables from the .env file
load_dotenv('enviroment.env')
# access the environment variables
dsn_name  = os.getenv("dsn_name")
user= os.getenv("user")
password = os.getenv("password")
# Cadena de conexión ODBC
conn_str = f"DSN={dsn_name};UID={user};PWD={password}"
# Establecer la conexión
conn = pyodbc.connect(conn_str)
# Crear un cursor
cursor = conn.cursor()


"""--------- datos para el email ---------- """
# Configuración
email_address = 'mundimotosrpa@outlook.com'
email_password =  'rxvpaszfucejgsol'

""" ------------------------ Generar token autenticacion con API graph microsoft ---------"""

client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
tenant_id = os.getenv("tenant_id")

authority = f"https://login.microsoftonline.com/{tenant_id}"
app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)

scope = ["https://graph.microsoft.com/.default"]
result = app.acquire_token_for_client(scopes=scope)

if "access_token" in result:
    token = result['access_token']
    print(f'Token: {token}')
else:
    print("Error acquiring token:", result.get("error"), result.get("error_description"))
# Realizar una solicitud

headers = {
    'Authorization': f'Bearer {token}'
}

response = requests.get(f"https://graph.microsoft.com/v1.0/sites/12750d54-6748-4206-97bd-94929c8d55a6/lists/55bf5444-d5f7-412a-a520-a6e70e36bfbb/items", headers=headers)

for form in response.json()['value']:
    response_id = requests.get(f"https://graph.microsoft.com/v1.0/sites/12750d54-6748-4206-97bd-94929c8d55a6/lists/55bf5444-d5f7-412a-a520-a6e70e36bfbb/items/{form['id']}", headers=headers)
    fields=response_id.json()['fields']
    pqrs=(fields['Solicitud'],fields['nombre_completo'],fields['tipo_documento'],int(fields['numero_documento']),fields['correo_electronico'],int(fields['telefono_contacto']),fields['fecha_compra'],fields['numero_factura'],fields['area'],fields['descripcion'],fields['sede'],fields['politica_datos'],fields['id'])
    if fields['area'] == "Servicio al cliente":
        fields['area'] = "ServicioCliente"
    print(pqrs)
    
    try:
        # Eliminar espacion vacios
        if None in pqrs:
            pqrs=['' if item is None else item for item in list(pqrs)]
            pqrs=tuple(pqrs)
        
        Solicitud,Nombre_completo,Tipo_documento,Documento,Correo,Telefono_contacto,Fecha_compra,No_factura,Area_pqrs,Descripcion_pqrs,Sede,Politica_datos,RecordID=pqrs
        try:
            # Convertir el string a objeto datetime
            fecha_obj = datetime.fromisoformat(Fecha_compra.replace('Z', '+00:00'))
            Fecha_compra=str(fecha_obj.day)+"/"+str(fecha_obj.month)+"/"+str(fecha_obj.year)
        except:
            Fecha_compra=""
        try:
            """ -------------------- Insertar datos -------------------------- """
            query="""INSERT INTO PQRS (Solicitud,Nombre_completo,Tipo_documento,Documento,Correo,Telefono_contacto,Fecha_compra_texto,No_factura,Area_pqrs,Descripcion_pqrs,Sede,Politica_datos,RecordID) 
            values ('{0}','{1}','{2}',{3},'{4}',{5},'{6}','{7}','{8}','{9}','{10}','{11}',{12})""".format(Solicitud,Nombre_completo,Tipo_documento,Documento,Correo,Telefono_contacto,Fecha_compra,No_factura,Area_pqrs,Descripcion_pqrs,Sede,Politica_datos,RecordID)
            insert_data=cursor.execute(query)
            conn.commit()
            sqlstate_insert =False
            """----------------------------------------------------------------"""
            try:
                """---------------------- Eliminar datos de lista -----------------"""
                #response_id_delete = requests.delete(f"https://graph.microsoft.com/v1.0/sites/12750d54-6748-4206-97bd-94929c8d55a6/lists/55bf5444-d5f7-412a-a520-a6e70e36bfbb/items/{int(RecordID)}", headers=headers)
                """----------------------------------------------------------------"""
                sqlstate_delete =False
            except pyodbc.Error as ex:
            # Captura errores específicos de pyodbc
                sqlstate_delete = True
                print(sqlstate_delete)
        except pyodbc.Error as ex:
        # Captura errores específicos de pyodbc
            sqlstate_insert = True
            print(sqlstate_insert)

        """-------------- Enviar correo ---------"""
        # Crear el mensaje
        mensaje = MIMEMultipart()
        mensaje['From'] = email_address
        
        mensaje['Subject'] = 'Gestion PQRSF'

        if sqlstate_delete == True or sqlstate_insert == True:
            Correo='diidierstev@gmail.com'
            contenido_html = f"""
                <h2 style="text-align: center">GESTION PQRS</h2>
                <p> Hola, ocurrio un error al enviar el correo con qprs {RecordID}</p>
            """
        else:
            mensaje['To'] = Correo
            # Contenido HTML del mensaje
            if Solicitud !='Felicitaciones':
                contenido_html = f"""
                    <h2 style="text-align: center">GESTION PQRS</h2>

                    <p> Hola, ¡esperamos te encuentres muy bien! <br>
                    <br>
                    Para Mundimotos es muy importante conocer tu opinión, por esto te confirmamos que hemos recibido tu PQR, la misma quedó radicada con el número {RecordID}. Este radicado te permitirá hacer seguimiento a tu trámite, <br>
                    
                    a través del correo electrónico servicioalcliente@mundimotos.com y  al número telefónico XXXXXXXXX. Recuerda que contamos con 15 días hábiles (lunes a viernes) para dar respuesta, de acuerdo con ley 1755 de 2015. <br>
                    <br> 
                    Gracias por escribirnos.</p>
                    <br>
                    <div class="footer">
                        <p>Este mensaje (y sus anexos) contiene información privada, confidencial y privilegiada. Si usted es el destinatario real del mismo, al abrir el contenido, acepta la responsabilidad de mantenerlo en estricta confidencialidad y la obligación de no compartirlo, sin previa autorización escrita del remitente. Si usted no es el destinatario real del mismo, por favor informe de ello a quien lo envía y destrúyalo en forma inmediata.</p>
                    </div>
                """
            else:
                contenido_html = f"""
                    <h2 style="text-align: center">Felicidades</h2>
                    <p> Mensaje de felicitacion</p>
                """
                continue
            # Adjuntar el contenido HTML al mensaje
            mensaje.attach(MIMEText(contenido_html, 'html'))

            # Configurar el servidor SMTP de Outlook
            servidor_smtp = 'smtp.office365.com'
            puerto_smtp = 587

            try:
                # Iniciar conexión SMTP
                server = smtplib.SMTP(servidor_smtp, puerto_smtp)
                server.starttls()

                # Autenticación
                server.login(email_address, email_password)

                # Enviar el correo electrónico
                server.sendmail(email_address, Correo, mensaje.as_string())
                print("Correo HTML enviado correctamente")

            except Exception as e:
                print(f"No se pudo enviar el correo HTML. Error: {str(e)}")

            finally:
                # Cerrar conexión SMTP
                server.quit()
    except:
        print('Error')
