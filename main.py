import re
import sys
import time
import random
# Import the speech library
import speech_recognition as sr

# ==========================================
# 1. THE COMPLETE LEXER (Now recognizes 🎙️)
# ==========================================
TOKEN_SPEC = [
    ('KEYWORD',  r'\b(set|s|if|chk|else|alt|end|en|say|p|loop|rp|listen|in|wait|wt|rand|rd|listen_voice|v_in)\b|✏️|🗣️|🤔|🤷|🛑|🔁|👂|⏱️|🎲|🎙️'), 
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
        
        if kind == 'SKIP' or kind == 'NEWLINE':
            continue
        elif kind == 'STRING':
            value = value.strip('"')
        elif kind == 'NUMBER':
            value = int(value)
        elif kind == 'KEYWORD':
            # Normalize shorthand/emojis into base tokens
            if value in ['set', 's', '✏️']: value = 'set'
            elif value in ['say', 'p', '🗣️']: value = 'say'
            elif value in ['if', 'chk', '🤔']: value = 'if'
            elif value in ['else', 'alt', '🤷']: value = 'else'
            elif value in ['end', 'en', '🛑']: value = 'end'
            elif value in ['loop', 'rp', '🔁']: value = 'loop'
            elif value in ['listen', 'in', '👂']: value = 'listen'
            elif value in ['wait', 'wt', '⏱️']: value = 'wait'
            elif value in ['rand', 'rd', '🎲']: value = 'rand'
            elif value in ['listen_voice', 'v_in', '🎙️']: value = 'listen_voice'
            
        tokens.append((kind, value))
    return tokens

# ==========================================
# 2. RUNTIME ENGINE INTERPRETER
# ==========================================
class MonScriptsEngine:
    def __init__(self):
        self.variables = {}
        self.loop_stack = []
        # Initialize the speech recognition tool
        self.recognizer = sr.Recognizer()

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

            # --- VARIABLE SETUP ---
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

            # --- OUTPUT ENGINE ---
            elif kind == 'KEYWORD' and val == 'say':
                print(self._resolve_value(tokens[idx+1]))
                idx += 2

            # --- TEXT INPUT ENGINE (👂) ---
            elif kind == 'KEYWORD' and val == 'listen':
                target_variable = tokens[idx+1][1]
                user_input = input()
                if user_input.isdigit():
                    user_input = int(user_input)
                self.variables[target_variable] = user_input
                idx += 2

            # --- NEW: VOICE INPUT ENGINE (🎙️) ---
            elif kind == 'KEYWORD' and val == 'listen_voice':
                target_variable = tokens[idx+1][1]
                print("[🎙️ Listening... Speak into your microphone now]")
                
                try:
                    with sr.Microphone() as source:
                        # Adjust for background room noise
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        
                    # Convert audio frequencies to text using Google's free Web Speech API
                    spoken_text = self.recognizer.recognize_google(audio)
                    print(f"[🎙️ Recognized: \"{spoken_text}\"]")
                    
                    # Convert to numbers if they spoke a single digit (e.g. "5")
                    if spoken_text.isdigit():
                        spoken_text = int(spoken_text)
                        
                    self.variables[target_variable] = spoken_text
                except Exception as e:
                    print(f"[⚠️ Voice Error: Couldn't understand audio or no mic detected]")
                    self.variables[target_variable] = "ERROR"
                
                idx += 2

            # --- TIMER UTILITY ---
            elif kind == 'KEYWORD' and val == 'wait':
                seconds = self._resolve_value(tokens[idx+1])
                time.sleep(seconds)
                idx += 2

            # --- RANDOM NUMBER GENERATOR ---
            elif kind == 'KEYWORD' and val == 'rand':
                target_variable = tokens[idx+1][1]
                max_limit = self._resolve_value(tokens[idx+2])
                self.variables[target_variable] = random.randint(1, max_limit)
                idx += 3

            # --- COUNTER LOOP SYSTEM ---
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

            # --- CONDITIONALS ---
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

            # --- SCOPE CLOSING ---
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
# 3. INTERACTIVE PRODUCTION EXECUTION
# ==========================================
if __name__ == "__main__":
    engine = MonScriptsEngine()
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                script_content = file.read()
            tokens = tokenize(script_content)
            engine.run(tokens)
        except FileNotFoundError:
            print(f"Error: Could not locate external script target '{file_path}'")
    else:
        # Showcase sandbox script using Voice Recognition!
        voice_test_script = """
        🗣️ "=== MonScripts Voice Authentication ==="
        🗣️ "Say your authorization code loud and clear..."
        
        🎙️ speech_input
        
        🗣️ "Processing voice signal data..."
        ⏱️ 1
        
        🤔 speech_input = 7
            🗣️ "🎉 Match confirmed! Command interface unlocked."
        🤷
            🗣️ "❌ Voice match mismatch. Audio data logged."
        🛑
        """
        tokens = tokenize(voice_test_script)
        engine.run(tokens)
