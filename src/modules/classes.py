"""
Module containing CRUD and validation functions for the Class (Turma) entity.
The entity is complex, relating Subject, Professor, Student, and Schedule.
"""
from typing import List, Dict, Union
from src.persistence import database
from src.shared import RETURN_CODES, WEEK_DAYS

__all__ = [
    'create_class', 'exists_class', 'retrieve_class', 
    'update_class', 'delete_class', 'validate_class', 
    'retrieve_all_classes'
]

# Variável global para gerar IDs sequenciais para Turmas (int codigo (pk))
next_class_id = 1

def _generate_class_id() -> int:
    """Objective: Generate a new unique ID for Class (Turma)."""
    global next_class_id
    id_atual = next_class_id
    next_class_id += 1
    return id_atual

# --- Repository Functions (Internal) ---

def repo_retrieve_class(code: int) -> Union[Dict, None]:
    """
    Objective: Find a class dictionary in memory by its code (primary key).
    Description: Corresponds to Turma* repo_busca_turma(int codigo).
    Coupling:
        :param code (int): The class's primary key (codigo).
        :return Union[Dict, None]: The class dictionary or None if not found.
    Coupling Conditions:
        Input Assertions: code must be a positive integer.
        Output Assertions: If a class is returned, class['code'] == code.
    User Interface: (None)
    """
    if not isinstance(code, int) or code <= 0:
        return None
        
    for class_record in database['classes']:
        if class_record.get('code') == code:
            return class_record
    return None

def repo_create_class(data: Dict) -> int:
    """
    Objective: Add a new class dictionary to the database list.
    Description: Corresponds to int repo_cria_turma(Turma dados).
    Coupling:
        :param data (Dict): The class dictionary containing all required fields.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: data must be a validated dictionary containing 'code'.
        Output Assertions: The size of database['classes'] increases by 1 upon SUCCESS.
    User Interface: (None)
    """
    try:
        database['classes'].append(data)
        return RETURN_CODES['SUCCESS']
    except Exception:
        return RETURN_CODES['ERROR'] # T2: Falha ao alocar memória ou inserir dados

def repo_delete_class(code: int) -> int:
    """
    Objective: Delete a class from the in-memory database by its code.
    Description: Corresponds to int repo_deleta_turma(int codigo).
    Coupling:
        :param code (int): The class's code.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: code must be a positive integer.
        Output Assertions: If SUCCESS, the class is removed from database['classes'].
    User Interface: (None)
    """
    class_to_delete = repo_retrieve_class(code)
    if class_to_delete:
        try:
            database['classes'].remove(class_to_delete)
            return RETURN_CODES['SUCCESS'] # T1: Encontra a turma e a remove
        except ValueError:
            return RETURN_CODES['ERROR']
    return RETURN_CODES['ERROR'] # T2: Falha ao encontrar a turma


# --- Validation Helpers ---

def _validate_period(period: int) -> bool:
    """
    Objective: Validate the format of the academic period (e.g., 20241, 20252).
    Description: Checks if the period format is YYYYX (X=1 or 2).
    Coupling:
        :param period (int): The academic period.
        :return bool: True if valid, False otherwise.
    Coupling Conditions:
        Input Assertions: period must be a positive integer.
        Output Assertions: True if period ends in 1 or 2, and is a plausible year.
    User Interface: (None)
    """
    if not isinstance(period, int) or period < 20001:
        return False
    
    last_digit = period % 10
    if last_digit not in [1, 2]:
        return False # T4: O formato do período é inválido (ex: 20253)
        
    return True

def _validate_schedule(horarios: List[Dict]) -> bool:
    """
    Objective: Validate the format and consistency of the class schedule.
    Description: Checks if all schedule entries have valid days and time format, and prevents conflicts (simplified).
    Coupling:
        :param horarios (List[Dict]): List of Schedule dictionaries (Horario).
        :return bool: True if valid, False otherwise.
    Coupling Conditions:
        Input Assertions: horarios must be a list of dictionaries with 'day', 'start_time', 'end_time'.
        Output Assertions: True if days are in WEEK_DAYS and times are sensible (start < end).
    User Interface: (None)
    """
    if not isinstance(horarios, list) or not horarios:
        return False # T5: Os horários são nulos
        
    for h in horarios:
        if h.get('day') not in WEEK_DAYS:
            return False
        start = h.get('start_time')
        end = h.get('end_time')
        
        if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end > 24:
            return False
        
        if start >= end:
            return False # Basic conflict check (end time must be after start time)
            
    # NOTE: Conflict between different time blocks is not implemented for simplicity.
    return True

