import sqlite3
import uuid
import datetime

# Función para generar UUID
def generate_uuid():
    return str(uuid.uuid4())

# Conexión a la base de datos
conn = sqlite3.connect('database/reservations.db')
cursor = conn.cursor()

# Habilitar las claves foráneas
cursor.execute('PRAGMA foreign_keys = ON')

# Crear tabla de usuarios
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)
''')

# Crear tabla de reservaciones
cursor.execute('''
CREATE TABLE IF NOT EXISTS reservations (
    id TEXT PRIMARY KEY DEFAULT (hex(randomblob(16))),
    user_id TEXT NOT NULL,
    service_name TEXT NOT NULL,
    appointment_date TIMESTAMP NOT NULL,
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

# -- Insertar usuario admin
cursor.execute('''
INSERT INTO users (id, email, name, password_hash, role, created_at, last_login)
VALUES ('7b9b1573-e7c2-4fa1-bedf-803d1340e923', 'anthdel22@gmail.com', 'Anthony Delgado', '$2b$12$yz8Ic..i8uY6zQUITkzyMe5q6kICMukbcmUIINWyeiJq/s.x66Snu','admin', DATETIME('now'), DATETIME('now'))
''')

# -- Insertar usuario normal
cursor.execute('''
INSERT INTO users (id, email, name, password_hash, role, created_at, last_login)
VALUES ('f671d864-378a-4424-9d1c-86c7b7f95276', 'anthonycdm2212@gmail.com', 'Regular User', '$2b$12$s0dXrQjEoop6.JJ2i1bdmO3XkO9kvvNrjKsLTepA/GQZyQ0hBTSpW','user', DATETIME('now'), DATETIME('now'))
''')

# -- Insertar una reservación para el usuario admin
cursor.execute('''
INSERT INTO reservations (id, user_id, service_name, appointment_date, notes, created_at, updated_at)
VALUES ('529f29f9-1083-4497-b352-71852c102e53', '7b9b1573-e7c2-4fa1-bedf-803d1340e923', 'Admin Meeting', '2025-04-10 10:00:00', 'Reunión de administración', DATETIME('now'), DATETIME('now'))
''')

# -- Insertar una reservación para el usuario normal
cursor.execute('''
INSERT INTO reservations (id, user_id, service_name, appointment_date, notes, created_at, updated_at)
VALUES ('d02215f7-c99b-46a7-9e6f-45b8ba2d3517', 'f671d864-378a-4424-9d1c-86c7b7f95276', 'User Consultation', '2025-04-11 15:00:00', 'Consulta general', DATETIME('now'), DATETIME('now'))
''')

cursor.execute('''
SELECT LENGTH(password_hash) FROM users WHERE email = 'anthdel22@gmail.com';
''')
