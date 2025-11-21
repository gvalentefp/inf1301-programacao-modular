"""
Module containing CRUD and validation functions for the Review (Avaliação) entity.
This is a central entity that references Student (author), Professor, and Class.
"""
from typing import List, Dict, Union
import datetime
from src.persistence import database
from src.shared import RETURN_CODES, CONSTANTS
from src.persistence import find_entity_by_pk
from src.persistence import find_entity_by_pk 
# from src.modules.student import create_student_review 
# from src.modules.professor import create_professor_review 
# from src.modules.classes import associate_review_to_class 
# from src.modules.student import delete_student_review 
# from src.modules.professor import remove_review_reference_from_professor
# from src.modules.classes import remove_review_reference_from_class

__all__ = [
    'create_review', 'retrieve_review', 'update_review', 
    'delete_review', 'validate_review', 'retrieve_all_reviews',
    'validate_review_category', 'REVIEW_CATEGORIES'
]

# Definição das Categorias de Avaliação (Baseado no enum CatAval)
# As categorias são usadas para taguear o foco da avaliação.
REVIEW_CATEGORIES = {
    # Categorias com foco em entidades específicas (professor, aluno, matéria, turma)
    'PROF_GOOD': "Elogio ao Professor",
    'PROF_BAD': "Crítica ao Professor",
    'PROF_CRAZY': "Professor Maluco",
    'CLASS_BORING': "Turma Chata",
    'CLASS_ROOM': "Sala de Aula da Turma",
    'STUDENT_ANNOYING': "Aluno Insuportável",
    'STUDENT_GENIUS': "Aluno Genial",
    'STUDENT_DUMB': "Aluno Burro",
    'STUDENT_PSYCHO': "Aluno Psicopata",
    'STUDENT_FUNNY': "Aluno Engraçado",
    'SUBJECT_DIFFICULT': "Matéria Difícil",
    'SUBJECT_EASY': "Matéria Fácil",
    'SUBJECT_IRRELEVANT': "Matéria Nada a Ver",
    'SUBJECT_BORING': "Matéria Chata",
    'SUBJECT_IMPOSSIBLE_TEST': "Matéria Prova Impossível",
    'SUBJECT_EASY_TEST': "Matéria Prova Fácil",
    'SUBJECT_MANY_PAPERS': "Matéria Muitos Trabalhos",
    'OTHER': "Outro (Categoria Indefinida)",
    
    # Categorias de Assuntos Gerais (aceitam Turma/Class nula)
    'GENERAL_TOPICS': "Assuntos Gerais",
    'CANTEEN': "Bandejão",
    'ROBBERY': "Assalto",
    'BIKE_PARKING': "Bicicletário",
    'GYMNASIUM': "Ginásio",
    'SPOTTED': "Spotted PUC",
    'PUC_URGENT': "PUC Urgente",
    'DIRECTORIES_VILLAGE': "Vila dos Diretórios",
    'EVENTS': "Eventos",
    'PARKING_LOT': "Estacionamento",
    'BLUE_STANDS': "Barraquinhas Azuis",
    'FOOD': "Comida",
    'INTERNSHIP_OPPS': "Oportunidades de Estágio",
    'JOB_OPPS': "Oportunidades de Trabalho",
    'RESEARCH_OPPS': "Oportunidades de Pesquisa",
    'INFORMATICS_WEEK': "Semana da Informática",
    'CAINF': "CAINF",
    'INF_DEPT': "Departamento de Informática",
    'UG_LAB': "LAB Grad",
    'DEV_SUGGESTION': "Sugestão aos Desenvolvedores"
}

# Variável global para gerar IDs sequenciais para Avaliações (int id_aval (pk))
next_review_id = 1 

def _generate_review_id() -> int:
    """Objective: Generate a new unique ID for Review (Avaliação)."""
    global next_review_id
    id_atual = next_review_id
    next_review_id += 1
    return id_atual

# --- Repository Functions (Internal) ---

