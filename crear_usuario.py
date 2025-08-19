import pymysql
from werkzeug.security import generate_password_hash

# Configuración de conexión a tu BD en línea
DB_HOST = "isladigital.xyz"
DB_USER = "nelson"
DB_PASS = "3011551141.Arias"
DB_NAME = "bd_hostal"
DB_PORT = 3311  # Puerto de tu servidor remoto

def crear_usuario(username, password):
    # Hashear la contraseña
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            charset="utf8mb4",
            autocommit=False,
            port=DB_PORT
        )
        cur = conn.cursor()

        # Verificar si la tabla usuarios existe (solo la crea si no está)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)

        # Verificar si el usuario ya existe
        cur.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        if cur.fetchone():
            print(f"⚠️ Error: el usuario '{username}' ya existe.")
            return

        # Insertar usuario en la tabla
        cur.execute(
            "INSERT INTO usuarios (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        conn.commit()
        print(f"✅ Usuario '{username}' creado con éxito en MySQL remoto.")

    except Exception as e:
        print("❌ Error al crear usuario:", e)
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    username = input("Usuario: ")
    password = input("Contraseña: ")  # <-- ahora se ve lo que escribes
    crear_usuario(username, password)
