import os
from datetime import datetime

SESSIONS_DIR = 'sessions'
CURR_SESSION_FILE = os.path.join(SESSIONS_DIR, 'current_session.txt')

def ensure_sessions_dir():
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)

def new_session_filepath():
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    return os.path.join(SESSIONS_DIR, f'session_{timestamp}.txt')

def set_current_session(filepath):
    ensure_sessions_dir()
    with open(CURR_SESSION_FILE, 'w', encoding="utf-8") as file:
        file.write(filepath)

def get_current_session():
    try:
        with open(CURR_SESSION_FILE, 'r', encoding='utf-8') as file:
            path = file.read().strip()

        if path and os.path.exists(path):
            return path
        
    except FileNotFoundError:
        return None
    
    return None

def save_session(filepath, doc_filename, doc_text, messages):
    escaped_doc = doc_text.replace('\\', '\\\\').replace('\n', '\\n')

    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(f'#DOCUMENT: {doc_filename}\n')
        file.write(f'#TEXT: {escaped_doc}\n')
        file.write('#MESSAGES\n')

        for msg in messages:
            content = msg['parts'].replace('\\', '\\\\').replace('\n', '\\n')
            file.write(f"{msg['role']}|{content}\n")

def load_session(filepath):
    if not filepath or not os.path.exists(filepath):
        return None, None, []

    doc_filename = ''
    doc_text = ''
    messages = []

    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            in_messages = False
            for line in file:
                line = line.rstrip('\n')

                if line.startswith('#DOCUMENT: '):
                    doc_filename = line[len('#DOCUMENT: '):]
                elif line.startswith('#TEXT: '):
                    escaped_doc = line[len('#TEXT: '):]
                    doc_text = escaped_doc.replace('\\n', '\n').replace('\\\\', '\\')
                elif line.strip() == '#MESSAGES':
                    in_messages = True
                elif in_messages and '|' in line:
                    role, content = line.split('|', 1)
                    content = content.replace('\\n', '\n').replace('\\\\', '\\')
                    messages.append({'role':role, 'parts':content})

    except OSError as e:
        return None, None, []

    return doc_filename, doc_text, messages

def rename_session(old_path, new_name):
    import re
    ensure_sessions_dir()
    safe_name = re.sub(r'[^a-zA-Z0-9_\- ]', '_', new_name).strip()
    if not safe_name:
        return None
    new_path = os.path.join(SESSIONS_DIR, f'{safe_name}.txt')

    try:
        os.rename(old_path, new_path)
        if get_current_session() == old_path:
            set_current_session(new_path)
        return new_path
    
    except OSError:
        return None

def delete_session(filepath):
    try:
        os.remove(filepath)
        if get_current_session() == filepath:
            os.remove(CURR_SESSION_FILE)
        return True
        
    except OSError:
        return False

def list_sessions():
    ensure_sessions_dir()
    items = []

    for name in os.listdir(SESSIONS_DIR):
        if name.endswith('.txt') and name != 'current_session.txt':
            full_path = os.path.join(SESSIONS_DIR, name)

            try:
                mtime = os.path.getmtime(full_path)
                ts = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                size = os.path.getsize(full_path)
                items.append((full_path, ts, size))

            except OSError:
                continue

    items.sort(key=lambda x: x[1], reverse=True)
    return items

def count_messages(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            in_messages = False
            count = 0
            for line in file:
                line = line.rstrip('\n')
                if line.strip() == '#MESSAGES':
                    in_messages = True
                    continue
                if in_messages and '|' in line:
                    count += 1
            return count
        
    except FileNotFoundError as e:
        return 0

def get_session_document_name(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            first_line = file.readline().rstrip('\n')
            return first_line[len('#DOCUMENT: '):]

    except FileNotFoundError:
        return '(untitled)'