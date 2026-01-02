import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager

class EmpleadosWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db = DatabaseManager()
        self.crear_widgets()
        self.cargar_empleados()

    def crear_widgets(self):
        # Título
        titulo = tk.Label(self.parent, text="👥 GESTIÓN DE EMPLEADOS",
                          font=("Arial", 18, "bold"),
                          bg="#ecf0f1")
        titulo.pack(pady=20)

        # Frame para botones
        frame_botones = tk.Frame(self.parent, bg="#ecf0f1")
        frame_botones.pack(pady=10)

        btn_agregar = tk.Button(frame_botones, text="➕ Agregar Empleado",
                                command=self.abrir_formulario_agregar,
                                bg="#27ae60", fg="white",
                                font=("Arial", 10, "bold"),
                                width=18, height=2,
                                cursor="hand2")
        btn_agregar.grid(row=0, column=0, padx=5)

        btn_editar = tk.Button(frame_botones, text="✏ Editar",
                               command=self.abrir_formulario_editar,
                               bg="#3498db", fg="white",
                               font=("Arial", 10, "bold"),
                               width=15, height=2,
                               cursor="hand2")
        btn_editar.grid(row=0, column=1, padx=5)

        btn_eliminar = tk.Button(frame_botones, text="🗑️ Eliminar",
                                 command=self.eliminar_empleado,
                                 bg="#e74c3c", fg="white",
                                 font=("Arial", 10, "bold"),
                                 width=15, height=2,
                                 cursor="hand2")
        btn_eliminar.grid(row=0, column=2, padx=5)

        btn_refrescar = tk.Button(frame_botones, text="🔄 Refrescar",
                                  command=self.cargar_empleados,
                                  bg="#95a5a6", fg="white",
                                  font=("Arial", 10, "bold"),
                                  width=15, height=2,
                                  cursor="hand2")
        btn_refrescar.grid(row=0, column=3, padx=5)

        # Frame para la tabla
        frame_tabla = tk.Frame(self.parent, bg="#ecf0f1")
        frame_tabla.pack(pady=20, padx=20, fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla)
        scrollbar.pack(side="right", fill="y")

        # Treeview (tabla)
        self.tabla = ttk.Treeview(frame_tabla,
                                  columns=("id", "nombre", "apellido", "puesto", "telefono", "usuario", "privilegio"),
                                  show="headings",
                                  yscrollcommand=scrollbar.set)

        scrollbar.config(command=self.tabla.yview)

        # Configurar columnas
        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("apellido", text="Apellido")
        self.tabla.heading("puesto", text="Puesto")
        self.tabla.heading("telefono", text="Teléfono")
        self.tabla.heading("usuario", text="Usuario")
        self.tabla.heading("privilegio", text="Privilegio")

        self.tabla.column("id", width=50, anchor="center")
        self.tabla.column("nombre", width=120, anchor="w")
        self.tabla.column("apellido", width=120, anchor="w")
        self.tabla.column("puesto", width=120, anchor="center")
        self.tabla.column("telefono", width=100, anchor="center")
        self.tabla.column("usuario", width=100, anchor="center")
        self.tabla.column("privilegio", width=120, anchor="center")

        self.tabla.pack(fill="both", expand=True)

        # Evento de doble click para editar
        self.tabla.bind('<Double-1>', lambda e: self.abrir_formulario_editar())

    def cargar_empleados(self):
        """Carga los empleados desde la base de datos"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        # Obtener empleados de la base de datos
        empleados = self.db.obtener_empleados()

        # Insertar en la tabla (sin mostrar la contraseña)
        for emp in empleados:
            datos_mostrar = (emp[0], emp[1], emp[2], emp[3], emp[4], emp[5], emp[7])
            self.tabla.insert("", "end", values=datos_mostrar)

    def abrir_formulario_agregar(self):
        """Abre ventana para agregar empleado"""
        FormularioEmpleado(self.parent, self.db, self.cargar_empleados)

    def abrir_formulario_editar(self):
        """Abre ventana para editar empleado seleccionado"""
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un empleado para editar")
            return

        # Obtener datos de la fila seleccionada
        item = self.tabla.item(seleccion[0])
        datos_tabla = item['values']

        # Necesitamos obtener el empleado completo de la BD (incluyendo password)
        empleado_id = datos_tabla[0]

        # Buscar en la lista completa de empleados
        empleados = self.db.obtener_empleados()
        empleado_completo = None

        for emp in empleados:
            if emp[0] == empleado_id:
                empleado_completo = emp
                break

        if empleado_completo:
            FormularioEmpleado(self.parent, self.db, self.cargar_empleados, empleado_completo)

    def eliminar_empleado(self):
        """Elimina el empleado seleccionado"""
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un empleado para eliminar")
            return

        # Obtener ID del empleado
        item = self.tabla.item(seleccion[0])
        empleado_id = item['values'][0]
        nombre = item['values'][1]
        apellido = item['values'][2]

        # No permitir eliminar al admin
        if empleado_id == 1:
            messagebox.showerror("Error", "No se puede eliminar el usuario administrador")
            return

        # Confirmar eliminación
        respuesta = messagebox.askyesno(
            "Confirmar",
            f"¿Está seguro de eliminar al empleado {nombre} {apellido}?"
        )

        if respuesta:
            self.db.eliminar_empleado(empleado_id)
            messagebox.showinfo("Éxito", "Empleado eliminado correctamente")
            self.cargar_empleados()


class FormularioEmpleado:
    def __init__(self, parent, db, callback_refrescar, datos=None):
        """
        parent: Ventana padre
        db: Instancia de DatabaseManager
        callback_refrescar: Función para refrescar la tabla
        datos: Si viene con datos, es para EDITAR, si no, es para AGREGAR
        """
        self.db = db
        self.callback_refrescar = callback_refrescar
        self.datos = datos

        # Crear ventana emergente
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Agregar Empleado" if not datos else "Editar Empleado")
        self.ventana.geometry("450x600")
        self.ventana.resizable(False, False)
        #self.ventana.grab_set() NO FUNCIONAL

        # Centrar ventana
        self.centrar_ventana()

        # Crear formulario
        self.crear_formulario()

    def centrar_ventana(self):
        self.ventana.update_idletasks()
        width = self.ventana.winfo_width()
        height = self.ventana.winfo_height()
        x = (self.ventana.winfo_screenwidth() // 2) - (width // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (height // 2)
        self.ventana.geometry(f'{width}x{height}+{x}+{y}')

    def crear_formulario(self):
        # Frame principal con scrollbar
        canvas = tk.Canvas(self.ventana, bg="#ecf0f1")
        scrollbar = tk.Scrollbar(self.ventana, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg="#ecf0f1", padx=30, pady=30)

        frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Título
        titulo = "AGREGAR EMPLEADO" if not self.datos else "EDITAR EMPLEADO"
        tk.Label(frame, text=titulo,
                 font=("Arial", 14, "bold"),
                 bg="#ecf0f1").pack(pady=20)

        # Campo: Nombre
        tk.Label(frame, text="Nombre:",
                 bg="#ecf0f1", font=("Arial", 10)).pack(anchor="w", pady=(10, 5))
        self.entry_nombre = tk.Entry(frame, font=("Arial", 11), width=35)
        self.entry_nombre.pack(pady=(0, 10))

        # Campo: Apellido
        tk.Label(frame, text="Apellido:",
                 bg="#ecf0f1", font=("Arial", 10)).pack(anchor="w", pady=(10, 5))
        self.entry_apellido = tk.Entry(frame, font=("Arial", 11), width=35)
        self.entry_apellido.pack(pady=(0, 10))

        # Campo: Puesto
        tk.Label(frame, text="Puesto:",
                 bg="#ecf0f1", font=("Arial", 10)).pack(anchor="w", pady=(10, 5))
        self.combo_puesto = ttk.Combobox(frame,
                                         values=["Gerente", "Recepcionista", "Limpieza",
                                                 "Mantenimiento", "Seguridad", "Cocina"],
                                         font=("Arial", 11),
                                         width=33,
                                         state="readonly")
        self.combo_puesto.pack(pady=(0, 10))
        self.combo_puesto.set("Recepcionista")

        # Campo: Teléfono
        tk.Label(frame, text="Teléfono:",
                 bg="#ecf0f1", font=("Arial", 10)).pack(anchor="w", pady=(10, 5))
        self.entry_telefono = tk.Entry(frame, font=("Arial", 11), width=35)
        self.entry_telefono.pack(pady=(0, 10))

        # Separador
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=20)

        tk.Label(frame, text="DATOS DE ACCESO AL SISTEMA",
                 font=("Arial", 11, "bold"),
                 bg="#ecf0f1", fg="#34495e").pack(pady=10)

        # Campo: Usuario
        tk.Label(frame, text="Usuario:",
                 bg="#ecf0f1", font=("Arial", 10)).pack(anchor="w", pady=(10, 5))
        self.entry_usuario = tk.Entry(frame, font=("Arial", 11), width=35)
        self.entry_usuario.pack(pady=(0, 10))

        # Campo: Contraseña
        tk.Label(frame, text="Contraseña:",
                 bg="#ecf0f1", font=("Arial", 10)).pack(anchor="w", pady=(10, 5))
        self.entry_password = tk.Entry(frame, font=("Arial", 11), width=35, show="*")
        self.entry_password.pack(pady=(0, 10))

        # Campo: Privilegio
        tk.Label(frame, text="Privilegio:",
                 bg="#ecf0f1", font=("Arial", 10)).pack(anchor="w", pady=(10, 5))
        self.combo_privilegio = ttk.Combobox(frame,
                                             values=["Administrador", "Empleado"],
                                             font=("Arial", 11),
                                             width=33,
                                             state="readonly")
        self.combo_privilegio.pack(pady=(0, 20))
        self.combo_privilegio.set("Empleado")

        # Si hay datos (modo editar), rellenar campos
        if self.datos:
            # datos = (id, nombre, apellido, puesto, telefono, usuario, password, privilegio)
            self.entry_nombre.insert(0, self.datos[1])
            self.entry_apellido.insert(0, self.datos[2])
            self.combo_puesto.set(self.datos[3])
            self.entry_telefono.insert(0, self.datos[4] if self.datos[4] else "")
            self.entry_usuario.insert(0, self.datos[5] if self.datos[5] else "")
            self.entry_password.insert(0, self.datos[6] if self.datos[6] else "")
            self.combo_privilegio.set(self.datos[7] if self.datos[7] else "Empleado")

            # Si es el admin, deshabilitar cambio de privilegio
            if self.datos[0] == 1:
                self.combo_privilegio.config(state="disabled")

        # Frame para botones
        frame_botones = tk.Frame(frame, bg="#ecf0f1")
        frame_botones.pack(pady=20)

        # Botón Guardar
        btn_guardar = tk.Button(frame_botones, text="💾 Guardar",
                                command=self.guardar,
                                bg="#27ae60", fg="white",
                                font=("Arial", 11, "bold"),
                                width=12, height=2,
                                cursor="hand2")
        btn_guardar.grid(row=0, column=0, padx=5)

        # Botón Cancelar
        btn_cancelar = tk.Button(frame_botones, text="❌ Cancelar",
                                 command=self.ventana.destroy,
                                 bg="#e74c3c", fg="white",
                                 font=("Arial", 11, "bold"),
                                 width=12, height=2,
                                 cursor="hand2")
        btn_cancelar.grid(row=0, column=1, padx=5)

    def guardar(self):
        """Guarda o actualiza el empleado"""
        # Obtener valores
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        puesto = self.combo_puesto.get()
        telefono = self.entry_telefono.get().strip()
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()
        privilegio = self.combo_privilegio.get()

        # Validaciones básicas
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return

        if not apellido:
            messagebox.showerror("Error", "El apellido es obligatorio")
            return

        # Validar teléfono (solo números)
        if telefono and not telefono.isdigit():
            messagebox.showerror("Error", "El teléfono debe contener solo números")
            return

        # Guardar en base de datos
        if self.datos:  # EDITAR
            empleado_id = self.datos[0]

            # Si cambió el usuario o password, actualizar también
            if usuario != self.datos[5] or password != self.datos[6]:
                # Actualizar con nuevos datos de acceso
                exito = self.db.actualizar_empleado(empleado_id, nombre, apellido,
                                                    puesto, telefono, privilegio)
            else:
                # Actualizar solo datos básicos
                exito = self.db.actualizar_empleado(empleado_id, nombre, apellido,
                                                    puesto, telefono, privilegio)

            if exito:
                messagebox.showinfo("Éxito", "Empleado actualizado correctamente")
                self.callback_refrescar()
                self.ventana.destroy()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el empleado")

        else:  # AGREGAR
            if not usuario or not password:
                messagebox.showerror("Error", "Usuario y contraseña son obligatorios para nuevos empleados")
                return

            exito = self.db.agregar_empleado(nombre, apellido, puesto, telefono,
                                             usuario, password, privilegio)

            if exito:
                messagebox.showinfo("Éxito", "Empleado agregado correctamente")
                self.callback_refrescar()
                self.ventana.destroy()
            else:
                messagebox.showerror("Error", "El nombre de usuario ya existe")