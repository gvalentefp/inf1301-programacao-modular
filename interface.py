"""
Simple Command Line Interface (CLI) Frontend.
Objective: Provides basic user interaction (Menu, Login, Register) to validate the backend logic.
Corresponds to the 'INTERFACE FRONTEND' module.
"""
from src.modules.credentialing import register_student_account, authenticate_user
from src.modules.student import retrieve_student_subjects
from src.modules.professor import retrieve_all_professors
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
        print("4. View All Professors")
        print("5. Logout")
    
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
        else:
            # Error code (1) received
            pass 
            
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
        print(subjects_codes) # Exibe apenas os códigos por simplicidade

def handle_view_professors():
    """Displays a list of all professors registered in the system."""
    if not CURRENT_USER: return
    
    professors = retrieve_all_professors()
    print("\n--- All Professors ---")
    if not professors:
        print("No professors registered in the system.")
    else:
        for prof in professors:
            # Use o cálculo de média do professor para demonstração
            # A chamada direta será feita no módulo professor (calcula_review_average_professor)
            print(f"ID {prof['id']} | Name: {prof['name']} | Dept: {prof['department']}")

def run_frontend():
    """The main loop for the CLI interface."""
    global CURRENT_USER
    
    while True:
        choice = display_menu()
        
        if choice == '0':
            break
        
        if choice == '1':
            handle_registration()
        elif choice == '2':
            handle_login()
        elif choice == '3' and CURRENT_USER:
            handle_view_subjects()
        elif choice == '4' and CURRENT_USER:
            handle_view_professors()
        elif choice == '5' and CURRENT_USER:
            CURRENT_USER = None
            print("Logged out successfully.")
        else:
            print("Invalid option or action requires login.")

if __name__ == '__main__':
    # Running frontend directly for testing purposes.
    # In a full system, this would be called by main.py
    run_frontend()