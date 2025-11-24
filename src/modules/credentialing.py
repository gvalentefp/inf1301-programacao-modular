"""
Module responsible for user authentication and account validation (Credentialing).
It ensures the user (Student) has valid credentials to access the system.
"""
from typing import Dict, Union
from src.shared import RETURN_CODES
from src.modules.student import create_student, retrieve_student, validate_student

from src.persistence import database

# Importação mockada para checagem de vínculo institucional
# from external_api.puc_registrar import check_puc_link 

__all__ = [
    'register_student_account',
    'authenticate_user'
]

# --- Validation and Registration ---

def _validate_institutional_link(enrollment: int, email: str) -> bool:
    """
    Objective: Simulate the validation of the institutional link (enrollment and email).
    Description: Checks if the provided enrollment and institutional email are linked and valid.
                 (For simplicity, this function always returns True, mimicking a successful external API call, 
                 as per the requirement: 'por simplicidade, será exigida a matrícula e o e-mail institucional' [cite: 180]).
    Coupling:
        :param enrollment (int): Student's enrollment ID.
        :param email (str): Student's institutional email.
        :return bool: True if link is proven, False otherwise.
    Coupling Conditions:
        Input Assertions: enrollment is positive, email is a non-empty string.
        Output Assertions: True if the pair (enrollment, email) is recognized as valid.
    User Interface: (Internal Log).
    """
    if not isinstance(enrollment, int) or enrollment <= 0:
        return False
    # Simplified validation: check for expected domain and non-empty email
    if "@puc-rio.br" not in email.lower() or not email:
        return False
        
    # Mocking successful check for simplicity [cite: 180]
    return True

def register_student_account(student_data: Dict) -> int:
    """
    Objective: Create a new student account, enforcing institutional linkage and data integrity.
    Description: Corresponds to the creation process where Matrícula, nome, username, e-mail e curso 
                 must be informed, plus password[cite: 181]. It uses the student module's creation function.
    Coupling:
        :param student_data (Dict): Dictionary containing all required fields for student creation.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: student_data must contain 'enrollment', 'institutional_email', 'name', 'username', 'password', 'course'.
        Output Assertions: If SUCCESS, a new student record is created and persistent.
    User Interface: Log success or error message.
    """
    # 1.    
    if validate_student(student_data) != RETURN_CODES['SUCCESS']:
        print("User Message: Registration failed. Invalid or incomplete data provided.")
        return RETURN_CODES['ERROR']
        
    # 2. Institutional Link Validation [cite: 180]
    if not _validate_institutional_link(student_data['enrollment'], student_data['institutional_email']):
        print("User Message: Registration failed. Enrollment and institutional email do not match PUC-Rio records.")
        return RETURN_CODES['ERROR']

    # --- NOVA VERIFICAÇÃO: USERNAME ÚNICO ---
    # Verifica se o username já existe no banco antes de tentar criar
    students = database.get('students', [])
    for s in students:
        if s['username'] == student_data['username']:
            print(f"User Message: Registration failed. Username '{student_data['username']}' is already taken.")
            return RETURN_CODES['ERROR']
    # ----------------------------------------

    # 3. Attempt to create the student record (handles PK conflict check internally)
    result = create_student(student_data)
    
    if result == RETURN_CODES['SUCCESS']:
        print(f"User Message: Account created successfully for {student_data['username']}.")
        return RETURN_CODES['SUCCESS']
    else:
        print("User Message: Registration failed. Enrollment may already exist.")
        return RETURN_CODES['ERROR']

# --- Authentication ---

def authenticate_user(enrollment: int, password: str) -> Union[Dict, int]:
    """
    Objective: Verify user credentials for login access.
    Description: Corresponds to the requirement: 'O usuário apenas poderá acessar o serviço caso possua uma conta e esteja logado'[cite: 179].
    Coupling:
        :param enrollment (int): Student's enrollment ID.
        :param password (str): The password provided by the user.
        :return Union[Dict, int]: The student dictionary (if successful) or ERROR (1).
    Coupling Conditions:
        Input Assertions: enrollment is valid, password is a string.
        Output Assertions: If a Dict is returned, Dict['enrollment'] == enrollment and password matches.
    User Interface: Log login attempt status.
    """
    # 1. Retrieve student by enrollment
    student = retrieve_student(enrollment)
    
    # 2. Check if student exists
    if student is None:
        print("User Message: Login failed. Invalid enrollment or account not registered.")
        return RETURN_CODES['ERROR']
        
    # 3. Check password (Case-sensitive comparison is assumed)
    if student['password'] == password:
        print(f"User Message: Login successful for {student['username']}.")
        return student # Returns the student dictionary (representing successful login)
    else:
        print("User Message: Login failed. Incorrect password.")
        return RETURN_CODES['ERROR']