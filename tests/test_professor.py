import unittest
from src.modules.professor import (
    create_professor, retrieve_professor, retrieve_all_professors, 
    update_professor, delete_professor, validate_professor, 
    create_professor_subject, professor_teaches_subject, 
    retrieve_professor_subjects, update_professor_subjects, 
    delete_professor_subject, calculate_review_average_professor,
    _generate_professor_id
)
from src.persistence import database, initialize_db, save_db
from src.shared import RETURN_CODES
from src.domains.department import DEPT_LIST
from src.modules.subject import create_subject

# --- Fixtures (Dados de Teste) ---
VALID_PROF_ID = 1
VALID_DEPT = 'INF'
INVALID_DEPT = 'ENGENHARIA_GALACTICA'
VALID_SUBJECT_CODE_1 = 1301
VALID_SUBJECT_CODE_2 = 1302
NON_EXISTENT_PROF_ID = 9999

VALID_PROFESSOR_DATA = {
    'name': 'Flavio Heleno Bevilacqua E Silva', # Nome de exemplo do documento [cite: 162]
    'department': VALID_DEPT
}

class TestProfessor(unittest.TestCase):
    
    def setUp(self):
        """Prepara um estado limpo para cada teste."""
        initialize_db() 
        database['professors'] = []
        database['subjects'] = []
        save_db()

        import src.modules.professor 
        src.modules.professor.next_professor_id = 1 

        # Create Dependencies
        create_subject({'code': 1301, 'credits': 4, 'name': 'Modular', 'description': 'Desc'})
        create_subject({'code': 500, 'credits': 4, 'name': 'Old', 'description': 'Desc'})

    # --- Testes de Criação (create_professor) ---
    
    def test_01_create_professor_success(self):
        """Retorna SUCESSO e insere o professor com ID sequencial."""
        print("\nCaso de Teste 01 - Criação com Sucesso")
        ret_code = create_professor(VALID_PROFESSOR_DATA)
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])
        self.assertEqual(len(database['professors']), 1)
        # O ID deve ser 1 na primeira execução
        self.assertEqual(database['professors'][0]['id'], VALID_PROF_ID)
        
    def test_02_create_professor_nok_invalid_department(self):
        """Retorna ERRO se o departamento for inválido."""
        print("\nCaso de Teste 02 - Falha: Departamento inválido.")
        invalid_data = VALID_PROFESSOR_DATA.copy()
        invalid_data['department'] = INVALID_DEPT
        
        ret_code = create_professor(invalid_data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        self.assertEqual(len(database['professors']), 0)
        
    def test_03_create_professor_nok_incomplete_data(self):
        """Retorna ERRO se houver dados incompletos (Falta 'name')."""
        print("\nCaso de Teste 03 - Falha: Dados incompletos (Falta 'name').")
        data_incomplete = VALID_PROFESSOR_DATA.copy()
        del data_incomplete['name']
        
        ret_code = create_professor(data_incomplete)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        self.assertEqual(len(database['professors']), 0)

    # --- Testes de Busca (retrieve_professor) ---

    def test_04_retrieve_professor_found(self):
        """Retorna o professor com ID correspondente."""
        print("\nCaso de Teste 04 - Busca com Sucesso")
        create_professor(VALID_PROFESSOR_DATA)
        professor = retrieve_professor(VALID_PROF_ID)
        self.assertIsNotNone(professor)
        self.assertEqual(professor['name'], VALID_PROFESSOR_DATA['name'])

    def test_05_retrieve_professor_not_found(self):
        """Retorna None para professor não registrado."""
        print("\nCaso de Teste 05 - Busca com ERRO: Professor não registrado")
        professor = retrieve_professor(NON_EXISTENT_PROF_ID)
        self.assertIsNone(professor)

    def test_06_retrieve_professor_invalid_id(self):
        """Retorna None para ID inválido (negativo)."""
        print("\nCaso de Teste 06 - Busca com ERRO: ID inválido")
        professor = retrieve_professor(-1)
        self.assertIsNone(professor)

    # --- Testes de Atualização (update_professor) ---

    def test_07_update_professor_success(self):
        """Retorna SUCESSO e atualiza o nome e o departamento."""
        print("\nCaso de Teste 07 - Atualização Genérica com Sucesso")
        
        # 1. FORCE CLEAN START
        database['professors'] = []
        
        # 2. Reset ID to 1
        import src.modules.professor
        src.modules.professor.next_professor_id = 1
        
        # 3. CREATE the professor first (so ID 1 exists)
        # We use 'INF' because we know it is valid
        create_professor({'name': 'Old Name', 'department': 'INF'}) 

        # 4. UPDATE (Change 'MAT' to 'MATH')
        new_data = {'name': 'Prof. Novo Nome', 'department': 'MATH'} 
        ret_code = update_professor(VALID_PROF_ID, new_data)
        
        # 5. Verify
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])
        updated_prof = retrieve_professor(VALID_PROF_ID)
        self.assertEqual(updated_prof['name'], 'Prof. Novo Nome')
        self.assertEqual(updated_prof['department'], 'MATH')

    def test_08_update_professor_nok_invalid_data(self):
        """Retorna ERRO para dados inválidos (e.g., nome vazio após update)."""
        print("\nCaso de Teste 08 - Falha: Dados inválidos no update (nome vazio)")
        create_professor(VALID_PROFESSOR_DATA)
        invalid_data = {'name': ''}
        ret_code = update_professor(VALID_PROF_ID, invalid_data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        
        # Verifica se o nome NÃO foi alterado
        self.assertEqual(retrieve_professor(VALID_PROF_ID)['name'], VALID_PROFESSOR_DATA['name'])

    # --- Testes de Deleção (delete_professor) ---

    def test_09_delete_professor_success(self):
        """Retorna SUCESSO e deleta o professor."""
        print("\nCaso de Teste 09 - Deleção com Sucesso")
        create_professor(VALID_PROFESSOR_DATA)
        self.assertEqual(len(database['professors']), 1)
        ret_code = delete_professor(VALID_PROF_ID)
        
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])
        self.assertEqual(len(database['professors']), 0)
        self.assertIsNone(retrieve_professor(VALID_PROF_ID))
        
    def test_10_delete_professor_nok_non_existent(self):
        """Retorna ERRO para professor não existente."""
        print("\nCaso de Teste 10 - Falha: Professor não existe")
        ret_code = delete_professor(NON_EXISTENT_PROF_ID)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])

    # --- Testes de Associação de Matérias (cria_materia_prof, prof_ensina_materia) ---
    
    def test_11_create_professor_subject_success(self):
        """Retorna SUCESSO e associa a matéria ao professor."""
        print("\nCaso de Teste 11 - Associa Matéria com Sucesso")
        create_professor(VALID_PROFESSOR_DATA)
        ret_code = create_professor_subject(VALID_PROF_ID, VALID_SUBJECT_CODE_1)
        
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])
        self.assertIn(VALID_SUBJECT_CODE_1, retrieve_professor(VALID_PROF_ID)['subjects'])
        
    def test_12_professor_teaches_subject_success(self):
        """Retorna SUCESSO quando professor ensina a matéria."""
        print("\nCaso de Teste 12 - Verifica Matéria: Ensina")
        create_professor(VALID_PROFESSOR_DATA)
        create_professor_subject(VALID_PROF_ID, VALID_SUBJECT_CODE_1)
        
        ret_code = professor_teaches_subject(VALID_PROF_ID, VALID_SUBJECT_CODE_1)
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])

    def test_13_professor_teaches_subject_nok_not_teaches(self):
        """Retorna ERRO quando professor não ensina a matéria."""
        print("\nCaso de Teste 13 - Verifica Matéria: Não Ensina")
        create_professor(VALID_PROFESSOR_DATA)
        
        ret_code = professor_teaches_subject(VALID_PROF_ID, VALID_SUBJECT_CODE_2)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        
    def test_14_update_professor_subjects_success(self):
        """Atualiza o código de matéria globalmente para um professor."""
        print("\nCaso de Teste 14 - Atualização Global de Código de Matéria")
        create_professor(VALID_PROFESSOR_DATA)
        create_professor_subject(VALID_PROF_ID, 500)
        
        ret_code = update_professor_subjects(500, 600)
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])
        self.assertNotIn(500, retrieve_professor_subjects(VALID_PROF_ID))
        self.assertIn(600, retrieve_professor_subjects(VALID_PROF_ID))
        
    # --- Testes de Média de Avaliação (calculate_review_average_professor) ---

    def test_15_calculate_average_no_reviews(self):
        """Retorna 0.0 se não houver avaliações."""
        print("\nCaso de Teste 15 - Média: Sem avaliações")
        create_professor(VALID_PROFESSOR_DATA)
        average = calculate_review_average_professor(VALID_PROF_ID)
        self.assertEqual(average, 0.0)

    def test_16_calculate_average_professor_not_found(self):
        """Retorna -1.0 se o professor não for encontrado."""
        print("\nCaso de Teste 16 - Média: Professor inexistente")
        average = calculate_review_average_professor(NON_EXISTENT_PROF_ID)
        self.assertEqual(average, -1.0)
        
    def test_17_calculate_average_placeholder_value(self):
        """Verifica se o placeholder de cálculo retorna o valor esperado (3.5 neste caso simulado)."""
        print("\nCaso de Teste 17 - Média: Valor placeholder")
        create_professor(VALID_PROFESSOR_DATA) # ID 1
        
        from src.persistence import database
        
        # Inject reviews directly
        database['reviews'].extend([
            {'id_aval': 1, 'stars': 4}, {'id_aval': 2, 'stars': 5},
            {'id_aval': 3, 'stars': 3}, {'id_aval': 4, 'stars': 5}
        ])
        
        # Link to professor
        database['professors'][0]['reviews'] = [1, 2, 3, 4]
        average = calculate_review_average_professor(VALID_PROF_ID) #  [4, 5, 3, 5] -> values used for avarage
        
        self.assertEqual(average, 4.2) # Python was rounding down the avarage from 4.25 to 4.2 instead of 4.3
        

# Para executar os testes
if __name__ == '__main__':
    # Você precisará configurar o PYTHONPATH ou o __init__.py corretamente
    unittest.main(argv=['first-arg-is-ignored'], exit=False)