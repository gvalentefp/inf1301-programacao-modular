"""
Module containing CRUD and association functions for the Professor entity.
The professor entity is a dictionary based on the typedef struct Prof.
Professor is NOT a user of the application.
"""
from typing import List, Dict, Union
from src.persistence import database
from src.shared import RETURN_CODES, CONSTANTS
from src.domains.department import validate_department
from src.persistence import find_entity_by_pk

__all__ = [
    'create_professor', 'retrieve_professor', 'retrieve_all_professors', 
    'update_professor', 'delete_professor', 'validate_professor', 
    'create_professor_subject', 'professor_teaches_subject', 
    'retrieve_professor_subjects', 'update_professor_subjects', 
    'delete_professor_subject', 'create_professor_review', 
    'retrieve_professor_reviews', 'retrieve_professor_review',
    'update_professor_review', 'delete_professor_review',
    'calculate_review_average_professor'
]

# Variável global para gerar IDs sequenciais para Professores (int id (pk))
next_professor_id = 1 

def _generate_professor_id() -> int:
    """
    Objective: Generate the next available unique ID for a Professor.
    Description: Calculates the maximum existing ID in the current 'professors' list and returns the next sequential integer. This ensures persistence consistency across test runs.
    Coupling:
        :return int: The next available professor ID (PK).
    Coupling Conditions:
        Input Assertions: (None).
        Output Assertions: The returned ID is greater than any existing professor ID in the database.
    User Interface: (None)
    """
    global next_professor_id

    profs = database.get('professors')
    if not isinstance(profs, list):
        profs = []
        database['professors'] = profs

    max_id = 0
    for prof in profs:
        pid = prof.get('id')
        if isinstance(pid, int) and pid > max_id:
            max_id = pid

    next_professor_id = max_id + 1
    return next_professor_id

# --- Repository Functions (Internal) ---

def repo_retrieve_professor(prof_id: int) -> Union[Dict, None]:
    """
    Objective: Find a professor dictionary in memory by their ID (primary key).
    Description: Corresponds to Prof busca_prof(int id).
    Coupling:
        :param prof_id (int): The professor's primary key.
        :return Union[Dict, None]: The professor dictionary or None if not found.
    Coupling Conditions:
        Input Assertions: prof_id must be a positive integer.
        Output Assertions: If a professor is returned, professor['id'] == prof_id.
    User Interface: (None)
    """
    if not isinstance(prof_id, int) or prof_id <= 0:
        return None
        
    for professor in database['professors']:
        if professor.get('id') == prof_id:
            return professor
    return None

def repo_create_professor(data: Dict) -> int:
    """
    Objective: Add a new professor dictionary to the database list.
    Description: Corresponds to repo_cria_prof(Prof* dados).
    Coupling:
        :param data (Dict): The professor dictionary containing all required fields.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: data must be a validated dictionary containing 'id'.
        Output Assertions: The size of database['professors'] increases by 1 upon SUCCESS.
    User Interface: (None)
    """
    try:
        database['professors'].append(data)
        return RETURN_CODES['SUCCESS']
    except Exception:
        return RETURN_CODES['ERROR']

# --- Public Access Functions (CRUD Professor) ---

def validate_professor(data: Dict) -> int:
    """
    Objective: Validate mandatory fields for creating or updating a professor record.
    Description: Checks required data fields and department validity. Corresponds to valida_prof.
    Coupling:
        :param data (Dict): The professor dictionary to be validated.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: data must be a dictionary.
        Output Assertions: If SUCCESS, required fields (name, department) are present and valid.
    User Interface: (None)
    """
    if not isinstance(data, dict):
        return RETURN_CODES['ERROR'] 

    # Check mandatory fields (name, department)
    name = data.get('name', '').strip()
    department = data.get('department', '').strip()

    if not name or len(name) > CONSTANTS['MAX_LENGTH_NAME']:
        return RETURN_CODES['ERROR'] # Invalid or empty name
        
    # Domain check for department
    if not validate_department(department):
        return RETURN_CODES['ERROR'] # Invalid department

    return RETURN_CODES['SUCCESS']

