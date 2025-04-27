import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import dotenv
from importlib.resources import files

from Calendario import static


dotenv.load_dotenv()

SMTP_SERVER = os.environ.get("SMTP_SERVER")  # O el servidor que uses (ej: smtp.office365.com, etc)
SMTP_PORT = os.environ.get("SMTP_PORT")
SMTP_USER = os.environ.get("SMTP_USER")  # Cambiar por tu correo
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")  # Cambiar por tu contraseña o token de app
def send_welcome_email(email, username):
    # Configuración del servidor SMTP

    # Crear mensaje multipart
    mensaje = MIMEMultipart('related')
    mensaje['From'] = SMTP_USER
    mensaje['To'] = email
    mensaje['Subject'] = "¡Bienvenido a tu Calendario!"


    # Cuerpo del mensaje en HTML con imagen
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
            <a href="https://calendario-red-ocean.reflex.run/" style="
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


    # Parte HTML del mensaje
    parte_html = MIMEText(html, 'html')
    mensaje.attach(parte_html)

    logo_path = files(static) / "logo.png"
    with open(logo_path, "rb") as img_file:
        img = MIMEImage(img_file.read())
        img.add_header('Content-ID', '<logo>')
        mensaje.attach(img)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, email, mensaje.as_string())
        print(f"Correo de bienvenida enviado a {email}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")



def send_password_reset_email(email: str, reset_link: str):
    # Configuración SMTP
    msg = MIMEMultipart("related")
    msg["Subject"] = "Restablece tu contraseña | CalendPy"
    msg["From"] = SMTP_USER
    msg["To"] = email

    # 1) Creamos la parte alternativa (texto plano + HTML)
    alt = MIMEMultipart("alternative")

    # Texto plano
    text = f"""\
    Hola,

    Hemos recibido una solicitud para restablecer tu contraseña.
    Pulsa en el siguiente enlace para crear una nueva contraseña:

    {reset_link}

    Si no solicitaste este cambio, puedes ignorar este correo.

    ¡Gracias por confiar en CalendPy!
    """
    alt.attach(MIMEText(text, "plain"))

    # HTML con el mismo diseño que el de bienvenida
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
    alt.attach(MIMEText(html, "html"))

    # Adjuntamos el alternative al mensaje principal
    msg.attach(alt)

    # 2) Adjuntar el logo inline
    try:
        logo_path = files(static) / "logo.png"
        with open(logo_path, "rb") as img_file:
            img = MIMEImage(img_file.read())
            img.add_header("Content-ID", "<logo>")
            img.add_header("Content-Disposition", "inline", filename="logo.png")
            msg.attach(img)
    except Exception as e:
        print("Error cargando logo:", e)

    # 3) Envío SMTP
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, email, msg.as_string())
        print(f"Correo de restablecimiento enviado a {email}")
    except Exception as e:
        print(f"Error enviando correo de restablecimiento: {e}")
