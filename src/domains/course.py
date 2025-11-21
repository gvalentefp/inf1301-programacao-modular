# Module defining the list of valid PUC-Rio Courses.

__all__ = ['COURSE_LIST', 'validate_course']

# Adapted from the Curso enum 
COURSE_LIST = {
    'ADM': 'Administração',
    'ARQ_URB': 'Arquitetura e Urbanismo',
    'ART_CEN': 'Artes Cênicas',
    'CIEN_ECON': 'Ciências Econômicas',
    'CIEN_SOCIOL': 'Ciências Sociais',
    'CIEN_COMP': 'Ciência da Computação',
    'COM_SOC': 'Comunicação Social',
    'DSGN': 'Design',
    'LAW': 'Direito', # DIR [cite: 364]
    'ENG_AMB': 'Engenharia Ambiental',
    'ENG_CIV': 'Engenharia Civil',
    'ENG_COMP': 'Engenharia de Computação',
    'ENG_CONTRLAUT': 'Engenharia de Controle e Automação',
    'ENG_ELETR': 'Engenharia Elétrica',
    'ENG_IND': 'Engenharia Industrial',
    'ENG_MEC': 'Engenharia Mecânica',
    'ENG_MAT': 'Engenharia de Materiais',
    'ENG_PROD': 'Engenharia de Produção',
    'ENG_QUIM': 'Engenharia Química',
    'PUBLI_COM': 'Publicidade e Comunicação',
    'CINEM': 'Cinema',
    'COMUNIC_TEC': 'Comunicação Digital',
    'PHARM': 'Farmácia', 
    'PHILOS': 'Filosofia', 
    'PHYS': 'Física', 
    'GEO': 'Geografia',
    'HIST': 'História',
    'AI': 'Inteligência Artificial', 
    'JOURN': 'Jornalismo', 
    'LIT': 'Letras', 
    'MATH': 'Matemática', 
    'APP_MATH': 'Matemática Aplicada', 
    'IR': 'Relações Internacionais', 
    'NEURO': 'Neurociência',
    'NUTR': 'Nutrição', 
    'PEDAG': 'Pedagogia',
    'PSYCH': 'Psicologia', 
    'CHEM': 'Química', 
    'SOC_SERV': 'Serviço Social' 
}

def validate_course(course_acronym: str) -> bool:
    """Checks if the course acronym is valid."""
    return course_acronym in COURSE_LIST