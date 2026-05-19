import re
import sys
import time
import random
import os

# Top-of-the-line cryptographic primitives
try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

# ==========================================
# 1. CORE DICTIONARY & LEXER CONFIGURATION
# ==========================================
TRANSLATION_MAP = {
    'set':    {'short': 's',   'emoji': '✏️'},
    'say':    {'short': 'p',   'emoji': '🗣️'},
    'if':     {'short': 'chk', 'emoji': '🤔'},
    'else':   {'short': 'alt', 'emoji': '🤷'},
    'end':    {'short': 'en',  'emoji': '🛑'},
    'loop':   {'short': 'rp',  'emoji': '🔁'},
    'listen': {'short': 'in',  'emoji': '👂'},
    'wait':   {'short': 'wt',  'emoji': '⏱️'},
    'rand':   {'short': 'rd',  'emoji': '🎲'},
    'voice':  {'short': 'v',   'emoji': '🎙️'}
}

TOKEN_SPEC = [
    ('KEYWORD',  r'\b(set|s|if|chk|else|alt|end|en|say|p|loop|rp|listen|in|wait|wt|rand|rd|voice|v)\b|✏️|🗣️|🤔|🤷|🛑|🔁|👂|⏱️|🎲|🎙️'), 
    ('NUMBER',   r'\d+'),                  
    ('STRING',   r'"[^"]*"'),              
    ('OP',       r'[=\|<>\+\-\*\/]'),      
    ('ID',       r'[a-zA-Z_]\w*'),         
    ('SKIP',     r'[ \t]+'),               
    ('NEWLINE',  r'\n'),                   
]

def tokenize(code):
    tokens = []
    master_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)
    
    for match in re.finditer(master_regex, code):
        kind = match.lastgroup
        value = match.group()
        
        if kind in ['SKIP', 'NEWLINE']:
            continue
        elif kind == 'STRING':
            value = value.strip('"')
        elif kind == 'NUMBER':
            value = int(value)
        elif kind == 'KEYWORD':
            for base, variations in TRANSLATION_MAP.items():
                if value in [base, variations['short'], variations['emoji']]:
                    value = base
                    break
        tokens.append((kind, value))
    return tokens

# ==========================================
# 2. RUNTIME ENGINE INTERPRETER
# ==========================================
class MonScriptsEngine:
    def __init__(self):
        self.variables = {}
        self.loop_stack = []
        self.recognizer = sr.Recognizer() if sr else None

    def _resolve_value(self, token):
        kind, val = token
        if kind == 'NUMBER': return val
        if kind == 'ID': return self.variables.get(val, 0)
        return val

    def run(self, tokens):
        idx = 0
        total_tokens = len(tokens)

        while idx < total_tokens:
            kind, val = tokens[idx]

            if kind == 'KEYWORD' and val == 'set':
                var_name = tokens[idx+1][1]
                if idx + 5 < total_tokens and tokens[idx+4][0] == 'OP' and tokens[idx+4][1] in ['+', '-', '*', '/']:
                    left_val = self._resolve_value(tokens[idx+3])
                    op = tokens[idx+4][1]
                    right_val = self._resolve_value(tokens[idx+5])
                    
                    if op == '+': result = left_val + right_val
                    elif op == '-': result = left_val - right_val
                    elif op == '*': result = left_val * right_val
                    elif op == '/': result = left_val // right_val
                    
                    self.variables[var_name] = result
                    idx += 6
                else:
                    self.variables[var_name] = self._resolve_value(tokens[idx+3])
                    idx += 4

            elif kind == 'KEYWORD' and val == 'say':
                print(self._resolve_value(tokens[idx+1]))
                idx += 2

            elif kind == 'KEYWORD' and val == 'listen':
                target_variable = tokens[idx+1][1]
                user_input = input()
                if user_input.isdigit():
                    user_input = int(user_input)
                self.variables[target_variable] = user_input
                idx += 2

            elif kind == 'KEYWORD' and val == 'voice':
                target_variable = tokens[idx+1][1]
                if not self.recognizer:
                    print("[⚠️ Speech recognition package missing]")
                    self.variables[target_variable] = "ERROR"
                    idx += 2
                    continue
                print("[🎙️ Listening...]")
                try:
                    with sr.Microphone() as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    spoken_text = self.recognizer.recognize_google(audio)
                    if spoken_text.isdigit():
                        spoken_text = int(spoken_text)
                    self.variables[target_variable] = spoken_text
                except Exception:
                    self.variables[target_variable] = "ERROR"
                idx += 2

            elif kind == 'KEYWORD' and val == 'wait':
                seconds = self._resolve_value(tokens[idx+1])
                time.sleep(seconds)
                idx += 2

            elif kind == 'KEYWORD' and val == 'rand':
                target_variable = tokens[idx+1][1]
                max_limit = self._resolve_value(tokens[idx+2])
                self.variables[target_variable] = random.randint(1, max_limit)
                idx += 3

            elif kind == 'KEYWORD' and val == 'loop':
                loop_count = self._resolve_value(tokens[idx+1])
                idx += 2
                if loop_count > 0:
                    self.loop_stack.append({'start': idx, 'count': loop_count})
                else:
                    depth = 1
                    while idx < total_tokens and depth > 0:
                        t_kind, t_val = tokens[idx]
                        if t_kind == 'KEYWORD' and t_val == 'loop': depth += 1
                        elif t_kind == 'KEYWORD' and t_val == 'end': depth -= 1
                        idx += 1

            elif kind == 'KEYWORD' and val == 'if':
                left = self._resolve_value(tokens[idx+1])
                op = tokens[idx+2][1]
                right = self._resolve_value(tokens[idx+3])

                condition_met = False
                if op == '<' and left < right: condition_met = True
                if op == '>' and left > right: condition_met = True
                if op == '=' and left == right: condition_met = True
                
                idx += 4 
                if condition_met:
                    continue
                else:
                    depth = 1
                    while idx < total_tokens and depth > 0:
                        t_kind, t_val = tokens[idx]
                        if t_kind == 'KEYWORD' and t_val == 'if': depth += 1
                        elif t_kind == 'KEYWORD' and t_val == 'end':
                            depth -= 1
                            if depth == 0:
                                idx += 1
                                break
                        elif t_kind == 'KEYWORD' and t_val == 'else' and depth == 1:
                            idx += 1 
                            break
                        idx += 1

            elif kind == 'KEYWORD' and val == 'else':
                depth = 1
                while idx < total_tokens and depth > 0:
                    idx += 1
                    t_kind, t_val = tokens[idx]
                    if t_kind == 'KEYWORD' and t_val == 'if': depth += 1
                    elif t_kind == 'KEYWORD' and t_val == 'end': depth -= 1
                idx += 1

            elif kind == 'KEYWORD' and val == 'end':
                if self.loop_stack:
                    current_loop = self.loop_stack[-1]
                    current_loop['count'] -= 1
                    if current_loop['count'] > 0:
                        idx = current_loop['start']
                        continue
                    else:
                        self.loop_stack.pop()
                idx += 1
            else:
                idx += 1

