import tkinter as tk
from tkinter import ttk, messagebox
from typing import Self

from database.db_manager import DatabaseManager

class HabitacionesWindow:
    def __init__(self, parent):
        self.parent = parent
        self.db = DatabaseManager()
        self.crear_widgets()
        self.cargar_habitaciones()

    def crear_widgets(self):
        #Titulo
        titulo = tk.Label(self.parent, text="🛏 GESTIÓN DE HABITACIONES",
                          bg="#ecf0f1",
                          font=("Arial", 12, "bold"))
        titulo.pack(pady=20)

        #Frame para botones
        frame_botones = tk.Frame(self.parent, bg="#ecf0f1")
        frame_botones.pack(pady=10)

        btn_agregar = tk.Button(frame_botones, text="➕ Agregar Habitacion=",
                                command= self.abrir_formulario_agregar,
                                bg="#27ae60", fg="white",
                                font=("Arial", 10, "bold"),
                                width=20, height=2,
                                cursor="hand2")
        btn_agregar.grid(row=0, column=0, padx=5)

        btn_editar = tk.Button(frame_botones, text="✏ Editar",
                               command= self.abrir_formulario_editar,
                               bg="#3498db", fg="white",
                               font=("Arial", 10, "bold"),
                               width=20, height=2,
                               cursor="hand2")
        btn_editar.grid(row=0, column=1, padx=5)

        btn_eliminar = tk.Button(frame_botones, text="🗑️ Eliminar",
                                 command=self.eliminar_habitacion,
                                 bg="#e74c3c", fg="white",
                                 font=("Arial", 10, "bold"),
                                 width=15, height=2,
                                 cursor="hand2")
        btn_eliminar.grid(row=0, column=2, padx=5)

        btn_refrescar = tk.Button(frame_botones, text="🔄 Refrescar",
                                  command=self.cargar_habitaciones,
                                  bg="#95a5a6", fg="white",
                                  font=("Arial", 10, "bold"),
                                  width=15, height=2,
                                  cursor="hand2")
        btn_refrescar.grid(row=0, column=3, padx=5)

        #Frame para tabla
        frame_tabla = tk.Frame(self.parent, bg="#ecf0f1")
        frame_tabla.pack(pady=20, padx=20, fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla)
        scrollbar.pack(side="right", fill="y")

        # Treeview (tabla)
        self.tabla = ttk.Treeview(frame_tabla,
                                  columns=("id", "numero", "tipo", "precio", "estado"),
                                  show="headings",
                                  yscrollcommand=scrollbar.set)

        scrollbar.config(command=self.tabla.yview)

        # Configurar columnas
        self.tabla.heading("id", text="ID")
        self.tabla.heading("numero", text="Número")
        self.tabla.heading("tipo", text="Tipo")
        self.tabla.heading("precio", text="Precio")
        self.tabla.heading("estado", text="Estado")

        self.tabla.column("id", width=50, anchor="center")
        self.tabla.column("numero", width=100, anchor="center")
        self.tabla.column("tipo", width=150, anchor="center")
        self.tabla.column("precio", width=100, anchor="center")
        self.tabla.column("estado", width=150, anchor="center")

        self.tabla.pack(fill="both", expand=True)

        # Evento de doble click para editar
        self.tabla.bind('<Double-1>', lambda e: self.abrir_formulario_editar())

    def cargar_habitaciones(self):
        """Carga las habitaciones desde la base de datos"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        # Obtener habitaciones de la base de datos
        habitaciones = self.db.obtener_habitaciones()

        # Insertar en la tabla
        for hab in habitaciones:
            self.tabla.insert("", "end", values=hab)

    def abrir_formulario_agregar(self):
        """Abre ventana para agregar habitación"""
        FormularioHabitacion(self.parent, self.db, self.cargar_habitaciones)

    def abrir_formulario_editar(self):
        """Abre ventana para editar habitación seleccionada"""
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una habitación para editar")
            return

        # Obtener datos de la fila seleccionada
        item = self.tabla.item(seleccion[0])
        datos = item['values']

        FormularioHabitacion(self.parent, self.db, self.cargar_habitaciones, datos)

    def eliminar_habitacion(self):
        """Elimina la habitación seleccionada"""
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una habitación para eliminar")
            return

        # Obtener ID de la habitación
        item = self.tabla.item(seleccion[0])
        habitacion_id = item['values'][0]
        numero = item['values'][1]

        # Confirmar eliminación
        respuesta = messagebox.askyesno(
            "Confirmar",
            f"¿Está seguro de eliminar la habitación {numero}?"
        )

        if respuesta:
            self.db.eliminar_habitacion(habitacion_id)
            messagebox.showinfo("Éxito", "Habitación eliminada correctamente")
            self.cargar_habitaciones()

    # gui/habitaciones_window.py (continuación)

    class FormularioHabitacion:
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

            # Crear ventana emergente (Toplevel)
            self.ventana = tk.Toplevel(parent)
            self.ventana.title("Agregar Habitación" if not datos else "Editar Habitación")
            self.ventana.geometry("400x400")
            self.ventana.resizable(False, False)
            self.ventana.grab_set()  # Hace la ventana modal (bloquea la principal)

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
            # Frame principal
            frame = tk.Frame(self.ventana, bg="#ecf0f1", padx=30, pady=30)
            frame.pack(fill="both", expand=True)

            # Título
            titulo = "AGREGAR HABITACIÓN" if not self.datos else "EDITAR HABITACIÓN"
            tk.Label(frame, text=titulo,
                     font=("Arial", 14, "bold"),
                     bg="#ecf0f1").pack(pady=20)

            # Campo: Número
            tk.Label(frame, text="Número de Habitación:",
                     bg="#ecf0f1", font=("Arial", 10)).pack(anchor="w", pady=(10, 5))
            self.entry_numero = tk.Entry(frame, font=("Arial", 11), width=30)
            self.entry_numero.pack(pady=(0, 10))

            # Campo: Tipo
            tk.Label(frame, text="Tipo:",
                     bg="#ecf0f1", font=("Arial", 10)).pack(anchor="w", pady=(10, 5))
            self.combo_tipo = ttk.Combobox(frame,
                                           values=["Sencilla", "Doble", "Familiar", "Deluxe"],
                                           font=("Arial", 11),
                                           width=28,
                                           state="readonly")
            self.combo_tipo.pack(pady=(0, 10))
            self.combo_tipo.set("Sencilla")

            # Campo: Precio
            tk.Label(frame, text="Precio:",
                     bg="#ecf0f1", font=("Arial", 10)).pack(anchor="w", pady=(10, 5))
            self.entry_precio = tk.Entry(frame, font=("Arial", 11), width=30)
            self.entry_precio.pack(pady=(0, 10))

            # Campo: Estado
            tk.Label(frame, text="Estado:",
                     bg="#ecf0f1", font=("Arial", 10)).pack(anchor="w", pady=(10, 5))
            self.combo_estado = ttk.Combobox(frame,
                                             values=["disponible", "ocupada", "limpieza", "mantenimiento"],
                                             font=("Arial", 11),
                                             width=28,
                                             state="readonly")
            self.combo_estado.pack(pady=(0, 20))
            self.combo_estado.set("disponible")

            # Si hay datos (modo editar), rellenar campos
            if self.datos:
                self.entry_numero.insert(0, self.datos[1])
                self.combo_tipo.set(self.datos[2])
                self.entry_precio.insert(0, self.datos[3])
                self.combo_estado.set(self.datos[4])

            # Frame para botones
            frame_botones = tk.Frame(frame, bg="#ecf0f1")
            frame_botones.pack(pady=10)

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
            """Guarda o actualiza la habitación"""
            # Obtener valores
            numero = self.entry_numero.get().strip()
            tipo = self.combo_tipo.get()
            precio_str = self.entry_precio.get().strip()
            estado = self.combo_estado.get()

            # Validaciones
            if not numero:
                messagebox.showerror("Error", "El número de habitación es obligatorio")
                return

            if not precio_str:
                messagebox.showerror("Error", "El precio es obligatorio")
                return

            # Validar que el precio sea un número
            try:
                precio = float(precio_str)
                if precio <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "El precio debe ser un número válido mayor a 0")
                return

            # Guardar en base de datos
            if self.datos:  # EDITAR
                habitacion_id = self.datos[0]
                exito = self.db.actualizar_habitacion(habitacion_id, numero, tipo, precio, estado)
                mensaje_exito = "Habitación actualizada correctamente"
            else:  # AGREGAR
                exito = self.db.agregar_habitacion(numero, tipo, precio, estado)
                mensaje_exito = "Habitación agregada correctamente"

            if exito:
                messagebox.showinfo("Éxito", mensaje_exito)
                self.callback_refrescar()  # Refresca la tabla
                self.ventana.destroy()  # Cierra la ventana
            else:
                messagebox.showerror("Error", "El número de habitación ya existe")

class FormularioHabitacion:
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

        # Crear ventana emergente (Toplevel)
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Agregar Habitación" if not datos else "Editar Habitación")
        self.ventana.geometry("600x600")
        self.ventana.resizable(False, False)
        #self.ventana.grab_set()  # Hace la ventana modal (bloquea la principal) SOLUCIONAR DESPUES

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
        # Frame principal
        frame = tk.Frame(self.ventana, bg="#ecf0f1", padx=30, pady=30)
        frame.pack(fill="both", expand=True)

        # Título
        titulo = "AGREGAR HABITACIÓN" if not self.datos else "EDITAR HABITACIÓN"
        tk.Label(frame, text=titulo,
                 font=("Arial", 14, "bold"),
                 bg="#ecf0f1").pack(pady=20)

        # Campo: Número
        tk.Label(frame, text="Número de Habitación:",
                 bg="#ecf0f1", font=("Arial", 10)).pack(anchor="w", pady=(10, 5))
        self.entry_numero = tk.Entry(frame, font=("Arial", 11), width=30)
        self.entry_numero.pack(pady=(0, 10))

        # Campo: Tipo
        tk.Label(frame, text="Tipo:",
                 bg="#ecf0f1", font=("Arial", 10)).pack(anchor="w", pady=(10, 5))
        self.combo_tipo = ttk.Combobox(frame,
                                       values=["Sencilla", "Doble", "Familiar", "Deluxe"],
                                       font=("Arial", 11),
                                       width=28,
                                       state="readonly")
        self.combo_tipo.pack(pady=(0, 10))
        self.combo_tipo.set("Sencilla")

        # Campo: Precio
        tk.Label(frame, text="Precio:",
                 bg="#ecf0f1", font=("Arial", 10)).pack(anchor="w", pady=(10, 5))
        self.entry_precio = tk.Entry(frame, font=("Arial", 11), width=30)
        self.entry_precio.pack(pady=(0, 10))

        # Campo: Estado
        tk.Label(frame, text="Estado:",
                 bg="#ecf0f1", font=("Arial", 10)).pack(anchor="w", pady=(10, 5))
        self.combo_estado = ttk.Combobox(frame,
                                         values=["Disponible", "Ocupada", "Limpieza", "Mantenimiento"],
                                         font=("Arial", 11),
                                         width=28,
                                         state="readonly")
        self.combo_estado.pack(pady=(0, 30))
        self.combo_estado.set("disponible")

        # Si hay datos (modo editar), rellenar campos
        if self.datos:
            self.entry_numero.insert(0, self.datos[1])
            self.combo_tipo.set(self.datos[2])
            self.entry_precio.insert(0, self.datos[3])
            self.combo_estado.set(self.datos[4])

        # Frame para botones
        frame_botones = tk.Frame(frame, bg="#ecf0f1")
        frame_botones.pack(pady=10)

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
        """Guarda o actualiza la habitación"""
        # Obtener valores
        numero = self.entry_numero.get().strip()
        tipo = self.combo_tipo.get()
        precio_str = self.entry_precio.get().strip()
        estado = self.combo_estado.get()

        # Validaciones
        if not numero:
            messagebox.showerror("Error", "El número de habitación es obligatorio")
            return

        if not precio_str:
            messagebox.showerror("Error", "El precio es obligatorio")
            return

        # Validar que el precio sea un número
        try:
            precio = float(precio_str)
            if precio <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número válido mayor a 0")
            return

        # Guardar en base de datos
        if self.datos:  # EDITAR
            habitacion_id = self.datos[0]
            exito = self.db.actualizar_habitacion(habitacion_id, numero, tipo, precio, estado)
            mensaje_exito = "Habitación actualizada correctamente"
        else:  # AGREGAR
            exito = self.db.agregar_habitacion(numero, tipo, precio, estado)
            mensaje_exito = "Habitación agregada correctamente"

        if exito:
            messagebox.showinfo("Éxito", mensaje_exito)
            self.callback_refrescar()  # Refresca la tabla
            self.ventana.destroy()  # Cierra la ventana
        else:
            messagebox.showerror("Error", "El número de habitación ya existe")