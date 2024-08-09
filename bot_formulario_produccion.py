import pyodbc
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import msal
from dotenv import load_dotenv
import os
import requests
import api_microsoft

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
else:
    print("Error acquiring token:", result.get("error"), result.get("error_description"))

api_client=api_microsoft.GraphAPIClient(client_id,client_secret,tenant_id)
token=api_client.acess_token()
if token == 'unauthorized_client':
    print('unauthorized_client')
else:
    # Realizar una solicitud
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response=api_client.get_items('12750d54-6748-4206-97bd-94929c8d55a6','55bf5444-d5f7-412a-a520-a6e70e36bfbb','*')

sqlstate_insert=False
sqlstate_delete=False
total_items=len(response['value'])
total_items_insertados=0
total_items_eliminados=0
total_correos_enviados=0

for form in response['value']:
    fields=form['fields']
    try:
        pqrs=(fields['Solicitud'],fields['nombre_completo'],fields['tipo_documento'],int(fields['numero_documento']),fields['correo_electronico'],int(fields['telefono_contacto']),fields['fecha_compra'],fields['numero_factura'],fields['area'],fields['descripcion'],fields['sede'],fields['politica_datos'],fields['id'])
    except:
        pqrs=(fields['Solicitud'],fields['nombre_completo'],fields['tipo_documento'],int(fields['numero_documento']),fields['correo_electronico'],int(fields['telefono_contacto']),'',fields['numero_factura'],fields['area'],fields['descripcion'],fields['sede'],fields['politica_datos'],fields['id'])
    finally:
        try:
            # Eliminar espacion vacios
            if None in pqrs:
                pqrs=['' if item is None else item for item in list(pqrs)]
                pqrs=tuple(pqrs)
            """--------------- creo los campos necesrios --------------------"""
            Solicitud,Nombre_completo,Tipo_documento,Documento,Correo,Telefono_contacto,Fecha_compra,No_factura,Area_pqrs,Descripcion_pqrs,Sede,Politica_datos,RecordID=pqrs
            try:
                # Convertir el string a objeto datetime
                fecha_obj = datetime.fromisoformat(Fecha_compra.replace('Z', '+00:00'))
                Fecha_compra=str(fecha_obj.day)+"/"+str(fecha_obj.month)+"/"+str(fecha_obj.year)
            except:
                Fecha_compra=""
            

            """ -------------------- Insertar datos -------------------------- """
            try:
                query="""INSERT INTO PQRS (Solicitud,Nombre_completo,Tipo_documento,Documento,Correo,Telefono_contacto,Fecha_compra_texto,No_factura,Area_pqrs,Descripcion_pqrs,Sede,Politica_datos,RecordID) 
                values ('{0}','{1}','{2}',{3},'{4}',{5},'{6}','{7}','{8}','{9}','{10}','{11}',{12})""".format(Solicitud,Nombre_completo,Tipo_documento,Documento,Correo,Telefono_contacto,Fecha_compra,No_factura,Area_pqrs,Descripcion_pqrs,Sede,Politica_datos,RecordID)
                insert_data=cursor.execute(query)
                conn.commit()
                sqlstate_insert =True
                """----------------------------------------------------------------"""
            except pyodbc.Error as ex:
                """------ Crea nuevamente la conecxion -------------"""
                # Cadena de conexión ODBC
                conn_str = f"DSN={dsn_name};UID={user};PWD={password}"
                # Establecer la conexión
                conn = pyodbc.connect(conn_str)
                # Crear un cursor
                cursor = conn.cursor()
                query="""INSERT INTO PQRS (Solicitud,Nombre_completo,Tipo_documento,Documento,Correo,Telefono_contacto,Fecha_compra_texto,No_factura,Area_pqrs,Descripcion_pqrs,Sede,Politica_datos,RecordID) 
                values ('{0}','{1}','{2}',{3},'{4}',{5},'{6}','{7}','{8}','{9}','{10}','{11}',{12})""".format(Solicitud,Nombre_completo,Tipo_documento,Documento,Correo,Telefono_contacto,Fecha_compra,No_factura,Area_pqrs,Descripcion_pqrs,Sede,Politica_datos,RecordID)
                insert_data=cursor.execute(query)
                conn.commit()
                sqlstate_insert =True
                """ -------------------------------------------------"""
            finally:
                if sqlstate_insert == False:
                    print("XXX Error insercion ID ",RecordID)
                else:
                    print("Inserción Exitosa ",RecordID)
                    total_items_insertados=total_items_insertados+1
        
            """ ---------------- Eliminar datos ---------------- """
            try:
                """---------------------- Eliminar datos de lista -----------------"""
                response_id_delete = requests.delete(f"https://graph.microsoft.com/v1.0/sites/12750d54-6748-4206-97bd-94929c8d55a6/lists/55bf5444-d5f7-412a-a520-a6e70e36bfbb/items/{int(RecordID)}", headers=headers)
                """----------------------------------------------------------------"""
                sqlstate_delete =True
            except:
            # Captura errores específicos de pyodbc
                """------ Crea nuevamente la conecxion -------------"""
                # Cadena de conexión ODBC
                conn_str = f"DSN={dsn_name};UID={user};PWD={password}"
                # Establecer la conexión
                conn = pyodbc.connect(conn_str)
                # Crear un cursor
                cursor = conn.cursor()
                response_id_delete = requests.delete(f"https://graph.microsoft.com/v1.0/sites/12750d54-6748-4206-97bd-94929c8d55a6/lists/55bf5444-d5f7-412a-a520-a6e70e36bfbb/items/{int(RecordID)}", headers=headers)
                """----------------------------------------------------------------"""
                sqlstate_delete = True
            finally:
                if sqlstate_delete == False:
                    print("XXX Error Eliminando ID ",RecordID)
                else:
                    print("Eliminado Exitoso ID",RecordID)
                    total_items_eliminados=total_items_eliminados+1

            """-------------- Enviar correo ---------"""

            # Contenido HTML del mensaje
            if Solicitud !='Felicitaciones':
                contenido_html = f"""
                    <h2 style="text-align: center">GESTION PQRS</h2>
                    <p> Hola, ¡esperamos te encuentres muy bien! <br>
                        
                    Para Mundimotos es muy importante conocer tu opinión, por esto te confirmamos que hemos recibido tu PQR, la misma quedó radicada con el número {RecordID}. Este radicado te permitirá hacer seguimiento a tu trámite,
                    
                    a través del correo electrónico servicioalcliente@mundimotos.com <br>

                    Recuerda que contamos con 15 días hábiles (lunes a viernes) para dar respuesta, de acuerdo con ley 1755 de 2015.<br>
                    
                    Gracias por escribirnos.</p>

                    <div class="footer">
                        <p>Este mensaje (y sus anexos) contiene información privada, confidencial y privilegiada. Si usted es el destinatario real del mismo, al abrir el contenido, acepta la responsabilidad de mantenerlo en estricta confidencialidad y la obligación de no compartirlo, sin previa autorización escrita del remitente. Si usted no es el destinatario real del mismo, por favor informe de ello a quien lo envía y destrúyalo en forma inmediata.</p>
                    </div>
                """
                dic={
                    "message": {
                            "subject": "GESTION PQRSF",
                            "body": {
                            "contentType": "HTML",
                            "content": contenido_html
                            },
                            "toRecipients": [
                            {
                                "emailAddress": {
                                "address": Correo
                                }
                            }
                            ],
                            "internetMessageHeaders": [
                            {
                                "name": "x-custom-header-group-name",
                                "value": "Nevada"
                            },
                            {
                                "name": "x-custom-header-group-id",
                                "value": "NV001"
                            }
                            ]
                        }
                    }
                try:
                    response=requests.post('https://graph.microsoft.com/v1.0/users/Servicioalcliente@mundimotos.com/sendMail',headers=headers,json=dic)
                    if response.status_code == 202:
                        total_correos_enviados=total_correos_enviados+1
                        print("Correo HTML enviado correctamente")
                    else:
                        #Generar token
                        app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)
                        scope = ["https://graph.microsoft.com/.default"]
                        result = app.acquire_token_for_client(scopes=scope)
                        if "access_token" in result:
                            token = result['access_token']
                            response=requests.post('https://graph.microsoft.com/v1.0/users/Servicioalcliente@mundimotos.com/sendMail',headers=headers,json=dic)
                            if response.status_code == 202:
                                total_correos_enviados=total_correos_enviados+1
                                print("Correo HTML enviado correctamente")
                            else:
                                print("XX Error al enviar correo")
                        else:
                            print("Error acquiring token:", result.get("error"), result.get("error_description"))
                except:
                    print("XX Error al enviar correo")
            else:
                #No envia correo
                None
        except:
            print('Error general')

print('total item: ',total_items)
print('total item insertados: ',total_items_insertados)
print('total items elimanados: ',total_items_eliminados)
print('total correos enviados',total_correos_enviados)