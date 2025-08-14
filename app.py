from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_mysqldb import MySQL
from openpyxl import Workbook, load_workbook
from openpyxl.styles import NamedStyle, Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime, time, date
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'hostal'
mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()

    # Obtener todas las habitaciones
    cur.execute("SELECT id, numero, estado, descripcion FROM habitaciones")
    habitaciones_db = cur.fetchall()

    rooms = []
    for habitacion in habitaciones_db:
        room_id, numero, estado_db, descripcion = habitacion # Renamed estado to estado_db to avoid conflict

        # Obtener todos los clientes (personas) activos en esta habitación CON FECHA DE CHECKOUT
        cur.execute("""
            SELECT id, nombre, tipo_doc, numero_doc, telefono, procedencia, check_out FROM clientes
            WHERE habitacion_id = %s AND (check_out IS NULL OR check_out > NOW())
        """, (room_id,))
        active_clientes_data = cur.fetchall()
        
        num_personas_ocupadas = len(active_clientes_data)
        personas_list = [ # Renamed huespedes_list to personas_list
            {
                'id': c[0],
                'nombre': c[1], 
                'tipo_doc': c[2], 
                'numero_doc': c[3], 
                'telefono': c[4], 
                'procedencia': c[5],
                'check_out': c[6]
            }
            for c in active_clientes_data
        ]
        
        current_room_state = estado_db # Start with DB state
        inquilino_principal = None # Will be the first person's name
        fecha_salida = None # Will store the checkout date

        if num_personas_ocupadas > 0:
            current_room_state = 'ocupada'
            inquilino_principal = active_clientes_data[0][1] # First person is considered principal for display
            fecha_salida = active_clientes_data[0][6] # Get checkout date from first person

        # If DB state is 'reservado' or 'mantenimiento', it overrides 'ocupada' for display
        # This ensures manual state changes take precedence
        if estado_db in ['reservado', 'mantenimiento']:
            current_room_state = estado_db
            if estado_db == 'reservado':
                # For reserved rooms, keep the person info if any
                pass
            else:
                inquilino_principal = None 
                num_personas_ocupadas = 0
                personas_list = []
                fecha_salida = None

        # Agregar habitación
        rooms.append({
            'id': room_id,
            'numero': numero,
            'estado': current_room_state,
            'inquilino_principal': inquilino_principal,
            'num_personas_ocupadas': num_personas_ocupadas,
            'personas_list': personas_list, # Renamed huespedes_list to personas_list
            'descripcion': descripcion,
            'fecha_salida': fecha_salida
        })

    # Obtener lista de clientes (todas las personas registradas históricamente)
    cur.execute("""
        SELECT c.id, c.hora_ingreso, c.nombre, c.tipo_doc, c.numero_doc,
               c.telefono, c.procedencia, c.check_in, c.check_out, c.valor, c.observacion,
               h.numero AS habitacion_numero
        FROM clientes c
        JOIN habitaciones h ON c.habitacion_id = h.id
        ORDER BY c.check_in DESC, c.hora_ingreso DESC
    """)
    clientes = cur.fetchall() # This 'clientes' list will now contain all individual people

    # Obtener habitaciones para el select (solo id, numero, descripcion, estado)
    # Y actualizar el estado a 'ocupada' si hay un cliente activo
    # AHORA TAMBIÉN PERMITIMOS SELECCIONAR HABITACIONES RESERVADAS PARA COMPLETAR LA RESERVA
    cur.execute("SELECT id, numero, descripcion, estado FROM habitaciones ORDER BY numero")
    habitaciones_para_select_db = cur.fetchall()

    habitaciones = []
    for h_id, h_numero, h_descripcion, h_estado_db in habitaciones_para_select_db:
        current_estado_for_select = h_estado_db
        if h_estado_db == 'libre':
            # Verificar si hay un cliente activo en esta habitación (any person in 'clientes' table)
            cur.execute("""
                SELECT COUNT(*) FROM clientes
                WHERE habitacion_id = %s AND (check_out IS NULL OR check_out > NOW())
            """, (h_id,))
            active_clients_count = cur.fetchone()[0]
            if active_clients_count > 0:
                current_estado_for_select = 'ocupada' # If there are active clients, the room is occupied

        habitaciones.append((h_id, h_numero, h_descripcion, current_estado_for_select))

    cur.close()

    return render_template('index.html', rooms=rooms, clientes=clientes, habitaciones=habitaciones)


