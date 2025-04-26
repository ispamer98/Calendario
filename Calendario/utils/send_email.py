import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def send_welcome_email(email, username):
    # Configuración del servidor SMTP
    servidor_smtp = "smtp.gmail.com"
    puerto = 587
    admin = "verificacionespython@gmail.com"
    pasw = "cmblnedixejwrqag"

    # Crear mensaje multipart
    mensaje = MIMEMultipart('related')
    mensaje['From'] = admin
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

    # Cargar y adjuntar imagen (cambiar la ruta de tu imagen)
    with open('assets/logo.png', 'rb') as img_file:
        img = MIMEImage(img_file.read())
        img.add_header('Content-ID', '<logo>')
        mensaje.attach(img)

    try:
        with smtplib.SMTP(servidor_smtp, puerto) as server:
            server.starttls()
            server.login(admin, pasw)
            server.sendmail(admin, email, mensaje.as_string())
        print(f"Correo de bienvenida enviado a {email}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")