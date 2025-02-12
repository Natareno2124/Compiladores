from ply.lex import lex

# Lista de tokens
tokens = (
    'VAR', 'NUM', 'SUM', 'RES', 'MUL', 'DIV', 'IGUAL', 'PAR_L', 'PAR_R',
    'IF','ELSE', 'WHILE', 'INT', 'CHAR','MAYOR','MENOR','LLAVE_R','LLAVE_L','PYC'
)

# Palabras reservadas
reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'int': 'INT',
    'char': 'CHAR'
}

# Expresiones regulares para operadores y símbolos
t_SUM   = r'\+'
t_RES   = r'-'
t_MUL   = r'\*'
t_DIV   = r'/'
t_IGUAL = r'='
t_PAR_L = r'\('
t_PAR_R = r'\)'
t_MAYOR = r'\>'
t_MENOR = r'\<'
t_LLAVE_L = r'\{'
t_LLAVE_R = r'\}'
t_PYC = r';'

# Expresión regular para números
def t_NUM(t):
    r'\d+'
    t.value = int(t.value)  
    return t

# Expresión regular para nombres de variables y palabras clave
def t_VAR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'VAR')  
    return t

# Ignorar espacios y tabulaciones
t_ignore = ' \t\n'

# Manejo de errores
def t_error(t):
    print(f"Carácter ilegal: {t.value[0]}")
    t.lexer.skip(1)

# Construcción del analizador léxico
lexer = lex()

# Prueba de entrada
code = """int x = 5;
if (x > 0) {
    while (x > 0) {
        x = x - 1;
    }
}
char letra = 'a';"
"""
lexer.input(code)

# Imprimir los tokens reconocidos
for tok in lexer:
    print(tok)
# 