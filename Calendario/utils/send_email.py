import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import dotenv
from importlib.resources import files
import reflex as rx
from Calendario import static

#Especificamos el archivo de variables de entorno
dotenv.load_dotenv(dotenv_path=".env", override=True)

#Recogemos los datos del archivo
SMTP_SERVER = os.environ.get("SMTP_SERVER", "").strip()
SMTP_PORT   = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER   = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")  

#Mensaje de bienvenida
def send_welcome_email(email, username):
    #Creamos el mensaje multiparte html + imágenes
    message = MIMEMultipart('related')
    message['From'] = SMTP_USER 
    message['To'] = email
    message['Subject'] = "¡Bienvenido a tu Calendario!"
    
    #Creamos la parte alternativa, texto plano + HTML
    alt = MIMEMultipart("alternative")

    #Texto plano
    text = f"""\
    ¡Hola {username}!

    Bienvenido a CalendPy 🎉

    Ahora puedes:
    - Organizar tus comidas/cenas 🍽️
    - Interactuar con comentarios 💬
    - Personalizar tu calendario 📅
    - Agregar artículos a tu lista de la compra 🛒
    - ¡Y compartirlo todo! 🌐

    Ir a CalendPy:
    https://calendpy.noxuscmmd.uk/

    El equipo de CalendPy
    """
    alt.attach(MIMEText(text, "plain"))  # Adjuntamos la versión de texto plano

    
    #Cuerpo del mensaje en HTML con imagen
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd;">
          <img src="cid:logo" style="max-width: 200px; display: block; margin: 0 auto;">
          <h2 style="color: #2c3e50;">¡Hola {username}!</h2>
          <p>¡Bienvenido a CalendPy! 🎉</p>
          <p>Estamos emocionados de tenerte con nosotros. Ahora puedes:</p>
          <ul>
            <li>Organizar tus comidas/cenas 🍽️</li>
            <li>Interactuar con comentarios 💬</li>
            <li>Personalizar tu calendario 📅</li>
            <li>Agregar artículos a tu lista de la compra 🛒</li>
            <li>¡Además puedes compartirlo todo! 🌐</li>
          </ul>

          <div style="text-align: center; margin: 30px 0;">
            <a href="https://calendpy.noxuscmmd.uk/" style="
                display: inline-block;
                padding: 12px 24px;
                font-size: 16px;
                color: #ffffff;
                background-color: #3498db;
                text-decoration: none;
                border-radius: 5px;
            ">
              Ir a CalendPy
            </a>
          </div>

          <div style="background-color: #f8f9fa; padding: 15px; margin-top: 20px; text-align: center;">
            <p>¡Gracias por unirte a nuestra comunidad!</p>
            <p>El equipo de CaleCalendPy</p>
          </div>
        </div>
      </body>
    </html>
    """

    alt.attach(MIMEText(html, "html"))  #Parte HTML del mensaje

    message.attach(alt)  #Adjuntamos el texto alternativo al mensaje principal

    #Abrimos el logo en modo binario para incluirlo
    try:
        logo_path = files(static) / "logo.png"  #Ruta al logo
        with open(logo_path, "rb") as img_file:
            img = MIMEImage(img_file.read())  #Creamos parte MIME con la imagen
            img.add_header("Content-ID", "<logo>")  #Content-ID para referenciarlo
            img.add_header("Content-Disposition", "inline", filename="logo.png")  #Marcamos como imagen embebida
            message.attach(img)  #Adjuntamos la imagen al mensaje
    except Exception as e:
        print("Error cargando logo:", e)  #Mostramos error si falla la carga del logo

    #Envío del mensaje
    try:
        #Creamos la conexión con el servidor
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo() #Identificamos al cliente y obtenemos capacidades del servidor
            server.starttls()  #Iniciamos conexión usando TLS
            server.login(SMTP_USER, SMTP_PASSWORD)  #Nos loggeamos en el servidor
            server.sendmail(SMTP_USER, email, message.as_string())  #Enviamos el mensaje
        print(f"Correo de bienvenida enviado a {email}")
        return rx.redirect("/login")  #Redirigimos al login tras el envío
    #Si algo falla, mostramos el fallo
    except Exception as e:
        print(f"Error enviando correo de bienvenida: {e}")
        return rx.toast.error(f"Error al enviar correo: {str(e)}")

#Mensaje para resetear la contraseña
def send_password_reset_email(email: str, reset_link: str):
    #Creamos el mensaje multiparte html + imágenes
    msg = MIMEMultipart("related")
    msg["Subject"] = "Restablece tu contraseña | CalendPy"
    msg["From"] = SMTP_USER
    msg["To"] = email

    #Creamos la parte alternativa, texto plano + HTML
    alt = MIMEMultipart("alternative")

    #Texto plano
    text = f"""\
    Hola,

    Hemos recibido una solicitud para restablecer tu contraseña.
    Pulsa en el siguiente enlace para crear una nueva contraseña:

    {reset_link}

    Si no solicitaste este cambio, puedes ignorar este correo.

    ¡Gracias por confiar en CalendPy!
    """
    alt.attach(MIMEText(text, "plain"))

    #Cuerpo del mensaje en HTML con imagen
    html = f"""\
    <html>
      <body style="font-family: Arial, sans-serif; margin:0; padding:0;">
        <div style="max-width:600px; margin:auto; padding:20px; border:1px solid #ddd;">
          <img src="cid:logo" style="max-width:200px; display:block; margin:0 auto;">

          <h2 style="color:#2c3e50; margin-top:20px;">Restablece tu contraseña</h2>
          <p>Hemos recibido una solicitud para cambiar la contraseña de tu cuenta de CalendPy.</p>
          <p>Para crear una nueva contraseña, haz clic en el botón de abajo:</p>

          <div style="text-align:center; margin:30px 0;">
            <a href="{reset_link}" style="
                display:inline-block;
                padding:12px 24px;
                font-size:16px;
                color:#ffffff;
                background-color:#3498db;
                text-decoration:none;
                border-radius:5px;
            ">
              Restablecer contraseña
            </a>
          </div>

          <p>Si no solicitaste este cambio, puedes ignorar este correo sin problema.</p>

          <div style="background-color:#f8f9fa; padding:15px; margin-top:20px; text-align:center;">
            <p>¡Gracias por confiar en nosotros!</p>
            <p>El equipo de CalendPy</p>
          </div>
        </div>
      </body>
    </html>
    """
    alt.attach(MIMEText(html, "html")) #Parte HTML del mensaje

     #Adjuntamos el texto alternativo al mensaje principal
    msg.attach(alt)

    #Abrimos el logo en modo binario para incluirlo
    try:
        logo_path = files(static) / "logo.png" #Ruta al logo
        with open(logo_path, "rb") as img_file:
            img = MIMEImage(img_file.read()) #Creamos parte MIME con la imagen
            img.add_header("Content-ID", "<logo>") #Content-ID para referenciarlo
            img.add_header("Content-Disposition", "inline", filename="logo.png") #Marcamos como imagen embebida
            msg.attach(img) #Adjuntamos la imagen al mensaje
            
    except Exception as e:
        print("Error cargando logo:", e) #Mostramos error si falla la carga del logo

    #Envío del mensaje
    try:
        #Creamos la conexión con el servidor
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo() #Identificamos al cliente y obtenemos capacidades del servidor
            server.starttls() #Iniciamos conexión usando TLS
            server.login(SMTP_USER, SMTP_PASSWORD) #Nos loggeamos en el servidor
            server.sendmail(SMTP_USER, email, msg.as_string()) #Enviamos el mensaje
        print(f"Correo de restablecimiento enviado a {email}")
        return rx.redirect("/login") #Redirigimos al login tras el envío
    #Si algo falla, mostramos el fallo
    except Exception as e:
        print(f"Error enviando correo de bienvenida: {e}")
        return rx.toast.error(f"Error al enviar correo: {str(e)}")