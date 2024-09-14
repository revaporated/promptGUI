import re

def make_safe_filename(s):
    """
    Convert a string into a filename-safe string.
    
    - Removes any character that is not alphanumeric, space, hyphen, or underscore.
    - Replaces spaces with underscores.
    - Strips leading and trailing whitespace.
    """
    s = re.sub(r'[^\w\s-]', '', s)
    s = s.strip().replace(' ', '_')
    return s
