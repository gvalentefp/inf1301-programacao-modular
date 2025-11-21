"""
Module containing CRUD and association functions for the Student entity.
The student entity is a dictionary based on the typedef struct Aluno.
"""
from typing import List, Dict, Union
from src.persistence import database
from src.shared import RETURN_CODES, CONSTANTS
from src.domains.course import validate_course
from src.persistence import find_entity_by_pk

__all__ = [
    'create_student', 'retrieve_student', 'retrieve_all_students', 
    'update_student_course', 'update_student', 'delete_student', 
    'validate_student', 
    'create_student_subject', 'student_took_subject', 'retrieve_student_subjects',
    'update_student_subjects', 'delete_student_subject',
    'create_student_review', 'retrieve_student_reviews', 'retrieve_student_review',
    'update_student_review', 'delete_student_review', 
]

# --- Repository Functions (Internal) ---

def repo_retrieve_student(enrollment: int) -> Union[Dict, None]:
    """
    Objective: Find a student dictionary in memory by their enrollment (primary key).
    Description: Corresponds to repo_busca_aluno(int matricula).
    Coupling:
        :param enrollment (int): The student's primary key (matricula).
        :return Union[Dict, None]: The student dictionary or None if not found.
    Coupling Conditions:
        Input Assertions: enrollment must be a positive integer.
        Output Assertions: If a student is returned, student['enrollment'] == enrollment.
    User Interface: (None)
    """
    if not isinstance(enrollment, int) or enrollment <= 0:
        return None
        
    for student in database['students']:
        if student.get('enrollment') == enrollment:
            return student
    return None

def repo_create_student(data: Dict) -> int:
    """
    Objective: Add a new student dictionary to the database list.
    Description: Corresponds to repo_cria_aluno(Aluno* dados)
    Coupling:
        :param data (Dict): The student dictionary containing all required fields.
        :return int: SUCCESS (0) or ERROR (1)
    Coupling Conditions:
        Input Assertions: data must be a validated dictionary.
        Output Assertions: The size of database['students'] increases by 1 upon SUCCESS.
    User Interface: (None)
    """
    try:
        database['students'].append(data)
        return RETURN_CODES['SUCCESS']
    except Exception:
        return RETURN_CODES['ERROR']
    
def repo_retrieve_subject(code: int) -> Union[Dict, None]:
    """
    Objective: Find a subject dictionary in memory by its code (primary key).
    Description: Calls the generic persistence search.
    Coupling:
        :param code (int): The subject's code.
        :return Union[Dict, None]: The subject dictionary or None.
    Coupling Conditions:
        Input Assertions: code must be a positive integer.
        Output Assertions: If returned, subject['code'] == code.
    User Interface: (None)
    """
    
    if not isinstance(code, int) or code <= 0:
        return None
    return find_entity_by_pk('subjects', code, 'code') # Usando a função genérica

def repo_retrieve_review(review_id: int) -> Union[Dict, None]:
    """
    Objective: Find a review dictionary in memory by its ID (primary key).
    Description: Calls the generic persistence search.
    Coupling:
        :param review_id (int): The review's ID.
        :return Union[Dict, None]: The review dictionary or None.
    Coupling Conditions:
        Input Assertions: review_id must be a positive integer.
        Output Assertions: If returned, review['id_aval'] == review_id.
    User Interface: (None)
    """

    if not isinstance(review_id, int) or review_id <= 0:
        return None
    return find_entity_by_pk('reviews', review_id, 'id_aval') # Usando a função genérica

# --- Public Access Functions ---

