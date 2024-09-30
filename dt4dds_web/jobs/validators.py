from django.core.exceptions import ValidationError

import re

SEQUENCES_MAX_LENGTH = 150
SEQUENCES_MAX_NUMBER = 10000


def validate_sequences(raw_sequence_string):

    sequence_list = raw_sequence_string.splitlines()

    # Check for allowed characters
    if re.compile(r'[^ACGT]').search(''.join(sequence_list)):
        raise ValidationError('Design sequences may only contain A, C, G, and T.')

    # Check for maximum number of sequences
    if len(sequence_list) > SEQUENCES_MAX_NUMBER:
        raise ValidationError(f'Maximum of {SEQUENCES_MAX_NUMBER} sequences are allowed.')
    
    # Check for maximum length of sequences
    if max(map(len, sequence_list)) > SEQUENCES_MAX_LENGTH:
        raise ValidationError(f'Maximum sequence length of {SEQUENCES_MAX_LENGTH} supported.')