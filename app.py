from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_file
from datetime import datetime, time
import MySQLdb
from openpyxl import Workbook
from openpyxl.styles import Font, Border, Side, PatternFill, Alignment, NamedStyle
from openpyxl.utils import get_column_letter
from werkzeug.security import check_password_hash
import pymysql

app = Flask(__name__)
app.secret_key = "una_clave_muy_secreta_y_larga"  # 🔑 obligatorio para sesión y flash

# ----------------- CONEXIÓN DB -----------------
def get_db_connection():
    """Obtiene una conexión a la base de datos con manejo de errores mejorado"""
    try:
        print("🔍 Intentando conectar a MySQL...")
        print(f"   Host: localhost")
        print(f"   Usuario: nelson")
        print(f"   Puerto: 3311")  # actualizado el puerto mostrado
        print(f"   Base de datos: bd_hostal")
        
        conn = pymysql.connect(
            host='isladigital.xyz',  # Asegurándonos que sea localhost
            user='nelson',
            password='3011551141.Arias',
            database='bd_hostal',
            charset='utf8mb4',
            autocommit=False,
            port=3311  # cambiado de 3306 a 3311
        )
        print("✅ Conexión exitosa a MySQL", flush=True)
        return conn
    except pymysql.err.OperationalError as e:
        error_code = e.args[0]
        if error_code == 2003:
            print("❌ Error 2003: No se puede conectar al servidor MySQL", flush=True)
            print("💡 Soluciones posibles:")
            print("   1. Verifica que MySQL esté ejecutándose: 'net start mysql' (Windows)")
            print("   2. Verifica que MySQL esté en el puerto 3311")  # actualizado el puerto en el mensaje
            print("   3. Intenta conectarte manualmente: mysql -u nelson -p -P 3311")  # agregado -P 3311
        elif error_code == 1045:
            print("❌ Error 1045: Acceso denegado - credenciales incorrectas")
            print("💡 Verifica usuario y contraseña en MySQL")
        elif error_code == 1049:
            print("❌ Error 1049: Base de datos 'bd_hostal' no existe")
            print("💡 Crea la base de datos: CREATE DATABASE bd_hostal;")
        else:
            print(f"❌ Error MySQL {error_code}: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado de conexión: {e}")
        return None

def get_current_user_id():
    """Obtiene el ID del usuario actual desde la sesión"""
    return session.get('usuario_id')

def require_user_session():
    """Verifica que el usuario esté logueado y retorna su ID"""
    user_id = get_current_user_id()
    if not user_id:
        flash("Debes iniciar sesión para acceder a esta función", "error")
        return None
    return user_id

# ----------------- LOGIN -----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.is_json:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
    else:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

    # Validación de campos vacíos
    if not username or not password:
        error_msg = "Usuario y contraseña son requeridos"
        if request.is_json:
            return jsonify({"success": False, "error": error_msg})
        else:
            flash(error_msg, "error")
            return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        error_msg = "Error de conexión a la base de datos. Verifica que MySQL esté ejecutándose."
        if request.is_json:
            return jsonify({"success": False, "error": error_msg})
        else:
            flash(error_msg, "error")
            return redirect(url_for('login'))

    try:
        cur = conn.cursor()
        cur.execute("SELECT id, username, password FROM usuarios WHERE username = %s", (username,))
        user = cur.fetchone()
        
        if user and check_password_hash(user[2], password):
            session['usuario_id'] = user[0]
            session['usuario'] = user[1]
            if request.is_json:
                return jsonify({"success": True, "redirect": url_for('index')})
            else:
                flash(f"Bienvenido, {username}!", "success")
                return redirect(url_for('index'))
        else:
            error_msg = "Usuario o contraseña incorrectos"
            if request.is_json:
                return jsonify({"success": False, "error": error_msg})
            else:
                flash(error_msg, "error")
                return redirect(url_for('login'))
            
    except pymysql.MySQLError as e:
        print(f"Error MySQL en login: {e}")
        error_msg = "Error en el sistema de autenticación"
        if request.is_json:
            return jsonify({"success": False, "error": error_msg})
        else:
            flash(error_msg, "error")
            return redirect(url_for('login'))
    except Exception as e:
        print(f"Error inesperado en login: {e}")
        error_msg = "Error interno del servidor"
        if request.is_json:
            return jsonify({"success": False, "error": error_msg})
        else:
            flash(error_msg, "error")
            return redirect(url_for('login'))
    finally:
        if 'cur' in locals():
            cur.close()
        if conn:
            conn.close()

