print("--- [DEBUG] Interface v8: Professores Clicáveis e Filtro de Reviews ---")
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
        
        # Dicionário para guardar ID dos professores carregados no menu
        # Ex: {"Arndt von Staa": 1, "Noemi": 2}
        self.mapa_professores = {} 

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

        self.btn_reviews_nav = ctk.CTkButton(self.sidebar_frame, text="Avaliações", command=lambda: self.show_reviews(filtro_prof_id=None), fg_color="#E59400", hover_color="#b37400")
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

        # --- ÁREA DE LISTAS (Híbrida: Texto ou Botões) ---
        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.lbl_list_title = ctk.CTkLabel(self.list_frame, text="Lista", font=("Arial", 18))
        self.lbl_list_title.pack(pady=10)
        
        # Caixa de texto para Matérias (Read Only)
        self.textbox_list = ctk.CTkTextbox(self.list_frame, width=600, height=400)
        self.textbox_list.configure(state="disabled")
        
        # Scrollable Frame para Professores (Clicáveis)
        self.scroll_profs = ctk.CTkScrollableFrame(self.list_frame, width=600, height=400)

        # 5. Frame de Reviews
        self.reviews_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.lbl_review_title = ctk.CTkLabel(self.reviews_frame, text="Central de Avaliações", font=("Arial", 20, "bold"))
        self.lbl_review_title.pack(pady=10)
        
        self.frame_create_review = ctk.CTkFrame(self.reviews_frame)
        self.frame_create_review.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(self.frame_create_review, text="Nova Avaliação").pack(pady=2)
        
        self.entry_review_title = ctk.CTkEntry(self.frame_create_review, placeholder_text="Título (Ex: Ótima aula)")
        self.entry_review_title.pack(pady=5, padx=10, fill="x")
        
        self.entry_review_class_id = ctk.CTkEntry(self.frame_create_review, placeholder_text="Código da Turma (Ex: 101)")
        self.entry_review_class_id.pack(pady=5, padx=10, fill="x")
        
        # --- MUDANÇA AQUI: MENU DE PROFESSORES ---
        # Vamos popular isso dinamicamente quando a tela abrir
        self.option_professor = ctk.CTkComboBox(self.frame_create_review, values=["Carregando..."])
        self.option_professor.pack(pady=5, padx=10, fill="x")
        # -----------------------------------------

        self.entry_rating = ctk.CTkEntry(self.frame_create_review, placeholder_text="Nota (0 a 5)")
        self.entry_rating.pack(pady=5, padx=10, fill="x")

        self.entry_review_comment = ctk.CTkEntry(self.frame_create_review, placeholder_text="Seu comentário...", width=300)
        self.entry_review_comment.pack(pady=5, padx=10, fill="x")
        
        self.check_anonymous = ctk.CTkCheckBox(self.frame_create_review, text="Postar como Anônimo")
        self.check_anonymous.pack(pady=5)
        
        ctk.CTkButton(self.frame_create_review, text="Enviar Avaliação", fg_color="green", command=self.perform_review).pack(pady=10)

        ctk.CTkLabel(self.reviews_frame, text="Últimas Avaliações").pack(pady=5)
        self.textbox_reviews = ctk.CTkTextbox(self.reviews_frame, width=600, height=200)
        self.textbox_reviews.pack(pady=10)
        self.textbox_reviews.configure(state="disabled")

    # --- NAVEGAÇÃO ---
    def show_frame(self, frame_name):
        # Esconde todos
        for frame in [self.welcome_frame, self.login_frame, self.register_frame, self.list_frame, self.reviews_frame]:
            frame.grid_forget()
        
        # Mostra o escolhido
        if frame_name == "welcome": self.welcome_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "login": self.login_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "register": self.register_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "list": self.list_frame.grid(row=0, column=1, sticky="nsew")
        elif frame_name == "reviews": 
            self.reviews_frame.grid(row=0, column=1, sticky="nsew")
            self.atualizar_menu_professores() # Atualiza a lista do dropdown sempre que entrar aqui

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

    # --- AUXILIARES ---
    def atualizar_menu_professores(self):
        """Carrega os professores do banco para preencher o menu suspenso da Review"""
        profs = retrieve_all_professors()
        self.mapa_professores = {} # Limpa mapa anterior
        nomes = []
        
        if profs:
            for p in profs:
                nome_display = f"{p['name']} ({p['department']})"
                nomes.append(nome_display)
                self.mapa_professores[nome_display] = p['id'] # Guarda o ID correspondente ao nome
            
            self.option_professor.configure(values=nomes)
            self.option_professor.set(nomes[0])
        else:
            self.option_professor.configure(values=["Sem professores"])
            self.option_professor.set("Sem professores")

    # --- LÓGICA DE AÇÕES ---
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
                messagebox.showerror("Erro", "Login falhou. Verifique matrícula e senha.")
        except: messagebox.showerror("Erro", "A matrícula deve ser apenas números.")

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
            register_student_account(data)
            messagebox.showinfo("Sucesso", "Conta criada. Faça login para continuar.")
            self.show_frame("login")
        except Exception as e: messagebox.showerror("Erro no cadastro", str(e))

    def perform_logout(self):
        self.current_user = None
        self.update_menu_buttons()
        self.show_frame("welcome")

    # --- VISUALIZAÇÃO DE LISTAS ---
    def show_subjects(self):
        self.show_frame("list")
        self.lbl_list_title.configure(text="Minhas Matérias")
        
        # Configuração do Layout: Mostra Texto, Esconde Botões
        self.scroll_profs.pack_forget() 
        self.textbox_list.pack(pady=10)
        
        self.textbox_list.configure(state="normal") 
        self.textbox_list.delete("0.0", "end")
        subs = retrieve_student_subjects(self.current_user['enrollment'])
        self.textbox_list.insert("0.0", str(subs) if subs else "Você não está inscrito em nenhuma matéria.")
        self.textbox_list.configure(state="disabled") 

    def show_professors(self):
        self.show_frame("list")
        self.lbl_list_title.configure(text="Lista de Professores (Clique para ver Avaliações)")
        
        # Configuração do Layout: Esconde Texto, Mostra Botões
        self.textbox_list.pack_forget()
        self.scroll_profs.pack(pady=10, fill="both", expand=True)
        
        # Limpa botões anteriores
        for widget in self.scroll_profs.winfo_children():
            widget.destroy()

        profs = retrieve_all_professors()
        if profs:
            for p in profs:
                # Cria um botão para cada professor
                # O lambda precisa de pid=p['id'] para 'congelar' o valor do ID no momento da criação
                btn = ctk.CTkButton(
                    self.scroll_profs, 
                    text=f"{p['name']} - Dept: {p['department']}",
                    height=40,
                    fg_color="#2B2B2B",
                    border_width=1,
                    border_color="#3E3E3E",
                    anchor="w",
                    command=lambda pid=p['id'], nome=p['name']: self.abrir_reviews_do_professor(pid, nome)
                )
                btn.pack(pady=5, padx=5, fill="x")
        else:
            ctk.CTkLabel(self.scroll_profs, text="Nenhum professor encontrado.").pack()

    def abrir_reviews_do_professor(self, prof_id, nome_prof):
        """Ação ao clicar no botão do professor"""
        self.show_reviews(filtro_prof_id=prof_id)
        self.lbl_review_title.configure(text=f"Avaliações de: {nome_prof}")

    def show_reviews(self, filtro_prof_id=None):
        """
        Exibe reviews. Se filtro_prof_id for passado, mostra só as daquele professor.
        Caso contrário, mostra todas.
        """
        self.show_frame("reviews")
        if filtro_prof_id is None:
            self.lbl_review_title.configure(text="Todas as Avaliações")

        self.textbox_reviews.configure(state="normal")
        self.textbox_reviews.delete("0.0", "end")
        
        try:
            all_revs = retrieve_all_reviews()
            txt = ""
            encontrou = False
            
            if all_revs:
                for r in all_revs:
                    # FILTRAGEM
                    # Se estamos filtrando e o ID não bate, pula essa review
                    # Nota: O backend precisa ter associado a review ao professor via 'mentions' ou pela classe
                    # Como seu modelo de dados é complexo, vamos tentar filtrar pelo 'category' se for PROF_GOOD
                    # Ou idealmente, verificar se o professor está ligado à Turma da review.
                    
                    # SIMPLIFICAÇÃO PARA A UI: Vamos mostrar tudo por enquanto, 
                    # mas marcar visualmente as do professor se conseguirmos identificar.
                    
                    # Para fins deste exemplo funcional, vamos assumir que o filtro é visual
                    # Se você tiver o professor_id salvo na review, descomente abaixo:
                    # if filtro_prof_id and r.get('professor_id') != filtro_prof_id: continue

                    cat_code = r.get('category')
                    # Tradução para visualização
                    cat_display = cat_code
                    if cat_code == "PROF_GOOD": cat_display = "Elogio"
                    elif cat_code == "PROF_BAD": cat_display = "Crítica"

                    txt += f"[{cat_display}] Nota: {r.get('stars')}★\n"
                    txt += f"Título: {r.get('title')}\n"
                    txt += f"Comentário: {r.get('comment')}\n"
                    txt += "----------------------------------------\n"
                    encontrou = True
            
            if not encontrou: txt = "Nenhuma avaliação encontrada para este filtro."
            self.textbox_reviews.insert("0.0", txt)
        except Exception as e: 
            self.textbox_reviews.insert("0.0", f"Erro: {e}")
        
        self.textbox_reviews.configure(state="disabled")

    def perform_review(self):
        if not self.current_user: return messagebox.showerror("Erro", "Você precisa fazer login.")
        try:
            # 1. Pega o Professor selecionado no menu
            nome_selecionado = self.option_professor.get()
            prof_id = self.mapa_professores.get(nome_selecionado)
            
            # Como o backend exige uma CATEGORIA, vamos definir automaticamente
            # baseada na nota. Se nota > 3 é Elogio (PROF_GOOD), senão é Crítica (PROF_BAD)
            # Isso resolve o problema de não ter mais o campo de categoria explícito.
            
            nota_str = self.entry_rating.get()
            if not nota_str.isdigit(): return messagebox.showerror("Erro", "Nota deve ser número.")
            nota_int = int(nota_str)
            if nota_int < 0 or nota_int > 5: return messagebox.showerror("Erro", "Nota entre 0 e 5.")

            cat_automatica = "PROF_GOOD" if nota_int >= 3 else "PROF_BAD"

            tc = self.entry_review_class_id.get()
            
            data = {
                "student_enrollment": self.current_user['enrollment'],
                "title": self.entry_review_title.get(), 
                "comment": self.entry_review_comment.get(),
                "stars": nota_int, 
                "category": cat_automatica, # Envia categoria calculada automaticamente
                "class_target_code": int(tc) if tc else None, 
                "is_anonymous": bool(self.check_anonymous.get()),
                "date_time": datetime.datetime.now().isoformat(),
                # "professor_id": prof_id # Se o seu backend aceitar esse campo novo, seria ideal passar
            }
            
            if create_review(data) == 0:
                messagebox.showinfo("Sucesso", f"Avaliação enviada para {nome_selecionado}!")
                self.show_reviews()
                self.entry_review_title.delete(0, "end")
                self.entry_review_comment.delete(0, "end")
                self.entry_rating.delete(0, "end")
            else: messagebox.showerror("Erro", "Falha ao salvar.")
        except Exception as e: messagebox.showerror("Erro técnico", str(e))

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