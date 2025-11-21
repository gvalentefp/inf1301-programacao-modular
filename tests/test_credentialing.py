import unittest
from src.modules.credentialing import (
    register_student_account, authenticate_user
)
from src.modules.student import retrieve_student
from src.persistence import database, initialize_db
from src.shared import RETURN_CODES

# --- Fixtures (Dados de Teste) ---
VALID_ENROLLMENT = 1234567
INVALID_ENROLLMENT = 9999999
VALID_PASSWORD = 'safePassword123'
INVALID_PASSWORD = 'wrongPassword'
VALID_COURSE = 'INF' # Usando um curso válido existente no módulo domain/course (ex: INF ou CIEN_COMP)
VALID_EMAIL = 'aluno@puc-rio.br'
INVALID_EMAIL = 'aluno@gmail.com' # Email não institucional

VALID_REGISTRATION_DATA = {
    'enrollment': VALID_ENROLLMENT,
    'username': 'testuser',
    'password': VALID_PASSWORD,
    'name': 'Test User Name',
    'institutional_email': VALID_EMAIL,
    'course': VALID_COURSE
}

class TestCredentialing(unittest.TestCase):
    
    def setUp(self):
        """Prepara um estado limpo, zerando o banco de dados de alunos."""
        database['students'] = []
        initialize_db()

    # --- Testes de Registro (register_student_account) ---
    
    def test_01_register_success(self):
        """Testa o registro com sucesso: Validação de dados e vínculo institucional OK."""
        print("\nCaso de Teste 01 - Registro de Conta com Sucesso")
        ret_code = register_student_account(VALID_REGISTRATION_DATA)
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])
        self.assertIsNotNone(retrieve_student(VALID_ENROLLMENT))
        
    def test_02_register_failure_invalid_email(self):
        """Testa falha: E-mail não institucional (vínculo falho)."""
        print("\nCaso de Teste 02 - Falha: E-mail não institucional.")
        data = VALID_REGISTRATION_DATA.copy()
        data['institutional_email'] = INVALID_EMAIL
        ret_code = register_student_account(data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        self.assertIsNone(retrieve_student(VALID_ENROLLMENT))

    def test_03_register_failure_incomplete_data(self):
        """Testa falha: Dados incompletos (validação de Student falha)."""
        print("\nCaso de Teste 03 - Falha: Dados incompletos.")
        data = VALID_REGISTRATION_DATA.copy()
        del data['name']
        ret_code = register_student_account(data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])

    def test_04_register_failure_pk_conflict(self):
        """Testa falha: Matrícula já existente (conflito PK repassado do módulo Student)."""
        print("\nCaso de Teste 04 - Falha: Matrícula já existe.")
        register_student_account(VALID_REGISTRATION_DATA)
        # Tenta registrar novamente (enrollment já existe)
        ret_code = register_student_account(VALID_REGISTRATION_DATA)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])

    # --- Testes de Autenticação (authenticate_user) ---

    def test_05_authenticate_success(self):
        """Testa login com credenciais válidas."""
        print("\nCaso de Teste 05 - Autenticação com Sucesso")
        register_student_account(VALID_REGISTRATION_DATA)
        
        user_or_error = authenticate_user(VALID_ENROLLMENT, VALID_PASSWORD)
        self.assertIsInstance(user_or_error, dict)
        self.assertEqual(user_or_error['enrollment'], VALID_ENROLLMENT)
        
    def test_06_authenticate_failure_wrong_password(self):
        """Testa login com senha incorreta."""
        print("\nCaso de Teste 06 - Falha: Senha Incorreta")
        register_student_account(VALID_REGISTRATION_DATA)
        
        user_or_error = authenticate_user(VALID_ENROLLMENT, INVALID_PASSWORD)
        self.assertEqual(user_or_error, RETURN_CODES['ERROR'])
        
    def test_07_authenticate_failure_non_existent_enrollment(self):
        """Testa login com matrícula não registrada."""
        print("\nCaso de Teste 07 - Falha: Matrícula Inexistente")
        user_or_error = authenticate_user(INVALID_ENROLLMENT, VALID_PASSWORD)
        self.assertEqual(user_or_error, RETURN_CODES['ERROR'])


# Para executar os testes
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)