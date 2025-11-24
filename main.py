"""
Main Controller Module.
Objective: Orchestrates the system lifecycle: TDD verification, data loading, user interaction, and data persistence.
Requirement: The system must validate integrity (tests) before running and ensure data is saved upon exit.
"""
import unittest
import sys
from src.persistence import initialize_db, save_db, set_test_mode, set_prod_mode
from src.shared import RETURN_CODES
from interface import run_frontend

def run_all_unit_tests() -> bool:
    """
    Objective: Execute the complete suite of unit tests to ensure system integrity.
    Description: Switches the persistence layer to 'Test Mode' to protect production data, discovers tests in the 'tests/' directory, and runs them using Python's unittest framework.
    Coupling:
        :return bool: True if ALL tests pass, False otherwise.
    Coupling Conditions:
        Input Assertions: The 'tests' directory exists and contains valid 'test_*.py' files.
        Output Assertions: Returns True only if results.wasSuccessful() is True. Returns False if any failure or error occurs.
    User Interface: Prints test execution details and final summary (PASSED/FAILED) to stdout.
    """
    print("\n--- Running All Unit Tests (TDD Check) ---")
    
    # 1. Enable Test Mode (Protects real data)
    set_test_mode()

    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    
    # EXECUTE ONCE
    results = runner.run(suite)

    # 2. Disable Test Mode (Back to real data)
    set_prod_mode()

    print("--- Test Execution Summary ---")
    print(f"Ran {results.testsRun} tests.")
    
    if results.wasSuccessful():
        print("Test Result: ✔ ALL TESTS PASSED.")
        return True
    else:
        print(f"Test Result: FAILED (Failures={len(results.failures)}, Errors={len(results.errors)})")
        return False

def main():
    """
    Objective: Main entry point of the application.
    Description: Controls the execution flow: 1. Runs Tests (Aborts if failed), 2. Loads Data, 3. Starts Frontend CLI, 4. Saves Data on exit.
    Coupling:
        :return: None.
    Coupling Conditions:
        Input Assertions: None.
        Output Assertions: System exits with code 1 if tests fail. Data is persisted if application closes normally.
    User Interface: Logs system status messages (Start, Error, Save, Exit).
    """
    print("--- Filhos da PUC System ---")
    
    # 1. Run Unit Tests (TDD requirement)
    if not run_all_unit_tests():
        print("\nFATAL ERROR: Unit tests failed. Cannot start application until fixes are made.")
        sys.exit(1) # Sai com código de erro se os testes falharem

    # 2. Initialize Database (Load JSON)
    if initialize_db() != RETURN_CODES['SUCCESS']:
        print("\nERROR: Failed to initialize the database. Exiting.")
        return

    # 3. Run Application Interface
    run_frontend()

    # 4. Save Database (Persist JSON)
    print("\n--- Saving data and exiting system... ---")
    if save_db() == RETURN_CODES['SUCCESS']:
        print("Data saved successfully.")
    else:
        print("ERROR: Failed to save data.")

if __name__ == '__main__':
    main()