import unittest
from src.modules.subject import (
    create_subject, retrieve_subject, retrieve_all_subjects, 
    update_subject, delete_subject, validate_subject,
    exists_subject
)
from src.persistence import database, initialize_db, save_db
from src.shared import RETURN_CODES

# Subject fixture (template data)
VALID_SUBJECT_DATA = {
    'code': 101,
    'credits': 4,
    'name': 'Modular Programming',
    'description': 'Advanced programming concepts.'
}

# Sorry Flavio, we knew classes were prohibited but we used them here in order to use unittest library :(
class TestSubject(unittest.TestCase):
    
    def setUp(self):
        """Prepares a clean state."""
        initialize_db()          # 1. Load DB first
        database['subjects'] = [] # 2. THEN wipe it clean
        save_db()
        
    def tearDown(self):
        """Ensures the database is clean after each test."""
        database['subjects'] = []

    # --- Test Case 01: create_subject ---
    
    def test_01_create_subject_ok_return_success(self):
        """T1: Returns SUCCESS (0) when all parameters are passed correctly[cite: 619]."""
        print("\nTest Case 01 - Create subject with success (return code check)")
        ret_code = create_subject(VALID_SUBJECT_DATA)
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])
        self.assertEqual(len(database['subjects']), 1)
        self.assertDictEqual(database['subjects'][0], VALID_SUBJECT_DATA)
        
    def test_02_create_subject_nok_existing_code(self):
        """T3: Returns ERROR (1) if the primary key (code) already exists[cite: 621]."""
        print("\nTest Case 02 - Impede insertion if code exists")
        create_subject(VALID_SUBJECT_DATA)
        
        # Try to insert again with the same code
        duplicate_data = VALID_SUBJECT_DATA.copy()
        ret_code = create_subject(duplicate_data)
        
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        self.assertEqual(len(database['subjects']), 1) # Must remain 1
        
    def test_03_create_subject_nok_invalid_data(self):
        """T4: Returns ERROR (1) for invalid data (e.g., negative credits)[cite: 625]."""
        print("\nTest Case 03 - Invalid data (negative credits)")
        invalid_data = VALID_SUBJECT_DATA.copy()
        invalid_data['credits'] = -1
        invalid_data['code'] = 102 # Use a unique code to avoid T3 conflict
        
        ret_code = create_subject(invalid_data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        self.assertEqual(len(database['subjects']), 0)
        
    def test_04_create_subject_nok_null_data(self):
        """T2: Returns ERROR (1) if the data dictionary/pointer is NULL (None)[cite: 620]."""
        print("\nTest Case 04 - Null data")
        ret_code = create_subject(None)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])

    # --- Test Case 05: retrieve_subject ---
    
    def test_05_retrieve_subject_ok_found(self):
        """T1: Returns the subject dictionary for a corresponding code[cite: 628]."""
        print("\nTest Case 05 - Retrieve subject found")
        create_subject(VALID_SUBJECT_DATA)
        subject = retrieve_subject(VALID_SUBJECT_DATA['code'])
        self.assertIsNotNone(subject)
        self.assertEqual(subject['name'], 'Modular Programming')
        
    def test_06_retrieve_subject_nok_not_found(self):
        """T2: Returns NULL (None) for a non-existent code[cite: 629]."""
        print("\nTest Case 06 - Retrieve subject not found")
        subject = retrieve_subject(999) # Code 999 does not exist
        self.assertIsNone(subject)
        
    def test_07_retrieve_subject_nok_invalid_code(self):
        """T3: Returns NULL (None) for an invalid parameter (e.g., negative code)[cite: 630]."""
        print("\nTest Case 07 - Retrieve subject with invalid code")
        subject = retrieve_subject(-101) 
        self.assertIsNone(subject)
        
    # --- Test Case 08: update_subject ---
    
    def test_08_update_subject_ok_success(self):
        """T1: Returns SUCCESS (0) and updates fields with valid new data[cite: 633]."""
        print("\nTest Case 08 - Update subject with success")
        create_subject(VALID_SUBJECT_DATA)
        new_data = {
            'name': 'Advanced Modular Programming',
            'credits': 6 
        }
        ret_code = update_subject(VALID_SUBJECT_DATA['code'], new_data)
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])
        
        updated_subject = retrieve_subject(VALID_SUBJECT_DATA['code'])
        self.assertEqual(updated_subject['name'], 'Advanced Modular Programming')
        self.assertEqual(updated_subject['credits'], 6)

    def test_09_update_subject_nok_not_found(self):
        """T2: Returns ERROR (1) if the code is not registered[cite: 634]."""
        print("\nTest Case 09 - Update non-existent subject")
        new_data = {'name': 'New Name'}
        ret_code = update_subject(999, new_data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])

    def test_10_update_subject_nok_invalid_new_data(self):
        """T4: Returns ERROR (1) if the new data is invalid."""
        print("\nTest Case 10 - Update with invalid new data (negative credits)")
        
        # NUCLEAR RESET: WIPE AND RE-ADD
        database['subjects'] = []
        database['subjects'].append({
            'code': 101,
            'credits': 4,  # Explicitly 4
            'name': 'Modular Programming',
            'description': 'Desc'
        })
        
        # Verify state BEFORE action
        self.assertEqual(retrieve_subject(101)['credits'], 4)

        invalid_data = {'credits': -5}
        ret_code = update_subject(101, invalid_data) # Use explicit code 101
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        
        # Verify state AFTER action
        self.assertEqual(retrieve_subject(101)['credits'], 4)
        
    # --- Test Case 11: delete_subject ---

    def test_11_delete_subject_ok_success(self):
        """T1: Returns SUCCESS (0) and removes the subject[cite: 639]."""
        print("\nTest Case 11 - Delete subject with success")
        create_subject(VALID_SUBJECT_DATA)
        ret_code = delete_subject(VALID_SUBJECT_DATA['code'])
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])
        self.assertIsNone(retrieve_subject(VALID_SUBJECT_DATA['code']))

    def test_12_delete_subject_nok_not_found(self):
        """T2: Returns ERROR (1) if the subject is not registered[cite: 640]."""
        print("\nTest Case 12 - Delete non-existent subject")
        ret_code = delete_subject(999)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        
    def test_13_delete_subject_nok_invalid_code(self):
        """T3: Returns ERROR (1) if the code parameter is invalid (e.g., negative)[cite: 644]."""
        print("\nTest Case 13 - Delete with invalid code")
        ret_code = delete_subject(-101)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        
    # --- Test Case 14: retrieve_all_subjects ---

    def test_14_retrieve_all_subjects_ok_multiple(self):
        """Returns all registered subjects."""
        print("\nTest Case 14 - Retrieve all subjects (multiple)")
        create_subject(VALID_SUBJECT_DATA)
        create_subject({'code': 102, 'credits': 2, 'name': 'Ethics', 'description': ''})
        
        all_subjects = retrieve_all_subjects()
        self.assertEqual(len(all_subjects), 2)
        self.assertTrue(any(s['code'] == 101 for s in all_subjects))
        self.assertTrue(any(s['code'] == 102 for s in all_subjects))

# To run the tests, add this block:
if __name__ == '__main__':
    unittest.main()