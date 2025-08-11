import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from calendar_helper import create_calendar_event
import json
import smtplib
from email.mime.text import MIMEText
import requests

load_dotenv()  # Cargar variables de entorno desde .env

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5000",
            "https://scheduler-dda37.web.app"
        ]
    }
})

# Cargar configuración desde config.json
with open('config.json', 'r') as f:
    config = json.load(f)



SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASS = os.getenv('SENDER_PASS')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')
ADMIN_VIVI_WHATSAPP = os.getenv('VIVI_NUMBER')
ADMIN_CATHE_WHATSAPP = os.getenv('CATHE_NUMBER')
VIVI_WHATSAPP_API = os.getenv('VIVI_API_URL')
CATHE_WHATSAPP_API = os.getenv('CATHE_API_URL')
VIVI_WHATSAPP_API_KEY = os.getenv('VIVI_API_KEY')
CATHE_WHATSAPP_API_KEY = os.getenv('CATHE_API_KEY')


# SENDER_EMAIL = config["email"]["sender"]["email"]
# SENDER_PASS = config["email"]["sender"]["password"]
# RECEIVER_EMAIL = config["email"]["receiver"]["email"]
# ADMIN_VIVI_WHATSAPP = config["whatsapp"]["artist"]["viviana"]["number"]
# ADMIN_CATHE_WHATSAPP = config["whatsapp"]["artist"]["cathe"]["number"]
# VIVI_WHATSAPP_API = config["whatsapp"]["artist"]["viviana"]["api_url"]
# CATHE_WHATSAPP_API = config["whatsapp"]["artist"]["cathe"]["api_url"]
# VIVI_WHATSAPP_API_KEY = config["whatsapp"]["artist"]["viviana"]["api_key"]
# CATHE_WHATSAPP_API_KEY = config["whatsapp"]["artist"]["cathe"]["api_key"]

# @app.route('/')
# def home():
#     # return render_template('index.html')

# @app.route('/admin')
# def admin():
#     # return render_template('admin.html')

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Backend funcionando correctamente"})

# Ruta de prueba para verificar que el backend funciona
@app.route('/api/test')
def test():
    return jsonify({"status": "ok", "message": "Backend funcionando!"})


@app.route('/api/book', methods=['POST'])
def book_appointment():
    data = request.json

    name = data.get('name')
    phone = data.get('phone')
    artist = data.get('artist')
    service_feet = data.get('serviceFeet')
    service_hands = data.get('serviceHands')
    date = data.get('date')
    time = data.get('time')

    # Enviar notificaciones
    send_email_notification(name, phone, artist, service_feet, service_hands, date, time)
    send_whatsapp_to_admin(name, phone, artist, service_feet, service_hands, date, time)
     
    # Crear texto de servicios para el evento
    services_text = ""
    if service_feet != "NO APLICA":
        services_text += f"Pies: {service_feet}\n"
    if service_hands != "NO APLICA":
        services_text += f"Manos: {service_hands}"

    # Asignar calendar_id dinámicamente
    if artist == 'viviana':
        calendar_id = '7fac5116bf5a2aa34b2988800d86ce29f529117d6b35d6ebf8c9aaf29e1f65bc@group.calendar.google.com'
    else:  # Por defecto será Cathe
        calendar_id = 'spa.turquesa.manizales@gmail.com'

    # Crear evento en Google Calendar
    try:
        event_link = create_calendar_event(
            name=name,
            phone=phone,
            date_str=date,        # formato 'YYYY-MM-DD'
            time_range=time,      # ejemplo '14:00-15:00'
            artist=artist,        # 'viviana' o 'cathe'
            services=services_text,
            calendar_id=calendar_id  # o usa un calendar_id propio
        )
        # print(event_link['summary'], event_link['start'], event_link['htmlLink'])
        print("✅ Evento creado en el link:", event_link.get('htmlLink'))
    except Exception as e:
        print("❌ Error al crear evento en Google Calendar:", e)

    return jsonify({"status": "success"})

# -------------------------------
# ✉️ Enviar email al administrador
# -------------------------------
def send_email_notification(name, phone, artist, service_feet, service_hands, date, time):
    subject = f"📢[{artist.capitalize()}]: Nueva Reserva Agendada"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="margin-bottom: 40px;">🔔 ¡Nueva reserva recibida!</h2>
            <p><strong>👤 Cliente:</strong> {name}</p>
            <p><strong>📞 Teléfono:</strong> {phone}</p>
            <p><strong>🦶 Pies:</strong> {service_feet}</p>
            <p><strong>🖐️ Manos:</strong> {service_hands}</p>
            <p><strong>📅 Fecha:</strong> {date}</p>
            <p><strong>⏰ Horario:</strong> {time}</p>
        </body>
    </html>
    """

    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASS)
            server.send_message(msg)
            print("✅ Email enviado al admin.")
    except Exception as e:
        print("❌ Error al enviar email:", e)

# -------------------------------
# 📲 WhatsApp al administrador
# -------------------------------
def send_whatsapp_to_admin(name, phone, artist, service_feet, service_hands, date, time):
    message = (
        f"    📢*Nueva reserva*\n\n"
        f"👤 {name}\n"
        f"📞 {phone}\n"
        f"🦶 Pies: {service_feet}\n"
        f"🖐️ Manos: {service_hands}\n"
        f"📅 Fecha: {date}\n"
        f"⏰ Horario: {time}"
    )
    
    # Enviar WhatsApp al artista correspondiente
    if artist == 'viviana':
        send_whatsapp_callmebot(ADMIN_VIVI_WHATSAPP, message, VIVI_WHATSAPP_API, VIVI_WHATSAPP_API_KEY)
    else:  # cathe
        send_whatsapp_callmebot(ADMIN_CATHE_WHATSAPP, message, CATHE_WHATSAPP_API, CATHE_WHATSAPP_API_KEY)

# -------------------------------
# Función genérica para CallMeBot
# -------------------------------
def send_whatsapp_callmebot(phone, message, api_url, api_key):
    try:
        payload = {
            'phone': phone.replace("+", ""),
            'text': message,
            'apikey': api_key
        }
        response = requests.get(api_url, params=payload)
        print("✅ WhatsApp enviado:", response.text)
    except Exception as e:
        print("❌ Error al enviar WhatsApp:", e)

# -------------------------------
# if __name__ == '__main__':
#     app.run(debug=True, port=5001)  # Cambia el puerto si es necesario
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))  # Usa el puerto de Render o 5001 por defecto
    app.run(host='0.0.0.0', port=port)  # ¡Cambia host a 0.0.0.0!