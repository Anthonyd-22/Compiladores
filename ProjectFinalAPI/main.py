import zoneinfo
from flask import Flask, request, jsonify, render_template
import uuid
import bcrypt
from datetime import datetime, timedelta, timezone
import os
import jwt
from functools import wraps
from dotenv import load_dotenv
from supabase import create_client, Client
from flask_cors import CORS

try:
    load_dotenv()
except Exception as e:
    print("Not needed to load dotenv", e)
    pass

APP_CLIENT = os.getenv("APP_CLIENT")
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=[APP_CLIENT])
# CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5254"])
# Secret key to encode/decode JWT
SECRET_KEY = os.getenv("SECRET_KEY")
API_VERSION = os.getenv("API_VERSION")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")


def get_db_connection():
    supabase: Client = create_client(url, key)
    return supabase

def generate_uuid():
    return str(uuid.uuid4())

def get_current_time():
    utc_time = datetime.now(timezone.utc)
    est = zoneinfo.ZoneInfo('America/Panama')
    est_time = utc_time.astimezone(est)
    return est_time.strftime("%Y-%m-%d %H:%M:%S")

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

# Helper function to check if the user is admin
def is_admin(user_id):
    supabase = get_db_connection()
    response = (
        supabase.table("users")
        .select("role")
        .eq("id", user_id)
        .single()
        .execute()
    )
    user = response.data
    return user and user['role'] == 'admin'

# ====================================
# JWT Token Decoding Function
# ====================================
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Buscar token en el encabezado Authorization
        if 'Authorization' in request.headers:
            print(request.headers)
            parts = request.headers['Authorization'].split(" ")
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]

        # Si no hay token en header, buscarlo en cookies
        if not token and 'access_token' in request.cookies:
            token = request.cookies.get('access_token')

        if not token:
            return jsonify({"message": "Token is missing!"}), 403

        try:
            # Decodificar el token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data['user_id']

            # Verificar expiración
            token_exp = datetime.fromtimestamp(data['exp'], tz=timezone.utc)
            if datetime.now(timezone.utc) > token_exp:
                return jsonify({"message": "Token has expired!"}), 403

        except Exception as e:
            return jsonify({"message": "Token is invalid!"}), 403

        return f(current_user_id, *args, **kwargs)

    return decorated_function


# ====================================
# Authentication: Login and Generate JWT
# ====================================

