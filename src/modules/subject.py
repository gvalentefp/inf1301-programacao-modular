"""
Module containing CRUD functions for the Subject entity.
The entity is represented as a dictionary.
"""
from typing import List, Dict, Union
from src.persistence import database
from src.shared import RETURN_CODES
from src.shared import CONSTANTS

__all__ = [
    'create_subject', 'exists_subject', 'retrieve_subject', 
    'update_subject', 'delete_subject', 'validate_subject', 
    'retrieve_all_subjects'
]

# --- Repository Functions (Private/Internal) ---

def repo_create_subject(data: Dict) -> int:
    """
    Objective: Persist a new subject in the database.
    Description: Low-level function that appends the subject dictionary to the global list. Corresponds to repo_cria_materia.
    Coupling:
        :param data (Dict): The subject dictionary representing the entity.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: data is a valid dictionary.
        Output Assertions: data is appended to database['subjects'].
    User Interface: (Internal Log).
    """
    try:
        database['subjects'].append(data)
        return RETURN_CODES['SUCCESS']
    except Exception:
        return RETURN_CODES['ERROR']

def repo_retrieve_subject(code: int) -> Union[Dict, None]:
    """
    Objective: Search for a subject record by its primary key.
    Description: Iterates through the database to find a match. Corresponds to repo_busca_materia.
    Coupling:
        :param code (int): The unique code of the subject.
        :return Union[Dict, None]: The subject dictionary if found, otherwise None.
    Coupling Conditions:
        Input Assertions: code is an integer.
        Output Assertions: Returns the reference to the dictionary where dict['code'] == code.
    User Interface: (Internal Log).
    """
    for subject in database['subjects']:
        if subject.get('code') == code:
            return subject
    return None

# --- Public Access Functions ---

def validate_subject(data: Dict) -> int:
    """
    Objective: Verify the integrity and format of subject data.
    Description: Checks if mandatory fields (code, credits, name) exist and respect constraints (types, length, values). Corresponds to valida_materia.
    Coupling:
        :param data (Dict): Dictionary containing subject data.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: data is a dictionary.
        Output Assertions: Returns SUCCESS only if 'code' > 0, 'credits' >= 0, and 'name' is non-empty and within max length.
    User Interface: (Internal Log).
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
    Objective: Create a new subject entity in the system.
    Description: Orchestrates validation, uniqueness check, and persistence. Corresponds to cria_materia.
    Coupling:
        :param data (Dict): Dictionary containing all required fields for the subject.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: data is not None. data contains valid fields (checked by validate_subject). data['code'] must not already exist.
        Output Assertions: If SUCCESS, the new subject is stored in the database.
    User Interface: Log "Subject {code} created successfully" (Internal Log).
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
    Objective: Retrieve a specific subject's details.
    Description: Public interface to search for a subject. Corresponds to busca_materia.
    Coupling:
        :param code (int): Subject's unique code.
        :return Union[Dict, None]: The subject object or None if not found/invalid.
    Coupling Conditions:
        Input Assertions: code must be a positive integer.
        Output Assertions: Returns the subject dictionary matching the code.
    User Interface: (Internal Log).
    """
    # T3 - Validate code parameter (Assuming non-positive is invalid) 
    if not isinstance(code, int) or code <= 0:
        return None 

    # T1/T2 - Retrieve the subject 
    return repo_retrieve_subject(code)
    
def retrieve_all_subjects() -> List[Dict]:
    """
    Objective: List all registered subjects.
    Description: Returns a complete list of subjects available in the system. Corresponds to busca_todas_materias.
    Coupling:
        :return List[Dict]: A list containing all subject dictionaries.
    Coupling Conditions:
        Input Assertions: None.
        Output Assertions: Returns a list (can be empty).
    User Interface: (Internal Log).
    """
    # Assuming the in-memory structure is always accessible. Returns a copy.
    return list(database['subjects'])

def exists_subject(data: Dict) -> int:
    """
    Objective: Check if a subject is already registered based on its code.
    Description: Validates the input structure and checks existence in the repository. Corresponds to existe_materia.
    Coupling:
        :param data (Dict): A dictionary containing at least the 'code'.
        :return int: SUCCESS (0) if it exists, ERROR (1) if it does not or input is invalid.
    Coupling Conditions:
        Input Assertions: data is valid structure.
        Output Assertions: Returns SUCCESS if repo_retrieve_subject finds the code.
    User Interface: (Internal Log).
    """
    if validate_subject(data) != RETURN_CODES['SUCCESS']:
        return RETURN_CODES['ERROR']
    
    if repo_retrieve_subject(data['code']):
        return RETURN_CODES['SUCCESS'] # Subject exists
    return RETURN_CODES['ERROR'] # Subject does not exist

def update_subject(code: int, new_data: Dict) -> int:
    """
    Objective: Update the information of an existing subject.
    Description: Modifies fields of a subject identified by code. Ensures the new data is valid. Corresponds to atualiza_materia.
    Coupling:
        :param code (int): The code of the subject to update.
        :param new_data (Dict): Dictionary containing the updated fields.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: code must exist in DB. new_data must be valid (validated via temp copy to preserve PK).
        Output Assertions: If SUCCESS, the subject record in DB is modified with values from new_data (except 'code').
    User Interface: Log "Subject {code} updated" (Internal Log).
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
    Objective: Permanently remove a subject record and enforce referential integrity.
    Description: Orchestrates a cascading delete. Removes dependent Classes (Turmas), and cleans references in Student History and Professor records before deleting the Subject itself. Corresponds to remove_materia.
    Coupling:
        :param code (int): The code of the subject to delete.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: code is a positive integer. Subject must exist.
        Output Assertions: If SUCCESS, subject is removed from DB and all references in Classes, Students, and Professors are cleared.
    User Interface: Log "Subject {code} and dependencies deleted" (Internal Log).
    """
    
    from src.modules.classes import delete_classes_by_subject
    from src.modules.student import remove_subject_reference_from_all_students
    from src.modules.professor import remove_subject_reference_from_all_professors

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