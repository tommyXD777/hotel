-- ============================================
-- 🏨 Migración Multi-Tenancy para el sistema hotelero
-- ============================================

-- 1. Agregar columna usuario_id a habitaciones (si no existe)
ALTER TABLE habitaciones 
ADD COLUMN usuario_id INT NULL;

-- 2. Obtener el id de Angie
-- ⚠️ Verifica primero que existe un usuario con username 'angie'
SELECT id, username FROM usuarios WHERE username = 'angie';

-- 3. Actualizar todas las habitaciones para asignarlas a Angie
UPDATE habitaciones 
SET usuario_id = (SELECT id FROM usuarios WHERE username = 'angie' LIMIT 1);

-- 4. Cambiar usuario_id a NOT NULL una vez asignado
ALTER TABLE habitaciones 
MODIFY COLUMN usuario_id INT NOT NULL;

-- 5. Crear índice para mejorar performance
CREATE INDEX idx_habitaciones_usuario_id ON habitaciones(usuario_id);

-- 6. Agregar foreign key hacia usuarios
ALTER TABLE habitaciones 
ADD CONSTRAINT fk_habitaciones_usuario 
FOREIGN KEY (usuario_id) REFERENCES usuarios(id) 
ON DELETE CASCADE;

-- 7. (Opcional) Agregar columnas extra a usuarios si las necesitas
ALTER TABLE usuarios 
ADD COLUMN nombre VARCHAR(100) NULL,
ADD COLUMN correo VARCHAR(150) NULL;

-- 8. (Opcional) Guardar datos de Angie en los nuevos campos
UPDATE usuarios 
SET nombre = 'Angie', correo = 'angie@email.com'
WHERE username = 'angie';
