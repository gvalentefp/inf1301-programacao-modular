"""
Simple Command Line Interface (CLI) Frontend.
Objective: Provides basic user interaction (Menu, Login, Register, Reviews) to validate the backend logic.
Corresponds to the 'INTERFACE FRONTEND' module.
"""
import datetime
from src.modules.credentialing import register_student_account, authenticate_user
from src.modules.student import retrieve_student_subjects
from src.modules.professor import retrieve_all_professors
from src.modules.review import create_review, retrieve_all_reviews
from src.persistence import database, save_db 
from src.shared import RETURN_CODES

# Variável de estado para manter o usuário logado
CURRENT_USER = None 

def display_menu():
    """Displays the main options menu."""
    if CURRENT_USER:
        print(f"\n--- Logged in as: {CURRENT_USER['username']} (Enrollment: {CURRENT_USER['enrollment']}) ---")
    else:
        print("\n--- Welcome to Filhos da PUC ---")
        print("1. Register New Student Account")
        print("2. Login")
        
    if CURRENT_USER:
        print("3. View My Subjects")
        print("4. View All Professors & Reviews")
        print("5. Create Review")
        print("6. Logout")
    
    print("0. Exit Application")
    return input("Select an option: ")

def handle_registration():
    """Handles the user registration process."""
    print("\n--- New Account Registration ---")
    try:
        data = {
            'enrollment': int(input("Enrollment (Matrícula): ")),
            'username': input("Username: "),
            'password': input("Password: "),
            'name': input("Full Name: "),
            'institutional_email': input("Institutional Email (@puc-rio.br): "),
            'course': input("Course Acronym (e.g., CIEN_COMP): ")
        }
        register_student_account(data)
        save_db()
        print(">> Usuário registrado e salvo com sucesso!")
    except ValueError:
        print("Input Error: Enrollment must be a number.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def handle_login():
    """Handles the user login process."""
    global CURRENT_USER
    if CURRENT_USER:
        print("You are already logged in.")
        return
        
    print("\n--- Login ---")
    try:
        enrollment = int(input("Enrollment (Matrícula): "))
        password = input("Password: ")
        
        user_or_error = authenticate_user(enrollment, password)
        
        if isinstance(user_or_error, dict):
            CURRENT_USER = user_or_error
            print(">> Login realizado com sucesso!")
        else:
            print(">> Erro: Credenciais inválidas.")
            
    except ValueError:
        print("Input Error: Enrollment must be a number.")

def handle_view_subjects():
    """Displays the list of subjects the logged-in student has taken."""
    if not CURRENT_USER: return
    
    subjects_codes = retrieve_student_subjects(CURRENT_USER['enrollment'])
    
    print("\n--- My Subject Codes ---")
    if subjects_codes is None or not subjects_codes:
        print("You have not registered any subjects yet.")
    else:
        print(subjects_codes)

def handle_view_professors():
    """Displays a list of all professors registered in the system."""
    if not CURRENT_USER: return
    
    professors = retrieve_all_professors()
    all_reviews = retrieve_all_reviews()
    all_classes = database.get('classes', [])

    print("\n--- All Professors & Reviews ---")
    if not professors:
        print("No professors registered in the system.")
    else:
        for prof in professors:
            print(f"\n[ID: {prof['id']}] {prof['name']} | Dept: {prof['department']}")
            print("-" * 40)
            
            # Filtra turmas e reviews
            turmas_do_prof = [c['code'] for c in all_classes if prof['id'] in c.get('professors_ids', [])]
            
            reviews_encontradas = False
            if all_reviews:
                for r in all_reviews:
                    if r.get('class_target_code') in turmas_do_prof:
                        reviews_encontradas = True
                        
                        # --- LÓGICA DE EXIBIÇÃO DO AUTOR (CORRIGIDA) ---
                        if r.get('is_anonymous'):
                            autor_display = "Anônimo"
                        else:
                            autor_display = f" {r.get('student_enrollment')}"
                        # -----------------------------------------------

                        # Nota visual (estrelas)
                        nota = int(r.get('stars', 0))
                        estrelas = "*" * nota
                        
                        print(f"   -> Nota: {nota} {estrelas}")
                        print(f"      Autor: {autor_display}")  # Agora mostra quem escreveu!
                        print(f"      Comentário: {r.get('comment')}")
                        print(f"      (Ref. Turma: {r.get('class_target_code')})")
                        print("      ---")
            
            if not reviews_encontradas:
                print("   (Nenhuma avaliação disponível)")

def handle_create_review():
    """Handles creation of a new review."""
    if not CURRENT_USER: return
    print("\n--- Create New Review ---")
    
    # Mostra turmas para facilitar
    classes = database.get('classes', [])
    codes = [c['code'] for c in classes]
    print(f"Turmas disponíveis para avaliar: {codes}")

    try:
        turma_code = int(input("Código da Turma (Ex: 101): "))
        titulo = input("Título: ")
        comentario = input("Comentário: ")
        
        # Tratamento da Nota (Aceita 4.5 mas envia 4 para o backend antigo)
        nota_input = input("Nota (0 a 5): ").replace(",", ".")
        nota_int = int(float(nota_input)) 
        
        anonimo_input = input("Anônimo? (s/n): ").strip().lower()
        is_anon = anonimo_input == 's'

        review_data = {
            "student_enrollment": CURRENT_USER['enrollment'],
            "title": titulo,
            "comment": comentario,
            "stars": nota_int,
            "category": "PROF_GOOD",
            "class_target_code": turma_code,
            "is_anonymous": is_anon,
            "date_time": datetime.datetime.now().isoformat()
        }

        resultado = create_review(review_data)
        
        if resultado == 0:
            save_db()
            print("\n>> Sucesso! Avaliação registrada e salva.")
        else:
            print("\n>> Erro: O backend rejeitou a avaliação. (Verifique se a turma existe)")

    except ValueError:
        print("Erro: Digite valores numéricos válidos.")
    except Exception as e:
        print(f"Erro técnico: {e}")

def run_frontend():
    """The main loop for the CLI interface."""
    global CURRENT_USER
    while True:
        choice = display_menu()
        if choice == '0': break
        elif choice == '1': handle_registration()
        elif choice == '2': handle_login()
        elif choice == '3' and CURRENT_USER: handle_view_subjects()
        elif choice == '4' and CURRENT_USER: handle_view_professors()
        elif choice == '5' and CURRENT_USER: handle_create_review()
        elif choice == '6' and CURRENT_USER:
            CURRENT_USER = None
            print("Logged out successfully.")
        else:
            print("Invalid option.")

if __name__ == '__main__':
    run_frontend()