# ----------------- LOGOUT -----------------
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # limpia la sesión
    flash("Sesión cerrada con éxito", "success")
    return redirect(url_for('login'))

# ----------------- PROTECCIÓN DE RUTAS -----------------
@app.before_request
def require_login():
    rutas_libres = {'login', 'static'}
    if request.endpoint not in rutas_libres and 'usuario_id' not in session:
        return redirect(url_for('login'))

@app.route('/test-db')
def test_db():
    """Ruta para probar la conexión a la base de datos con diagnóstico detallado"""
    print("🧪 Ejecutando prueba de conexión...")
    
    try:
        import pymysql
        print("✅ Módulo pymysql importado correctamente")
    except ImportError:
        return jsonify({"success": False, "error": "pymysql no está instalado. Ejecuta: pip install pymysql"})
    
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT VERSION()")
            version = cur.fetchone()
            cur.execute("SELECT DATABASE()")
            database = cur.fetchone()
            cur.close()
            conn.close()
            
            return jsonify({
                "success": True, 
                "message": "✅ Conexión a base de datos exitosa",
                "mysql_version": version[0] if version else "Desconocida",
                "database": database[0] if database else "Desconocida"
            })
        except Exception as e:
            return jsonify({"success": False, "error": f"Error en query: {str(e)}"})
    else:
        return jsonify({
            "success": False, 
            "error": "❌ No se pudo conectar a la base de datos. Revisa la consola para más detalles."
        })

# ----------------- INDEX -----------------
@app.route('/')
def index():
    user_id = require_user_session()
    if not user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash("Error de conexión a la base de datos")
        return render_template('index.html', habitaciones=[], rooms=[])

    try:
        cur = conn.cursor()

        cur.execute("SELECT id, numero, descripcion, estado FROM habitaciones WHERE usuario_id = %s ORDER BY numero", (user_id,))
        habitaciones_db = cur.fetchall()

        rooms = []
        for h in habitaciones_db:
            room_id, numero, descripcion, estado = h

            cur.execute("""
                SELECT nombre, telefono, observacion, check_out, id, check_in, valor, tipo_doc, numero_doc, procedencia
                FROM clientes 
                WHERE habitacion_id = %s AND (check_out IS NULL OR check_out > NOW()) 
                ORDER BY check_in DESC
            """, (room_id,))
            clientes = cur.fetchall()

            inquilino_principal = clientes[0][0] if clientes else None
            telefono = clientes[0][1] if clientes else None
            observacion = clientes[0][2] if clientes else None
            fecha_salida = clientes[0][3] if clientes and clientes[0][3] else None
            cliente_id = clientes[0][4] if clientes else None
            fecha_ingreso = clientes[0][5] if clientes and clientes[0][5] else None
            valor = clientes[0][6] if clientes and clientes[0][6] else None
            tipo_doc = clientes[0][7] if clientes and clientes[0][7] else None
            numero_doc = clientes[0][8] if clientes and clientes[0][8] else None
            procedencia = clientes[0][9] if clientes and clientes[0][9] else None

            dias_ocupada = 0
            if fecha_ingreso and fecha_salida:
                dias_ocupada = (fecha_salida - fecha_ingreso).days
                if dias_ocupada <= 0:
                    dias_ocupada = 1  # Minimum 1 day
            elif fecha_ingreso:
                dias_ocupada = (datetime.now() - fecha_ingreso).days + 1

            if estado == 'ocupada' and dias_ocupada >= 30:
                cur.execute("UPDATE habitaciones SET estado = 'mensualidad' WHERE id = %s AND usuario_id = %s", (room_id, user_id))
                estado = 'mensualidad'
                conn.commit()

            rooms.append({
                "id": room_id,
                "numero": numero,
                "descripcion": descripcion,
                "estado": estado,
                "inquilino_principal": inquilino_principal,
                "telefono": telefono,
                "observacion": observacion,
                "fecha_salida": fecha_salida,
                "fecha_ingreso": fecha_ingreso,
                "valor": valor,
                "dias_ocupada": dias_ocupada,
                "num_personas_ocupadas": len(clientes) if clientes else 0,
                "personas_list": [{"nombre": c[0], "telefono": c[1], "id": c[4]} for c in clientes] if clientes else [],
                "cliente_id": cliente_id,
                "tipo_doc": tipo_doc,
                "numero_doc": numero_doc,
                "procedencia": procedencia
            })

        return render_template('index.html', habitaciones=habitaciones_db, rooms=rooms)

    except pymysql.MySQLError as e:
        flash(f"Error en la base de datos: {str(e)}")
        return render_template('index.html', habitaciones=[], rooms=[])
    finally:
        if 'cur' in locals():
            cur.close()
        if conn:
            conn.close()

