import os
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()
import uuid
from datetime import datetime, timezone
import bcrypt
import random

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def generate_uuid():
    return str(uuid.uuid4())


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


# Create users
"""
try:
    response = (
        supabase.table("users")
        .insert([
            {"id": generate_uuid(), "email": "anthdel22@gmail.com", "name": "Anthony Delgado", "password_hash": hash_password("9092$!1222"), "role": "admin", "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), "last_login": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")},
            {"id": generate_uuid(), "email": "usuario1@gmail.com", "name": "Usuario Uno", "password_hash": hash_password("123456789$Ad"), "role": "user", "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), "last_login": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")},
        ])
        .execute()
    )
    print(response)
except Exception as e:
    print("Something went wrong", e)
"""

# Create Reservation
"""
def create_reservations():
    try:
        users_response = supabase.table("users").select("id").execute()
        users = users_response.data

        services = ["Consultoría Técnica", "Revisión Médica", "Asesoría Financiera"]

        reservations = []
        for user in users:
            reservations.append({
                "id": generate_uuid(),
                "user_id": user["id"],
                "service_name": random.choice(services),
                "appointment_date": (datetime.now(timezone.utc)).strftime("%Y-%m-%d %H:%M:%S"),
                "status": "scheduled",
                "notes": "Reservación generada automáticamente",
                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            })

        response = supabase.table("reservations").insert(reservations).execute()
        print("Reservaciones insertadas:", response)
    except Exception as e:
        print("Something went wrong", e)


# Ejecutar la función
create_reservations()
"""