# --- Public Access Functions (CRUD Class) ---

def validate_class(data: Dict) -> int:
    """
    Objective: Validate all necessary data fields and entity references (FKs) for a Class.
    Description: Corresponds to valida_turma. Checks period, schedule, and existence of related Subject and Professors.
    Coupling:
        :param data (Dict): The class dictionary to be validated.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: data is a dictionary containing all required keys.
        Output Assertions: If SUCCESS, all constraints (FKs, domain rules) are met.
    User Interface: (Internal Log).
    """

    from src.modules.professor import retrieve_professor
    from src.modules.subject import retrieve_subject

    # Check mandatory fields
    required_fields = ['subject_code', 'professors_ids', 'period', 'schedule', 'students_enrollments']
    if not all(field in data for field in required_fields):
        return RETURN_CODES['ERROR']
        
    # T4 - Invalid period
    if not _validate_period(data['period']):
        return RETURN_CODES['ERROR']
        
    # T5 - Invalid schedule
    if not _validate_schedule(data['schedule']):
        return RETURN_CODES['ERROR']

    # T2 - Subject Reference Check (FK)
    # Using mock function for validation
    if retrieve_subject(data['subject_code']) is None:
        print(f"User Message: Validation failed. Subject code {data['subject_code']} not found.")
        return RETURN_CODES['ERROR'] # T2: A matéria referenciada não existe.

    # T3 - Professor Reference Check (FK)
    if not data['professors_ids'] or not isinstance(data['professors_ids'], list):
        return RETURN_CODES['ERROR']
        
    for prof_id in data['professors_ids']:
        # Using mock function for validation
        if retrieve_professor(prof_id) is None:
            print(f"User Message: Validation failed. Professor ID {prof_id} not found.")
            return RETURN_CODES['ERROR'] # T3: Pelo menos um dos professores referenciados não existe.

    # NOTE: Student enrollment check is omitted here as per simplified requirements 
    # (students are added later), but the list must be present.
    
    return RETURN_CODES['SUCCESS'] # T1: Todos os campos válidos

def create_class(data: Dict) -> int:
    """
    Objective: Register a new Class/Turma in the system.
    Description: Generates a unique code and validates all references. Corresponds to cria_turma.
    Coupling:
        :param data (Dict): Class data (subject_code, professors_ids, period, schedule, etc.).
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: validate_class(data) == SUCCESS. Class must not be a duplicate (exists_class == ERROR).
        Output Assertions: A new class record exists in the database with a unique 'code'.
    User Interface: (Internal Log).
    """
    # T6 - Data validation
    if validate_class(data) != RETURN_CODES['SUCCESS']:
        return RETURN_CODES['ERROR']
        
    # T5 - Check for duplicate class (same Subject + Period + Professors)
    if exists_class(data) == RETURN_CODES['SUCCESS']:
        print("User Message: Creation failed. Already exists an identical class.")
        return RETURN_CODES['ERROR']
        
    new_code = _generate_class_id()
    
    class_record = {
        'code': new_code, # int codigo (pk)
        'subject_code': data['subject_code'], # Materia materia (Reference)
        'period': data['period'], # int periodo (e.g., 20241)
        'schedule': data['schedule'], # Horario horarios (List of dicts)
        'professors_ids': data['professors_ids'], # Prof profs[MAX_PROF_COUNT] (References)
        'students_enrollments': data.get('students_enrollments', []), # Aluno alunos [MAX_ALUNO_COUNT] (References)
        'reviews_ids': []
    }
    
    return repo_create_class(class_record) # T1: Sucesso

