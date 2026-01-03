# gui/empleados_window.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager


class EmpleadosWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db = DatabaseManager()
        self.crear_widgets()
        self.cargar_empleados()

    def crear_widgets(self):
        # Container principal
        main_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header = ctk.CTkFrame(main_container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(header,
                     text="👥 Gestión de Empleados",
                     font=("Segoe UI", 24, "bold")).pack(anchor="w")

        # Frame para botones
        frame_botones = ctk.CTkFrame(main_container, fg_color="transparent")
        frame_botones.pack(fill="x", pady=(0, 15))

        btn_agregar = ctk.CTkButton(frame_botones,
                                    text="➕ Agregar Empleado",
                                    command=self.abrir_formulario_agregar,
                                    font=("Segoe UI", 12, "bold"),
                                    height=40,
                                    corner_radius=10,
                                    fg_color="#27ae60",
                                    hover_color="#229954")
        btn_agregar.pack(side="left", padx=(0, 10))

        btn_editar = ctk.CTkButton(frame_botones,
                                   text="✏️ Editar",
                                   command=self.abrir_formulario_editar,
                                   font=("Segoe UI", 12, "bold"),
                                   height=40,
                                   corner_radius=10,
                                   fg_color="#3498db",
                                   hover_color="#2980b9")
        btn_editar.pack(side="left", padx=(0, 10))

        btn_eliminar = ctk.CTkButton(frame_botones,
                                     text="🗑️ Eliminar",
                                     command=self.eliminar_empleado,
                                     font=("Segoe UI", 12, "bold"),
                                     height=40,
                                     corner_radius=10,
                                     fg_color="#e74c3c",
                                     hover_color="#c0392b")
        btn_eliminar.pack(side="left", padx=(0, 10))

        btn_refrescar = ctk.CTkButton(frame_botones,
                                      text="🔄 Refrescar",
                                      command=self.cargar_empleados,
                                      font=("Segoe UI", 12, "bold"),
                                      height=40,
                                      corner_radius=10,
                                      fg_color="#95a5a6",
                                      hover_color="#7f8c8d")
        btn_refrescar.pack(side="left")

        # Frame para la tabla
        frame_tabla = ctk.CTkFrame(main_container)
        frame_tabla.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla)
        scrollbar.pack(side="right", fill="y")

        # Estilo para Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        borderwidth=0,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#1f538d",
                        foreground="white",
                        borderwidth=0,
                        font=("Segoe UI", 11, "bold"))
        style.map("Treeview",
                  background=[("selected", "#3498db")])

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

        self.tabla.pack(fill="both", expand=True, padx=2, pady=2)

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
            # emp = (id, nombre, apellido, puesto, telefono, usuario, password, privilegio)
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

        # Buscar empleado completo en la BD
        empleado_id = datos_tabla[0]
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
        self.db = db
        self.callback_refrescar = callback_refrescar
        self.datos = datos

        # Crear ventana emergente
        from tkinter import Toplevel
        self.ventana = Toplevel(parent)
        self.ventana.title("Agregar Empleado" if not datos else "Editar Empleado")
        self.ventana.geometry("550x700")
        self.ventana.resizable(False, False)
        #self.ventana.grab_set()

        # Aplicar tema oscuro
        self.ventana.configure(bg="#2b2b2b")

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
        # Frame principal con scroll
        main_frame = ctk.CTkScrollableFrame(self.ventana, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        titulo = "AGREGAR EMPLEADO" if not self.datos else "EDITAR EMPLEADO"
        ctk.CTkLabel(main_frame,
                     text=titulo,
                     font=("Segoe UI", 18, "bold")).pack(pady=(10, 25))

        # DATOS PERSONALES
        ctk.CTkLabel(main_frame,
                     text="DATOS PERSONALES",
                     font=("Segoe UI", 13, "bold"),
                     text_color="#3498db").pack(anchor="w", padx=20, pady=(10, 15))

        # Nombre
        ctk.CTkLabel(main_frame,
                     text="Nombre",
                     font=("Segoe UI", 11),
                     anchor="w").pack(anchor="w", padx=20, pady=(0, 5))

        self.entry_nombre = ctk.CTkEntry(main_frame,
                                         placeholder_text="Ej: Juan",
                                         height=40,
                                         font=("Segoe UI", 12),
                                         corner_radius=10)
        self.entry_nombre.pack(fill="x", padx=20, pady=(0, 12))

        # Apellido
        ctk.CTkLabel(main_frame,
                     text="Apellido",
                     font=("Segoe UI", 11),
                     anchor="w").pack(anchor="w", padx=20, pady=(0, 5))

        self.entry_apellido = ctk.CTkEntry(main_frame,
                                           placeholder_text="Ej: Pérez",
                                           height=40,
                                           font=("Segoe UI", 12),
                                           corner_radius=10)
        self.entry_apellido.pack(fill="x", padx=20, pady=(0, 12))

        # Puesto
        ctk.CTkLabel(main_frame,
                     text="Puesto",
                     font=("Segoe UI", 11),
                     anchor="w").pack(anchor="w", padx=20, pady=(0, 5))

        self.combo_puesto = ctk.CTkComboBox(main_frame,
                                            values=["Gerente", "Recepcionista", "Limpieza",
                                                    "Mantenimiento", "Seguridad", "Cocina"],
                                            height=40,
                                            font=("Segoe UI", 12),
                                            corner_radius=10,
                                            button_color="#3498db",
                                            button_hover_color="#2980b9")
        self.combo_puesto.pack(fill="x", padx=20, pady=(0, 12))
        self.combo_puesto.set("Recepcionista")

        # Teléfono
        ctk.CTkLabel(main_frame,
                     text="Teléfono",
                     font=("Segoe UI", 11),
                     anchor="w").pack(anchor="w", padx=20, pady=(0, 5))

        self.entry_telefono = ctk.CTkEntry(main_frame,
                                           placeholder_text="Ej: 1234567890",
                                           height=40,
                                           font=("Segoe UI", 12),
                                           corner_radius=10)
        self.entry_telefono.pack(fill="x", padx=20, pady=(0, 20))

        # Separador
        ctk.CTkFrame(main_frame, height=2, fg_color=("gray70", "gray30")).pack(fill="x", padx=20, pady=15)

        # DATOS DE ACCESO
        ctk.CTkLabel(main_frame,
                     text="DATOS DE ACCESO AL SISTEMA",
                     font=("Segoe UI", 13, "bold"),
                     text_color="#e74c3c").pack(anchor="w", padx=20, pady=(10, 15))

        # Usuario
        ctk.CTkLabel(main_frame,
                     text="Usuario",
                     font=("Segoe UI", 11),
                     anchor="w").pack(anchor="w", padx=20, pady=(0, 5))

        self.entry_usuario = ctk.CTkEntry(main_frame,
                                          placeholder_text="Nombre de usuario único",
                                          height=40,
                                          font=("Segoe UI", 12),
                                          corner_radius=10)
        self.entry_usuario.pack(fill="x", padx=20, pady=(0, 12))

        # Contraseña
        ctk.CTkLabel(main_frame,
                     text="Contraseña",
                     font=("Segoe UI", 11),
                     anchor="w").pack(anchor="w", padx=20, pady=(0, 5))

        self.entry_password = ctk.CTkEntry(main_frame,
                                           placeholder_text="Mínimo 4 caracteres",
                                           height=40,
                                           font=("Segoe UI", 12),
                                           show="•",
                                           corner_radius=10)
        self.entry_password.pack(fill="x", padx=20, pady=(0, 12))

        # Privilegio
        ctk.CTkLabel(main_frame,
                     text="Nivel de Privilegio",
                     font=("Segoe UI", 11),
                     anchor="w").pack(anchor="w", padx=20, pady=(0, 5))

        self.combo_privilegio = ctk.CTkComboBox(main_frame,
                                                values=["Administrador", "Empleado"],
                                                height=40,
                                                font=("Segoe UI", 12),
                                                corner_radius=10,
                                                button_color="#3498db",
                                                button_hover_color="#2980b9")
        self.combo_privilegio.pack(fill="x", padx=20, pady=(0, 25))
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

            # Si es el admin, deshabilitar privilegio
            if self.datos[0] == 1:
                self.combo_privilegio.configure(state="disabled")

        # Frame para botones
        frame_botones = ctk.CTkFrame(main_frame, fg_color="transparent")
        frame_botones.pack(pady=(10, 15))

        # Botón Guardar
        btn_guardar = ctk.CTkButton(frame_botones,
                                    text="💾 Guardar",
                                    command=self.guardar,
                                    width=180,
                                    height=45,
                                    font=("Segoe UI", 13, "bold"),
                                    corner_radius=10,
                                    fg_color="#27ae60",
                                    hover_color="#229954")
        btn_guardar.pack(side="left", padx=5)

        # Botón Cancelar
        btn_cancelar = ctk.CTkButton(frame_botones,
                                     text="❌ Cancelar",
                                     command=self.ventana.destroy,
                                     width=180,
                                     height=45,
                                     font=("Segoe UI", 13, "bold"),
                                     corner_radius=10,
                                     fg_color="#e74c3c",
                                     hover_color="#c0392b")
        btn_cancelar.pack(side="left", padx=5)

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
                messagebox.showerror("Error", "Usuario y contraseña son obligatorios")
                return

            exito = self.db.agregar_empleado(nombre, apellido, puesto, telefono,
                                             usuario, password, privilegio)

            if exito:
                messagebox.showinfo("Éxito", "Empleado agregado correctamente")
                self.callback_refrescar()
                self.ventana.destroy()
            else:
                messagebox.showerror("Error", "El nombre de usuario ya existe")