def validate_student(data: Dict) -> int:
    """
    Objective: Validate mandatory fields for creating or updating a student record.
    Description: Checks required data fields and domain constraints (e.g., Course validity)
    Coupling:
        :param data (Dict): The student dictionary to be validated.
        :return int: SUCCESS (0) or ERROR (1)
    Coupling Conditions:
        Input Assertions: data must be a dictionary.
        Output Assertions: If SUCCESS, all required fields (enrollment, username, name, email, course, password) are present and valid.
    User Interface: (None)
    """
    if not isinstance(data, dict):
        return RETURN_CODES['ERROR'] 

    # Check mandatory fields (T3: Dados incompletos ou campos obrigatórios nulos) 
    required_fields = ['enrollment', 'username', 'password', 'name', 'institutional_email', 'course']
    if not all(field in data for field in required_fields):
        return RETURN_CODES['ERROR']
    
    enrollment = data.get('enrollment')
    username = data.get('username', '').strip()
    name = data.get('name', '').strip()
    course = data.get('course', '').strip()

    # T2/T3: enrollment format check 
    if not isinstance(enrollment, int) or enrollment <= 0:
        return RETURN_CODES['ERROR'] 

    # Max length and not empty check
    if not username or len(username) > CONSTANTS['MAX_USERNAME_LENGTH']:
        return RETURN_CODES['ERROR']
        
    if not name or len(name) > CONSTANTS['MAX_LENGTH_NAME']:
        return RETURN_CODES['ERROR']
        
    # Domain check for course
    if not validate_course(course):
        return RETURN_CODES['ERROR']

    return RETURN_CODES['SUCCESS']

def create_student(data: Dict) -> int:
    """
    Objective: Register a new student account in the platform.
    Description: Requires proving link to PUC-Rio (enrollment/email). Ensures PK integrity (matricula). 
    Coupling:
        :param data (Dict): Student data including enrollment (pk), username (pk), and required fields
        :return int: SUCCESS (1) or ERROR (0)
    Coupling Conditions:
        Input Assertions: validate_student(data) == SUCCESS.
        Output Assertions: A new student record exists in the database.
    User Interface: Log "Creating student with enrollment {enrollment}" (Internal Log).
    """
    # T4/T3 - Data validation and completeness 
    if validate_student(data) != RETURN_CODES['SUCCESS']:
        print("Log: Failed to create student. Invalid or incomplete data.")
        return RETURN_CODES['ERROR']
        
    # PK Check (T2: Cannot use same enrollment for two accounts) 
    if repo_retrieve_student(data['enrollment']) is not None:
        print(f"Log: Failed to create student. Enrollment {data['enrollment']} already exists.")
        return RETURN_CODES['ERROR']
        
    # T1 - Success 
    return repo_create_student({
        'enrollment': data['enrollment'], # int matricula (pk) 
        'username': data['username'], # char nome_de_usuario[MAX_USERNAME_LENGTH] (pk) 
        'password': data['password'], # char senha [MAX_PASSWORD_LENGTH] 
        'name': data['name'], # char nome[MAX_NAME_LENGTH] 
        'institutional_email': data['institutional_email'], # char email_institucional [MAX_NAME_LENGTH] 
        'course': data['course'], # Curso curso 
        'subjects': [], # Materia* materias [MAX_MATERIAS] 
        'reviews': [], # Avaliacao* avaliacoes[MAX_AVALS] 
        'profile_private': True # Default setting (not specified, but safer default)
    })

def retrieve_student(enrollment: int) -> Union[Dict, None]:
    """
    Objective: Find a student record using their unique enrollment number.
    Description: Corresponds to busca_aluno
    Coupling:
        :param enrollment (int): The student's enrollment ID.
        :return Union[Dict, None]: The student dictionary or None
    Coupling Conditions:
        Input Assertions: enrollment must be a valid positive integer.
        Output Assertions: If returned, the student exists in the database.
    User Interface: Log "Attempting to retrieve student with enrollment {enrollment}" (Internal Log).
    """
    # T3/T4 - Parameter validation 
    if not isinstance(enrollment, int) or enrollment <= 0:
        print(f"User Message: Error. Enrollment {enrollment} passed in wrong format.")
        return None
        
    # T1/T2 - Search and return 
    student = repo_retrieve_student(enrollment)
    if student is None:
        print(f"User Message: Student with enrollment {enrollment} not registered.")
    return student