def repo_retrieve_review(review_id: int) -> Union[Dict, None]:
    """
    Objective: Find a review dictionary in memory by its ID (primary key).
    Description: Corresponds to Aval repo_busca_aval(int id_aval).
    Coupling:
        :param review_id (int): The review's primary key.
        :return Union[Dict, None]: The review dictionary or None if not found.
    Coupling Conditions:
        Input Assertions: review_id must be a positive integer.
        Output Assertions: If a review is returned, review['id_aval'] == review_id.
    User Interface: (None)
    """
    if not isinstance(review_id, int) or review_id <= 0:
        return None
        
    for review in database['reviews']:
        if review.get('id_aval') == review_id:
            return review
    return None

def repo_create_review(data: Dict) -> int:
    """
    Objective: Add a new review dictionary to the database list.
    Description: Corresponds to int repo_cria_aval(Aval* dados).
    Coupling:
        :param data (Dict): The review dictionary containing all required fields.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: data must be a validated dictionary containing 'id_aval'.
        Output Assertions: The size of database['reviews'] increases by 1 upon SUCCESS.
    User Interface: (None)
    """
    try:
        database['reviews'].append(data)
        return RETURN_CODES['SUCCESS']
    except Exception:
        return RETURN_CODES['ERROR']

# --- Validation Functions ---

def validate_review_category(category_key: str, class_code: Union[int, None]) -> bool:
    """
    Objective: Validate if a category key is recognized.
    Description: Ensures the chosen tag is from the defined list. Checks if 'class_code' is mandatory for the category.
    Coupling:
        :param category_key (str): The category acronym (e.g., 'PROF_GOOD').
        :param class_code (Union[int, None]): The class code associated, or None if general.
        :return bool: True if valid, False otherwise.
    Coupling Conditions:
        Input Assertions: category_key is a string.
        Output Assertions: True if category is in REVIEW_CATEGORIES and class_code requirement is met.
    User Interface: (None)
    """
    if category_key not in REVIEW_CATEGORIES:
        return False
        
    # Categories that MUST have a Class code (focus on an academic entity)
    categories_requiring_class = [
        'PROF_GOOD', 'PROF_BAD', 'PROF_CRAZY', 'CLASS_BORING', 'CLASS_ROOM', 
        'STUDENT_ANNOYING', 'STUDENT_GENIUS', 'STUDENT_DUMB', 'STUDENT_PSYCHO', 
        'STUDENT_FUNNY', 'SUBJECT_DIFFICULT', 'SUBJECT_EASY', 'SUBJECT_IRRELEVANT', 
        'SUBJECT_BORING', 'SUBJECT_IMPOSSIBLE_TEST', 'SUBJECT_EASY_TEST', 
        'SUBJECT_MANY_PAPERS', 'OTHER'
    ]
    
    if category_key in categories_requiring_class and class_code is None:
        return False
        
    # Categories that MUST NOT have a Class code (General Topics, PUC-wide)
    # The requirement is that *abaixo, categorias que aceitam turma NULL*, so having a code is not forbidden, but often unnecessary.
    # We enforce that if it is a general topic, the class code should ideally be None. 
    # For simplicity, we only fail if a required class is missing.
        
    return True