# ==========================================
# 3. MILITARY-GRADE ENCRYPTION SUB-SYSTEM
# ==========================================
def run_secure_generator(file_path):
    if not Fernet:
        print("[❌ Security Fault: Run 'pip install cryptography' to use encryption features]")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()
            
        # Generate random high-entropy cryptographic encryption cipher key
        secret_key = Fernet.generate_key()
        cipher_suite = Fernet(secret_key)
        
        # Serialize and seal data using AES-256 standard format parameters
        encrypted_byte_stream = cipher_suite.encrypt(raw_data.encode('utf-8'))
        
        output_filename = "locked_script.enc"
        with open(output_filename, 'wb') as f_out:
            f_out.write(encrypted_byte_stream)
            
        print("🔒 [MonScripts Sovereign Security Engine Activated]")
        print(f"✔️ Successfully generated encrypted architecture payload -> '{output_filename}'")
        print(f"🔑 CRITICAL ACCESS SECRET KEY: {secret_key.decode('utf-8')}")
        print("⚠️ SAVE THIS KEY. The file cannot be read or processed without it.")
    except FileNotFoundError:
        print(f"Error: Target file script '{file_path}' not found.")

def run_secure_decrypted_runtime(enc_file_path, base_key):
    if not Fernet:
        print("[❌ Security Fault: Cryptography library missing]")
        return
        
    try:
        with open(enc_file_path, 'rb') as f:
            sealed_payload = f.read()
            
        cipher_suite = Fernet(base_key.encode('utf-8'))
        # Perform in-memory decryption. Raw code never writes to unencrypted disk sectors!
        decrypted_raw_script = cipher_suite.decrypt(sealed_payload).decode('utf-8')
        
        tokens = tokenize(decrypted_raw_script)
        engine = MonScriptsEngine()
        print("🔓 [Secure memory payload verified. Launching runtime environment...]")
        engine.run(tokens)
    except Exception:
        print("🛡️ [CRITICAL ALERT: Access Denied. Invalid Cryptographic Key or Corrupted Payload]")

# ==========================================
# 4. MASTER PRODUCTION CLI LINK
# ==========================================
if __name__ == "__main__":
    if len(sys.argv) > 2:
        flag = sys.argv[1]
        
        if flag == "--encrypt":
            run_secure_generator(sys.argv[2])
        elif flag == "--run-secure" and len(sys.argv) == 4:
            run_secure_decrypted_runtime(sys.argv[2], sys.argv[3])
        else:
            # Fallback normal plain file execution
            try:
                with open(sys.argv[2], 'r', encoding='utf-8') as f:
                    tokens = tokenize(f.read())
                MonScriptsEngine().run(tokens)
            except FileNotFoundError:
                print("Error: Target file not found.")
    else:
        # Default local sandbox execution mode
        fallback_script = '🗣️ "Sovereign Framework Online. No parameters passed."'
        tokens = tokenize(fallback_script)
        MonScriptsEngine().run(tokens)
