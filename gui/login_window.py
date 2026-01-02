import tkinter as tk
from tkinter import messagebox
from gui.dashboard_window import DashboardWindow
from database.db_manager import DatabaseManager

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Hotel - Login")
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        #Inicializar db
        self.db = DatabaseManager()

        #Centrar ventana
        self.centrar_ventana()

        #Crear widgets
        self.crear_widgets()

    def centrar_ventana(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def crear_widgets(self):

        #Frame principal
        frame = tk.Frame(self.root, bg="#2c3e50", padx=30, pady=30)
        frame.pack(fill="both", expand=True)

        #Titulo
        titulo = tk.Label(frame, text="🏨 SISTEMA HOTELERO", font = ("ARIAL",12, "bold"), bg="#2c3e50", fg="white")
        titulo.pack(pady=20)

        #Usuario
        tk.Label(frame, text="Usuario:", bg="#2c3e50", fg="white", font= ("ARIAL",11)).pack(anchor="w", pady=(10, 5))
        self.entry_usuario = tk.Entry(frame, font= ("ARIAL",11), width= 30)
        self.entry_usuario.pack(pady=(0, 10))
        self.entry_usuario.insert(0,"admin") #Usuario para pruebas

        #Contrasena
        tk.Label(frame, text="Contrasena:", bg="#2c3e50", fg="white", font=("ARIAL", 11)).pack(anchor="w", pady=(10, 5))
        self.entry_password = tk.Entry(frame, font=("ARIAL", 11), width=30, show="*")
        self.entry_password.pack(pady=(0, 20))
        self.entry_password.insert(0, "1234")  # Contra para pruebas

        #Enter para login
        self.entry_password.bind('<Return>', lambda e: self.validar_login())

        #Boton login
        btn_login = tk.Button(frame, text="ACCEDER",
                              command=self.validar_login,
                              bg="#27ae60", fg="white",
                              font= ("ARIAL", 12, "bold"),
                              width=20, height=2,
                              cursor="hand2"
                              )
        btn_login.pack(pady=10)

    def validar_login(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()

        if not usuario or not password:
            messagebox.showerror("ADVERTENCIA", "DATOS INCOMPLETOS")

        # Validacion db
        empleado = self.db.validar_login(usuario, password)
        if empleado:
            empleado_id, nombre, apellido, puesto = empleado
            self.db.cerrar()
            self.root.destroy()
            self.abrir_dashboard(nombre, apellido, puesto)
        else:
            messagebox.showerror("ERROR", "Usuario o contrasena incorretos")
            self.entry_password.delete(0, tk.END)

    def abrir_dashboard(self, nombre, apellido, puesto):
        root = tk.Tk()
        DashboardWindow(root, nombre, apellido, puesto)
        root.mainloop()


