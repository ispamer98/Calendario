import smtplib

def send_welcome_email(email, username):
    # Configuración del servidor SMTP (Gmail en este ejemplo)
    servidor_smtp = "smtp.gmail.com"
    puerto = 587
    admin = "verificacionespython@gmail.com"
    pasw = "cmblnedixejwrqag"  # Reemplaza con tu contraseña de aplicación

    # Configuración del mensaje de bienvenida
    asunto = "¡Bienvenido a tu Calendario!"
    cuerpo = f"""
    Hola {username},

    ¡Bienvenido a tu Calendario!

    Estamos emocionados de tenerte con nosotros. Ahora puedes organizar tus comidas/cenas, e interactuar con los comentarios.

    ¡Gracias por unirte a nuestra comunidad!

    Saludos,
    El equipo de Calendario
    """
    correo = f"Subject: {asunto}\n\n{cuerpo}"

    try:
        with smtplib.SMTP(servidor_smtp, puerto) as server:
            server.starttls()
            server.login(admin, pasw)
            server.sendmail(admin, email, correo.encode('utf-8'))
        print(f"Correo de bienvenida enviado a {email}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

