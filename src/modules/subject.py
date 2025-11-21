"""
Module containing CRUD functions for the Subject entity.
The entity is represented as a dictionary.
"""
from typing import List, Dict, Union
from src.persistence import database
from src.shared import RETURN_CODES
from src.shared import CONSTANTS
from src.modules.classes import delete_classes_by_subject
from src.modules.student import remove_subject_reference_from_all_students
from src.modules.professor import remove_subject_reference_from_all_professors
from src.modules.classes import delete_classes_by_subject

__all__ = [
    'create_subject', 'exists_subject', 'retrieve_subject', 
    'update_subject', 'delete_subject', 'validate_subject', 
    'retrieve_all_subjects'
]

# --- Repository Functions (Private/Internal) ---
# Functions prefixed with repo_ 

def repo_create_subject(data: Dict) -> int:
    """
    Adds a subject dictionary to the global database['subjects'] list.
    Corresponds to repo_cria_materia
    """
    try:
        database['subjects'].append(data)
        return RETURN_CODES['SUCCESS']
    except Exception:
        return RETURN_CODES['ERROR']

def repo_retrieve_subject(code: int) -> Union[Dict, None]:
    """
    Searches for a subject dictionary by its code (primary key).
    Corresponds to repo_busca_materia
    """
    for subject in database['subjects']:
        if subject.get('code') == code:
            return subject
    return None

# Placeholder for other repo functions (to be implemented later if needed)

# --- Public Access Functions ---

def validate_subject(data: Dict) -> int:
    """
    Validates mandatory fields and integrity constraints for a Subject.
    Corresponds to valida_materia
    
    Subject structure (dict): {'code': int (pk), 'credits': int, 'name': str, 'description': str}
    """
    if not isinstance(data, dict):
        return RETURN_CODES['ERROR'] # T4 - Data is invalid 

    # Check mandatory fields (assuming code, credits, and name are mandatory)
    code = data.get('code')
    credits = data.get('credits')
    name = data.get('name', '').strip()
    
    if not isinstance(code, int) or code <= 0:
        return RETURN_CODES['ERROR'] # T4 - Invalid code 
        
    if not isinstance(credits, int) or credits < 0:
        return RETURN_CODES['ERROR'] # T4 - Negative credits 
        
    if not name or len(name) > CONSTANTS['MAX_LENGTH_NAME']:
        return RETURN_CODES['ERROR'] # T4 - Empty or too long name 
    
    return RETURN_CODES['SUCCESS']


def create_subject(data: Dict) -> int:
    """
    Creates a new subject and adds it to the database.
    Corresponds to cria_materia
    """
    # T2 - Check if data pointer is NULL (data is None) 
    if data is None:
        return RETURN_CODES['ERROR']

    # T4 - Validate data fields 
    if validate_subject(data) != RETURN_CODES['SUCCESS']:
        return RETURN_CODES['ERROR']

    # T3 - Check for existing subject (Primary Key constraint) 
    if repo_retrieve_subject(data['code']) is not None:
        return RETURN_CODES['ERROR']
        
    # T1 - Success (call repo function) 
    return repo_create_subject(data)

def retrieve_subject(code: int) -> Union[Dict, None]:
    """
    Finds and returns a subject by its code.
    Corresponds to busca_materia
    """
    # T3 - Validate code parameter (Assuming non-positive is invalid) 
    if not isinstance(code, int) or code <= 0:
        return None 

    # T1/T2 - Retrieve the subject 
    return repo_retrieve_subject(code)
    
def retrieve_all_subjects() -> List[Dict]:
    """
    Returns a list of all subjects.
    Corresponds to busca_todas_materias
    """
    # Assuming the in-memory structure is always accessible. Returns a copy.
    return list(database['subjects'])

def exists_subject(data: Dict) -> int:
    """
    Checks if a subject with the same code already exists.
    Corresponds to existe_materia
    """
    if validate_subject(data) != RETURN_CODES['SUCCESS']:
        return RETURN_CODES['ERROR']
    
    if repo_retrieve_subject(data['code']):
        return RETURN_CODES['SUCCESS'] # Subject exists
    return RETURN_CODES['ERROR'] # Subject does not exist

def update_subject(code: int, new_data: Dict) -> int:
    """
    Updates the data of an existing subject.
    Corresponds to atualiza_materia
    """
    # T2 - Check if the subject exists 
    subject = repo_retrieve_subject(code)
    if subject is None:
        return RETURN_CODES['ERROR']
        
    # T3 - Check if new_data is NULL 
    if new_data is None:
        return RETURN_CODES['ERROR']

    # T4 - Validate the new data (exclude the code update from validation to allow the code to be the key) 
    # Create a temporary dict for validation, keeping the original code
    temp_data = new_data.copy()
    temp_data['code'] = code # Ensure the validation function has a code
    if validate_subject(temp_data) != RETURN_CODES['SUCCESS']:
        return RETURN_CODES['ERROR']
        
    # T1 - Success: Update the fields (excluding 'code' itself) 
    for key, value in new_data.items():
        if key != 'code':
            subject[key] = value
            
    return RETURN_CODES['SUCCESS']

def delete_subject(code: int) -> int:
    """
    Objective: Permanently remove a subject record (PK) and orchestrate the deletion of all dependent records (cascading delete).
    """

    # T3 - Validate code parameter 
    if not isinstance(code, int) or code <= 0:
        return RETURN_CODES['ERROR']

    # T2 - Check if the subject exists 
    subject = repo_retrieve_subject(code)
    if subject is None:
        return RETURN_CODES['ERROR']
    
    # T1 - Success: Remove the subject 
    # --- ORQUESTRAÇÃO DE LIMPEZA DE REFERÊNCIAS ---

    # 1. Deleção em Cascata de Turmas dependentes
    delete_classes_by_subject(code)
    
    # 2. Limpeza de Referência em Alunos (Histórico)
    remove_subject_reference_from_all_students(code)
    
    # 3. Limpeza de Referência em Professores (Matérias que Lecionam)
    remove_subject_reference_from_all_professors(code)
    
    # 4. Deleção do Registro Principal (Matéria)
    try:
        database['subjects'].remove(subject)
        return RETURN_CODES['SUCCESS']
    except ValueError:
        return RETURN_CODES['ERROR']