def create_professor(data: Dict) -> int:
    """
    Objective: Register a new professor in the system.
    Description: Generates a unique ID and validates data. Corresponds to cria_prof.
    Coupling:
        :param data (Dict): Professor data (name, department). Does not require 'id'.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: validate_professor(data) == SUCCESS.
        Output Assertions: A new professor record exists in the database with a unique 'id'.
    User Interface: Log "Creating professor {name}" (Internal Log).
    """
    if validate_professor(data) != RETURN_CODES['SUCCESS']:
        print("Log: Failed to create professor. Invalid data.")
        return RETURN_CODES['ERROR']
        
    new_id = _generate_professor_id()
    
    professor_record = {
        'id': new_id,
        'name': data['name'], # char nome[MAX_NAME_LENGTH]
        'department': data['department'], # Depto depto
        'subjects': [], # Materia materias [MAX_MATERIAS] (Subject codes)
        'reviews': []   # Aval avaliacoes[MAX_AVALS] (Review IDs)
    }
    
    return repo_create_professor(professor_record)

def retrieve_professor(prof_id: int) -> Union[Dict, None]:
    """
    Objective: Find a professor record using their unique ID.
    Description: Corresponds to busca_prof.
    Coupling:
        :param prof_id (int): The professor's ID.
        :return Union[Dict, None]: The professor dictionary or None.
    Coupling Conditions:
        Input Assertions: prof_id must be a valid positive integer.
        Output Assertions: If returned, the professor exists in the database.
    User Interface: (Internal Log).
    """
    return repo_retrieve_professor(prof_id)

def retrieve_all_professors() -> List[Dict]:
    """
    Objective: Retrieve the entire list of registered professors.
    Description: Corresponds to busca_todos_profs.
    Coupling:
        :return List[Dict]: A list containing all professor dictionaries.
    Coupling Conditions:
        Input Assertions: (None).
        Output Assertions: Returns a list (possibly empty) containing valid professor records.
    User Interface: (None)
    """
    return database['professors']

def update_professor(prof_id: int, new_data: Dict) -> int:
    """
    Objective: Update one or more fields of an existing professor record.
    Description: Corresponds to atualiza_prof.
    Coupling:
        :param prof_id (int): The professor's ID.
        :param new_data (Dict): Dictionary containing the fields to update (name, department).
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: prof_id is valid. new_data combined with existing data passes validate_professor.
        Output Assertions: If SUCCESS, the professor record reflects the changes in new_data.
    User Interface: (Internal Log).
    """
    professor = repo_retrieve_professor(prof_id)
    
    if professor is None:
        return RETURN_CODES['ERROR'] # Professor not found
        
    # Validation of the resulting professor object
    temp_data = professor.copy()
    temp_data.update(new_data)
    
    if validate_professor(temp_data) != RETURN_CODES['SUCCESS']:
        return RETURN_CODES['ERROR'] # Invalid resulting data

    # Success
    for key, value in new_data.items():
        if key != 'id': # ID (PK) cannot be changed
            professor[key] = value
            
    return RETURN_CODES['SUCCESS']

def delete_professor(prof_id: int) -> int:
    """
    Objective: Permanently remove a professor record from the database.
    Description: Corresponds to deleta_prof.
    Coupling:
        :param prof_id (int): The professor's ID.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: prof_id is a valid positive integer.
        Output Assertions: If SUCCESS, the professor record is removed from database['professors'].
    User Interface: (Internal Log).
    """
    professor = repo_retrieve_professor(prof_id)
    
    if professor is None:
        return RETURN_CODES['ERROR'] # Professor not found
        
    try:
        database['professors'].remove(professor)
        return RETURN_CODES['SUCCESS']
    except ValueError:
        return RETURN_CODES['ERROR']


# --- Subject Association Functions (Matérias) ---

