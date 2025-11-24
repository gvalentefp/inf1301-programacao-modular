# Module defining the list of valid PUC-Rio Departments.

__all__ = ['DEPT_LIST', 'validate_department']

# Adapted from the Depto enum 
DEPT_LIST = {
    'ADM': 'Administração',
    'DAU': 'Arquitetura e Urbanismo',
    'DAD': 'Design e Artes',
    'BIO': 'Biologia',
    'CIS': 'Ciências Sociais',
    'COM': 'Comunicação',
    'LAW': 'Direito', 
    'ECON': 'Economia',
    'EDU': 'Educação',
    'CIV': 'Engenharia Civil',
    'ELE': 'Engenharia Elétrica',
    'IND': 'Engenharia Industrial',
    'DEQM': 'Engenharia Química e de Materiais',
    'MEC': 'Engenharia Mecânica',
    'PHILOS': 'Filosofia', 
    'PHYS': 'Física', 
    'GEO': 'Geografia',
    'HIS': 'História',
    'INF': 'Informática',
    'LIT': 'Letras',
    'MATH': 'Matemática',
    'MED': 'Medicina',
    'PSYCH': 'Psicologia', 
    'CHEM': 'Química', 
    'SOC_SERV': 'Serviço Social', 
    'THEO': 'Teologia', 
    'IRI': 'Relações Internacionais'
}

def validate_department(dept_acronym: str) -> bool:
    """Checks if the department acronym is valid. Corresponds to valida_depto."""
    return dept_acronym in DEPT_LIST