# ----------------- REGISTRAR -----------------
@app.route('/registrar', methods=['POST'])
def registrar():
    flash("Reserva registrada con éxito")
    return redirect(url_for('index'))

@app.route('/guardar_cliente', methods=['POST'])
def guardar_cliente():
    user_id = require_user_session()
    if not user_id:
        return redirect(url_for('login'))
    
    habitacion_id = request.form['habitacion_id']
    nombre = request.form['nombre']
    telefono = request.form.get('telefono')
    observacion = request.form.get('observacion')
    check_in = request.form['check_in']
    check_out = request.form['check_out']
    valor = request.form['valor']

    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos.', 'error')
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM habitaciones WHERE id = %s AND usuario_id = %s", (habitacion_id, user_id))
        if not cur.fetchone():
            flash('No tienes permisos para modificar esta habitación.', 'error')
            return redirect(url_for('index'))
        
        cur.execute("""SELECT COUNT(*) FROM clientes WHERE habitacion_id = %s AND (check_out IS NULL OR check_out > NOW())""", (habitacion_id,))
        clientes_actuales = cur.fetchone()[0]

        if clientes_actuales >= 4:
            flash('La habitación ha alcanzado el límite máximo de 4 clientes.', 'error')
            return redirect(url_for('index'))

        cur.execute("""INSERT INTO clientes (habitacion_id, nombre, telefono, observacion, check_in, check_out, valor) VALUES (%s, %s, %s, %s, %s, %s, %s)""", (habitacion_id, nombre, telefono, observacion, check_in, check_out, valor))

        cur.execute("""UPDATE habitaciones SET estado = 'ocupada' WHERE id = %s AND usuario_id = %s""", (habitacion_id, user_id))

        conn.commit()
        flash('Cliente registrado y habitación marcada como ocupada.', 'success')

    except pymysql.MySQLError as e:
        conn.rollback()
        flash(f'Error al registrar cliente: {e}', 'danger')
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('index'))

@app.route('/editar_cliente/<int:cliente_id>')
def editar_cliente(cliente_id):
    user_id = require_user_session()
    if not user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos.', 'error')
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        cur.execute("""SELECT c.id, c.nombre, c.tipo_doc, c.numero_doc, c.telefono, c.procedencia, c.check_in, c.check_out, c.valor, c.observacion, c.habitacion_id, h.numero AS habitacion_numero, h.descripcion AS habitacion_descripcion FROM clientes c JOIN habitaciones h ON c.habitacion_id = h.id WHERE c.id = %s AND h.usuario_id = %s""", (cliente_id, user_id))
        cliente = cur.fetchone()

        if not cliente:
            flash('Cliente no encontrado o no tienes permisos para editarlo.', 'error')
            return redirect(url_for('index'))

        return render_template('editar_cliente.html', cliente=cliente)

    except pymysql.MySQLError as e:
        flash(f'Error en la base de datos: {str(e)}', 'error')
        return redirect(url_for('index'))
    finally:
        cur.close()
        conn.close()