def create_professor_subject(prof_id: int, subject_code: int) -> int:
    """
    Objective: Associate a subject code to a professor's list of subjects they teach/taught.
    Description: Corresponds to cria_materia_prof.
    Coupling:
        :param prof_id (int): Professor's ID.
        :param subject_code (int): Subject's code.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: prof_id and subject_code are valid positive integers. Professor must exist.
        Output Assertions: If SUCCESS, subject_code is added to professor['subjects'].
    User Interface: (Internal Log).
    """
    professor = repo_retrieve_professor(prof_id)
    
    if professor is None or subject_code <= 0:
        return RETURN_CODES['ERROR'] # Invalid professor/code
        
    if subject_code in professor['subjects']:
        return RETURN_CODES['ERROR'] # Already associated

    professor['subjects'].append(subject_code)
    return RETURN_CODES['SUCCESS']

def professor_teaches_subject(prof_id: int, subject_code: int) -> int:
    """
    Objective: Check if a professor teaches a specific subject.
    Description: Corresponds to prof_ensina_materia.
    Coupling:
        :param prof_id (int): Professor's ID.
        :param subject_code (int): Subject's code.
        :return int: SUCCESS (0) (if true) or ERROR (1) (if false or error).
    Coupling Conditions:
        Input Assertions: prof_id and subject_code are valid positive integers.
        Output Assertions: If SUCCESS, subject_code is present in professor['subjects'].
    User Interface: (Internal Log).
    """
    professor = repo_retrieve_professor(prof_id)
    
    if professor is None or subject_code <= 0:
        return RETURN_CODES['ERROR'] 
        
    if subject_code in professor['subjects']:
        return RETURN_CODES['SUCCESS'] 
    else:
        return RETURN_CODES['ERROR'] 

def retrieve_professor_subjects(prof_id: int) -> Union[List[int], None]:
    """
    Objective: Retrieve the list of subject codes associated with a professor.
    Description: Corresponds to busca_materias_prof.
    Coupling:
        :param prof_id (int): Professor's ID.
        :return Union[List[int], None]: List of subject codes or None (ERROR).
    Coupling Conditions:
        Input Assertions: prof_id is a valid positive integer.
        Output Assertions: Returns a list of codes (possibly empty).
    User Interface: (Internal Log).
    """
    professor = repo_retrieve_professor(prof_id)
    
    if professor is None:
        return None
        
    return professor['subjects']

def update_professor_subjects(old_code: int, new_code: int) -> int:
    """
    Objective: Globally update an old subject code reference to a new one across all professor records.
    Description: Corresponds to atualiza_materia_profs. Used when a subject code is changed by the admin.
    Coupling:
        :param old_code (int): The subject code to be replaced.
        :param new_code (int): The new subject code.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: old_code and new_code are valid positive integers.
        Output Assertions: If SUCCESS, all instances of old_code in professor['subjects'] lists are replaced by new_code.
    User Interface: (Internal Log).
    """
    if not isinstance(old_code, int) or old_code <= 0 or not isinstance(new_code, int) or new_code <= 0:
        return RETURN_CODES['ERROR']
        
    updated_count = 0
    for professor in database['professors']:
        if old_code in professor['subjects']:
            try:
                professor['subjects'].remove(old_code)
                professor['subjects'].append(new_code)
                updated_count += 1
            except Exception:
                return RETURN_CODES['ERROR']
                
    if updated_count == 0 and old_code not in [sub for prof in database['professors'] for sub in prof['subjects']]:
        return RETURN_CODES['ERROR'] # Old code not found in any professor's list

    return RETURN_CODES['SUCCESS']