def retrieve_all_students() -> List[Dict]:
    """
    Objective: Retrieve the entire list of registered students.
    Description: Corresponds to busca_todos_alunos
    Coupling:
        :return List[Dict]: A list containing all student dictionaries
    Coupling Conditions:
        Input Assertions: (None, void function)
        Output Assertions: Returns a list (possibly empty) containing valid student records.
    User Interface: (None)
    """
    # T1/T3 - Always returns the stored list 
    return database['students'] # T2 - Returns empty list if no students are found 

def update_student_course(enrollment: int, new_course: str) -> int:
    """
    Objective: Update the course associated with a specific student.
    Description: Corresponds to troca_curso_aluno
    Coupling:
        :param enrollment (int): The student's enrollment ID.
        :param new_course (str): The new course acronym.
        :return int: SUCCESS (1) or ERROR (0)
    Coupling Conditions:
        Input Assertions: enrollment is valid. new_course is valid (validate_course == True).
        Output Assertions: If SUCCESS, student['course'] == new_course.
    User Interface: Log "Updating course for enrollment {enrollment} to {new_course}" (Internal Log).
    """
    # T2 - Enrollment format check 
    student = repo_retrieve_student(enrollment)
    if student is None:
        print(f"User Message: Enrollment {enrollment} not found.")
        return RETURN_CODES['ERROR']
        
    # T3 - Course format check 
    if not validate_course(new_course):
        print(f"User Message: Course {new_course} passed in wrong format or is invalid.")
        return RETURN_CODES['ERROR']
        
    # T4 - Type check (implicity handled by parameter typing)

    # T1 - Success 
    student['course'] = new_course
    return RETURN_CODES['SUCCESS']

def update_student(enrollment: int, new_data: Dict) -> int:
    """
    Objective: Update one or more fields of an existing student record.
    Description: Corresponds to atualiza_aluno
    Coupling:
        :param enrollment (int): The student's enrollment ID.
        :param new_data (Dict): Dictionary containing the fields to update.
        :return int: SUCCESS (1) or ERROR (0)
    Coupling Conditions:
        Input Assertions: enrollment is valid. new_data contains only valid fields and values.
        Output Assertions: If SUCCESS, the student record in memory reflects the changes in new_data.
    User Interface: Log "Updating student data for enrollment {enrollment}" (Internal Log).
    """
    student = repo_retrieve_student(enrollment)
    
    # T2/T3 - Enrollment check 
    if student is None:
        print(f"User Message: Failed to update. Enrollment {enrollment} not found or passed in wrong format.")
        return RETURN_CODES['ERROR']
        
    # T4 - New data validation 
    temp_data = student.copy()
    temp_data.update(new_data)
    
    if validate_student(temp_data) != RETURN_CODES['SUCCESS']:
        print("User Message: Failed to update. New data is incomplete or invalid.")
        return RETURN_CODES['ERROR']

    # T1 - Success 
    for key, value in new_data.items():
        if key not in ['enrollment']: # Enrollment (PK) cannot be changed via update
            student[key] = value
            
    return RETURN_CODES['SUCCESS']
    
def delete_student(enrollment: int) -> int:
    """
    Objective: Permanently remove a student record from the database and clean up all associated data (cascading delete).
    Description: Corresponds to deleta_aluno
    Coupling:
        :param enrollment (int): The student's enrollment ID.
        :return int: SUCCESS (1) or ERROR (0)
    Coupling Conditions:
        Input Assertions: enrollment is a valid positive integer.
        Output Assertions: If SUCCESS, the student record is removed from database['students'].
    User Interface: Log "Deleting student with enrollment {enrollment}" (Internal Log).
    """

    from src.modules.classes import delete_student_reference_from_all_classes 
    from src.modules.review import delete_review

    student = repo_retrieve_student(enrollment)
    
    # T2/T3 - Enrollment check 
    if student is None:
        print(f"User Message: Failed to delete. Enrollment {enrollment} not found or passed in wrong format.")
        return RETURN_CODES['ERROR']
        
    # T1 - Success 

    # 1. Deleção em Cascata de Reviews
    review_ids_to_delete = list(student.get('reviews', [])) # Usa list() para evitar modificação durante iteração
    for review_id in review_ids_to_delete:
        # NOTE: A função delete_review deve ser implementada para LIMPAR as referências 
        # nos Professores e Turmas afetadas.
        delete_review(review_id) 
        
    # 2. Deleção da Referência em Turmas
    delete_student_reference_from_all_classes(enrollment)

    # 3. Deleção do Registro Principal (Aluno)
    try:
        database['students'].remove(student)
        return RETURN_CODES['SUCCESS']
    except ValueError:
        return RETURN_CODES['ERROR']