@app.route('/actualizar_cliente', methods=['POST'])
def actualizar_cliente():
    user_id = require_user_session()
    if not user_id:
        return redirect(url_for('login'))
    
    try:
        cliente_id_str = request.form.get('cliente_id', '').strip()
        if not cliente_id_str:
            flash('ID de cliente no válido.', 'error')
            return redirect(url_for('index'))
        
        cliente_id = int(cliente_id_str)
        nombre = request.form['nombre']
        tipo_doc = request.form['tipo_doc']
        numero_doc = request.form['numero_doc']
        telefono = request.form['telefono']
        procedencia = request.form['procedencia']

        conn = get_db_connection()
        if not conn:
            flash("Error de conexión a la base de datos", "error")
            return redirect(url_for('index'))

        cur = conn.cursor()
        
        cur.execute("""SELECT c.id FROM clientes c JOIN habitaciones h ON c.habitacion_id = h.id WHERE c.id = %s AND h.usuario_id = %s""", (cliente_id, user_id))
        if not cur.fetchone():
            flash('No tienes permisos para editar este cliente.', 'error')
            return redirect(url_for('index'))
        
        cur.execute("""UPDATE clientes SET nombre = %s, tipo_doc = %s, numero_doc = %s, telefono = %s, procedencia = %s WHERE id = %s""", (nombre, tipo_doc, numero_doc, telefono, procedencia, cliente_id))
        conn.commit()

        flash('Cliente actualizado exitosamente.')
        return redirect(url_for('index'))

    except pymysql.MySQLError as e:
        flash(f'Error en la base de datos: {str(e)}', 'error')
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

    return redirect(url_for('index'))

@app.route('/agregar_cliente_habitacion/<int:habitacion_id>')
def agregar_cliente_habitacion(habitacion_id):
    user_id = require_user_session()
    if not user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos.', 'error')
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        cur.execute("SELECT numero, descripcion FROM habitaciones WHERE id = %s AND usuario_id = %s", (habitacion_id, user_id))
        habitacion = cur.fetchone()

        if not habitacion:
            flash('Habitación no encontrada o no tienes permisos para acceder a ella.', 'error')
            return redirect(url_for('index'))

        cur.execute("""SELECT COUNT(*) FROM clientes WHERE habitacion_id = %s AND (check_out IS NULL OR check_out > NOW())""", (habitacion_id,))
        clientes_actuales = cur.fetchone()[0]

        cur.execute("""SELECT check_in, check_out, valor, observacion FROM clientes WHERE habitacion_id = %s AND (check_out IS NULL OR check_out > NOW()) LIMIT 1""", (habitacion_id,))
        datos_referencia = cur.fetchone()

        if clientes_actuales >= 4:
            flash(f'La habitación {habitacion[1]} ya está en su capacidad máxima (4 personas).', 'error')
            return redirect(url_for('index'))

        return render_template('agregar_cliente.html', habitacion=habitacion, habitacion_id=habitacion_id, datos_referencia=datos_referencia)

    except pymysql.MySQLError as e:
        flash(f'Error en la base de datos: {str(e)}', 'error')
        return redirect(url_for('index'))
    finally:
        cur.close()
        conn.close()

