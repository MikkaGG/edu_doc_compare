import re

def extract_subject_name(subject_line):
    match = re.match(r'^(.*?)\s*-\s*\d+\s*часов', subject_line, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return subject_line.strip()