# --- Subject Association Functions (Materias) ---

# Note: The original specification implies Subject objects are stored on the Student.
# Since we only use dicts, the 'subjects' list on the student dict will store 
# the Subject's Code (Materia* materias [MAX_MATERIAS] 

def create_student_subject(enrollment: int, subject_code: int) -> int:
    """
    Objective: Associate a subject to a student's history of taken subjects.
    Description: Corresponds to cria_materia_aluno. This is just the reference; the full subject/class details are handled in the Turma/Class module (Step 4).
    Coupling:
        :param enrollment (int): Student's enrollment ID.
        :param subject_code (int): Subject's code.
        :return int: SUCCESS (1) or ERROR (0).
    Coupling Conditions:
        Input Assertions: enrollment is valid. subject_code is valid. Both student and subject must exist (checked in T4).
        Output Assertions: If SUCCESS, subject_code is added to student['subjects'].
    User Interface: Log "Adding subject {subject_code} to student {enrollment}" (Internal Log).
    """
    student = repo_retrieve_student(enrollment)
    
    # T2/T4 - Student check 
    if student is None:
        print(f"User Message: Failed to add subject. Student {enrollment} not found.")
        return RETURN_CODES['ERROR']
        
    # T3/T4 - Subject existence check is required
    if repo_retrieve_subject(subject_code) is None: 
         print(f"User Message: Failed to add subject. Subject {subject_code} not found.")
         return RETURN_CODES['ERROR']
        
    # Check if student already has the subject (to prevent duplicates)
    if subject_code in student['subjects']:
        print(f"User Message: Student {enrollment} already has subject {subject_code}.")
        return RETURN_CODES['ERROR']

    # T1 - Success 
    student['subjects'].append(subject_code)
    return RETURN_CODES['SUCCESS']

def student_took_subject(enrollment: int, subject_code: int) -> int:
    """
    Objective: Check if a student has registered a specific subject in their history.
    Description: Corresponds to aluno_fez_materia.
    Coupling:
        :param enrollment (int): Student's enrollment ID.
        :param subject_code (int): Subject's code.
        :return int: SUCCESS (1) (if true) or ERROR (0) (if false or error).
    Coupling Conditions:
        Input Assertions: enrollment and subject_code are valid positive integers.
        Output Assertions: If SUCCESS, subject_code is present in student['subjects'].
    User Interface: (Internal Log).
    """
    student = repo_retrieve_student(enrollment)
    
    if student is None or subject_code <= 0:
        return RETURN_CODES['ERROR'] # T3/T4: Invalid inputs/non-existent entities
        
    if subject_code in student['subjects']:
        return RETURN_CODES['SUCCESS'] # T1: Aluno completou a matéria
    else:
        return RETURN_CODES['ERROR'] # T2: Aluno não fez a matéria

def retrieve_student_subjects(enrollment: int) -> Union[List[int], None]:
    """
    Objective: Retrieve the list of subject codes associated with a student.
    Description: Corresponds to busca_materias_aluno.
    Coupling:
        :param enrollment (int): Student's enrollment ID.
        :return Union[List[int], None]: List of subject codes or None (ERRO).
    Coupling Conditions:
        Input Assertions: enrollment is a valid positive integer.
        Output Assertions: Returns a list of codes (possibly empty).
    User Interface: (Internal Log).
    """
    student = repo_retrieve_student(enrollment)
    
    if student is None:
        return None # T2/T3: Matrícula Inválida ou Mal Formatada/Aluno não encontrado
        
    return student['subjects'] # T1/T4: Retorna Matérias (codes) ou lista vazia