@app.route('/guardar_nuevo_cliente', methods=['POST'])
def guardar_nuevo_cliente():
    user_id = require_user_session()
    if not user_id:
        return jsonify({"success": False, "error": "Sesión expirada"})
    
    try:
        if request.is_json:
            data = request.get_json()
            habitacion_id_str = str(data.get('habitacion_id', '')).strip()
            if not habitacion_id_str:
                return jsonify({"success": False, "error": "ID de habitación no válido"})
            habitacion_id = int(habitacion_id_str)
            
            nombre = data['nombre']
            tipo_doc = data['tipo_doc']
            numero_doc = data['numero_doc']
            telefono = data['telefono']
            procedencia = data['procedencia']
            check_in = data['check_in']
            check_out_fecha = data['check_out_fecha']
            valor = data['valor']
            observacion = data['observacion']
            personas_adicionales = data.get('personas_adicionales', [])
        else:
            habitacion_id_str = request.form.get('habitacion_id', '').strip()
            if not habitacion_id_str:
                flash('ID de habitación no válido.', 'error')
                return redirect(url_for('index'))
            habitacion_id = int(habitacion_id_str)
            
            nombre = request.form['nombre']
            tipo_doc = request.form['tipo_doc']
            numero_doc = request.form['numero_doc']
            telefono = request.form['telefono']
            procedencia = request.form['procedencia']
            check_in = request.form['check_in']
            check_out_fecha = request.form['check_out_fecha']
            valor = request.form['valor']
            observacion = request.form['observacion']
            personas_adicionales = []

        check_in_dt = datetime.strptime(check_in, "%Y-%m-%dT%H:%M")
        check_out_dt = datetime.strptime(check_out_fecha, "%Y-%m-%d")
        check_out_dt = datetime(check_out_dt.year, check_out_dt.month, check_out_dt.day, 13, 0)

        conn = get_db_connection()
        if not conn:
            if request.is_json:
                return jsonify({"success": False, "error": "Error de conexión a la base de datos"})
            flash('Error de conexión a la base de datos.', 'error')
            return redirect(url_for('index'))

        cur = conn.cursor()
        
        cur.execute("SELECT id FROM habitaciones WHERE id = %s AND usuario_id = %s", (habitacion_id, user_id))
        if not cur.fetchone():
            if request.is_json:
                return jsonify({"success": False, "error": "No tienes permisos para modificar esta habitación"})
            flash('No tienes permisos para modificar esta habitación.', 'error')
            return redirect(url_for('index'))
        
        cur.execute("""SELECT COUNT(*) FROM clientes WHERE habitacion_id = %s AND (check_out IS NULL OR check_out > NOW())""", (habitacion_id,))
        clientes_actuales = cur.fetchone()[0]
        
        total_personas = 1 + len(personas_adicionales)  # Main client + additional persons
        if clientes_actuales + total_personas > 4:
            if request.is_json:
                return jsonify({"success": False, "error": f"La habitación excedería el límite máximo de 4 clientes (actuales: {clientes_actuales}, intentando agregar: {total_personas})"})
            flash('La habitación excedería el límite máximo de 4 clientes.', 'error')
            return redirect(url_for('agregar_cliente_habitacion', habitacion_id=habitacion_id))

        cur.execute("""
            INSERT INTO clientes (
                hora_ingreso, nombre, tipo_doc, numero_doc, telefono, procedencia, 
                check_in, check_out, valor, observacion, habitacion_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            check_in_dt.time(), nombre, tipo_doc, numero_doc, telefono, procedencia, 
            check_in_dt, check_out_dt, valor, observacion, habitacion_id
        ))

        for persona in personas_adicionales:
            cur.execute("""
                INSERT INTO clientes (
                    hora_ingreso, nombre, tipo_doc, numero_doc, telefono, procedencia, 
                    check_in, check_out, valor, observacion, habitacion_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                check_in_dt.time(), persona['nombre'], persona['tipo_doc'], persona['numero_doc'], 
                persona['telefono'], persona['procedencia'], check_in_dt, check_out_dt, 
                0, '', habitacion_id  # Additional persons don't have separate value/observation
            ))

        cur.execute("UPDATE habitaciones SET estado = 'ocupada' WHERE id = %s AND usuario_id = %s", (habitacion_id, user_id))

        conn.commit()
        
        if request.is_json:
            return jsonify({"success": True, "message": f"Cliente principal y {len(personas_adicionales)} persona(s) adicional(es) registrado(s) exitosamente"})
        else:
            flash('Cliente(s) registrado(s) exitosamente.', 'success')
            return redirect(url_for('index'))

    except pymysql.MySQLError as e:
        if request.is_json:
            return jsonify({"success": False, "error": f"Error en la base de datos: {str(e)}"})
        flash(f'Error en la base de datos: {str(e)}', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        if request.is_json:
            return jsonify({"success": False, "error": f"Error al guardar cliente: {str(e)}"})
        flash(f'Error al guardar nuevo cliente: {str(e)}', 'error')
        return redirect(url_for('index'))
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
@app.route('/liberar/<int:habitacion_id>')
def liberar(habitacion_id):
    user_id = require_user_session()
    if not user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos.', 'error')
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        
        cur.execute("SELECT numero FROM habitaciones WHERE id = %s AND usuario_id = %s", (habitacion_id, user_id))
        habitacion = cur.fetchone()
        if not habitacion:
            flash('No tienes permisos para liberar esta habitación.', 'error')
            return redirect(url_for('index'))
        
        # Intentar liberar clientes activos
        cur.execute("""UPDATE clientes SET check_out = NOW() WHERE habitacion_id = %s AND (check_out IS NULL OR check_out > NOW())""", (habitacion_id,))
        clientes_liberados = cur.rowcount

        # Siempre liberar la habitación, tenga o no clientes
        cur.execute("UPDATE habitaciones SET estado = 'libre' WHERE id = %s AND usuario_id = %s", (habitacion_id, user_id))

        if clientes_liberados > 0:
            flash(f'Habitación {habitacion[0]} y sus ocupantes liberados.')
        else:
            flash(f'Habitación {habitacion[0]} liberada (no había clientes activos).', 'warning')

        conn.commit()
        return redirect(url_for('index'))

    except pymysql.MySQLError as e:
        flash(f'Error en la base de datos: {str(e)}', 'error')
        return redirect(url_for('index'))
    finally:
        cur.close()
        conn.close()

@app.route('/exportar_excel')
def exportar_excel():
    user_id = require_user_session()
    if not user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos.', 'error')
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        cur.execute("""SELECT c.hora_ingreso, c.nombre, c.tipo_doc, c.numero_doc, c.telefono, c.procedencia, c.check_in, c.check_out, c.valor, c.observacion, h.numero AS habitacion_numero FROM clientes c JOIN habitaciones h ON c.habitacion_id = h.id WHERE h.usuario_id = %s ORDER BY c.check_in DESC, c.hora_ingreso DESC""", (user_id,))
        all_clientes_data = cur.fetchall()

        if not all_clientes_data:
            flash('No hay datos para exportar', 'error')
            return redirect(url_for('index'))

        import os
        desktop = os.path.join(os.path.expanduser("~"), "Desktop", "Nelson")
        os.makedirs(desktop, exist_ok=True)  # crea la carpeta si no existe
        excel_path = os.path.join(desktop, "clientes_hotel.xlsx")

        columnas = [
            'Hora Ingreso', 'Nombre', 'Tipo Doc', 'Número Doc', 'Teléfono',
            'Procedencia', 'Check-in', 'Check-out', 'Valor', 'Observación', 'Habitación'
        ]

        wb = Workbook()
        ws = wb.active
        ws.title = "Todos los Clientes"
        ws.append(columnas)

        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'), 
            top=Side(style='thin'), bottom=Side(style='thin')
        )

        header_style = NamedStyle(name="header_style")
        header_style.font = Font(bold=True, color="FFFFFF")
        header_style.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_style.alignment = Alignment(horizontal="center")

        if header_style.name not in wb.named_styles:
            wb.add_named_style(header_style)

        for fila in all_clientes_data:
            hora_str = fila[0].strftime('%H:%M') if isinstance(fila[0], time) else str(fila[0])
            checkin_str = fila[6].strftime('%d/%m/%Y %H:%M') if isinstance(fila[6], datetime) else str(fila[6])
            checkout_str = fila[7].strftime('%d/%m/%Y %H:%M') if isinstance(fila[7], datetime) else str(fila[7])

            nueva_fila = [
                hora_str, fila[1] or '', fila[2] or '', fila[3] or '',
                fila[4] or '', fila[5] or '', checkin_str, checkout_str,
                fila[8] or 0, fila[9] or '', fila[10] or ''
            ]
            ws.append(nueva_fila)

        for cell in ws[1]:
            cell.style = header_style

        for col_idx, column in enumerate(ws.iter_cols(min_row=1, max_row=ws.max_row), 1):
            max_length = 0
            column_letter = get_column_letter(col_idx)
            for cell in column:
                cell.border = thin_border
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
                if col_idx == 9 and cell.row > 1:
                    cell.number_format = '#,##0.00'
            
            adjusted_width = (max_length + 2) * 1.2
            if adjusted_width > 0:
                ws.column_dimensions[column_letter].width = adjusted_width

        ws.freeze_panes = 'A2'
        wb.save(excel_path)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_name = f'clientes_hotel_{timestamp}.xlsx'
        return send_file(excel_path, as_attachment=True, download_name=download_name)

    except pymysql.MySQLError as e:
        flash(f'Error en la base de datos: {str(e)}', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error al exportar Excel: {str(e)}', 'error')
        return redirect(url_for('index'))
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

@app.route('/cambiar_color_general', methods=['POST'])
def cambiar_color_general():
    user_id = require_user_session()
    if not user_id:
        return redirect(url_for('login'))
    
    habitacion_id_str = request.form.get('habitacion_id', '').strip()
    if not habitacion_id_str:
        flash("ID de habitación no válido", "error")
        return redirect(url_for('index'))
    
    try:
        habitacion_id = int(habitacion_id_str)
    except ValueError:
        flash("ID de habitación no válido", "error")
        return redirect(url_for('index'))
    
    nuevo_estado = request.form.get('nuevo_estado')

    conn = get_db_connection()
    if not conn:
        flash("Error de conexión a la base de datos")
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        cur.execute("UPDATE habitaciones SET estado = %s WHERE id = %s AND usuario_id = %s", (nuevo_estado, habitacion_id, user_id))
        if cur.rowcount > 0:
            conn.commit()
            flash("Estado de habitación actualizado con éxito")
        else:
            flash("No tienes permisos para modificar esta habitación", "error")
    except pymysql.MySQLError as e:
        flash(f"Error en la base de datos: {str(e)}")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('index'))

