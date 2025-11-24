"""
Module responsible for loading and saving data (JSON).
Requirement: The system must persist data, not just in memory.
"""

import json
import os
from src.shared import RETURN_CODES
from typing import Union, Dict, List

__all__ = ['initialize_db', 'save_db', 'database', 'find_entity_by_pk', 'set_test_mode', 'set_prod_mode']

DB_FILE = os.path.join('data', 'db.json')

# Global in-memory structure (Lists of Dictionaries)
database = {
    'students': [],
    'professors': [],
    'subjects': [],
    'classes': [],
    'reviews': []
}

def initialize_db():
    """
    Objective: Initialize the system's persistence layer by loading data into memory.
    Description: Corresponds to inicializa_banco. It handles the creation of the storage directory/file if they don't exist and manages empty files to prevent JSON errors.
    Coupling:
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: DB_FILE path is valid (OS handled).
        Output Assertions: The global 'database' variable is populated with data from disk OR initialized with empty lists if the file is new/empty.
    User Interface: Log warnings if file is empty or errors if loading fails.
    """
    global database
    
    # Create folder if it doesn't exist
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    
    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} not found. Starting with an empty database.")
        save_db() # Create the empty file
        return RETURN_CODES['SUCCESS']

    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            # Novo: Verifica se o arquivo está vazio antes de tentar carregar JSON
            content = f.read().strip()
            if not content:
                print(f"Warning: Database file {DB_FILE} is empty. Initializing empty structure.")
                return RETURN_CODES['SUCCESS']

            loaded_data = json.loads(content)
            database.update(loaded_data)
        return RETURN_CODES['SUCCESS']
    except Exception as e:
        print(f"Error loading database: {e}")
        return RETURN_CODES['ERROR']

def save_db():
    """
    Objective: Persist the current state of the memory to the file system.
    Description: Corresponds to salva_banco. Dumps the global 'database' dictionary into a JSON file.
    Coupling:
        :return int: SUCCESS (0) or ERROR (1).
    Coupling Conditions:
        Input Assertions: Global 'database' must be a serializable dictionary.
        Output Assertions: The file at DB_FILE contains the exact JSON representation of 'database'.
    User Interface: Log errors if write permission fails.
    """
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=4, ensure_ascii=False)
        return RETURN_CODES['SUCCESS']
    except Exception as e:
        print(f"Error saving database: {e}")
        return RETURN_CODES['ERROR']
    
def find_entity_by_pk(entity_name: str, pk_value: Union[int, str], pk_field: str) -> Union[Dict, None]:
    """
    Objective: Searches for an entity (subject, professor, etc.) by its primary key (PK) 
                in the global database.
    Description: Provides a generic repository search to break circular dependencies.
    Coupling:
        :param entity_name (str): The list name in the database dict (e.g., 'subjects', 'professors').
        :param pk_value (Union[int, str]): The primary key value to search for.
        :param pk_field (str): The primary key field name (e.g., 'code', 'id_aval', 'enrollment').
        :return Union[Dict, None]: The found dictionary entity or None.
    Coupling Conditions:
        Input Assertions: entity_name is a valid key in the database dict.
        Output Assertions: If a dictionary is returned, entity[pk_field] == pk_value.
    User Interface: (None)
    """
    global database
    if entity_name not in database:
        return None
        
    for entity in database[entity_name]:
        if entity.get(pk_field) == pk_value:
            return entity
    return None

# === Functions for testing === #
def set_test_mode():
    """
    Objective: Configure the persistence layer for the Testing Environment.
    Description: Redirects database operations to a temporary file ('test_db.json') to avoid corrupting production data during unit tests.
    Coupling:
        :return: None.
    Coupling Conditions:
        Input Assertions: None.
        Output Assertions: Global DB_FILE points to 'data/test_db.json'.
    User Interface: Log "Switched to TEST mode".
    """
    global DB_FILE
    DB_FILE = os.path.join('data', 'test_db.json')
    print("Persistence: Switched to TEST mode (data/test_db.json)")

def set_prod_mode():
    """
    Objective: Configure the persistence layer for the Production Environment.
    Description: Redirects database operations back to the main file ('db.json').
    Coupling:
        :return: None.
    Coupling Conditions:
        Input Assertions: None.
        Output Assertions: Global DB_FILE points to 'data/db.json'.
    User Interface: Log "Switched to PRODUCTION mode".
    """
    global DB_FILE
    DB_FILE = os.path.join('data', 'db.json')
    print("Persistence: Switched to PRODUCTION mode (data/db.json)")