def update_student_subjects(old_code: int, new_code: int) -> int:
    """
    Objective: Globally update an old subject code reference to a new one in all student records.
    Description: Corresponds to atualiza_materia_alunos. Used when a subject code is changed by the admin.
    Coupling:
        :param old_code (int): The subject code to be replaced.
        :param new_code (int): The new subject code.
        :return int: SUCCESS (1) or ERROR (0).
    Coupling Conditions:
        Input Assertions: old_code and new_code are valid positive integers.
        Output Assertions: If SUCCESS, all instances of old_code in student['subjects'] lists are replaced by new_code.
    User Interface: (Internal Log).
    """
    # T3/T4 - Input validation (assuming subject existence check is done externally)
    if not isinstance(old_code, int) or old_code <= 0 or not isinstance(new_code, int) or new_code <= 0:
        return RETURN_CODES['ERROR']
        
    updated_count = 0
    for student in database['students']:
        if old_code in student['subjects']:
            try:
                # Remove old code and add new code
                student['subjects'].remove(old_code)
                student['subjects'].append(new_code)
                updated_count += 1
            except Exception:
                # T4: Falha de alocação no vetor ou memória (simulated)
                return RETURN_CODES['ERROR']
                
    if updated_count == 0: 
        # T2: Código antigo não encontrado (verificação mais robusta: garante que o código não foi encontrado *em nenhuma* lista)
        # Se for 0, e a lista de alunos não for vazia, significa que o código velho não estava em uso.
        if old_code not in [sub for student in database['students'] for sub in student['subjects']]:
            return RETURN_CODES['ERROR']

    return RETURN_CODES['SUCCESS'] # T1: Atualiza corretamente todas as matérias

def delete_student_subject(enrollment: int, subject_code: int) -> int:
    """
    Objective: Remove a specific subject code from a student's history.
    Description: Corresponds to deleta_materia_aluno.
    Coupling:
        :param enrollment (int): Student's enrollment ID.
        :param subject_code (int): Subject's code to remove.
        :return int: SUCCESS (1) or ERROR (0).
    Coupling Conditions:
        Input Assertions: enrollment and subject_code are valid positive integers.
        Output Assertions: If SUCCESS, subject_code is removed from student['subjects'].
    User Interface: (Internal Log).
    """
    student = repo_retrieve_student(enrollment)
    
    if student is None or subject_code <= 0 or subject_code not in student['subjects']:
        return RETURN_CODES['ERROR'] # Invalid student, invalid code, or subject not associated
        
    try:
        student['subjects'].remove(subject_code)
        return RETURN_CODES['SUCCESS']
    except ValueError:
        return RETURN_CODES['ERROR']
    
# --- Review Association Functions (Avaliações) ---

def create_student_review(enrollment: int, review_data: Dict) -> int:
    """
    Objective: Associate a new review created by the student to their record.
    Description: Corresponds to cria_aval_aluno. This adds a reference (e.g., ID) to the student's list of authored reviews. The full review is persisted elsewhere.
    Coupling:
        :param enrollment (int): Student's enrollment ID (author).
        :param review_data (Dict): The full review dictionary (must contain PK 'id_aval').
        :return int: SUCCESS (1) or ERROR (0).
    Coupling Conditions:
        Input Assertions: enrollment is valid. review_data is a validated review object and contains 'id_aval'.
        Output Assertions: If SUCCESS, the review PK is added to student['reviews'].
    User Interface: (Internal Log).
    """
    student = repo_retrieve_student(enrollment)
    review_id = review_data.get('id_aval') 
    
    if student is None or not isinstance(review_id, int) or review_id <= 0:
        return RETURN_CODES['ERROR']
        
    if review_id in student['reviews']:
        return RETURN_CODES['ERROR'] # Review already associated

    # In a full system, you would call the Review module's creation function here.
    student['reviews'].append(review_id)
    return RETURN_CODES['SUCCESS']