@app.route('/registrar', methods=['POST'])
def registrar():
    #hora_ingreso = datetime.strptime(request.form['hora_ingreso'], "%H:%M").time()
    check_in = request.form['check_in']
    valor = request.form['valor']
    observacion = request.form['observacion']
    habitacion_id = int(request.form['habitacion_id'])

    check_in_dt = datetime.strptime(check_in, "%Y-%m-%dT%H:%M")
    check_out_fecha = request.form['check_out_fecha']
    check_out_dt = datetime.strptime(check_out_fecha, "%Y-%m-%d")
    check_out_dt = datetime(check_out_dt.year, check_out_dt.month, check_out_dt.day, 13, 0)

    cur = mysql.connection.cursor()

    # Obtener la descripción de la habitación para validar la capacidad
    cur.execute("SELECT descripcion, estado FROM habitaciones WHERE id = %s", (habitacion_id,))
    habitacion_info = cur.fetchone()
    if not habitacion_info:
        flash('Habitación no encontrada.', 'error')
        cur.close()
        return redirect(url_for('index'))
    
    habitacion_descripcion, habitacion_estado = habitacion_info

    # Contar el número de personas enviadas en el formulario
    num_personas_form = 0
    while f'persona_nombre_{num_personas_form}' in request.form: # Changed name from huesped_nombre to persona_nombre
        num_personas_form += 1
    
    # Validar número de personas según el tipo de habitación
    if num_personas_form == 0: # Ensure at least one person is registered
        flash('Debes registrar al menos una persona para la reserva.', 'error')
        cur.close()
        return redirect(url_for('index'))
    elif habitacion_descripcion.lower() == 'sencilla' and num_personas_form > 2:
        flash(f'Las habitaciones sencillas solo permiten un máximo de 2 personas. Intentaste registrar {num_personas_form}.', 'error')
        cur.close()
        return redirect(url_for('index'))
    elif habitacion_descripcion.lower() == 'doble' and num_personas_form > 4:
        flash(f'Las habitaciones dobles solo permiten un máximo de 4 personas. Intentaste registrar {num_personas_form}.', 'error')
        cur.close()
        return redirect(url_for('index'))
    
    # NUEVA LÓGICA: Permitir registrar en habitaciones RESERVADAS (completar reserva)
    # Verificar si la habitación ya está ocupada por CUALQUIER cliente activo
    cur.execute("""
        SELECT COUNT(*) FROM clientes
        WHERE habitacion_id = %s AND (check_out IS NULL OR check_out > NOW())
    """, (habitacion_id,))
    current_active_occupants = cur.fetchone()[0]

    # Solo bloquear si la habitación está ocupada Y no es una reserva que se está completando
    if current_active_occupants > 0 and habitacion_estado != 'reservado':
        flash('Esta habitación ya está ocupada por otros clientes. Por favor, selecciona una habitación libre o libera la actual.', 'error')
        cur.close()
        return redirect(url_for('index'))
    
    # Si es una habitación reservada con clientes existentes, actualizar en lugar de insertar nuevos
    if habitacion_estado == 'reservado' and current_active_occupants > 0:
        # Actualizar los datos de los clientes existentes con la nueva información
        cur.execute("""
            DELETE FROM clientes 
            WHERE habitacion_id = %s AND (check_out IS NULL OR check_out > NOW())
        """, (habitacion_id,))
        mysql.connection.commit()

    # Insertar los datos de cada persona en la tabla 'clientes'
    for i in range(num_personas_form):
        persona_nombre = request.form[f'persona_nombre_{i}']
        persona_tipo_doc = request.form[f'persona_tipo_doc_{i}']
        persona_numero_doc = request.form[f'persona_numero_doc_{i}']
        persona_telefono = request.form.get(f'persona_telefono_{i}', '')
        persona_procedencia = request.form.get(f'persona_procedencia_{i}', '')

        cur.execute("""
            INSERT INTO clientes 
            (hora_ingreso, nombre, tipo_doc, numero_doc, telefono, procedencia, check_in, check_out, valor, observacion, habitacion_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (check_in_dt.time(), persona_nombre, persona_tipo_doc, persona_numero_doc, persona_telefono, persona_procedencia, check_in_dt, check_out_dt, valor, observacion, habitacion_id))
        mysql.connection.commit()

    # Si era una habitación reservada, cambiar su estado a ocupada
    if habitacion_estado == 'reservado':
        cur.execute("UPDATE habitaciones SET estado = 'ocupada' WHERE id = %s", (habitacion_id,))
        mysql.connection.commit()
        flash('Reserva completada exitosamente. La habitación ahora está ocupada.')
    else:
        flash('Personas registradas exitosamente en la habitación.')

    cur.close()
    return redirect(url_for('index'))


@app.route('/editar_cliente/<int:cliente_id>')
def editar_cliente(cliente_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.id, c.nombre, c.tipo_doc, c.numero_doc, c.telefono, c.procedencia, 
               c.check_in, c.check_out, c.valor, c.observacion, c.habitacion_id,
               h.numero AS habitacion_numero, h.descripcion AS habitacion_descripcion
        FROM clientes c
        JOIN habitaciones h ON c.habitacion_id = h.id
        WHERE c.id = %s
    """, (cliente_id,))
    cliente = cur.fetchone()
    cur.close()
    
    if not cliente:
        flash('Cliente no encontrado.', 'error')
        return redirect(url_for('index'))
    
    return render_template('editar_cliente.html', cliente=cliente)


