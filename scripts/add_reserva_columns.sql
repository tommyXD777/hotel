-- Agregar columnas para sistema de reservas y estados de cliente
ALTER TABLE clientes ADD COLUMN IF NOT EXISTS estado_cliente ENUM('reservado', 'llegado', 'activo') DEFAULT 'activo';
ALTER TABLE clientes ADD COLUMN IF NOT EXISTS hora_ingreso TIME NULL;

-- Actualizar clientes existentes
UPDATE clientes SET estado_cliente = 'activo' WHERE estado_cliente IS NULL;