def validate_review(data: Dict) -> int:
    """
    Objective: Validate mandatory fields and integrity constraints for a Review.
    Description: Corresponds to valida_aval. Checks author, timestamp, title, comment, stars (0-5), category, and FKs.
    Coupling:
        :param data (Dict): The review dictionary to be validated.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: data is a dictionary.
        Output Assertions: If SUCCESS, all required fields are present, valid, and references exist.
    User Interface: (None)
    """
    required_fields = ['student_enrollment', 'title', 'comment', 'date_time', 'category', 'is_anonymous']
    if not all(field in data for field in required_fields):
        return RETURN_CODES['ERROR'] 

    # 1. Author and Timestamp Check (Mandatory fields)
    if find_entity_by_pk('students', data['student_enrollment'], 'enrollment') is None:
        return RETURN_CODES['ERROR'] # Author (Student) must exist
        
    if not data['title'] or len(data['title']) > CONSTANTS['MAX_TITLE_LENGTH']:
        return RETURN_CODES['ERROR'] # Title check
        
    if not data['comment'] or len(data['comment']) > CONSTANTS['MAX_COMMENT_LENGTH']:
        return RETURN_CODES['ERROR'] # Comment check
        
    if not isinstance(data['date_time'], str): # Simplified check for a string representation of struct tm
        return RETURN_CODES['ERROR']
        
    # 2. Stars Check (Optional, but if present, must be 0-5)
    stars = data.get('stars')
    if stars is not None and (not isinstance(stars, int) or stars < 0 or stars > 5):
        return RETURN_CODES['ERROR']

    # 3. Category and Class Check (Optional/Contextual fields)
    class_code = data.get('class_target_code')
    if not validate_review_category(data['category'], class_code):
        return RETURN_CODES['ERROR']
    
    # 4. Class Reference Check (FK)
    if class_code is not None:
        if not isinstance(class_code, int) or class_code <= 0:
            return RETURN_CODES['ERROR']
            
        # Substituir retrieve_class(class_code)
        if find_entity_by_pk('classes', class_code, 'code') is None:
             return RETURN_CODES['ERROR'] # Class target must exist if specified

    # 5. Anonymous Check (Mandatory booleano field)
    if data['is_anonymous'] not in [True, False]: # Using standard Python booleans
        return RETURN_CODES['ERROR']
        
    return RETURN_CODES['SUCCESS']

# --- Public Access Functions (CRUD Review) ---

def create_review(data: Dict) -> int:
    """
    Objective: Register a new review (avaliação) in the system and update associated entities.
    Description: Generates a unique ID, validates content/references, persists the review, 
                 and orchestrates the update of the Student (author) and Professor(es) references.
    Coupling:
        :param data (Dict): Review data (author, title, comment, optional stars/class/category).
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: validate_review(data) == SUCCESS.
        Output Assertions: A new review record exists in the database with a unique 'id_aval'.
    User Interface: Log "Creating review by student {enrollment}" (Internal Log).
    """

    from src.modules.student import create_student_review
    from src.modules.professor import create_professor_review
    from src.modules.classes import associate_review_to_class
    from src.persistence import find_entity_by_pk

    if validate_review(data) != RETURN_CODES['SUCCESS']:
        print("Log: Failed to create review. Invalid or incomplete data.")
        return RETURN_CODES['ERROR']
        
    new_id = _generate_review_id()
    
    # 1. Set up review_record register
    review_record = {
        'id_aval': new_id,
        'student_enrollment': data['student_enrollment'],
        'date_time': datetime.datetime.now().isoformat(),
        'title': data['title'],
        'comment': data['comment'],
        'category': data['category'],
        'is_anonymous': data['is_anonymous'],
        'stars': data.get('stars'),
        'class_target_code': data.get('class_target_code'),
        'mentions': data.get('mentions', '')
    }
    
    # 2. Persist register (Repo Review)
    ret_code = repo_create_review(review_record)
    if ret_code != RETURN_CODES['SUCCESS']:
        print("Log: Failed to persist review record.")
        return RETURN_CODES['ERROR']
        
    # 3. Orchestration After Creation (Update References in Other Entities)
    
    # 3.1. Update Student (Author)
    author_enrollment = review_record['student_enrollment']
    # Creates a reference of the review in the student's list of reviews.
    create_student_review(author_enrollment, {'id_aval': new_id}) 
    
    # 3.2. Update Professors and Classes (if required)
    class_code = review_record.get('class_target_code')
    
    if class_code is not None:
        # Tries to search for the Class Turma 
        class_record = find_entity_by_pk('classes', class_code, 'code')
        
        if class_record:
            # Maps the Review to Class
            associate_review_to_class(class_code, new_id)

            # Maps the Review to Class Professors'
            for prof_id in class_record.get('professors_ids', []):
                # create_professor_review function only needs professor's ID and review's ID
                create_professor_review(prof_id, {'id_aval': new_id})

    print(f"Log: Review {new_id} created and associated with Author, Class, and Professor(es).")
    return RETURN_CODES['SUCCESS']

