import unittest
from src.modules.student import (
    create_student, retrieve_student, retrieve_all_students, 
    update_student_course, update_student, delete_student, 
    validate_student, create_student_subject, student_took_subject,
    retrieve_student_subjects, update_student_subjects, delete_student_subject
)
from src.persistence import database, initialize_db, save_db
from src.shared import RETURN_CODES
from src.domains.course import COURSE_LIST

# --- Fixtures (Dados de Teste) ---
VALID_ENROLLMENT = 2310488 # Baseado no documento 
NON_EXISTENT_ENROLLMENT = 9999999
VALID_COURSE = 'CIEN_COMP'
INVALID_COURSE = 'ENGENHARIA_MAGIA'
VALID_SUBJECT_CODE_1 = 1301
VALID_SUBJECT_CODE_2 = 1302

VALID_STUDENT_DATA = {
    'enrollment': VALID_ENROLLMENT,
    'username': 'gabrielpires',
    'password': 'safePassword123',
    'name': 'Gabriel Valente Ferreira Pires',
    'institutional_email': 'gabriel.pires@puc-rio.br',
    'course': VALID_COURSE
}

class TestStudent(unittest.TestCase):
    
    def setUp(self):
        """Prepara um estado limpo para cada teste, zerando o banco de dados de alunos."""
        database['students'] = []
        # Inicializa para garantir que a estrutura base exista
        initialize_db()

    # --- Testes de Criação (create_student) ---
    
    def test_01_create_student_t1_success(self):
        """T1: Retorna SUCESSO e insere o aluno no banco."""
        print("\nCaso de Teste 01 - Criação com Sucesso")
        ret_code = create_student(VALID_STUDENT_DATA)
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS']) # Espera 1 (Sucesso) 
        self.assertEqual(len(database['students']), 1)
        self.assertEqual(database['students'][0]['enrollment'], VALID_ENROLLMENT)

    def test_02_create_student_t2_failure_pk_exists(self):
        """T2: Retorna ERRO se a matrícula já existir."""
        print("\nCaso de Teste 02 - Falha: Matrícula já existe (PK).")
        create_student(VALID_STUDENT_DATA)
        
        # Tenta inserir novamente com a mesma matrícula
        data_duplicate = VALID_STUDENT_DATA.copy()
        data_duplicate['username'] = 'another_user'
        ret_code = create_student(data_duplicate)
        
        self.assertEqual(ret_code, RETURN_CODES['ERROR']) # Espera 0 (Falha) 
        self.assertEqual(len(database['students']), 1) # Não deve ter aumentado

    def test_03_create_student_t4_failure_incomplete_data(self):
        """T4: Retorna ERRO se houver dados incompletos (campo obrigatório nulo)."""
        print("\nCaso de Teste 03 - Falha: Dados incompletos (Falta 'name').")
        data_incomplete = VALID_STUDENT_DATA.copy()
        del data_incomplete['name']
        
        ret_code = create_student(data_incomplete)
        self.assertEqual(ret_code, RETURN_CODES['ERROR']) # Espera 0 (Falha) 
        self.assertEqual(len(database['students']), 0)

    # --- Testes de Busca (retrieve_student) ---

    def test_04_retrieve_student_t1_success_found(self):
        """T1: Retorna o aluno com matrícula correspondente."""
        print("\nCaso de Teste 04 - Busca com Sucesso")
        create_student(VALID_STUDENT_DATA)
        student = retrieve_student(VALID_ENROLLMENT)
        self.assertIsNotNone(student) # Retorna Aluno 
        self.assertEqual(student['enrollment'], VALID_ENROLLMENT)

    def test_05_retrieve_student_t2_error_not_found(self):
        """T2: Retorna ERRO (None) para aluno não registrado."""
        print("\nCaso de Teste 05 - Busca com ERRO: Aluno não registrado")
        student = retrieve_student(NON_EXISTENT_ENROLLMENT)
        self.assertIsNone(student) # Retorna ERRO 

    def test_06_retrieve_student_t3_error_invalid_format(self):
        """T3: Retorna ERRO (None) para matrícula inválida (negativa)."""
        print("\nCaso de Teste 06 - Busca com ERRO: Formatação errada da matrícula")
        student = retrieve_student(-1)
        self.assertIsNone(student) # Retorna ERRO 

    # --- Testes de Troca de Curso (update_student_course) ---

    def test_07_update_course_t1_success(self):
        """T1: Retorna SUCESSO e troca o curso."""
        print("\nCaso de Teste 07 - Troca de Curso com Sucesso")
        create_student(VALID_STUDENT_DATA)
        new_course = 'ENG_COMP' # Outro curso válido
        ret_code = update_student_course(VALID_ENROLLMENT, new_course)
        
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS']) # Espera 1 (Sucesso) 
        updated_student = retrieve_student(VALID_ENROLLMENT)
        self.assertEqual(updated_student['course'], new_course)

    def test_08_update_course_t3_error_invalid_course(self):
        """T3: Retorna ERRO para curso em formatação errada ou inválido."""
        print("\nCaso de Teste 08 - Falha: Curso em formatação errada")
        create_student(VALID_STUDENT_DATA)
        ret_code = update_student_course(VALID_ENROLLMENT, INVALID_COURSE)
        self.assertEqual(ret_code, RETURN_CODES['ERROR']) # Espera 0 (Falha) 
        
        # Verifica se o curso não foi alterado
        updated_student = retrieve_student(VALID_ENROLLMENT)
        self.assertEqual(updated_student['course'], VALID_COURSE)

    # --- Testes de Atualização Genérica (update_student) ---

    def test_09_update_student_t1_success(self):
        """T1: Retorna SUCESSO e atualiza um campo não-PK."""
        print("\nCaso de Teste 09 - Atualização Genérica com Sucesso")
        create_student(VALID_STUDENT_DATA)
        new_data = {'username': 'gpires_novo', 'name': 'G. Pires'}
        ret_code = update_student(VALID_ENROLLMENT, new_data)
        
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS']) # Espera 1 (Sucesso) 
        updated_student = retrieve_student(VALID_ENROLLMENT)
        self.assertEqual(updated_student['username'], 'gpires_novo')
        
    def test_10_update_student_t3_error_non_existent(self):
        """T3: Retorna ERRO para matrícula inexistente."""
        print("\nCaso de Teste 10 - Falha: Matrícula inexistente")
        new_data = {'username': 'gpires_novo'}
        ret_code = update_student(NON_EXISTENT_ENROLLMENT, new_data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR']) # Espera 0 (Falha) 
        
    def test_11_update_student_t4_error_invalid_data(self):
        """T4: Retorna ERRO para dados inválidos (ex: nome vazio após update)."""
        print("\nCaso de Teste 11 - Falha: Dados inválidos no update (nome vazio)")
        create_student(VALID_STUDENT_DATA)
        invalid_data = {'name': ''} # Nome não pode ser vazio
        ret_code = update_student(VALID_ENROLLMENT, invalid_data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR']) # Espera 0 (Falha) 
        
        # Verifica se o campo name não foi alterado
        self.assertEqual(retrieve_student(VALID_ENROLLMENT)['name'], VALID_STUDENT_DATA['name'])

    # --- Testes de Deleção (delete_student) ---

    def test_12_delete_student_t1_success(self):
        """T1: Retorna SUCESSO e deleta o aluno."""
        print("\nCaso de Teste 12 - Deleção com Sucesso")
        create_student(VALID_STUDENT_DATA)
        self.assertEqual(len(database['students']), 1)
        ret_code = delete_student(VALID_ENROLLMENT)
        
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS']) # Espera 1 (Sucesso) 
        self.assertEqual(len(database['students']), 0)
        self.assertIsNone(retrieve_student(VALID_ENROLLMENT))
        
    def test_13_delete_student_t3_error_non_existent(self):
        """T3: Retorna ERRO para aluno não existente."""
        print("\nCaso de Teste 13 - Falha: Aluno não existe")
        ret_code = delete_student(NON_EXISTENT_ENROLLMENT)
        self.assertEqual(ret_code, RETURN_CODES['ERROR']) # Espera 0 (Erro) 

    # --- Testes de Associação de Matérias (cria_materia_aluno, aluno_fez_materia) ---
    
    def test_14_create_student_subject_t1_success(self):
        """T1: Retorna SUCESSO e associa a matéria ao aluno."""
        print("\nCaso de Teste 14 - Associa Matéria com Sucesso")
        create_student(VALID_STUDENT_DATA)
        ret_code = create_student_subject(VALID_ENROLLMENT, VALID_SUBJECT_CODE_1)
        
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS']) # Espera 1 (Sucesso) 
        self.assertIn(VALID_SUBJECT_CODE_1, retrieve_student(VALID_ENROLLMENT)['subjects'])
        
    def test_15_student_took_subject_t1_success(self):
        """T1: Retorna SUCESSO quando aluno fez a matéria."""
        print("\nCaso de Teste 15 - Verifica Matéria: Fez")
        create_student(VALID_STUDENT_DATA)
        create_student_subject(VALID_ENROLLMENT, VALID_SUBJECT_CODE_1)
        
        ret_code = student_took_subject(VALID_ENROLLMENT, VALID_SUBJECT_CODE_1)
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS']) # Espera 1 (Sucesso) 

    def test_16_student_took_subject_t2_error_not_took(self):
        """T2: Retorna ERRO quando aluno não fez a matéria."""
        print("\nCaso de Teste 16 - Verifica Matéria: Não Fez")
        create_student(VALID_STUDENT_DATA)
        
        ret_code = student_took_subject(VALID_ENROLLMENT, VALID_SUBJECT_CODE_1)
        self.assertEqual(ret_code, RETURN_CODES['ERROR']) # Espera 0 (Erro) 
        
    def test_17_retrieve_student_subjects_t1_success(self):
        """T1: Retorna lista de matérias cursadas."""
        print("\nCaso de Teste 17 - Busca lista de Matérias")
        create_student(VALID_STUDENT_DATA)
        create_student_subject(VALID_ENROLLMENT, VALID_SUBJECT_CODE_1)
        create_student_subject(VALID_ENROLLMENT, VALID_SUBJECT_CODE_2)
        
        subjects = retrieve_student_subjects(VALID_ENROLLMENT)
        self.assertIsInstance(subjects, list)
        self.assertIn(VALID_SUBJECT_CODE_1, subjects) # Retorna Matérias de acordo com a matrícula do aluno 
        self.assertEqual(len(subjects), 2)
        
    def test_18_update_student_subjects_t1_success(self):
        """T1: Atualiza o código de matéria globalmente para um aluno."""
        print("\nCaso de Teste 18 - Atualização Global de Código de Matéria")
        create_student(VALID_STUDENT_DATA)
        create_student_subject(VALID_ENROLLMENT, 500)
        
        ret_code = update_student_subjects(500, 600)
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS']) # Espera 1 (Sucesso) 
        self.assertNotIn(500, retrieve_student_subjects(VALID_ENROLLMENT))
        self.assertIn(600, retrieve_student_subjects(VALID_ENROLLMENT))
        
    def test_19_update_student_subjects_t2_error_old_code_not_found(self):
        """T2: Retorna ERRO se o código antigo não for encontrado (em nenhum aluno)."""
        print("\nCaso de Teste 19 - Falha: Código antigo não encontrado")
        create_student(VALID_STUDENT_DATA)
        # Nenhuma matéria associada, código 500 não existe
        ret_code = update_student_subjects(500, 600)
        self.assertEqual(ret_code, RETURN_CODES['ERROR']) # Espera 0 (Erro) 


# Para executar os testes, similar ao exemplo do PDF
if __name__ == '__main__':
    # Você precisará configurar o PYTHONPATH ou o __init__.py corretamente
    # para que as importações 'backend.modules.student' funcionem.
    unittest.main(argv=['first-arg-is-ignored'], exit=False)