@app.route('/agregar_habitacion', methods=['GET', 'POST'])
def agregar_habitacion():
    user_id = require_user_session()
    if not user_id:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        numero = request.form['numero']
        descripcion = request.form['descripcion']
        estado = request.form['estado']

        conn = get_db_connection()
        if not conn:
            flash("Error de conexión a la base de datos", "error")
            return redirect(url_for('index'))

        try:
            cur = conn.cursor()
            
            cur.execute("SELECT id FROM habitaciones WHERE numero = %s AND usuario_id = %s", (numero, user_id))
            if cur.fetchone():
                flash(f"Ya tienes una habitación con el número {numero}. Cada habitación debe tener un número único en tu hotel.", "error")
                return render_template('agregar_habitacion.html')
            
            cur.execute("INSERT INTO habitaciones (numero, descripcion, estado, usuario_id) VALUES (%s, %s, %s, %s)", (numero, descripcion, estado, user_id))
            conn.commit()
            flash("Habitación agregada con éxito", "success")
        except Exception as e:
            flash(f"Error al agregar habitación: {e}", "error")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for('index'))

    return render_template('agregar_habitacion.html')

@app.route('/eliminar_habitacion/<int:habitacion_id>', methods=['POST'])
def eliminar_habitacion(habitacion_id):
    user_id = require_user_session()
    if not user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash("Error de conexión a la base de datos", "error")
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM habitaciones WHERE id = %s AND usuario_id = %s", (habitacion_id, user_id))
        if cur.rowcount > 0:
            conn.commit()
            flash("Habitación eliminada con éxito")
        else:
            flash("No tienes permisos para eliminar esta habitación", "error")
    except pymysql.MySQLError as e:
        flash(f"Error al eliminar habitación: {str(e)}", "error")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('index'))

