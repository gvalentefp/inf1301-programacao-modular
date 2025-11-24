"""
Simple Command Line Interface (CLI) Frontend.
Objective: Provides basic user interaction (Menu, Login, Register, Reviews) to validate the backend logic.
Corresponds to the 'INTERFACE FRONTEND' module.
"""
import datetime
from src.modules.credentialing import register_student_account, authenticate_user
from src.modules.student import retrieve_student_subjects
from src.modules.professor import retrieve_all_professors
from src.modules.review import create_review, retrieve_all_reviews, REVIEW_CATEGORIES
from src.persistence import database, save_db 
from src.shared import RETURN_CODES

# Variável de estado para manter o usuário logado
CURRENT_USER = None 

def display_menu():
    """
    Objective: Render the main navigation menu.
    Description: Displays options based on the user's authentication state (Logged in vs Guest).
    Coupling:
        :return str: The option selected by the user via input().
    Coupling Conditions:
        Input Assertions: User enters a string.
        Output Assertions: Returns the raw string from input.
    User Interface: Prints the menu options to stdout.
    """
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
    """
    Objective: Orchestrate the student registration workflow.
    Description: Captures user input, constructs the student data dictionary, calls the credentialing module, and persists the database.
    Coupling:
        :return: None.
    Coupling Conditions:
        Input Assertions: User provides valid enrollment (int) and strings for other fields.
        Output Assertions: If successful, new student is saved to DB.
    User Interface: Prompts for account details. Prints success or error messages.
    """
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
        resultado = register_student_account(data)
        if resultado == RETURN_CODES['SUCCESS']:
            print(">> User registered succesfully!")
        else:
            print(">> Error registering new user!")
    except ValueError:
        print("Input Error: Enrollment must be a number.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def handle_login():
    """
    Objective: Authenticate the user and manage the session state.
    Description: Takes credentials, verifies them via the backend, and updates the global CURRENT_USER variable.
    Coupling:
        :return: None.
    Coupling Conditions:
        Input Assertions: Enrollment must be an integer.
        Output Assertions: Updates CURRENT_USER if credentials are valid.
    User Interface: Prompts for login. Prints login status.
    """
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
            print(">> Logged in successfully!")
        else:
            print(">> Error: Invalid credentials.")
            
    except ValueError:
        print("Input Error: Enrollment must be a number.")

def handle_view_subjects():
    """
    Objective: Display the academic history of the logged-in student.
    Description: Calls the student module to retrieve the list of subject codes associated with the current user.
    Coupling:
        :return: None.
    Coupling Conditions:
        Input Assertions: CURRENT_USER must be set.
        Output Assertions: Displays a list of integers (subject codes).
    User Interface: Prints the list of subjects.
    """
    """Displays the list of subjects the logged-in student has taken."""
    if not CURRENT_USER: return
    
    subjects_codes = retrieve_student_subjects(CURRENT_USER['enrollment'])
    
    print("\n--- My Subject Codes ---")
    if subjects_codes is None or not subjects_codes:
        print("You have not registered any subjects yet.")
    else:
        print(subjects_codes)

def handle_view_professors():
    """
    Objective: generate a feed of professors and their respective reviews.
    Description: Aggregates data from Professors, Classes, Students, and Reviews modules to display a formatted report. Handles name resolution and date formatting.
    Coupling:
        :return: None.
    Coupling Conditions:
        Input Assertions: CURRENT_USER must be set. Relies on data existing in global 'database'.
        Output Assertions: Prints structured text to stdout.
    User Interface: Detailed list of professors and reviews (with stars, author, date).
    """
    if not CURRENT_USER: return
    
    professors = retrieve_all_professors()
    all_reviews = retrieve_all_reviews()
    all_classes = database.get('classes', [])
    
    # Carrega alunos para buscar os nomes
    all_students = database.get('students', [])

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
                        
                        # --- Lógica de Autor ---
                        if r.get('is_anonymous'):
                            autor_display = "Anonymous"
                        else:
                            # Procura o aluno na lista para pegar o nome
                            nome_aluno = "Desconhecido"
                            for s in all_students:
                                if s['enrollment'] == r.get('student_enrollment'):
                                    nome_aluno = s['name']
                                    break
                            autor_display = f"{nome_aluno} ({r.get('student_enrollment')})"

                        # --- Lógica de Data (NOVO) ---
                        raw_date = r.get('date_time', '')
                        # Limpa a formatação ISO (tira o T e segundos) para ficar bonito: YYYY-MM-DD HH:MM
                        date_display = raw_date.replace('T', ' ')[:16] if raw_date else "Data N/A"

                        # Nota visual (estrelas)
                        nota = float(r.get('stars', 0))
                        estrelas = "*" * int(nota)
                        
                        print(f"   -> Rating: {nota} {estrelas}")
                        print(f"      Author: {autor_display}")  
                        print(f"      Category: {r.get('category')}")
                        print(f"      Commentary: {r.get('comment')}")
                        print(f"      (Class Ref.: {r.get('class_target_code')})")
                        print("      ---")
            
            if not reviews_encontradas:
                print("   (No reviews available)")

def handle_create_review():
    """
    Objective: Collect data to publish a new review.
    Description: Prompts for rating, comment, and anonymity. Automatically assigns the current timestamp and student ID. Validates input and persists data.
    Coupling:
        :return: None.
    Coupling Conditions:
        Input Assertions: CURRENT_USER must be set. 'stars' must be 0-5. 'class_target_code' must exist.
        Output Assertions: If backend returns success, data is saved to DB.
    User Interface: Interactive prompts and validation messages.
    """
    if not CURRENT_USER: return
    print("\n--- Create New Review ---")
    
    # Mostra turmas para facilitar
    classes = database.get('classes', [])
    codes = [c['code'] for c in classes]
    print(f"Classes available to review: {codes}")

    try:
        turma_code = int(input("Class Code (Ex: 101): "))
        titulo = input("Title: ")
        comentario = input("Comments: ")
        
        # Tratamento da Nota (Aceita 4.5 mas envia 4 para o backend antigo)
        nota_input = input("Rating (0 to 5 stars): ").replace(",", ".")
        nota_int = int(float(nota_input)) 
        nota_decimal = int(10*(float(nota_input) - nota_int))
        nota_final = nota_int + nota_decimal

        category = input("Category (ex: 'PROF_GOOD'): ")

        anonimo_input = input("Anônimo? (s/n): ").strip().lower()
        is_anon = (anonimo_input == 's')

        review_data = {
            "student_enrollment": CURRENT_USER['enrollment'],
            "title": titulo,
            "comment": comentario,
            "stars": nota_final,
            "category": category,
            "class_target_code": turma_code,
            "is_anonymous": is_anon,
            "date_time": datetime.datetime.now().isoformat() # Já salva a data aqui
        }

        resultado = create_review(review_data)
        
        if resultado == 0:
            save_db()
            print("\n>> Sucesso! Avaliação registrada e salva.")
        else:
            print("\n>> Error: Review got rejected. (Verify if class exists)")

    except ValueError:
        print("Error: Type valid numerical values.")
    except Exception as e:
        print(f"Error: {e}")

def run_frontend():
    """
    Objective: Main execution loop for the CLI.
    Description: Initializes the application loop, routing user input to specific handler functions until exit is requested.
    Coupling:
        :return: None.
    Coupling Conditions:
        Input Assertions: None.
        Output Assertions: Application runs until '0' is selected.
    User Interface: Continuous menu loop.
    """
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