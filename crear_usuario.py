import MySQLdb
from werkzeug.security import generate_password_hash

# Configuración de conexión
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = ""
DB_NAME = "hostal"

def crear_usuario(username, password):
    # Hashear la contraseña
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

    try:
        conn = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME)
        cur = conn.cursor()

        # Verificar si el usuario ya existe
        cur.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        if cur.fetchone():
            print(f"Error: el usuario '{username}' ya existe.")
            return

        # Insertar usuario en la tabla
        cur.execute(
            "INSERT INTO usuarios (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        conn.commit()
        print(f"Usuario '{username}' creado con éxito.")

    except Exception as e:
        print("Error al crear usuario:", e)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    username = input("Usuario: ")
    password = input("Contraseña: ")

    crear_usuario(username, password)