@app.route('/registrar_cliente/<int:habitacion_id>', methods=['POST'])
def registrar_cliente(habitacion_id):
    user_id = require_user_session()
    if not user_id:
        return redirect(url_for('login'))
    
    nombre = request.form.get('nombre')
    tipo_doc = request.form.get('tipo_doc')
    numero_doc = request.form.get('numero_doc')
    telefono = request.form.get('telefono')
    procedencia = request.form.get('procedencia')
    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')
    valor = request.form.get('valor')
    observacion = request.form.get('observacion')

    personas_adicionales = []
    form_keys = list(request.form.keys())
    
    # Extract additional persons data from form
    for key in form_keys:
        if key.startswith('personas_adicionales[') and key.endswith('][nombre]'):
            # Extract the index from the key
            import re
            match = re.search(r'personas_adicionales\[(\d+)\]\[nombre\]', key)
            if match:
                index = match.group(1)
                nombre_adicional = request.form.get(f'personas_adicionales[{index}][nombre]')
                if nombre_adicional:
                    personas_adicionales.append({
                        'nombre': nombre_adicional,
                        'tipo_doc': request.form.get(f'personas_adicionales[{index}][tipo_doc]', 'C.c'),
                        'numero_doc': request.form.get(f'personas_adicionales[{index}][numero_doc]', ''),
                        'telefono': request.form.get(f'personas_adicionales[{index}][telefono]', ''),
                        'procedencia': request.form.get(f'personas_adicionales[{index}][procedencia]', '')
                    })

    conn = get_db_connection()
    if not conn:
        flash('Error de conexión a la base de datos.', 'error')
        return redirect(url_for('index'))

    try:
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM habitaciones WHERE id = %s AND usuario_id = %s", (habitacion_id, user_id))
        if not cur.fetchone():
            flash('No tienes permisos para modificar esta habitación.', 'error')
            return redirect(url_for('index'))
        
        cur.execute("""SELECT COUNT(*) FROM clientes WHERE habitacion_id = %s AND (check_out IS NULL OR check_out > NOW())""", (habitacion_id,))
        clientes_actuales = cur.fetchone()[0]

        total_personas = 1 + len(personas_adicionales)
        if clientes_actuales + total_personas > 4:
            flash(f'La habitación excedería el límite máximo de 4 clientes (actuales: {clientes_actuales}, intentando agregar: {total_personas}).', 'error')
            return redirect(url_for('agregar_cliente_habitacion', habitacion_id=habitacion_id))

        # Insert main client
        cur.execute("""INSERT INTO clientes (nombre, tipo_doc, numero_doc, telefono, procedencia, habitacion_id, check_in, check_out, valor, observacion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (nombre, tipo_doc, numero_doc, telefono, procedencia, habitacion_id, check_in, check_out, valor, observacion))

        # Insert additional persons
        for persona in personas_adicionales:
            cur.execute("""INSERT INTO clientes (nombre, tipo_doc, numero_doc, telefono, procedencia, habitacion_id, check_in, check_out, valor, observacion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (persona['nombre'], persona['tipo_doc'], persona['numero_doc'], persona['telefono'], persona['procedencia'], habitacion_id, check_in, check_out, 0, ''))

        cur.execute("""UPDATE habitaciones SET estado = 'ocupada' WHERE id = %s AND usuario_id = %s""", (habitacion_id, user_id))

        conn.commit()
        flash(f'Cliente principal y {len(personas_adicionales)} persona(s) adicional(es) registrado(s) exitosamente.', 'success')
        return redirect(url_for('index'))

    except pymysql.MySQLError as e:
        flash(f'Error en la base de datos: {str(e)}', 'error')
        return redirect(url_for('agregar_cliente_habitacion', habitacion_id=habitacion_id))
    finally:
        cur.close()
        conn.close()

@app.route('/obtener_huespedes/<int:habitacion_id>')
def obtener_huespedes(habitacion_id):
    user_id = require_user_session()
    if not user_id:
        return jsonify({"success": False, "error": "Sesión expirada"})
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "Error de conexión a la base de datos"})

    try:
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM habitaciones WHERE id = %s AND usuario_id = %s", (habitacion_id, user_id))
        if not cur.fetchone():
            return jsonify({"success": False, "error": "No tienes permisos para acceder a esta habitación"})
        
        cur.execute("""
            SELECT id, nombre, tipo_doc, numero_doc, telefono, procedencia, 
                   check_in, check_out, valor, observacion
            FROM clientes 
            WHERE habitacion_id = %s AND (check_out IS NULL OR check_out > NOW()) 
            ORDER BY check_in ASC, id ASC
        """, (habitacion_id,))
        
        huespedes_data = cur.fetchall()
        
        huespedes = []
        for huesped in huespedes_data:
            huespedes.append({
                'id': huesped[0],
                'nombre': huesped[1],
                'tipo_doc': huesped[2],
                'numero_doc': huesped[3],
                'telefono': huesped[4],
                'procedencia': huesped[5],
                'check_in': huesped[6].isoformat() if huesped[6] else None,
                'check_out': huesped[7].isoformat() if huesped[7] else None,
                'valor': float(huesped[8]) if huesped[8] else 0,
                'observacion': huesped[9]
            })
        
        return jsonify({"success": True, "huespedes": huespedes})

    except pymysql.MySQLError as e:
        return jsonify({"success": False, "error": f"Error en la base de datos: {str(e)}"})
    except Exception as e:
        return jsonify({"success": False, "error": f"Error al obtener huéspedes: {str(e)}"})
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    print("📊 Probando conexión a base de datos...")
    
    try:
        import pymysql
        print("✅ pymysql disponible")
    except ImportError:
        print("❌ pymysql no está instalado")
        print("💡 Instala con: pip install pymysql")
    
    test_conn = get_db_connection()
    if test_conn:
        print("✅ Conexión a base de datos exitosa")
        test_conn.close()
    else:
        print("❌ Error de conexión a base de datos")
        print("💡 Visita http://localhost:5000/test-db para más detalles")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
