import re

# ==========================================
# 1. THE LEXER (Now recognizes 🔁 and rp)
# ==========================================
TOKEN_SPEC = [
    ('KEYWORD',  r'\b(set|s|if|chk|else|alt|end|en|say|p|loop|rp)\b|✏️|🗣️|🤔|🤷|🛑|🔁'), 
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
            # Normalize loop keywords
            if value in ['set', 's', '✏️']: value = 'set'
            elif value in ['say', 'p', '🗣️']: value = 'say'
            elif value in ['if', 'chk', '🤔']: value = 'if'
            elif value in ['else', 'alt', '🤷']: value = 'else'
            elif value in ['end', 'en', '🛑']: value = 'end'
            elif value in ['loop', 'rp', '🔁']: value = 'loop'
            
        tokens.append((kind, value))
    return tokens

# ==========================================
# 2. THE INTERPRETER ENGINE WITH LOOP SUPPORT
# ==========================================
class MonScriptsEngine:
    def __init__(self):
        self.variables = {}
        self.loop_stack = [] # Tracks active loops: (loop_start_index, remaining_counts)

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

            # --- HANDLE VARIABLES ---
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

            # --- HANDLE OUTPUT ---
            elif kind == 'KEYWORD' and val == 'say':
                print(self._resolve_value(tokens[idx+1]))
                idx += 2

            # --- NEW: HANDLE LOOPS (🔁 3) ---
            elif kind == 'KEYWORD' and val == 'loop':
                loop_count = self._resolve_value(tokens[idx+1])
                idx += 2 # Move past the loop keyword and its count number
                
                if loop_count > 0:
                    # Save where the code inside the loop starts, and how many times to run
                    self.loop_stack.append({'start': idx, 'count': loop_count})
                else:
                    # If count is 0, skip directly to the end of the loop
                    depth = 1
                    while idx < total_tokens and depth > 0:
                        t_kind, t_val = tokens[idx]
                        if t_kind == 'KEYWORD' and t_val == 'loop': depth += 1
                        elif t_kind == 'KEYWORD' and t_val == 'end': depth -= 1
                        idx += 1

            # --- HANDLE CONDITIONS (IF) ---
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

            # --- HANDLE BLOCK CLOSURES (END / 🛑) ---
            elif kind == 'KEYWORD' and val == 'end':
                # Check if this 'end' belongs to a loop
                if self.loop_stack:
                    current_loop = self.loop_stack[-1]
                    current_loop['count'] -= 1
                    
                    if current_loop['count'] > 0:
                        # Jump back to the start of the loop code block
                        idx = current_loop['start']
                        continue
                    else:
                        # Loop is finished, remove it from stack
                        self.loop_stack.pop()
                
                idx += 1
            else:
                idx += 1

# ==========================================
# 3. RUNNING THE CODE
# ==========================================
source_script = """
🗣️ "Starting the countdown loop:"

🔁 3
    🗣️ "Loop running..."
🛑

🗣️ "Loop complete!"
"""

tokens = tokenize(source_script)
engine = MonScriptsEngine()
engine.run(tokens)