def retrieve_student_reviews(enrollment: int) -> Union[List[int], None]:
    """
    Objective: Retrieve the list of PKs for reviews authored by the student.
    Description: Corresponds to busca_avals_aluno.
    Coupling:
        :param enrollment (int): Student's enrollment ID.
        :return Union[List[int], None]: List of review IDs or None.
    Coupling Conditions:
        Input Assertions: enrollment is valid.
        Output Assertions: Returns a list of review IDs (possibly empty).
    User Interface: (Internal Log).
    """
    student = repo_retrieve_student(enrollment)
    if student is None:
        return None
        
    return student['reviews']


def retrieve_student_review(enrollment: int, review_id: int) -> Union[int, None]: 
    """
    Objective: Check if a specific review ID is associated with the student (authored by them).
    Description: Corresponds to busca_aval_aluno. Returns the ID if the student is the author.
    Coupling:
        :param enrollment (int): Student's enrollment ID.
        :param review_id (int): Review's primary key.
        :return Union[int, None]: Review ID if found, or None.
    Coupling Conditions:
        Input Assertions: enrollment and review_id are valid positive integers.
        Output Assertions: Returns review_id if present in student['reviews'].
    User Interface: (Internal Log).
    """
    student = repo_retrieve_student(enrollment)
    
    if student is None or not isinstance(review_id, int) or review_id <= 0:
        return None
        
    if review_id in student['reviews']:
        return review_id
    return None

def update_student_review(enrollment: int, review_id: int, new_review_data: Dict) -> int:
    """
    Objective: Validate the student's authorship of a review before updating the review data.
    Description: Corresponds to atualiza_aval_aluno. Assures that the author is the one attempting the update.
    Coupling:
        :param enrollment (int): Student's enrollment ID.
        :param review_id (int): Review's primary key.
        :param new_review_data (Dict): New data for the review.
        :return int: SUCCESS (1) or ERROR (0).
    Coupling Conditions:
        Input Assertions: Student exists and is the author. new_review_data must be valid.
        Output Assertions: If SUCCESS, implies the Review module can proceed with the update.
    User Interface: (Internal Log).
    """
    if retrieve_student_review(enrollment, review_id) is None:
        return RETURN_CODES['ERROR'] # Student is not the author or review/student does not exist.
        
    # Validation of new_review_data should ideally be done by the Review module here.
    return RETURN_CODES['SUCCESS']

def delete_student_review(enrollment: int, review_id: int) -> int:
    """
    Objective: Remove the review reference (PK) from the student's authored list.
    Description: Corresponds to deleta_aval_aluno. This should be coupled with deletion in the Review module.
    Coupling:
        :param enrollment (int): Student's enrollment ID.
        :param review_id (int): Review's primary key to delete.
        :return int: SUCCESS (1) or ERROR (0).
    Coupling Conditions:
        Input Assertions: Student exists and is the author (review_id in student['reviews']).
        Output Assertions: If SUCCESS, review_id is removed from student['reviews'].
    User Interface: (Internal Log).
    """
    student = repo_retrieve_student(enrollment)
    
    if student is None or review_id <= 0 or review_id not in student['reviews']:
        return RETURN_CODES['ERROR'] 
        
    try:
        student['reviews'].remove(review_id)
        return RETURN_CODES['SUCCESS']
    except ValueError:
        return RETURN_CODES['ERROR']
    
# backend/modules/student.py

def remove_subject_reference_from_all_students(subject_code: int) -> int:
    """
    Objective: Remove a specific subject code from the 'subjects' list of ALL students.
    Description: Maintains data integrity when a Subject is deleted.
    Coupling:
        :param subject_code (int): The code of the subject being deleted.
        :return int: SUCCESS (0).
    """
    if not isinstance(subject_code, int) or subject_code <= 0:
        return RETURN_CODES['ERROR']
        
    for student in database['students']:
        if subject_code in student.get('subjects', []):
            try:
                student['subjects'].remove(subject_code)
            except Exception:
                continue
                
    return RETURN_CODES['SUCCESS']
    
# Other functions (student_took_subject, retrieve_student_subjects, etc.) would be implemented here, 
# following the same detailed documentation format

