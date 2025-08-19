#!/usr/bin/env python3
"""
Script para ejecutar la migración de base de datos
Agrega soporte multi-tenancy al sistema hotelero (con debug)
"""

import pymysql
import sys
import os

def get_db_connection():
    """Obtiene conexión a la base de datos"""
    try:
        conn = pymysql.connect(
            host='isladigital.xyz',
            user='nelson',
            password='3011551141.Arias',
            database='bd_hostal',
            charset='utf8mb4',
            autocommit=False,
            port=3311
        )
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def check_migration_needed():
    """Verifica si la migración es necesaria"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'bd_hostal' 
            AND TABLE_NAME = 'habitaciones' 
            AND COLUMN_NAME = 'usuario_id'
        """)
        
        exists = cur.fetchone()[0] > 0
        return not exists
        
    except Exception as e:
        print(f"Error verificando migración: {e}")
        return False
    finally:
        if 'cur' in locals():
            cur.close()
        conn.close()

def run_migration():
    """Ejecuta la migración de base de datos"""
    if not check_migration_needed():
        print("✅ La migración ya fue ejecutada anteriormente")
        return True
    
    print("🔄 Ejecutando migración de base de datos...")
    
    conn = get_db_connection()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    try:
        cur = conn.cursor()
        
        # Leer el archivo SQL de migración
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file = os.path.join(script_dir, '001_add_usuario_id_to_habitaciones.sql')
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Separar statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        for statement in statements:
            if statement:
                try:
                    print(f"Ejecutando SQL: {statement[:80]}...")
                    cur.execute(statement)
                except Exception as e:
                    print(f"⚠️ Error ejecutando: {statement[:80]} -> {e}")
                    conn.rollback()
                    return False
        
        conn.commit()
        print("✅ Migración ejecutada exitosamente")
        
        # Verificar resultados
        cur.execute("SHOW COLUMNS FROM habitaciones;")
        cols = [row[0] for row in cur.fetchall()]
        print("\n📊 Columnas actuales en 'habitaciones':", cols)
        
        if "usuario_id" in cols:
            cur.execute("SELECT COUNT(*) as total_habitaciones, usuario_id FROM habitaciones GROUP BY usuario_id")
            results = cur.fetchall()
            
            print("\n📊 Resumen de habitaciones por usuario:")
            for result in results:
                print(f"   Usuario ID {result[1]}: {result[0]} habitaciones")
        else:
            print("❌ La columna usuario_id no fue creada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error ejecutando migración: {e}")
        conn.rollback()
        return False
    finally:
        if 'cur' in locals():
            cur.close()
        conn.close()

def main():
    """Función principal"""
    print("🏨 Sistema Hotelero - Migración Multi-Tenancy")
    print("=" * 50)
    
    if run_migration():
        print("\n✅ Migración completada (con debug)")
    else:
        print("\n❌ Error en la migración")
        sys.exit(1)

if __name__ == "__main__":
    main()