def exists_class(data: Dict) -> int:
    """
    Objective: Check if an identical class already exists (same subject, period, and professors).
    Description: Corresponds to existe_turma. Note: This check uses fields that define uniqueness, not the PK 'code'.
    Coupling:
        :param data (Dict): Class dictionary containing identification fields (subject_code, period, professors_ids).
        :return int: SUCCESS (0) (Exists) or ERROR (1) (Does not exist or Error).
    Coupling Conditions:
        Input Assertions: data is a dictionary containing at least subject_code, period, professors_ids.
        Output Assertions: If SUCCESS, an identical record exists in the database.
    User Interface: (Internal Log).
    """
    # T3 - Basic data validation
    if not isinstance(data, dict) or not all(k in data for k in ['subject_code', 'period', 'professors_ids']):
        return RETURN_CODES['ERROR']
        
    for class_record in database['classes']:
        # Compare based on unique identifiers (Subject, Period, Professors)
        is_duplicate = (
            class_record.get('subject_code') == data['subject_code'] and
            class_record.get('period') == data['period'] and
            # Comparing sets of professors_ids ensures order doesn't matter
            set(class_record.get('professors_ids', [])) == set(data['professors_ids'])
        )
        if is_duplicate:
            return RETURN_CODES['SUCCESS'] # T1: Uma turma com as mesmas características já está cadastrada.
            
    return RETURN_CODES['ERROR'] # T2: Nenhuma turma com as características informadas foi encontrada.

def retrieve_class(code: int) -> Union[Dict, None]:
    """
    Objective: Find a class record using its unique code.
    Description: Corresponds to busca_turma.
    Coupling:
        :param code (int): The class's code.
        :return Union[Dict, None]: The class dictionary or None (Erro).
    Coupling Conditions:
        Input Assertions: code must be a valid positive integer.
        Output Assertions: If returned, the class exists in the database.
    User Interface: (Internal Log).
    """
    if not isinstance(code, int) or code <= 0:
        return None # T3: O código da turma foi passado em um formato inválido.
        
    class_record = repo_retrieve_class(code)
    
    if class_record is None:
        print(f"User Message: Class with code {code} not found.")
    return class_record # T1: A turma com o código correspondente é encontrada e retornada.

def retrieve_all_classes() -> Union[List[Dict], None]:
    """
    Objective: Retrieve the entire list of registered classes.
    Description: Corresponds to busca_todas_turmas.
    Coupling:
        :return Union[List[Dict], None]: A pointer to the list of all class dictionaries or None (Error).
    Coupling Conditions:
        Input Assertions: (None).
        Output Assertions: Returns the list of class records (possibly empty).
    User Interface: (Internal Log).
    """
    if not database['classes']:
        return None # T2: Nenhuma turma está cadastrada no sistema.
    
    return database['classes'] # T1: Retorna um ponteiro para o vetor de todas as turmas.

def update_class(code: int, new_data: Dict) -> int:
    """
    Objective: Update one or more fields of an existing class record.
    Description: Corresponds to atualiza_turma.
    Coupling:
        :param code (int): The class's code.
        :param new_data (Dict): Dictionary containing the fields to update.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: code is valid. new_data combined with existing data passes validate_class.
        Output Assertions: If SUCCESS, the class record reflects the changes in new_data.
    User Interface: (Internal Log).
    """
    class_record = repo_retrieve_class(code)
    
    if class_record is None:
        return RETURN_CODES['ERROR'] # T2: O cod_turma especificado não corresponde a nenhuma turma existente.
        
    # Validation of the resulting class object (T3)
    temp_data = class_record.copy()
    temp_data.update(new_data)
    
    if validate_class(temp_data) != RETURN_CODES['SUCCESS']:
        return RETURN_CODES['ERROR'] # T3: Os novos dados são inválidos (ex: referenciam uma matéria ou professor que não existe).

    # T1 - Success
    for key, value in new_data.items():
        if key != 'code': # Code (PK) cannot be changed
            class_record[key] = value
            
    return RETURN_CODES['SUCCESS']

def delete_class(code: int) -> int:
    """
    Objective: Permanently remove a class record from the database.
    Description: Corresponds to deleta_turma.
    Coupling:
        :param code (int): The class's code.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: code is a valid positive integer.
        Output Assertions: If SUCCESS, the class record is removed from database['classes'].
    User Interface: (Internal Log).
    """
    if not isinstance(code, int) or code <= 0:
        return RETURN_CODES['ERROR'] # T3: O cod_turma foi passado em formato inválido.
        
    result = repo_delete_class(code)
    
    if result == RETURN_CODES['SUCCESS']:
        return RETURN_CODES['SUCCESS'] # T1: A turma com o código especificado é encontrada e removida.
    else:
        return RETURN_CODES['ERROR'] # T2: Nenhuma turma com o código especificado foi encontrada.
    
