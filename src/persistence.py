"""
Module responsible for loading and saving data (JSON).
Requirement: The system must persist data, not just in memory[cite: 209].
"""

import json
import os
from src.shared import RETURN_CODES

__all__ = ['initialize_db', 'save_db', 'database']

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
    """Loads the JSON into memory or creates an empty structure."""
    global database
    
    # Create folder if it doesn't exist
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    
    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} not found. Starting with an empty database.")
        save_db() # Create the empty file
        return RETURN_CODES['SUCCESS']

    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            # Update the global dict
            database.update(loaded_data)
        return RETURN_CODES['SUCCESS']
    except Exception as e:
        print(f"Error loading database: {e}")
        return RETURN_CODES['ERROR']

def save_db():
    """Persists the current memory state to the JSON file."""
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