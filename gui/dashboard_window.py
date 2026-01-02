import tkinter as tk
from tkinter import ttk
from gui.habitaciones_window import HabitacionesWindow
from database.db_manager import DatabaseManager

class DashboardWindow:
    def __init__(self, root, nombre_empleado, apellido_empleado, puesto):
        self.root = root
        self.nombre_empleado = nombre_empleado
        self.apellido_empleado = apellido_empleado
        self.puesto = puesto
        self.db = DatabaseManager()

        self.root.title("Sistema Hotel - Panel Principal")
        self.root.geometry("900x600")

        #Maximizar ventana
        #self.root.state('zoomed') #Windows
        #self.root.attributes('-zoomed', True) #Linuxgod

        self.crear_widgets()

    def crear_widgets(self):

        #Barra superior
        barra_superior = tk.Frame(self.root, bg= "#34495e", height=400, width=60)
        barra_superior.pack(side="top", fill="x")

        titulo = tk.Label(barra_superior, text= "🏨 SISTEMA DE GESTIÓN HOTELERA",
                          font=("Arial", 18, "bold"),
                          bg="#34495e", fg="white")
        titulo.pack(pady=15)

        # Frame principal con dos columnas
        frame_principal = tk.Frame(self.root)
        frame_principal.pack(fill="both", expand=True)

        # Panel lateral (menú)
        self.panel_lateral = tk.Frame(frame_principal, bg="#2c3e50", width=200)
        self.panel_lateral.pack(side="left", fill="y")

        # Área de contenido
        self.area_contenido = tk.Frame(frame_principal, bg="#ecf0f1")
        self.area_contenido.pack(side="right", fill="both", expand=True)

        self.crear_menu()
        self.mostrar_inicio()

    def crear_menu(self):
        botones = [
            ("🏠 Inicio", self.mostrar_inicio),
            ("🛏 Habitaciones", self.abrir_habitaciones),
            ("👥 Empleados", self.abrir_empleados),
            ("📅 Reservas", self.abrir_reservas),
            ("🔧 Mantenimiento", self.abrir_mantenimiento),
            ("📊 Reportes", self.abrir_reportes),
            ("🚪 Salir", self.salir)
        ]

        for texto, comando in botones:
            btn = tk.Button(self.panel_lateral, text=texto,
                            command=comando,
                            bg="#34495e", fg="white",
                            font=("Arial", 11),
                            width=20, height=2,
                            bd=0, cursor="hand2",
                            activebackground="#1abc9c",
                            activeforeground="white")
            btn.pack(pady=5, padx=10)

    def limpiar_area_contenido(self):
        for widget in self.area_contenido.winfo_children():
            widget.destroy()

    def mostrar_inicio(self):
        self.limpiar_area_contenido()

        # Obtener estadisticas de la db
        stats = self.db.obtener_estadisticas()

        # Info empleado
        frame_info = tk.Frame(self.area_contenido, bg="#ecf0f1")
        frame_info.pack(pady=20)

        tk.Label(frame_info,
                 text=f"Bienvenido: {self.nombre_empleado} {self.apellido_empleado} - {self.puesto}",
                 font= ("Arial", 14, "bold"),
                 bg="#ecf0f1",).pack()

        # Frame para las tarjetas
        frame_tarjetas = tk.Frame(self.area_contenido, bg="#ecf0f1")
        frame_tarjetas.pack(expand=True)

        # Tarjetas de resumen
        tarjetas = [
            ("Habitaciones\nDisponibles", str(stats['disponibles']), "#27ae60"),
            ("Habitaciones\nOcupadas", str(stats['ocupadas']), "#e74c3c"),
            ("En Limpieza", str(stats['limpieza']), "#3498db"),
            ("Empleados\nActivos", str(stats['empleados']), "#9b59b6")
        ]

        for i, (titulo, valor, color) in enumerate(tarjetas):
            frame_tarjeta = tk.Frame(frame_tarjetas, bg=color,
                                     width=180, height=150)
            frame_tarjeta.grid(row=0, column=i, padx=20, pady=50)
            frame_tarjeta.pack_propagate(False)

            tk.Label(frame_tarjeta, text=valor,
                     font=("Arial", 36, "bold"),
                     bg=color, fg="white").pack(expand=True)

            tk.Label(frame_tarjeta, text=titulo,
                     font=("Arial", 11),
                     bg=color, fg="white").pack(pady=(0, 10))

    def abrir_habitaciones(self):
        self.limpiar_area_contenido()
        HabitacionesWindow(self.area_contenido)

    def abrir_empleados(self):
        self.limpiar_area_contenido()
        tk.Label(self.area_contenido, text="Módulo de Empleados",
                 font=("Arial", 20)).pack(pady=50)

    def abrir_reservas(self):
        self.limpiar_area_contenido()
        tk.Label(self.area_contenido, text="Módulo de Reservas",
                 font=("Arial", 20)).pack(pady=50)

    def abrir_mantenimiento(self):
        self.limpiar_area_contenido()
        tk.Label(self.area_contenido, text="Módulo de Mantenimiento",
                 font=("Arial", 20)).pack(pady=50)

    def abrir_reportes(self):
        self.limpiar_area_contenido()
        tk.Label(self.area_contenido, text="Módulo de Reportes",
                 font=("Arial", 20)).pack(pady=50)

    def salir(self):
        self.root.quit()