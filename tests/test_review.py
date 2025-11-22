import unittest
import datetime
from src.modules.review import (
    create_review, retrieve_review, update_review, 
    delete_review, validate_review, retrieve_all_reviews,
)
from src.persistence import database, initialize_db, set_test_mode
from src.shared import RETURN_CODES
from src.modules.student import create_student
from src.modules.subject import create_subject
from src.modules.professor import create_professor
from src.modules.classes import create_class

# --- Fixtures (Dados de Teste) ---
VALID_REVIEW_ID = 1 
NON_EXISTENT_REVIEW_ID = 9999

# Mocks para FKs (devem existir no banco de dados para a validação passar)
MOCK_ENROLLMENT = 2310488
MOCK_CLASS_CODE = 101

# Simula uma data ISO formatada (necessário para a validação)
MOCK_DATE_TIME = datetime.datetime.now().isoformat()

VALID_REVIEW_DATA = {
    'student_enrollment': MOCK_ENROLLMENT,
    'title': 'INF1301 - Excellent Professor',
    'comment': 'Professor Flávio is clear and objective in his classes.',
    'date_time': MOCK_DATE_TIME,
    'category': 'PROF_GOOD', # Categoria que exige Class target
    'is_anonymous': False,
    'stars': 5,
    'class_target_code': MOCK_CLASS_CODE,
    'mentions': ''
}

