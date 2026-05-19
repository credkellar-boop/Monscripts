import re

# ==========================================
# 1. CORE LEXICAL ANALYSIS (LEXER)
# ==========================================
# Updated KEYWORD list to include abbreviations and emojis
TOKEN_SPEC = [
    ('KEYWORD',  r'\b(set|s|if|chk|else|alt|end|en|say|p)\b|✏️|🗣️|🤔|🤷|🛑'), 
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
            # Normalize all abbreviations and emojis into the standard commands
            if value in ['set', 's', '✏️']: value = 'set'
            elif value in ['say', 'p', '🗣️']: value = 'say'
            elif value in ['if', 'chk', '🤔']: value = 'if'
            elif value in ['else', 'alt', '🤷']: value = 'else'
            elif value in ['end', 'en', '🛑']: value = 'end'
            
        tokens.append((kind, value))
    return tokens

# ==========================================
# 2. RUNTIME VIRTUAL INTERPRETER
# ==========================================
class UnifiedInterpreter:
    def __init__(self):
        self.variables = {}

    def _resolve_value(self, token):
        kind, val = token
        if kind == 'NUMBER':
            return val
        if kind == 'ID':
            return self.variables.get(val, 0)
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
                        if t_kind == 'KEYWORD' and t_val == 'if':
                            depth += 1
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
                    if t_kind == 'KEYWORD' and t_val == 'if':
                        depth += 1
                    elif t_kind == 'KEYWORD' and t_val == 'end':
                        depth -= 1
                idx += 1

            elif kind == 'KEYWORD' and val == 'end':
                idx += 1
            else:
                idx += 1
# ==========================================
# 3. PRODUCTION RUNNER ENGINE
# ==========================================
import sys

if __name__ == "__main__":
    interpreter = UnifiedInterpreter()
    
    # Check if a file was passed as an argument (e.g., python main.py myscript.ms)
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                script_content = file.read()
            print(f"--- Running {file_path} ---")
            tokens = tokenize(script_content)
            interpreter.run(tokens)
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' could not be found.")
    else:
        # Fallback inline test script if no file is provided
        fallback_script = """
        ✏️ score = 95
        🤔 score > 90
            🗣️ "Success! MonScripts is running perfectly."
        🛑
        """
        print("--- Running Local Sandbox Script ---")
        tokens = tokenize(fallback_script)
        interpreter.run(tokens)
