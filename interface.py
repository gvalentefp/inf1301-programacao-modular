print("--- [DEBUG] Interface v10: Mostrando APENAS avaliações do usuário ---")
import customtkinter as ctk
from tkinter import messagebox
import datetime 

# --- IMPORTAÇÕES DO BACKEND ---
from src.modules.credentialing import register_student_account, authenticate_user
from src.modules.student import retrieve_student_subjects
from src.modules.professor import retrieve_all_professors, create_professor
from src.modules.classes import create_class
from src.modules.review import create_review, retrieve_all_reviews, REVIEW_CATEGORIES
from src.persistence import database 

# Configuração visual
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class FilhosDaPUCApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Filhos da PUC - Sistema Acadêmico")
        self.geometry("1000x700")
        self.current_user = None
        
        # Preparação das Categorias (Códigos Crus)
        if REVIEW_CATEGORIES:
            self.categories_raw_list = list(REVIEW_CATEGORIES.keys())
        else:
            self.categories_raw_list = ["OTHER"]

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_sidebar()
        self.create_frames()
        self.show_frame("welcome")
        self.update_menu_buttons()

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Filhos da PUC", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_login_nav = ctk.CTkButton(self.sidebar_frame, text="Login", command=lambda: self.show_frame("login"))
        self.btn_login_nav.grid(row=1, column=0, padx=20, pady=10)

        self.btn_register_nav = ctk.CTkButton(self.sidebar_frame, text="Registrar", command=lambda: self.show_frame("register"))
        self.btn_register_nav.grid(row=2, column=0, padx=20, pady=10)

        self.btn_subjects_nav = ctk.CTkButton(self.sidebar_frame, text="Minhas Matérias", command=self.show_subjects)
        self.btn_subjects_nav.grid(row=3, column=0, padx=20, pady=10)

        self.btn_profs_nav = ctk.CTkButton(self.sidebar_frame, text="Ver Professores", command=self.show_professors)
        self.btn_profs_nav.grid(row=4, column=0, padx=20, pady=10)

        self.btn_reviews_nav = ctk.CTkButton(self.sidebar_frame, text="Avaliações", command=self.show_reviews, fg_color="#E59400", hover_color="#b37400")
        self.btn_reviews_nav.grid(row=5, column=0, padx=20, pady=10)

        self.btn_logout = ctk.CTkButton(self.sidebar_frame, text="Sair", fg_color="transparent", border_width=2, command=self.perform_logout)
        self.btn_logout.grid(row=8, column=0, padx=20, pady=20)

    def create_frames(self):
        # Welcome
        self.welcome_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.welcome_frame, text="Bem-vindo ao Sistema!", font=ctk.CTkFont(size=24)).pack(pady=100)

        # Login
        self.login_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.login_frame, text="Login do Aluno", font=("Arial", 20)).pack(pady=20)
        self.entry_login_enrollment = ctk.CTkEntry(self.login_frame, placeholder_text="Matrícula")
        self.entry_login_enrollment.pack(pady=10)
        self.entry_login_password = ctk.CTkEntry(self.login_frame, placeholder_text="Senha", show="*")
        self.entry_login_password.pack(pady=10)
        ctk.CTkButton(self.login_frame, text="Entrar", command=self.perform_login).pack(pady=20)

        # Registro
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

        # Listas (Genérico)
        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.lbl_list_title = ctk.CTkLabel(self.list_frame, text="Lista", font=("Arial", 18))
        self.lbl_list_title.pack(pady=10)
        self.textbox_list = ctk.CTkTextbox(self.list_frame, width=700, height=500)
        self.textbox_list.pack(pady=10)

        # Reviews (Criação e Lista Pessoal)
        self.reviews_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.reviews_frame, text="Central de Avaliações", font=("Arial", 20, "bold")).pack(pady=10)
        
        self.frame_create_review = ctk.CTkFrame(self.reviews_frame)
        self.frame_create_review.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(self.frame_create_review, text="Nova Avaliação").pack(pady=2)
        self.entry_review_title = ctk.CTkEntry(self.frame_create_review, placeholder_text="Título (Ex: Ótima didática)")
        self.entry_review_title.pack(pady=5, padx=10, fill="x")
        
        self.entry_review_class_id = ctk.CTkEntry(self.frame_create_review, placeholder_text="Código da Turma (Ex: 101)")
        self.entry_review_class_id.pack(pady=5, padx=10, fill="x")
        
        # SELETOR DE PROFESSOR
        profs_db = retrieve_all_professors()
        if profs_db:
            self.professors_list = [f"{p['name']} (ID: {p['id']})" for p in profs_db]
        else:
            self.professors_list = ["Nenhum professor encontrado"]

        ctk.CTkLabel(self.frame_create_review, text="Selecione o Professor:").pack(pady=2)
        self.option_professor = ctk.CTkComboBox(self.frame_create_review, values=self.professors_list)
        if self.professors_list:
            self.option_professor.set(self.professors_list[0])
        self.option_professor.pack(pady=5, padx=10, fill="x")

        # Nota 0-5 (Input Decimal)
        self.entry_rating = ctk.CTkEntry(self.frame_create_review, placeholder_text="Nota (0.0 a 5.0)")
        self.entry_rating.pack(pady=5, padx=10, fill="x")

        self.entry_review_comment = ctk.CTkEntry(self.frame_create_review, placeholder_text="Seu comentário...", width=300)
        self.entry_review_comment.pack(pady=5, padx=10, fill="x")
        
        self.check_anonymous = ctk.CTkCheckBox(self.frame_create_review, text="Postar como Anônimo")
        self.check_anonymous.pack(pady=5)
        
        ctk.CTkButton(self.frame_create_review, text="Enviar", fg_color="green", command=self.perform_review).pack(pady=10)

        # --- MUDANÇA NO TÍTULO ---
        ctk.CTkLabel(self.reviews_frame, text="Minhas Avaliações Recentes").pack(pady=5)
        self.textbox_reviews = ctk.CTkTextbox(self.reviews_frame, width=600, height=200)
        self.textbox_reviews.pack(pady=10)

    # --- NAVEGAÇÃO ---
    def show_frame(self, frame_name):
        if frame_name == "reviews":
            profs_db = retrieve_all_professors()
            if profs_db:
                lista_atualizada = [f"{p['name']} (ID: {p['id']})" for p in profs_db]
                self.option_professor.configure(values=lista_atualizada)
                if not self.option_professor.get() in lista_atualizada:
                    self.option_professor.set(lista_atualizada[0])

        for frame in [self.welcome_frame, self.login_frame, self.register_frame, self.list_frame, self.reviews_frame]:
            frame.grid_forget()
        
        if frame_name == "welcome": self.welcome_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "login": self.login_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "register": self.register_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "list": self.list_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "reviews": self.reviews_frame.grid(row=0, column=1, sticky="nsew")

    def update_menu_buttons(self):
        if self.current_user:
            self.btn_login_nav.grid_forget()
            self.btn_register_nav.grid_forget()
            self.btn_subjects_nav.grid(row=3, column=0, padx=20, pady=10)
            self.btn_profs_nav.grid(row=4, column=0, padx=20, pady=10)
            self.btn_reviews_nav.grid(row=5, column=0, padx=20, pady=10)
            self.btn_logout.grid(row=8, column=0, padx=20, pady=20)
            self.logo_label.configure(text=f"Olá, {self.current_user['username']}")
        else:
            self.btn_login_nav.grid(row=1, column=0, padx=20, pady=10)
            self.btn_register_nav.grid(row=2, column=0, padx=20, pady=10)
            self.btn_subjects_nav.grid_forget()
            self.btn_profs_nav.grid_forget()
            self.btn_reviews_nav.grid_forget()
            self.btn_logout.grid_forget()
            self.logo_label.configure(text="Filhos da PUC")

    # --- AÇÕES DO SISTEMA ---
    def perform_login(self):
        try:
            m = int(self.entry_login_enrollment.get())
            s = self.entry_login_password.get()
            res = authenticate_user(m, s)
            if isinstance(res, dict):
                self.current_user = res
                self.update_menu_buttons()
                self.show_frame("welcome")
                messagebox.showinfo("Sucesso", "Logado com sucesso!")
            else:
                messagebox.showerror("Erro", "Login falhou.")
        except: messagebox.showerror("Erro", "A matrícula deve ser apenas números.")

    def perform_register(self):
        try:
            data = {
                'enrollment': int(self.reg_enrollment.get()), 'username': self.reg_username.get(), 
                'password': self.reg_password.get(), 'name': self.reg_name.get(), 
                'institutional_email': self.reg_email.get(), 'course': self.reg_course.get()
            }
            register_student_account(data)
            messagebox.showinfo("Sucesso", "Conta criada.")
            self.show_frame("login")
        except Exception as e: messagebox.showerror("Erro", str(e))

    def perform_logout(self):
        self.current_user = None
        self.update_menu_buttons()
        self.show_frame("welcome")

    # --- EXIBIÇÃO DE DADOS (READ-ONLY) ---

    def set_text_readonly(self, textbox, text):
        textbox.configure(state="normal") 
        textbox.delete("0.0", "end")
        textbox.insert("0.0", text)
        textbox.configure(state="disabled") 

    def show_subjects(self):
        self.show_frame("list")
        self.lbl_list_title.configure(text="Minhas Matérias")
        subs = retrieve_student_subjects(self.current_user['enrollment'])
        texto = str(subs) if subs else "Você não está inscrito em nenhuma matéria."
        self.set_text_readonly(self.textbox_list, texto)

    def show_professors(self):
        self.show_frame("list")
        self.lbl_list_title.configure(text="Professores & Avaliações")
        
        profs = retrieve_all_professors()
        all_reviews = retrieve_all_reviews()
        all_classes = database.get('classes', []) 

        if not profs:
            self.set_text_readonly(self.textbox_list, "Nenhum professor encontrado.")
            return

        texto_final = ""
        for p in profs:
            texto_final += f"========================================\n"
            texto_final += f"PROFESSOR: {p['name']} (ID: {p['id']}) - {p['department']}\n"
            texto_final += f"========================================\n"
            
            turmas_do_prof = [c['code'] for c in all_classes if p['id'] in c.get('professors_ids', [])]
            reviews_do_prof = [r for r in all_reviews if r.get('class_target_code') in turmas_do_prof]

            if reviews_do_prof:
                for r in reviews_do_prof:
                    # Formatação de nota float
                    nota = r.get('stars', 0)
                    texto_final += f"   -> [{r.get('category')}] Nota: {nota}\n"
                    texto_final += f"      \"{r.get('comment')}\"\n"
                    texto_final += f"      (Turma: {r.get('class_target_code')})\n\n"
            else:
                texto_final += "   (Sem avaliações ainda)\n\n"
            
            texto_final += "\n"

        self.set_text_readonly(self.textbox_list, texto_final)

    def show_reviews(self):
        self.show_frame("reviews")
        
        if not self.current_user:
            self.set_text_readonly(self.textbox_reviews, "Faça login para ver suas avaliações.")
            return

        try:
            # --- MUDANÇA AQUI: FILTRAR PELO USUÁRIO LOGADO ---
            # retrieve_all_reviews aceita um argumento opcional para filtrar por matrícula
            minhas_matricula = self.current_user['enrollment']
            revs = retrieve_all_reviews(minhas_matricula)
            # -------------------------------------------------

            txt = ""
            if revs:
                for r in revs:
                    cat = r.get('category')
                    nota = r.get('stars', 0)
                    txt += f"[{cat}] Nota: {nota}\n"
                    txt += f"Título: {r.get('title')}\n"
                    txt += f"Comentário: {r.get('comment')}\n"
                    txt += "----------------------------------------\n"
            else: txt = "Você ainda não fez nenhuma avaliação."
            
            self.set_text_readonly(self.textbox_reviews, txt)
            
        except Exception as e: 
            self.set_text_readonly(self.textbox_reviews, f"Erro: {e}")

    def perform_review(self):
        if not self.current_user: return messagebox.showerror("Erro", "Logue primeiro.")
        try:
            cat_code = "PROF_GOOD" 

            # Validação Float
            nota_str = self.entry_rating.get()
            nota_str = nota_str.replace(",", ".")
            
            try:
                nota_float = float(nota_str)
            except ValueError:
                return messagebox.showerror("Erro", "Nota deve ser um número (Ex: 4.5).")

            if nota_float < 0 or nota_float > 5: 
                return messagebox.showerror("Erro", "Nota deve ser entre 0.0 e 5.0.")

            tc = self.entry_review_class_id.get()
            
            data = {
                "student_enrollment": self.current_user['enrollment'],
                "title": self.entry_review_title.get(), 
                "comment": self.entry_review_comment.get(),
                "stars": nota_float,
                "category": cat_code, 
                "class_target_code": int(tc) if tc else None, 
                "is_anonymous": bool(self.check_anonymous.get()),
                "date_time": datetime.datetime.now().isoformat()
            }
            
            ret = create_review(data)
            
            if ret == 0:
                messagebox.showinfo("Sucesso", "Enviado!")
                self.show_reviews() 
                self.entry_review_title.delete(0, "end")
                self.entry_review_comment.delete(0, "end")
                self.entry_rating.delete(0, "end")
            else: 
                messagebox.showerror("Erro", "Falha no backend.")
                
        except Exception as e: messagebox.showerror("Erro", str(e))

def run_frontend():
    print("[Interface] Iniciando GUI...")
    if not database.get('professors'):
        try:
            create_professor({'id': 1, 'name': 'Arndt von Staa', 'department': 'INF'})
            create_professor({'id': 2, 'name': 'Noemi Rodriguez', 'department': 'INF'})
            create_class({'code': 101, 'subject_code': 'INF1301', 'semester': '2025.1', 'professors_ids': [1, 2]})
        except: pass
    app = FilhosDaPUCApp()
    app.mainloop()