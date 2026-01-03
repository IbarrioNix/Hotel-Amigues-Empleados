import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name= "hotel.db"):
        #obtener ruta de la carpeta db
        db_path = os.path.join(os.path.dirname(__file__), db_name)
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.crear_tablas()

    def crear_tablas(self):

        # THabitaciones
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habitaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE NOT NULL,
                tipo TEXT NOT NULL,
                precio REAL NOT NULL,
                estado TEXT DEFAULT 'disponible'
            )
        ''')

        # TEmpleados
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS empleados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                puesto TEXT NOT NULL,
                telefono TEXT,
                usuario TEXT UNIQUE,
                password TEXT,
                privilegio TEXT
            )
        ''')

        # THuespedes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS huespedes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                telefono TEXT UNIQUE,
                password TEXT,
                email TEXT
            )
        ''')

        # TReservaciones
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                huesped_id INTEGER NOT NULL,
                habitacion_id INTEGER NOT NULL,
                fecha_entrada DATE NOT NULL,
                fecha_salida DATE NOT NULL,
                estado TEXT DEFAULT 'activa',
                total REAL,
                FOREIGN KEY (huesped_id) REFERENCES huespedes (id),
                FOREIGN KEY (habitacion_id) REFERENCES habitaciones (id)
            )
        ''')

        self.conn.commit()

        # Insertar datos de prueba si no existen
        self.insertar_datos_prueba()

    def insertar_datos_prueba(self):
        # Verificar si ya hay datos
        self.cursor.execute("SELECT COUNT(*) FROM habitaciones")
        if self.cursor.fetchone()[0] == 0:
            habitaciones = [
                ('101', 'Sencilla', 500.00, 'disponible'),
                ('102', 'Doble', 500.00, 'ocupada'),
                ('103', 'Familiar', 800.00, 'disponible'),
                ('104', 'Deluxe', 800.00, 'limpieza'),
                ('201', 'Sencilla', 1500.00, 'disponible'),
                ('202', 'Doble', 1500.00, 'disponible'),
                ('203', 'Familiar', 500.00, 'disponible'),
                ('204', 'Deluxe', 800.00, 'mantenimiento'),
            ]
            self.cursor.executemany(
            'INSERT INTO habitaciones (numero, tipo, precio, estado) VALUES (?, ?, ?, ?)',
                habitaciones
            )

        # Insertar empleado admin si no existe
        self.cursor.execute("SELECT COUNT(*) FROM empleados WHERE usuario = 'admin'")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('''
                                INSERT INTO empleados (nombre, apellido, puesto, usuario, password, privilegio)
                                VALUES ('Admin', 'Sistema', 'Gerente', 'admin', '1234', 'Administrador')
                                ''')

        self.conn.commit()

        # Insertar empleado de prueba (no admin)
        self.cursor.execute("SELECT COUNT(*) FROM empleados WHERE usuario = 'empleado1'")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('''
                                INSERT INTO empleados (nombre, apellido, puesto, usuario, password, privilegio)
                                VALUES ('Juan', 'Pérez', 'Recepcionista', 'empleado1', '1234', 'Empleado')
                                ''')

        self.conn.commit()

    # CRUD para Habitaciones
    def obtener_habitaciones(self):
        """Obtiene todas las habitaciones"""
        self.cursor.execute('SELECT * FROM habitaciones')
        return self.cursor.fetchall()

    def agregar_habitacion(self, numero, tipo, precio, estado='disponible'):
        """Agrega una nueva habitación"""
        try:
            self.cursor.execute('''
                                INSERT INTO habitaciones (numero, tipo, precio, estado)
                                VALUES (?, ?, ?, ?)
                                ''', (numero, tipo, precio, estado))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Número de habitación duplicado

    def actualizar_habitacion(self, id, numero, tipo, precio, estado):
        """Actualiza una habitación existente"""
        try:
            self.cursor.execute('''
                                UPDATE habitaciones
                                SET numero=?,
                                    tipo=?,
                                    precio=?,
                                    estado=?
                                WHERE id = ?
                                ''', (numero, tipo, precio, estado, id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def eliminar_habitacion(self, id):
        """Elimina una habitación"""
        self.cursor.execute('DELETE FROM habitaciones WHERE id=?', (id,))
        self.conn.commit()

    def cambiar_estado_habitacion(self, id, nuevo_estado):
        """Cambia el estado de una habitación"""
        self.cursor.execute('''
                            UPDATE habitaciones
                            SET estado=?
                            WHERE id = ?
                            ''', (nuevo_estado, id))
        self.conn.commit()

        # CRUD para Empleados

    def obtener_empleados(self):
        """Obtiene todos los empleados"""
        self.cursor.execute('SELECT * FROM empleados')
        return self.cursor.fetchall()

    def validar_login(self, usuario, password):
        """Valida credenciales de empleado"""
        self.cursor.execute('''
                            SELECT id, nombre, apellido, puesto
                            FROM empleados
                            WHERE usuario = ?
                              AND password = ?
                            ''', (usuario, password))
        return self.cursor.fetchone()

    def agregar_empleado(self, nombre, apellido, puesto, telefono='', usuario='', password='', privilegio=''):
        """Agrega un nuevo empleado"""
        try:
            self.cursor.execute('''
                                INSERT INTO empleados (nombre, apellido, puesto, telefono, usuario, password, privilegio)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                ''', (nombre, apellido, puesto, telefono, usuario, password, privilegio))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def actualizar_empleado(self, id, nombre, apellido, puesto, telefono, privilegio):
        """Actualiza un empleado"""
        self.cursor.execute('''
                            UPDATE empleados
                            SET nombre=?,
                                apellido=?,
                                privilegio=?,
                                puesto=?,
                                telefono=?
                            WHERE id = ?
                            ''', (nombre, apellido, privilegio, puesto, telefono, id))
        self.conn.commit()

    def eliminar_empleado(self, id):
        """Elimina un empleado"""
        self.cursor.execute('DELETE FROM empleados WHERE id=?', (id,))
        self.conn.commit()

        # Estadísticas

    def obtener_estadisticas(self):
        """Obtiene estadísticas generales del hotel"""
        stats = {}

        # Habitaciones por estado
        self.cursor.execute('''
                            SELECT estado, COUNT(*)
                            FROM habitaciones
                            GROUP BY estado
                            ''')
        estados = self.cursor.fetchall()

        stats['disponibles'] = 0
        stats['ocupadas'] = 0
        stats['limpieza'] = 0
        stats['mantenimiento'] = 0

        for estado, cantidad in estados:
            if estado == 'disponible':
                stats['disponibles'] = cantidad
            elif estado == 'ocupada':
                stats['ocupadas'] = cantidad
            elif estado == 'limpieza':
                stats['limpieza'] = cantidad
            elif estado == 'mantenimiento':
                stats['mantenimiento'] = cantidad

        # Total de empleados
        self.cursor.execute('SELECT COUNT(*) FROM empleados')
        stats['empleados'] = self.cursor.fetchone()[0]

        # Reservas activas
        self.cursor.execute("SELECT COUNT(*) FROM reservaciones WHERE estado='activa'")
        stats['reservas_activas'] = self.cursor.fetchone()[0]

        return stats

    #CRUD Huespedes
    def obtener_huespedes(self):
        """Obtiene todos los huéspedes"""
        self.cursor.execute('SELECT * FROM huespedes')
        return self.cursor.fetchall()

    def buscar_huesped_por_telefono(self, telefono):
        """Busca un huésped por su usuario"""
        self.cursor.execute('SELECT * FROM huespedes WHERE telefono=?', (telefono,))
        return self.cursor.fetchone()

    def agregar_huesped(self, nombre, apellido, telefono, email='', password=''):
        """Agrega un nuevo huésped"""
        try:
            self.cursor.execute('''
                                INSERT INTO huespedes (nombre, apellido, telefono, email, password)
                                VALUES (?, ?, ?, ?, ?)
                                ''', (nombre, apellido, telefono, email, password))
            self.conn.commit()
            return self.cursor.lastrowid  # Devuelve el ID del huésped creado
        except sqlite3.IntegrityError:
            return None

    def actualizar_huesped(self, id, nombre, apellido, telefono, email):
        """Actualiza un huésped"""
        try:
            self.cursor.execute('''
                                UPDATE huespedes
                                SET nombre=?,
                                    apellido=?,
                                    telefono=?,
                                    email=?
                                WHERE id = ?
                                ''', (nombre, apellido, telefono, email, id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def eliminar_huesped(self, id):
        """Elimina un huésped"""
        self.cursor.execute('DELETE FROM huespedes WHERE id=?', (id,))
        self.conn.commit()

    # ==================== CRUD para Reservas ====================

    def obtener_reservas(self):
        """Obtiene todas las reservas con información del huésped y habitación"""
        self.cursor.execute('''
                            SELECT r.id,
                                   r.huesped_id,
                                   h.nombre || ' ' || h.apellido AS huesped,
                                   r.habitacion_id,
                                   hab.numero                    AS habitacion,
                                   hab.tipo,
                                   r.fecha_entrada,
                                   r.fecha_salida,
                                   r.estado,
                                   r.total
                            FROM reservaciones r
                                     INNER JOIN huespedes h ON r.huesped_id = h.id
                                     INNER JOIN habitaciones hab ON r.habitacion_id = hab.id
                            ORDER BY r.fecha_entrada DESC
                            ''')
        return self.cursor.fetchall()

    def obtener_reserva_por_id(self, reserva_id):
        """Obtiene una reserva específica"""
        self.cursor.execute('SELECT * FROM reservaciones WHERE id=?', (reserva_id,))
        return self.cursor.fetchone()

    def agregar_reserva(self, huesped_id, habitacion_id, fecha_entrada, fecha_salida, total):
        """Agrega una nueva reserva"""
        try:
            self.cursor.execute('''
                                INSERT INTO reservaciones (huesped_id, habitacion_id, fecha_entrada, fecha_salida, total, estado)
                                VALUES (?, ?, ?, ?, ?, 'activa')
                                ''', (huesped_id, habitacion_id, fecha_entrada, fecha_salida, total))

            # Cambiar estado de la habitación a ocupada
            self.cambiar_estado_habitacion(habitacion_id, 'ocupada')

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error al agregar reserva: {e}")
            return False

    def actualizar_reserva(self, id, huesped_id, habitacion_id, fecha_entrada, fecha_salida, estado, total):
        """Actualiza una reserva"""
        self.cursor.execute('''
                            UPDATE reservaciones
                            SET huesped_id=?,
                                habitacion_id=?,
                                fecha_entrada=?,
                                fecha_salida=?,
                                estado=?,
                                total=?
                            WHERE id = ?
                            ''', (huesped_id, habitacion_id, fecha_entrada, fecha_salida, estado, total, id))
        self.conn.commit()

    def eliminar_reserva(self, id):
        """Elimina una reserva"""
        # Obtener la reserva antes de eliminar
        reserva = self.obtener_reserva_por_id(id)

        if reserva:
            habitacion_id = reserva[2]

            # Eliminar la reserva
            self.cursor.execute('DELETE FROM reservaciones WHERE id=?', (id,))

            # Cambiar estado de la habitación a disponible
            self.cambiar_estado_habitacion(habitacion_id, 'disponible')

            self.conn.commit()

    def cancelar_reserva(self, id):
        """Cancela una reserva (cambia estado a cancelada)"""
        reserva = self.obtener_reserva_por_id(id)

        if reserva:
            habitacion_id = reserva[2]

            # Cambiar estado de la reserva
            self.cursor.execute('UPDATE reservaciones SET estado="cancelada" WHERE id=?', (id,))

            # Liberar la habitación
            self.cambiar_estado_habitacion(habitacion_id, 'disponible')

            self.conn.commit()

    def finalizar_reserva(self, id):
        """Finaliza una reserva (checkout)"""
        reserva = self.obtener_reserva_por_id(id)

        if reserva:
            habitacion_id = reserva[2]

            # Cambiar estado de la reserva
            self.cursor.execute('UPDATE reservaciones SET estado="finalizada" WHERE id=?', (id,))

            # Cambiar habitación a limpieza
            self.cambiar_estado_habitacion(habitacion_id, 'limpieza')

            self.conn.commit()

    def obtener_habitaciones_disponibles(self):
        """Obtiene solo las habitaciones disponibles"""
        self.cursor.execute("SELECT * FROM habitaciones WHERE estado='disponible'")
        return self.cursor.fetchall()

    def cerrar(self):
        """Cierra la conexión a la base de datos"""
        self.conn.close()