@app.route('/actualizar_cliente', methods=['POST'])
def actualizar_cliente():
    cliente_id = int(request.form['cliente_id'])
    nombre = request.form['nombre']
    tipo_doc = request.form['tipo_doc']
    numero_doc = request.form['numero_doc']
    telefono = request.form['telefono']
    procedencia = request.form['procedencia']
    
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE clientes 
        SET nombre = %s, tipo_doc = %s, numero_doc = %s, telefono = %s, procedencia = %s
        WHERE id = %s
    """, (nombre, tipo_doc, numero_doc, telefono, procedencia, cliente_id))
    mysql.connection.commit()
    cur.close()
    
    flash('Cliente actualizado exitosamente.')
    return redirect(url_for('index'))


@app.route('/agregar_cliente_habitacion/<int:habitacion_id>')
def agregar_cliente_habitacion(habitacion_id):
    cur = mysql.connection.cursor()
    
    # Obtener información de la habitación
    cur.execute("SELECT numero, descripcion FROM habitaciones WHERE id = %s", (habitacion_id,))
    habitacion = cur.fetchone()
    
    # Contar clientes actuales en la habitación
    cur.execute("""
        SELECT COUNT(*) FROM clientes 
        WHERE habitacion_id = %s AND (check_out IS NULL OR check_out > NOW())
    """, (habitacion_id,))
    clientes_actuales = cur.fetchone()[0]
    
    # Obtener datos de un cliente existente para usar como referencia (check_in, check_out, valor, observacion)
    cur.execute("""
        SELECT check_in, check_out, valor, observacion FROM clientes 
        WHERE habitacion_id = %s AND (check_out IS NULL OR check_out > NOW())
        LIMIT 1
    """, (habitacion_id,))
    datos_referencia = cur.fetchone()
    
    cur.close()
    
    if not habitacion:
        flash('Habitación no encontrada.', 'error')
        return redirect(url_for('index'))
    
    # Validar capacidad
    max_capacidad = 2 if habitacion[1].lower() == 'sencilla' else 4
    if clientes_actuales >= max_capacidad:
        flash(f'La habitación {habitacion[1]} ya está en su capacidad máxima ({max_capacidad} personas).', 'error')
        return redirect(url_for('index'))
    
    return render_template('agregar_cliente.html', 
                         habitacion=habitacion, 
                         habitacion_id=habitacion_id,
                         datos_referencia=datos_referencia)


@app.route('/guardar_nuevo_cliente', methods=['POST'])
def guardar_nuevo_cliente():
    habitacion_id = int(request.form['habitacion_id'])
    nombre = request.form['nombre']
    tipo_doc = request.form['tipo_doc']
    numero_doc = request.form['numero_doc']
    telefono = request.form['telefono']
    procedencia = request.form['procedencia']
    check_in = request.form['check_in']
    check_out_fecha = request.form['check_out_fecha']
    valor = request.form['valor']
    observacion = request.form['observacion']
    
    check_in_dt = datetime.strptime(check_in, "%Y-%m-%dT%H:%M")
    check_out_dt = datetime.strptime(check_out_fecha, "%Y-%m-%d")
    check_out_dt = datetime(check_out_dt.year, check_out_dt.month, check_out_dt.day, 13, 0)
    
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO clientes 
        (hora_ingreso, nombre, tipo_doc, numero_doc, telefono, procedencia, check_in, check_out, valor, observacion, habitacion_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (check_in_dt.time(), nombre, tipo_doc, numero_doc, telefono, procedencia, check_in_dt, check_out_dt, valor, observacion, habitacion_id))
    mysql.connection.commit()
    cur.close()
    
    flash('Nuevo cliente agregado exitosamente a la habitación.')
    return redirect(url_for('index'))


@app.route('/liberar/<int:habitacion_id>')
def liberar(habitacion_id):
    cur = mysql.connection.cursor()
    # Actualizar el check_out de TODOS los clientes (personas) asociados a esta habitación y que aún no han hecho check-out
    cur.execute("""
        UPDATE clientes 
        SET check_out = NOW() 
        WHERE habitacion_id = %s AND (check_out IS NULL OR check_out > NOW())
    """, (habitacion_id,))
    mysql.connection.commit()
    
    if cur.rowcount > 0: # Check if any rows were updated
        # NUEVA LÍNEA: Cambiar el estado de la habitación a 'libre' después de liberar a los clientes
        cur.execute("UPDATE habitaciones SET estado = 'libre' WHERE id = %s", (habitacion_id,))
        mysql.connection.commit()
        flash(f'Habitación {habitacion_id} y sus ocupantes liberados.')
    else:
        flash(f'No hay clientes activos para liberar en la habitación {habitacion_id}', 'error')
    
    cur.close()
    return redirect(url_for('index'))

@app.route('/exportar_excel')
def exportar_excel():
    try:
        excel_path = r"C:\Users\USUARIO\Desktop\Nelson\clientes_hotel.xlsx"

        # Obtener datos de todos los clientes (personas)
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT c.hora_ingreso, c.nombre, c.tipo_doc, c.numero_doc,
                   c.telefono, c.procedencia, c.check_in, c.check_out,
                   c.valor, c.observacion, h.numero AS habitacion_numero
            FROM clientes c
            JOIN habitaciones h ON c.habitacion_id = h.id
            ORDER BY c.check_in DESC, c.hora_ingreso DESC
        """)
        all_clientes_data = cur.fetchall()
        cur.close()

        if not all_clientes_data:
            flash('No hay datos para exportar')
            return redirect(url_for('index'))

        # Encabezados actualizados
        columnas = [
            'Hora Ingreso', 'Nombre', 'Tipo Doc', 'Número Doc', 'Teléfono',
            'Procedencia', 'Check-in', 'Check-out', 'Valor', 'Observación', 'Habitación'
        ]

        # Crear nuevo workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Todos los Clientes"

        # Agregar encabezados
        ws.append(columnas)

        # Estilo para bordes
        thin_border = Border(left=Side(style='thin'), 
                         right=Side(style='thin'), 
                         top=Side(style='thin'), 
                         bottom=Side(style='thin'))

        # Estilo encabezado
        header_style = NamedStyle(name="header_style")
        header_style.font = Font(bold=True, color="FFFFFF")
        header_style.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_style.alignment = Alignment(horizontal="center")

        if header_style.name not in wb.named_styles:
            wb.add_named_style(header_style)

        # Procesar y agregar datos
        for fila in all_clientes_data:
            hora_str = fila[0].strftime('%H:%M') if isinstance(fila[0], time) else str(fila[0])
            checkin_str = fila[6].strftime('%d/%m/%Y %H:%M') if isinstance(fila[6], datetime) else str(fila[6])
            checkout_str = fila[7].strftime('%d/%m/%Y %H:%M') if isinstance(fila[7], datetime) else str(fila[7])

            nueva_fila = [
                hora_str,
                fila[1] or '',   # Nombre
                fila[2] or '',   # Tipo Doc
                fila[3] or '',   # Número Doc
                fila[4] or '',   # Teléfono
                fila[5] or '',   # Procedencia
                checkin_str,
                checkout_str,
                fila[8] or 0,    # Valor
                fila[9] or '',   # Observación
                fila[10] or ''   # Habitación
            ]
            ws.append(nueva_fila)

        # Estilos encabezados
        for cell in ws[1]:
            cell.style = header_style

        # Ajustar ancho de columnas dinámicamente y aplicar bordes
        for col_idx, column in enumerate(ws.iter_cols(min_row=1, max_row=ws.max_row), 1):
            max_length = 0
            column_letter = get_column_letter(col_idx) # Import get_column_letter from openpyxl.utils
            for cell in column:
                # Aplicar bordes a todas las celdas
                cell.border = thin_border
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            
                # Formato para la columna 'Valor' (columna I, índice 9)
                if col_idx == 9 and cell.row > 1: # Asumiendo que 'Valor' es la 9na columna (índice 8 en 0-based)
                    cell.number_format = '#,##0.00' # Formato de número con 2 decimales y separador de miles
        
            adjusted_width = (max_length + 2) * 1.2 # Añadir un poco de padding
            if adjusted_width > 0: # Evitar anchos negativos o cero
                ws.column_dimensions[column_letter].width = adjusted_width

        # Congelar la primera fila (encabezados)
        ws.freeze_panes = 'A2'

        # Guardar archivo
        wb.save(excel_path)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_name = f'clientes_hotel_{timestamp}.xlsx'
        return send_file(excel_path, as_attachment=True, download_name=download_name)

    except Exception as e:
        flash(f'Error al exportar Excel: {str(e)}')
        return redirect(url_for('index'))
    finally:
        if 'cur' in locals() and cur is not None: # Asegura que cur existe y no es None
            cur.close()

@app.route('/cambiar_color_general', methods=['POST'])
def cambiar_color_general():
    print("DEBUG: La función cambiar_color_general ha sido llamada.") # Debug print
    habitacion_id = request.form['habitacion_id']
    nuevo_estado = request.form['nuevo_estado']
    
    cur = mysql.connection.cursor()
    cur.execute("UPDATE habitaciones SET estado = %s WHERE id = %s", (nuevo_estado, habitacion_id))
    mysql.connection.commit()
    cur.close()

    flash(f"El estado de la habitación {habitacion_id} ha sido cambiado a {nuevo_estado}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