@app.route('/login', methods=['POST'])
def login():
    supabase = get_db_connection()
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        response = (
            supabase.table("users")
            .select("*")
            .eq("email", email)
            .maybe_single()
            .execute()
        )
        if response is None:
            return jsonify({"message": "User not found!"}), 404

        user = response.data
        if user is None or not verify_password(password, user["password_hash"]):
            return jsonify({"error": "Invalid credentials"}), 401


        # Crear el token JWT con fecha y hora UTC-aware
        payload = {
            "user_id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)  # Expiración con timezone-aware
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        supabase.table("users").update({"last_login": get_current_time()}).eq("id", user["id"]).execute()
        return jsonify({"message": "Success Login", "token": token, "user": dict(user)}), 200
    except Exception as e:
        return jsonify({"message": "Something went wrong!", "error": str(e)}), 500

# ====================================
# CRUD for Users (Secured with JWT)
# ====================================

# Endpoint para crear un nuevo usuario
@app.route('/users', methods=['POST'])
@token_required
def create_user(current_user_id):
    supabase = get_db_connection()
    try:
        if not is_admin(current_user_id):
            return jsonify({"error": "You are not authorized to create a user"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": "No fields provided to create an user"}), 400

        email = data.get('email')
        name = data.get('name')
        password = data.get('password')
        role = data.get('role', 'user')

        if not email or not name or not password:
            return jsonify({"error": "Email, name and password are required"}), 400

        user_id = generate_uuid()
        current_time = get_current_time()
        password_hash = hash_password(password)
        supabase.table("users").insert([
                {"id": user_id,
                 "email": email,
                 "name": name,
                 "password_hash": password_hash,
                 "role": role,
                 "created_at": current_time,
                 "last_login": current_time
                 }
            ]).execute()
        return jsonify({"message": "User created", "user_id": user_id}), 201
    except Exception as e:
        return jsonify({"message": "Something went wrong!", "error": str(e)}), 500


# Endpoint para obtener todos los usuarios
@app.route('/users', methods=['GET'])
@token_required
def get_users(current_user_id):
    supabase = get_db_connection()
    try:
        # Solo los administradores pueden ver todos los usuarios
        if not is_admin(current_user_id):
            return jsonify({"error": "You are not authorized to view users"}), 403

        response = (
            supabase.table("users")
            .select("*")
            .execute()
        )

        return jsonify([dict(row) for row in response.data]), 200
    except Exception as e:
        return jsonify({"message": "Something went wrong!", "error": str(e)}), 500


@app.route('/users/<user_id>', methods=['GET'])
@token_required
def get_user(current_user_id, user_id):
    supabase = get_db_connection()
    try:
        if current_user_id != user_id and not is_admin(current_user_id):
            return jsonify({"error": "You are not authorized to view this user's information"}), 403

        response = (
            supabase.table("users")
            .select("*")
            .eq("id", user_id)
            .single()
            .execute()
        )
        user = response.data
        if user is None:
            return jsonify({"error": "User not found"}), 404

        return jsonify(dict(user)), 200
    except Exception as e:
        return jsonify({"message": "Something went wrong!", "error": str(e)}), 500


@app.route('/users/<user_id>', methods=['POST'])
@token_required
def update_user(current_user_id, user_id):
    supabase = get_db_connection()
    try:
        if current_user_id != user_id and not is_admin(current_user_id):
            return jsonify({"error": "You are not authorized to update this user's information"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": "No fields provided for update"}), 400

        # Update fields provided
        valid_fields = ["email", "name", "password", "role"]
        params = {key: data[key] for key in valid_fields if key in data}

        params["updated_at"] = get_current_time()

        if "password" in params:
            params["password_hash"] = hash_password(params.pop("password"))

        if not params:
            return jsonify({"error": "No valid fields provided for update"}), 400

        response = (
            supabase.table("users")
            .update(params)
            .eq("id", user_id)
            .execute()
        )

        if not response.data:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "User updated", "updated_fields": params, "updated_user": response.data[0]}), 200


    except Exception as e:
        return jsonify({"message": "Something went wrong!", "error": str(e)}), 500

@app.route('/users/<user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user_id, user_id):
    supabase = get_db_connection()
    try:
        if current_user_id != user_id and not is_admin(current_user_id):
            return jsonify({"error": "You are not authorized to delete this user"}), 403
        response = (
            supabase.table("users")
            .delete()
            .eq("id", user_id)
            .execute()
        )
        if not response.data:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "User deleted"}), 200
    except Exception as e:
        return jsonify({"message": "Something went wrong!", "error": str(e)}), 500


# ====================================
# CRUD for Reservations (Secured with JWT)
# ====================================
@app.route('/reservations', methods=['GET'])
@token_required
def get_reservations(current_user_id):
    supabase = get_db_connection()
    try:
        # Solo los administradores pueden ver todas las reservaciones
        if not is_admin(current_user_id):
            return jsonify({"error": "You are not authorized to view reservations"}), 403

        response = (
            supabase.table("reservations")
            .select("*")
            .execute()
        )
        return jsonify([dict(row) for row in response.data]), 200
    except Exception as e:
        return jsonify({"message": "Something went wrong!", "error": str(e)}), 500

@app.route('/reservations/<reservation_id>', methods=['GET'])
@token_required
def get_single_reservations(current_user_id, reservation_id):
    supabase = get_db_connection()
    try:
        # Solo los administradores pueden ver las reservaciones
        if not is_admin(current_user_id):
            return jsonify({"error": "You are not authorized to view reservations"}), 403

        response = (
            supabase.table("reservations")
            .select("*")
            .eq("id", reservation_id)
            .maybe_single()
            .execute()
        )

        if response is None:
            return jsonify({"error": "Reservation not found"}), 404
        reservation = response.data
        return jsonify(dict(reservation)), 200
    except Exception as e:
        return jsonify({"message": "Something went wrong!", "error": str(e)}), 500


@app.route('/reservations', methods=['POST'])
@token_required
def create_reservation(current_user_id):
    supabase = get_db_connection()
    try:
        data = request.get_json()
        appointment_name = data.get('appointment_name')
        appointment_date = data.get('appointment_date')
        notes = data.get('notes', None)

        if not appointment_name or not appointment_date:
            return jsonify({"error": "appointment_name and appointment_date are required"}), 400

        reservation_id = generate_uuid()
        current_time = get_current_time()

        supabase.table("reservations").insert([
            {"id": reservation_id,
             "user_id": current_user_id,
             "appointment_name": appointment_name,
             "appointment_date": appointment_date,
             "notes": notes,
             "created_at": current_time,
             "updated_at": current_time,
             "status": "scheduled"
             }
        ]).execute()
        return jsonify({"message": "Reservation created", "reservation_id": reservation_id}), 201
    except Exception as e:
        return jsonify({"message": "Something went wrong!", "error": str(e)}), 500

@app.route('/reservations/user/<user_id>', methods=['GET'])
@token_required
def get_user_reservations(current_user_id, user_id):
    supabase = get_db_connection()
    try:
        if current_user_id != user_id and not is_admin(current_user_id):
            return jsonify({"error": "You can only view your own reservations"}), 403

        response = (
            supabase.table("reservations")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        if response.data is None:
            return jsonify({"error": "User not found"}), 404

        reservations = response.data

        return jsonify([dict(row) for row in reservations]), 200
    except Exception as e:
        return jsonify({"message": "Something went wrong!", "error": str(e)}), 500


@app.route('/reservations/<reservation_id>', methods=['POST'])
@token_required
def update_reservation(current_user_id, reservation_id):
    supabase = get_db_connection()
    try:
        response = (
            supabase.table("reservations")
            .select("id, user_id")
            .eq("id", reservation_id)
            .maybe_single()
            .execute()
        )

        if response is None:
            return jsonify({"error": "Reservation not found"}), 404

        reservation = response.data

        if current_user_id != reservation["user_id"] and not is_admin(current_user_id):
            return jsonify({"error": "You are not authorized to update this reservation"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": "No fields provided for update"}), 400

        valid_fields = ["appointment_name", "appointment_date", "status", "notes"]
        params = {key: data[key] for key in valid_fields if key in data}
        params["updated_at"] = get_current_time()

        if "status" in params and params["status"] not in ('scheduled', 'completed', 'cancelled'):
            return jsonify({"error": "Invalid status"}), 400


        (supabase.table("reservations")
         .update(params)
         .eq("id", reservation_id)
         .execute())

        return jsonify({"message": "Reservation updated", "updates": list(params.keys()), "reservation_id": reservation_id}), 200

    except Exception as e:
        return jsonify({"message": "Something went wrong!", "error": str(e)}), 500


@app.route('/reservations/<reservation_id>', methods=['DELETE'])
@token_required
def delete_reservation(current_user_id, reservation_id):
    supabase = get_db_connection()
    try:
        response = (
            supabase.table("reservations")
            .select("id, user_id")
            .eq("id", reservation_id)
            .maybe_single()
            .execute()
        )

        if response is None:
            return jsonify({"error": "Reservation not found"}), 404

        reservation = response.data

        if current_user_id != reservation["user_id"] and not is_admin(current_user_id):
            return jsonify({"error": "You are not authorized to update this reservation"}), 403


        supabase.table("reservations").delete().eq("id", reservation_id).execute()

        return jsonify({"message": "Reservation deleted"}), 200
    except Exception as e:
        return jsonify({"message": "Something went wrong!", "error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return render_template("welcome.html", api_version=API_VERSION)


if __name__ == '__main__':
    app.run(port=8080)
