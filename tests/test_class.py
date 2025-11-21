import unittest
from src.modules.classes import (
    create_class, exists_class, retrieve_class, 
    update_class, delete_class, validate_class, 
    retrieve_all_classes, _generate_class_id
)

from src.persistence import database, initialize_db
from src.shared import RETURN_CODES

# --- Fixtures (Dados de Teste) ---
VALID_CLASS_CODE = 1 # O primeiro ID gerado
NON_EXISTENT_CLASS_CODE = 999

# Dados simulados para Chaves Estrangeiras (FKs)
# Estes dados devem ser inseridos no banco para simular a existência de entidades válidas.
MOCK_SUBJECT_CODE = 1301 
MOCK_PROF_ID_1 = 1 
MOCK_PROF_ID_2 = 2 
MOCK_STUDENT_ENROLLMENT = 2310488

# Horário e Período Válidos
VALID_SCHEDULE = [
    {'day': 'MON', 'start_time': 9, 'end_time': 11}
]
VALID_PERIOD = 20242 # Formato YYYYX

VALID_CLASS_DATA = {
    'subject_code': MOCK_SUBJECT_CODE,
    'professors_ids': [MOCK_PROF_ID_1],
    'period': VALID_PERIOD,
    'schedule': VALID_SCHEDULE,
    'students_enrollments': [MOCK_STUDENT_ENROLLMENT]
}

