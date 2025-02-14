from ply.lex import lex
import sys

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

def ingreso_datos():
    global code
    print("\t--- Ingreso de texto en el editor ---")
    code = input("Ingrese el código a analizar:\n")

def lexico():
    print("\t--- Análisis léxico ---")
    lexer.input(code)
    for tok in lexer:
        print(tok)

def sintactico():
    print("\t--- Análisis sintáctico en árbol ---")
    #Codigo analizador sintáctico

def tabla_simbolos():
    print("\t--- Tabla de símbolos ---")
    #Codigo tabla de símbolos

def salir():
    print("\t--- Feliz Día ---")
    print("--------------------------------------------------")
    exit()

opciones = {
    "1": ingreso_datos,
    "2": lexico,
    "3": sintactico,
    "4": tabla_simbolos,
    "5": salir
}

code = ""

if __name__ == "__main__":
    while True:
        print("\n--- MENU PRINCIPAL ---")
        print("1. Ingreso de texto en el editor")
        print("2. Análisis léxico")
        print("3. Análisis sintáctico en árbol")
        print("4. Tabla de símbolos")
        print("5. Salir")

        opcion = input("Escoja una de las siguientes opciones ---> ")

        if opcion in opciones:
            opciones[opcion]()
        else:
            print("Opción incorrecta, por favor intente nuevamente.")