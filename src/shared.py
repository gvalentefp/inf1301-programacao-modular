# Module with shared constants and configurations.

from typing import List, Dict, Union

__all__ = [
    'CONSTANTS',
    'RETURN_CODES',
    'WEEK_DAYS', 
    'parse_schedule'
]

CONSTANTS = {
    'MAX_LENGTH_NAME': 100,
    'MAX_SUBJECTS': 150,
    'MAX_REVIEWS': 100,
    'MAX_STUDENT_COUNT': 100,
    'MAX_PROF_COUNT': 100,
    'MAX_REVIEW_COUNT': 1000,
    'MAX_SUB_COUNT': 1000,
    'MAX_CLASS_COUNT': 1000,
    'MAX_COMMENT_LENGTH': 1000,
    'MAX_TITLE_LENGTH': 100,
    'MAX_USERNAME_LENGTH': 200,
    'MAX_PASSWORD_LENGTH': 1000,
    'MAX_MENTIONS_LENGTH': 10,
    'MAX_DESCRIPTION_LENGTH': 500
}

# Return codes to standardize function responses 
RETURN_CODES = {
    'SUCCESS': 0,  # Corresponds to #define SUCESSO 0 
    'ERROR': 1     # Corresponds to #define ERRO 1 
}

WEEK_DAYS = [
    'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN' 
]

def parse_schedule(raw_schedule: str) -> List[Dict]:
    """
    Função auxiliar para converter a string de horário (e.g., 'TUE 9-11, THU 14-16') 
    para uma lista de dicionários.
    Lança ValueError em caso de formato inválido.
    """
    parsed_schedules = []
    
    # Itera sobre cada bloco de horário separado por vírgula
    for item in raw_schedule.split(','):
        item = item.strip()
        if not item: continue
            
        parts = item.split()
        if len(parts) != 2:
            raise ValueError(f"Formato inválido: '{item}'. Esperado: DIA HORA-HORA.")
            
        day, time_range = parts[0].upper(), parts[1]
        
        # 1. Validação do Dia
        if day not in WEEK_DAYS:
             raise ValueError(f"Dia inválido: {day}. Deve ser um dos: {', '.join(WEEK_DAYS)}")
             
        # 2. Parsing das Horas
        if '-' not in time_range:
            raise ValueError(f"Horário inválido: {time_range}. Esperado: HORA_INICIO-HORA_FIM.")

        start_str, end_str = time_range.split('-')
        
        # Conversão para inteiro (ValueError será capturado pelo try/except principal)
        start_time = int(start_str)
        end_time = int(end_str)
        
        # 3. Validação da Consistência de Tempo (0 <= start < end <= 24)
        if not (0 <= start_time < end_time <= 24):
            raise ValueError(f"Período de tempo inválido: {time_range}.")
            
        parsed_schedules.append({
            'day': day, 
            'start_time': start_time, 
            'end_time': end_time
        })
        
    return parsed_schedules