import customtkinter as ctk
from tkinter import messagebox

# --- CORREÇÃO DAS IMPORTAÇÕES (Adicionei 'src.' na frente) ---
# Como estamos na raiz, precisamos entrar na pasta src primeiro
from src.modules.credentialing import register_student_account, authenticate_user
from src.modules.student import retrieve_student_subjects
from src.modules.professor import retrieve_all_professors
# -------------------------------------------------------------

# Configuração visual básica
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class FilhosDaPUCApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela
        self.title("Filhos da PUC - Sistema Acadêmico")
        self.geometry("900x600")
        
        # Variável de Estado (Quem está logado)
        self.current_user = None

        # Layout Principal: Grid de 2 colunas
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Cria Menu e Frames
        self.create_sidebar()
        self.create_frames()

        # Inicia na tela de boas-vindas
        self.show_frame("welcome")
        self.update_menu_buttons()

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Filhos da PUC", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Botões de Navegação
        self.btn_login_nav = ctk.CTkButton(self.sidebar_frame, text="Login", command=lambda: self.show_frame("login"))
        self.btn_login_nav.grid(row=1, column=0, padx=20, pady=10)

        self.btn_register_nav = ctk.CTkButton(self.sidebar_frame, text="Registrar", command=lambda: self.show_frame("register"))
        self.btn_register_nav.grid(row=2, column=0, padx=20, pady=10)

        self.btn_subjects_nav = ctk.CTkButton(self.sidebar_frame, text="Minhas Matérias", command=self.show_subjects)
        self.btn_subjects_nav.grid(row=3, column=0, padx=20, pady=10)

        self.btn_profs_nav = ctk.CTkButton(self.sidebar_frame, text="Ver Professores", command=self.show_professors)
        self.btn_profs_nav.grid(row=4, column=0, padx=20, pady=10)

        self.btn_logout = ctk.CTkButton(self.sidebar_frame, text="Sair", fg_color="transparent", border_width=2, command=self.perform_logout)
        self.btn_logout.grid(row=7, column=0, padx=20, pady=20)

    def create_frames(self):
        # Frame Welcome
        self.welcome_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.lbl_welcome = ctk.CTkLabel(self.welcome_frame, text="Bem-vindo ao Sistema!", font=ctk.CTkFont(size=24))
        self.lbl_welcome.pack(pady=100)

        # Frame Login
        self.login_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.login_frame, text="Login do Aluno", font=("Arial", 20)).pack(pady=20)
        self.entry_login_enrollment = ctk.CTkEntry(self.login_frame, placeholder_text="Matrícula")
        self.entry_login_enrollment.pack(pady=10)
        self.entry_login_password = ctk.CTkEntry(self.login_frame, placeholder_text="Senha", show="*")
        self.entry_login_password.pack(pady=10)
        ctk.CTkButton(self.login_frame, text="Entrar", command=self.perform_login).pack(pady=20)

        # Frame Registro
        self.register_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.register_frame, text="Nova Conta", font=("Arial", 20)).pack(pady=10)
        self.reg_enrollment = ctk.CTkEntry(self.register_frame, placeholder_text="Matrícula")
        self.reg_enrollment.pack(pady=5)
        self.reg_username = ctk.CTkEntry(self.register_frame, placeholder_text="Username")
        self.reg_username.pack(pady=5)
        self.reg_password = ctk.CTkEntry(self.register_frame, placeholder_text="Senha", show="*")
        self.reg_password.pack(pady=5)
        self.reg_name = ctk.CTkEntry(self.register_frame, placeholder_text="Nome Completo")
        self.reg_name.pack(pady=5)
        self.reg_email = ctk.CTkEntry(self.register_frame, placeholder_text="Email @puc-rio.br")
        self.reg_email.pack(pady=5)
        self.reg_course = ctk.CTkEntry(self.register_frame, placeholder_text="Curso (Ex: CIEN_COMP)")
        self.reg_course.pack(pady=5)
        ctk.CTkButton(self.register_frame, text="Cadastrar", fg_color="green", command=self.perform_register).pack(pady=20)

        # Frame Lista (Matérias/Profs)
        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.lbl_list_title = ctk.CTkLabel(self.list_frame, text="Lista", font=("Arial", 18))
        self.lbl_list_title.pack(pady=10)
        self.textbox_list = ctk.CTkTextbox(self.list_frame, width=500, height=400)
        self.textbox_list.pack(pady=10)

    def show_frame(self, frame_name):
        self.welcome_frame.grid_forget()
        self.login_frame.grid_forget()
        self.register_frame.grid_forget()
        self.list_frame.grid_forget()

        if frame_name == "welcome": self.welcome_frame.grid(row=0, column=1, sticky="nsew")
        if frame_name == "login": self.login_frame.grid(row=0, column=1, sticky="nsew")
        if frame_name == "register": self.register_frame.grid(row=0, column=1, sticky="nsew")
        if frame_name == "list": self.list_frame.grid(row=0, column=1, sticky="nsew")

    def update_menu_buttons(self):
        if self.current_user:
            self.btn_login_nav.grid_forget()
            self.btn_register_nav.grid_forget()
            self.btn_subjects_nav.grid(row=3, column=0, padx=20, pady=10)
            self.btn_profs_nav.grid(row=4, column=0, padx=20, pady=10)
            self.btn_logout.grid(row=7, column=0, padx=20, pady=20)
            self.logo_label.configure(text=f"Olá, {self.current_user['username']}")
        else:
            self.btn_login_nav.grid(row=1, column=0, padx=20, pady=10)
            self.btn_register_nav.grid(row=2, column=0, padx=20, pady=10)
            self.btn_subjects_nav.grid_forget()
            self.btn_profs_nav.grid_forget()
            self.btn_logout.grid_forget()
            self.logo_label.configure(text="Filhos da PUC")

    def perform_login(self):
        try:
            matricula = int(self.entry_login_enrollment.get())
            senha = self.entry_login_password.get()
            resultado = authenticate_user(matricula, senha) # Chama Backend
            if isinstance(resultado, dict):
                self.current_user = resultado
                messagebox.showinfo("Sucesso", "Login realizado!")
                self.update_menu_buttons()
                self.show_frame("welcome")
            else:
                messagebox.showerror("Erro", "Dados incorretos.")
        except ValueError:
            messagebox.showerror("Erro", "Matrícula deve ser número.")

    def perform_register(self):
        try:
            data = {
                'enrollment': int(self.reg_enrollment.get()),
                'username': self.reg_username.get(),
                'password': self.reg_password.get(),
                'name': self.reg_name.get(),
                'institutional_email': self.reg_email.get(),
                'course': self.reg_course.get()
            }
            register_student_account(data) # Chama Backend
            messagebox.showinfo("Sucesso", "Conta criada! Faça login.")
            self.show_frame("login")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def perform_logout(self):
        self.current_user = None
        self.update_menu_buttons()
        self.show_frame("welcome")

    def show_subjects(self):
        self.show_frame("list")
        self.lbl_list_title.configure(text="Minhas Matérias")
        self.textbox_list.delete("0.0", "end")
        subjects = retrieve_student_subjects(self.current_user['enrollment']) # Chama Backend
        self.textbox_list.insert("0.0", str(subjects) if subjects else "Nenhuma matéria.")

    def show_professors(self):
        self.show_frame("list")
        self.lbl_list_title.configure(text="Todos os Professores")
        self.textbox_list.delete("0.0", "end")
        profs = retrieve_all_professors() # Chama Backend
        texto = ""
        if profs:
            for p in profs:
                texto += f"ID: {p['id']} | {p['name']} | {p['department']}\n"
        else:
            texto = "Nenhum professor."
        self.textbox_list.insert("0.0", texto)

if __name__ == "__main__":
    app = FilhosDaPUCApp()
    app.mainloop()