def delete_professor_subject(prof_id: int, subject_code: int) -> int:
    """
    Objective: Remove a specific subject code from a professor's teaching list.
    Description: Corresponds to deleta_materia_prof.
    Coupling:
        :param prof_id (int): Professor's ID.
        :param subject_code (int): Subject's code to remove.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: prof_id and subject_code are valid positive integers. Professor must exist and teach the subject.
        Output Assertions: If SUCCESS, subject_code is removed from professor['subjects'].
    User Interface: (Internal Log).
    """
    professor = repo_retrieve_professor(prof_id)
    
    if professor is None or subject_code <= 0 or subject_code not in professor['subjects']:
        return RETURN_CODES['ERROR'] 
        
    try:
        professor['subjects'].remove(subject_code)
        return RETURN_CODES['SUCCESS']
    except ValueError:
        return RETURN_CODES['ERROR']

# --- Review Association Functions (Avaliações) ---

def create_professor_review(prof_id: int, review_data: Dict) -> int:
    """
    Objective: Associate a new review directed at the professor to their record.
    Description: Corresponds to cria_aval_prof. Stores the Review ID (PK).
    Coupling:
        :param prof_id (int): Professor's ID.
        :param review_data (Dict): The full review dictionary (must contain PK 'id_aval').
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: prof_id is valid. review_data contains 'id_aval' and is valid. Professor must exist.
        Output Assertions: If SUCCESS, the review PK is added to professor['reviews'].
    User Interface: (Internal Log).
    """
    professor = repo_retrieve_professor(prof_id)
    review_id = review_data.get('id_aval') 
    
    if professor is None or not isinstance(review_id, int) or review_id <= 0:
        return RETURN_CODES['ERROR']
        
    if review_id in professor['reviews']:
        return RETURN_CODES['ERROR'] # Review already associated

    professor['reviews'].append(review_id)
    return RETURN_CODES['SUCCESS']


def retrieve_professor_reviews(prof_id: int) -> Union[List[int], None]:
    """
    Objective: Retrieve the list of PKs for reviews received by the professor.
    Description: Corresponds to busca_avaliacoes_prof.
    Coupling:
        :param prof_id (int): Professor's ID.
        :return Union[List[int], None]: List of review IDs or None.
    Coupling Conditions:
        Input Assertions: prof_id is valid.
        Output Assertions: Returns a list of review IDs (possibly empty).
    User Interface: (Internal Log).
    """
    professor = repo_retrieve_professor(prof_id)
    if professor is None:
        return None
        
    return professor['reviews']


def retrieve_professor_review(prof_id: int, review_id: int) -> Union[int, None]: 
    """
    Objective: Check if a specific review ID is associated with the professor (received by them).
    Description: Corresponds to busca_aval_prof. Returns the ID if the professor received it.
    Coupling:
        :param prof_id (int): Professor's ID.
        :param review_id (int): Review's primary key.
        :return Union[int, None]: Review ID if found, or None.
    Coupling Conditions:
        Input Assertions: prof_id and review_id are valid positive integers.
        Output Assertions: Returns review_id if present in professor['reviews'].
    User Interface: (Internal Log).
    """
    professor = repo_retrieve_professor(prof_id)
    
    if professor is None or not isinstance(review_id, int) or review_id <= 0:
        return None
        
    if review_id in professor['reviews']:
        return review_id
    return None

def update_professor_review(prof_id: int, review_id: int, new_review_data: Dict) -> int:
    """
    Objective: Validate that a review update concerns a review received by the professor.
    Description: Corresponds to atualiza_aval_prof. Assures the review is correctly linked before update logic.
    Coupling:
        :param prof_id (int): Professor's ID.
        :param review_id (int): Review's primary key.
        :param new_review_data (Dict): New data for the review.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: Professor exists and received the review. new_review_data must be valid.
        Output Assertions: If SUCCESS, implies the Review module can proceed with the update.
    User Interface: (Internal Log).
    """
    if retrieve_professor_review(prof_id, review_id) is None:
        return RETURN_CODES['ERROR'] # Professor did not receive this review or review/professor does not exist.
        
    return RETURN_CODES['SUCCESS']