def associate_review_to_class(class_code: int, review_id: int) -> int:
    """
    Objective: Add a review ID reference to the target class record.
    Description: Called by the Review module to maintain referential integrity.
    Coupling:
        :param class_code (int): The code of the class to be updated.
        :param review_id (int): The ID of the newly created review.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: Both IDs must be valid positive integers. Class must exist.
        Output Assertions: If SUCCESS, review_id is appended to class_record['reviews_ids'].
    User Interface: (Internal Log).
    """
    
    class_record = repo_retrieve_class(class_code)
    
    if class_record is None or review_id <= 0:
        return RETURN_CODES['ERROR']
        
    if 'reviews_ids' not in class_record:
        class_record['reviews_ids'] = []
        
    if review_id in class_record['reviews_ids']:
        return RETURN_CODES['ERROR'] # Já associado
        
    class_record['reviews_ids'].append(review_id)
    return RETURN_CODES['SUCCESS']

def delete_student_reference_from_all_classes(enrollment: int) -> int:
    """
    Objective: Remove a student's enrollment from the 'students_enrollments' list in ALL classes.
    Description: Maintains integrity when a Student account is deleted.
    Coupling:
        :param enrollment (int): The enrollment ID of the student being deleted.
        :return int: SUCCESS (0).
    Coupling Conditions:
        Input Assertions: enrollment is a valid positive integer.
        Output Assertions: Enrollment ID is removed from all class records' student lists.
    User Interface: (Internal Log).
    """
    if not isinstance(enrollment, int) or enrollment <= 0:
        return RETURN_CODES['ERROR']
        
    for class_record in database['classes']:
        if enrollment in class_record.get('students_enrollments', []):
            try:
                class_record['students_enrollments'].remove(enrollment)
            except Exception:
                # Should not happen if existence is checked, but defensive programming.
                continue
                
    return RETURN_CODES['SUCCESS']

def delete_professor_reference_from_all_classes(prof_id: int) -> int:
    """
    Objective: Remove a professor's ID from the 'professors_ids' list in ALL classes.
    Description: Maintains integrity when a Professor record is deleted. If a class loses its last professor, it should be flagged (not implemented here).
    Coupling:
        :param prof_id (int): The ID of the professor being deleted.
        :return int: SUCCESS (0).
    Coupling Conditions:
        Input Assertions: prof_id is a valid positive integer.
        Output Assertions: Prof ID is removed from all class records' professor lists.
    User Interface: (Internal Log).
    """
    if not isinstance(prof_id, int) or prof_id <= 0:
        return RETURN_CODES['ERROR']
        
    for class_record in database['classes']:
        if prof_id in class_record.get('professors_ids', []):
            try:
                class_record['professors_ids'].remove(prof_id)
            except Exception:
                continue
                
    return RETURN_CODES['SUCCESS']

def delete_classes_by_subject(subject_code: int) -> int:
    """
    Objective: Delete ALL class records tied to a specific subject code.
    Description: Enforces the implicit business rule that a class cannot exist without its subject.
    Coupling:
        :param subject_code (int): The code of the subject being deleted.
        :return int: SUCCESS (0).
    Coupling Conditions:
        Input Assertions: subject_code is a valid positive integer.
        Output Assertions: All class records where 'subject_code' matches are removed from the database.
    User Interface: (Internal Log).
    """
    if not isinstance(subject_code, int) or subject_code <= 0:
        return RETURN_CODES['ERROR']
        
    initial_count = len(database['classes'])
    
    # Remove as classes filtrando a lista
    database['classes'][:] = [
        class_record for class_record in database['classes'] 
        if class_record.get('subject_code') != subject_code
    ]
    
    # Verifica se houve remoções
    if len(database['classes']) < initial_count:
        return RETURN_CODES['SUCCESS']
        
    # Retorna sucesso mesmo que nada tenha sido encontrado, pois o objetivo foi atingido
    return RETURN_CODES['SUCCESS']

# backend/modules/class_module.py

def remove_review_reference_from_class(class_code: int, review_id: int) -> int:
    """
    Objective: Remove a review ID reference from the target class record.
    """
    class_record = repo_retrieve_class(class_code)
    
    if class_record is None or review_id <= 0:
        return RETURN_CODES['ERROR']
        
    if review_id in class_record.get('reviews_ids', []):
        try:
            class_record['reviews_ids'].remove(review_id)
            return RETURN_CODES['SUCCESS']
        except ValueError:
            return RETURN_CODES['ERROR']
            
    return RETURN_CODES['ERROR']