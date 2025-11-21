"""
Main Controller Module.
Objective: Orchestrates the system: loads persistent data, runs the application loop (frontend), and saves data upon exit.
Includes functionality to run all unit tests before launching the application interface.
"""
import unittest
import sys
from src.persistence import initialize_db, save_db
from src.shared import RETURN_CODES
from interface import run_frontend

def run_all_unit_tests() -> bool:
    """
    Runs all tests in the 'tests' directory using unittest discover.
    Returns True if all tests passed (OK), False otherwise (FAILED or ERROR).
    """
    print("\n--- Running All Unit Tests (TDD Check) ---")
    
    # Cria um TestLoader
    loader = unittest.TestLoader()
    # Descobre todos os testes no diretório 'tests'
    suite = loader.discover('tests', pattern='test_*.py')
    
    # Cria um TestRunner que executa os testes
    # O verbosity=2 mostra o nome de cada caso de teste (similar ao relatório)
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Redireciona temporariamente a saída para capturar o resultado
    # Isso é opcional, mas garante que a saída dos testes não interfira no frontend.
    
    # Para simplificar a rodagem, vamos usar o runner padrão:
    results = runner.run(suite)
    
    print("--- Test Execution Summary ---")
    # Imprime o resumo no formato solicitado (sem modificar a saída interna do unittest)
    print(f"Ran {results.testsRun} tests.")
    if results.wasSuccessful():
        print("Test Result: ✔ ALL TESTS PASSED.")
        return True
    else:
        # A saída de erro e falha detalhada é impressa pelo TextTestRunner.
        print(f"Test Result: FAILED (Failures={len(results.failures)}, Errors={len(results.errors)})")
        return False


def main():
    """
    Initializes the database, runs unit tests, starts the frontend interface, and saves data on termination.
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