def retrieve_review(review_id: int) -> Union[Dict, None]:
    """
    Objective: Find a review record using its unique ID.
    Description: Corresponds to busca_aval.
    Coupling:
        :param review_id (int): The review's ID.
        :return Union[Dict, None]: The review dictionary or None (Erro).
    Coupling Conditions:
        Input Assertions: review_id must be a valid positive integer.
        Output Assertions: If returned, the review exists in the database.
    User Interface: (Internal Log).
    """
    if not isinstance(review_id, int) or review_id <= 0:
        return None
        
    review_record = repo_retrieve_review(review_id)
    
    if review_record is None:
        print(f"User Message: Review with ID {review_id} not found.")
    return review_record

def retrieve_all_reviews(student_enrollment: Union[int, None] = None) -> List[Dict]:
    """
    Objective: Retrieve the entire list of registered reviews, optionally filtered by author.
    Description: Corresponds to busca_todas_avals (with optional matricula_aluno_avalliador).
    Coupling:
        :param student_enrollment (Union[int, None]): Optional enrollment ID to filter by author.
        :return List[Dict]: A list containing matching review dictionaries.
    Coupling Conditions:
        Input Assertions: student_enrollment is None or a valid positive integer.
        Output Assertions: Returns a list (possibly empty) containing valid review records.
    User Interface: (None).
    """
    if student_enrollment is None:
        return database['reviews']
        
    # Filter by author
    return [review for review in database['reviews'] if review['student_enrollment'] == student_enrollment]


def update_review(review_id: int, new_data: Dict) -> int:
    """
    Objective: Update one or more fields of an existing review record.
    Description: Corresponds to atualiza_aval. Only allows updating non-PK fields.
    Coupling:
        :param review_id (int): The review's ID.
        :param new_data (Dict): Dictionary containing the fields to update (title, comment, stars, category, etc.).
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: review_id is valid. new_data combined with existing data passes validate_review.
        Output Assertions: If SUCCESS, the review record reflects the changes in new_data.
    User Interface: (Internal Log).
    """
    review_record = repo_retrieve_review(review_id)
    
    if review_record is None:
        return RETURN_CODES['ERROR'] # Review not found
        
    # Validation of the resulting review object
    temp_data = review_record.copy()
    temp_data.update(new_data)
    
    if validate_review(temp_data) != RETURN_CODES['SUCCESS']:
        return RETURN_CODES['ERROR'] # Invalid resulting data

    # Success
    for key, value in new_data.items():
        if key != 'id_aval': # ID (PK) cannot be changed
            review_record[key] = value
            
    return RETURN_CODES['SUCCESS']
    
def delete_review(review_id: int) -> int:
    """
    Objective: Permanently remove a review record from the database.
    Description: Corresponds to deleta_aval. Should be coupled with removal of references in Student/Professor/Class modules.
    Coupling:
        :param review_id (int): The review's ID.
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: review_id is a valid positive integer.
        Output Assertions: If SUCCESS, the review record is removed from database['reviews'].
    User Interface: (Internal Log).
    """
    
    from src.modules.student import delete_student_review 
    from src.modules.professor import remove_review_reference_from_professor
    from src.modules.classes import remove_review_reference_from_class
    from src.persistence import find_entity_by_pk

    review_record = repo_retrieve_review(review_id)
    
    if review_record is None:
        return RETURN_CODES['ERROR'] # Review not found
        
    # --- ORQUESTRAÇÃO DE LIMPEZA DE REFERÊNCIAS ---
    
    # 1. Limpar referência do Aluno (Autor)
    author_enrollment = review_record['student_enrollment']
    delete_student_review(author_enrollment, review_id)
    
    # 2. Limpar referências de Professor e Turma (se houver alvo)
    class_code = review_record.get('class_target_code')
    
    if class_code is not None:
        # Limpar referência na Turma
        remove_review_reference_from_class(class_code, review_id)
        
        # Limpar referências nos Professores associados à Turma
        class_record = find_entity_by_pk('classes', class_code, 'code')
        if class_record:
            for prof_id in class_record.get('professors_ids', []):
                remove_review_reference_from_professor(prof_id, review_id)

    # --- DELEÇÃO DO REGISTRO PRINCIPAL ---
    try:
        database['reviews'].remove(review_record)
        return RETURN_CODES['SUCCESS']
    except ValueError:
        return RETURN_CODES['ERROR']