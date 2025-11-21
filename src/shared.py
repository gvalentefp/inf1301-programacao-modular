# Module with shared constants and configurations.

__all__ = [
    'CONSTANTS',
    'RETURN_CODES',
    'WEEK_DAYS'
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