class TestClass(unittest.TestCase):
    
    def setUp(self):
        """Prepara um estado limpo e insere dados MOCK para validar FKs."""
        database['classes'] = []
        
        # Simula a existência de entidades referenciadas (FKs)
        database['subjects'] = [{'code': MOCK_SUBJECT_CODE, 'name': 'Modular Programming'}]
        database['professors'] = [
            {'id': MOCK_PROF_ID_1, 'name': 'Prof A', 'department': 'INF'},
            {'id': MOCK_PROF_ID_2, 'name': 'Prof B', 'department': 'MAT'}
        ]
        database['students'] = [
            {'enrollment': MOCK_STUDENT_ENROLLMENT, 'name': 'Student X', 'course': 'CIEN_COMP'}
        ]

        # Reseta o contador de ID da classe
        global next_class_id
        try:
             from src.modules.classes import next_class_id
             next_class_id = 1
        except ImportError:
            pass 
        initialize_db()

    # --- Testes de Validação (validate_class) ---

    def test_01_validate_class_t1_success(self):
        """T1: Retorna SUCESSO quando todos os campos e FKs são válidos."""
        print("\nCaso de Teste 01 - Validação com Sucesso")
        ret_code = validate_class(VALID_CLASS_DATA)
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])

    def test_02_validate_class_t2_error_subject_not_exist(self):
        """T2: Retorna ERRO se a Matéria referenciada não existe."""
        print("\nCaso de Teste 02 - Validação Falha: Matéria não existe.")
        data = VALID_CLASS_DATA.copy()
        data['subject_code'] = 999 # Código não mockado
        ret_code = validate_class(data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])

    def test_03_validate_class_t3_error_professor_not_exist(self):
        """T3: Retorna ERRO se um Professor referenciado não existe."""
        print("\nCaso de Teste 03 - Validação Falha: Professor não existe.")
        data = VALID_CLASS_DATA.copy()
        data['professors_ids'] = [MOCK_PROF_ID_1, 999] # ID 999 não existe
        ret_code = validate_class(data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        
    def test_04_validate_class_t4_error_invalid_period(self):
        """T4: Retorna ERRO se o formato do período é inválido (ex: 20253)."""
        print("\nCaso de Teste 04 - Validação Falha: Período inválido.")
        data = VALID_CLASS_DATA.copy()
        data['period'] = 20253
        ret_code = validate_class(data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])

    def test_05_validate_class_t5_error_null_schedule(self):
        """T5: Retorna ERRO se os horários são nulos."""
        print("\nCaso de Teste 05 - Validação Falha: Horário nulo.")
        data = VALID_CLASS_DATA.copy()
        data['schedule'] = []
        ret_code = validate_class(data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])

    # --- Testes de Criação (create_class) ---

    def test_06_create_class_t1_success(self):
        """T1: Retorna SUCESSO e insere a turma."""
        print("\nCaso de Teste 06 - Criação com Sucesso")
        ret_code = create_class(VALID_CLASS_DATA)
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])
        self.assertEqual(len(database['classes']), 1)
        self.assertEqual(database['classes'][0]['code'], VALID_CLASS_CODE)

    def test_07_create_class_t5_error_duplicate(self):
        """T5: Retorna ERRO se já existe uma turma idêntica."""
        print("\nCaso de Teste 07 - Falha: Turma idêntica já existe.")
        create_class(VALID_CLASS_DATA)
        
        # Tenta inserir duplicata
        ret_code = create_class(VALID_CLASS_DATA)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        self.assertEqual(len(database['classes']), 1) # Não deve ter aumentado
        
    def test_08_create_class_t6_error_invalid_data(self):
        """T6: Retorna ERRO se a validação falhar (dados inválidos)."""
        print("\nCaso de Teste 08 - Falha: Dados inválidos (período).")
        data = VALID_CLASS_DATA.copy()
        data['period'] = 20253
        ret_code = create_class(data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        self.assertEqual(len(database['classes']), 0)
        
    # --- Testes de Existência (exists_class) ---

    def test_09_exists_class_t1_exists(self):
        """T1: Retorna SUCESSO quando a turma existe."""
        print("\nCaso de Teste 09 - Existe Turma (Sucesso)")
        create_class(VALID_CLASS_DATA)
        ret_code = exists_class(VALID_CLASS_DATA)
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])

    def test_10_exists_class_t2_not_exist(self):
        """T2: Retorna ERRO quando a turma não existe."""
        print("\nCaso de Teste 10 - Não Existe Turma (Erro)")
        data = VALID_CLASS_DATA.copy()
        data['period'] = 20251 # Período diferente
        ret_code = exists_class(data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])

    # --- Testes de Busca (retrieve_class) ---

    def test_11_retrieve_class_t1_success(self):
        """T1: Retorna a turma com o código correspondente."""
        print("\nCaso de Teste 11 - Busca Turma por Código (Sucesso)")
        create_class(VALID_CLASS_DATA)
        class_record = retrieve_class(VALID_CLASS_CODE)
        self.assertIsNotNone(class_record)
        self.assertEqual(class_record['subject_code'], MOCK_SUBJECT_CODE)

    def test_12_retrieve_class_t2_error_not_found(self):
        """T2: Retorna NULL para turma não encontrada."""
        print("\nCaso de Teste 12 - Busca Turma por Código (Não Encontrada)")
        class_record = retrieve_class(NON_EXISTENT_CLASS_CODE)
        self.assertIsNone(class_record)

    def test_13_retrieve_class_t3_error_invalid_code(self):
        """T3: Retorna NULL para código inválido (negativo)."""
        print("\nCaso de Teste 13 - Busca Turma por Código (Código Inválido)")
        class_record = retrieve_class(-1)
        self.assertIsNone(class_record)

    # --- Testes de Atualização (update_class) ---

    def test_14_update_class_t1_success(self):
        """T1: Retorna SUCESSO e atualiza o período."""
        print("\nCaso de Teste 14 - Atualização com Sucesso")
        create_class(VALID_CLASS_DATA)
        new_data = {'period': 20251}
        ret_code = update_class(VALID_CLASS_CODE, new_data)
        
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])
        updated_class = retrieve_class(VALID_CLASS_CODE)
        self.assertEqual(updated_class['period'], 20251)
        
    def test_15_update_class_t2_error_not_found(self):
        """T2: Retorna ERRO para código inexistente."""
        print("\nCaso de Teste 15 - Falha: Código não existente")
        new_data = {'period': 20251}
        ret_code = update_class(NON_EXISTENT_CLASS_CODE, new_data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])

    def test_16_update_class_t3_error_invalid_new_data(self):
        """T3: Retorna ERRO se os novos dados forem inválidos (e.g., professor inexistente)."""
        print("\nCaso de Teste 16 - Falha: Novos dados inválidos (Professor inexistente)")
        create_class(VALID_CLASS_DATA)
        invalid_data = {'professors_ids': [9999]} # Professor 9999 não existe
        ret_code = update_class(VALID_CLASS_CODE, invalid_data)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        
        # Verifica se os IDs antigos foram mantidos
        self.assertEqual(retrieve_class(VALID_CLASS_CODE)['professors_ids'], [MOCK_PROF_ID_1])

    # --- Testes de Deleção (delete_class) ---

    def test_17_delete_class_t1_success(self):
        """T1: Retorna SUCESSO e remove a turma."""
        print("\nCaso de Teste 17 - Deleção com Sucesso")
        create_class(VALID_CLASS_DATA)
        self.assertEqual(len(database['classes']), 1)
        ret_code = delete_class(VALID_CLASS_CODE)
        
        self.assertEqual(ret_code, RETURN_CODES['SUCCESS'])
        self.assertEqual(len(database['classes']), 0)
        self.assertIsNone(retrieve_class(VALID_CLASS_CODE))
        
    def test_18_delete_class_t2_error_not_found(self):
        """T2: Retorna ERRO para turma não encontrada."""
        print("\nCaso de Teste 18 - Falha: Turma não existe")
        ret_code = delete_class(NON_EXISTENT_CLASS_CODE)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])
        
    def test_19_delete_class_t3_error_invalid_code(self):
        """T3: Retorna ERRO para código inválido."""
        print("\nCaso de Teste 19 - Falha: Código inválido")
        ret_code = delete_class(-1)
        self.assertEqual(ret_code, RETURN_CODES['ERROR'])


# Para executar os testes
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)