def delete_professor_review(prof_id: int, review_id: int) -> int:
    """
    Objective: Remove the review reference (PK) from the professor's received list.
    Description: Corresponds to deleta_aval_prof. Should be coupled with deletion in the Review module.
    Coupling:
        :param prof_id (int): Professor's ID.
        :param review_id (int): Review's primary key to delete.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: Professor exists and received the review.
        Output Assertions: If SUCCESS, review_id is removed from professor['reviews'].
    User Interface: (Internal Log).
    """
    professor = repo_retrieve_professor(prof_id)
    
    if professor is None or review_id <= 0 or review_id not in professor['reviews']:
        return RETURN_CODES['ERROR'] 
        
    try:
        professor['reviews'].remove(review_id)
        return RETURN_CODES['SUCCESS']
    except ValueError:
        return RETURN_CODES['ERROR']

def calculate_review_average_professor(prof_id: int) -> float:
    """
    Objective: Calculate the average star rating for a professor.
    Description: Corresponds to calcula_aval_media_prof. Returns the average with 1 decimal place.
    Coupling:
        :param prof_id (int): Professor's ID.
        :return float: The average rating (0.0 if no reviews) or -1.0 on error.
    Coupling Conditions:
        Input Assertions: prof_id is a valid positive integer. Professor must exist.
        Output Assertions: Returns a float between 0.0 and 5.0 (or -1.0 for error).
    User Interface: (Internal Log).
    """
    professor = repo_retrieve_professor(prof_id)
    if professor is None:
        return -1.0 # Error: Professor not found
        
    review_ids = professor['reviews']
    if not review_ids:
        return 0.0 # No reviews, average is 0.0

    total_stars = 0
    count = 0
    
    # Realiza a busca das avaliações usando a nova função de persistência
    for review_id in review_ids:
        review = find_entity_by_pk('reviews', review_id, 'id_aval')
        
        # Apenas inclui reviews que existem e possuem avaliação por estrelas
        if review and review.get('stars') is not None:
            total_stars += review['stars']
            count += 1

    if count == 0:
        return 0.0 # Retorna 0.0 se houver reviews, mas nenhuma com estrelas válidas
        
    average = total_stars / count
    
    return round(average, 1) # Retorna a média com 1 casa decimal

def remove_review_reference_from_professor(prof_id: int, review_id: int) -> int:
    """
    Objective: Remove a review ID reference from the professor's received list.
    Description: Corresponds to deleta_aval_prof. Ensures consistency when a Review directed at this Professor is deleted (cascading cleanup).
    Coupling:
        :param prof_id (int): Professor's ID.
        :param review_id (int): Review's primary key to remove.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: prof_id and review_id are valid positive integers. Professor must exist.
        Output Assertions: If SUCCESS, review_id is removed from professor['reviews'].
    User Interface: (Internal Log).
    """
    professor = repo_retrieve_professor(prof_id)
    
    if professor is None or review_id <= 0:
        return RETURN_CODES['ERROR']
        
    if review_id in professor.get('reviews', []):
        try:
            professor['reviews'].remove(review_id)
            return RETURN_CODES['SUCCESS']
        except ValueError:
            return RETURN_CODES['ERROR']
            
    return RETURN_CODES['ERROR']

def remove_subject_reference_from_all_professors(subject_code: int) -> int:
    """
    Objective: Remove a specific subject code from the 'subjects' list of ALL professors.
    Description: Maintains data integrity across the database when a Subject is deleted (cascading cleanup).
    Coupling:
        :param subject_code (int): The code of the subject being deleted.
        :return int: SUCCESS (0).
    Coupling Conditions:
        Input Assertions: subject_code is a valid positive integer.
        Output Assertions: subject_code is removed from all professor['subjects'] lists where it was present.
    User Interface: (Internal Log).
    """
    if not isinstance(subject_code, int) or subject_code <= 0:
        return RETURN_CODES['ERROR']
        
    for professor in database['professors']:
        if subject_code in professor.get('subjects', []):
            try:
                professor['subjects'].remove(subject_code)
            except Exception:
                continue
                
    return RETURN_CODES['SUCCESS']