class TestReview(unittest.TestCase):
    
    def setUp(self):
        """Prepara um estado limpo e insere dados MOCK."""
        set_test_mode()
        initialize_db()
        
        # Clean ALL tables
        database['reviews'] = []
        database['students'] = []
        database['classes'] = []
        database['subjects'] = []
        database['professors'] = []

        # Reset IDs manually if needed (safety net)
        import src.modules.review
        src.modules.review.next_review_id = 1 
        
        try:
             from src.modules.review import next_review_id
             next_review_id = 1
        except ImportError: pass

        # --- Create the Environment Chain ---
        # 1. Author (Student)
        create_student({
            'enrollment': MOCK_ENROLLMENT, 'username': 'author', 'name': 'Author', 
            'password': '123', 'institutional_email': 'a@puc-rio.br', 'course': 'CIEN_COMP'
        })
        
        # 2. Subject
        create_subject({'code': 1301, 'credits': 4, 'name': 'Subject', 'description': 'Desc'})
        
        # 3. Professor (ID 1)
        create_professor({'name': 'Prof A', 'department': 'INF'})

        # 4. Class (Code 101) - Needs Subject 1301 and Prof 1
        database['classes'].append({
            'code': MOCK_CLASS_CODE, # 101
            'subject_code': 1301, 
            'period': 20242, 
            'professors_ids': [1],
            'students_enrollments': [],
            'reviews_ids': []
        })
    # --- Testes de Validação (validate_review) ---
    def test_01_validate_review_t1_success(self):
        """T1: Retorna SUCESSO quando todos os campos e FKs são válidos."""
        print("\nCaso de Teste 01 - Validação com Sucesso (5 estrelas)")
        ret_code = validate_review(VALID_REVIEW_DATA)
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])
        
    def test_02_validate_review_t1_success_general_topic(self):
        """T1: Retorna SUCESSO com categoria geral (não exige class_target_code)."""
        print("\nCaso de Teste 02 - Validação com Sucesso (Tópico Geral)")
        data = VALID_REVIEW_DATA.copy()
        data['category'] = 'CANTEEN' # Categoria que não exige Class
        data['class_target_code'] = None 
        ret_code = validate_review(data)
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])

    def test_03_validate_review_error_invalid_stars(self):
        """Retorna ERRO se as estrelas estiverem fora do range 0-5."""
        print("\nCaso de Teste 03 - Validação Falha: Estrelas inválidas (6)")
        data = VALID_REVIEW_DATA.copy()
        data['stars'] = 6
        ret_code = validate_review(data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])

    def test_04_validate_review_error_class_required_but_null(self):
        """Retorna ERRO se a categoria exige Class, mas class_target_code é nulo."""
        print("\nCaso de Teste 04 - Validação Falha: Categoria exige Class, mas não fornecida.")
        data = VALID_REVIEW_DATA.copy()
        data['category'] = 'PROF_BAD' # Exige Class
        data['class_target_code'] = None
        ret_code = validate_review(data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        
    def test_05_validate_review_error_non_existent_author(self):
        """Retorna ERRO se o aluno avaliador (autor) não existir."""
        print("\nCaso de Teste 05 - Validação Falha: Autor inexistente.")
        data = VALID_REVIEW_DATA.copy()
        data['student_enrollment'] = 9999999 
        ret_code = validate_review(data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])

    def test_06_validate_review_error_empty_comment(self):
        """Retorna ERRO se o campo 'comment' for vazio."""
        print("\nCaso de Teste 06 - Validação Falha: Comentário vazio.")
        data = VALID_REVIEW_DATA.copy()
        data['comment'] = '' 
        ret_code = validate_review(data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])

    # --- Testes de Criação (create_review) ---

    def test_07_create_review_success(self):
        """Retorna SUCESSO e insere a avaliação com ID sequencial."""
        print("\nCaso de Teste 07 - Criação com Sucesso")
        ret_code = create_review(VALID_REVIEW_DATA)
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])
        self.assertEqual(len(database['reviews']), 1)
        self.assertEqual(database['reviews'][0]['id_aval'], VALID_REVIEW_ID)

    def test_08_create_review_error_invalid_data(self):
        """Retorna ERRO se a validação falhar antes da criação (ex: título muito longo)."""
        print("\nCaso de Teste 08 - Falha: Dados inválidos (Título longo).")
        data = VALID_REVIEW_DATA.copy()
        data['title'] = 'A' * 200 # Título excede MAX_TITLE_LENGHT (100)
        ret_code = create_review(data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        self.assertEqual(len(database['reviews']), 0)

    # --- Testes de Busca (retrieve_review e retrieve_all_reviews) ---

    def test_09_retrieve_review_found(self):
        """Retorna a avaliação com ID correspondente."""
        print("\nCaso de Teste 09 - Busca Avaliação por ID (Sucesso)")
        create_review(VALID_REVIEW_DATA)
        review = retrieve_review(VALID_REVIEW_ID)
        self.assertIsNotNone(review)
        self.assertEqual(review['student_enrollment'], MOCK_ENROLLMENT)

    def test_10_retrieve_all_reviews_filtered_by_author(self):
        """Retorna apenas as avaliações de um autor específico."""
        print("\nCaso de Teste 10 - Busca Todas Avaliações Filtrada por Autor")
        create_review(VALID_REVIEW_DATA)
        
        # Cria uma avaliação de outro autor
        database['students'].append({
            'enrollment': 123, 
            'name': 'Another Author',
            'reviews': [],   # <--- CRITICAL FIX
            'subjects': []   # <--- Good practice
        })

        data_other_author = VALID_REVIEW_DATA.copy()
        data_other_author['student_enrollment'] = 123
        data_other_author['stars'] = 1
        create_review(data_other_author) # ID 2
        
        # Filtra pelo autor original (MOCK_ENROLLMENT)
        reviews = retrieve_all_reviews(student_enrollment=MOCK_ENROLLMENT)
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]['id_aval'], VALID_REVIEW_ID)

    # --- Testes de Atualização (update_review) ---

    def test_11_update_review_success(self):
        """Retorna SUCESSO e atualiza um campo (estrelas)."""
        print("\nCaso de Teste 11 - Atualização com Sucesso")
        create_review(VALID_REVIEW_DATA)
        new_data = {'stars': 2, 'comment': 'Changed my mind, professor is okay.'}
        ret_code = update_review(VALID_REVIEW_ID, new_data)
        
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])
        updated_review = retrieve_review(VALID_REVIEW_ID)
        self.assertEqual(updated_review['stars'], 2)
        
    def test_12_update_review_error_invalid_new_data(self):
        """Retorna ERRO se os novos dados forem inválidos (e.g., categoria ruim)."""
        print("\nCaso de Teste 12 - Falha: Novos dados inválidos (Categoria inexistente).")
        create_review(VALID_REVIEW_DATA)
        invalid_data = {'category': 'NON_EXISTENT_CATEGORY'}
        ret_code = update_review(VALID_REVIEW_ID, invalid_data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        
        # Verifica se o campo não foi alterado
        self.assertEqual(retrieve_review(VALID_REVIEW_ID)['category'], 'PROF_GOOD')

    # --- Testes de Deleção (delete_review) ---

    def test_13_delete_review_success(self):
        """Retorna SUCESSO e remove a avaliação."""
        print("\nCaso de Teste 13 - Deleção com Sucesso")
        create_review(VALID_REVIEW_DATA)
        self.assertEqual(len(database['reviews']), 1)
        ret_code = delete_review(VALID_REVIEW_ID)
        
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])
        self.assertEqual(len(database['reviews']), 0)
        self.assertIsNone(retrieve_review(VALID_REVIEW_ID))
        
    def test_14_delete_review_error_not_found(self):
        """Retorna ERRO para avaliação não encontrada."""
        print("\nCaso de Teste 14 - Falha: Avaliação não existe")
        ret_code = delete_review(NON_EXISTENT_REVIEW_ID)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])


# Para executar os testes
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)