from ply.lex import lex
import ply.yacc as yacc
import graphviz
import os

# Tabla de símbolos
tabla_simbolos = {}
id_contador = 1  # Contador para asignar IDs únicos

# Lista de tokens
tokens = (
    'VAR', 'NUM', 'SUM', 'RES', 'MUL', 'DIV', 'IGUAL', 'PAR_L', 'PAR_R',
    'IF', 'ELSE', 'WHILE', 'INT', 'CHAR', 'MAYOR', 'MENOR', 'LLAVE_R', 'LLAVE_L', 'PYC', 'AND', 'OR', 'NOT', 'STRING'
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
t_SUM = r'\+'
t_RES = r'-'
t_MUL = r'\*'
t_DIV = r'/'
t_IGUAL = r'='
t_PAR_L = r'\('
t_PAR_R = r'\)'
t_MAYOR = r'>'
t_MENOR = r'<'
t_LLAVE_L = r'\{'
t_LLAVE_R = r'\}'
t_PYC = r';'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'

def t_STRING(t):
    r'\".*?\"'
    t.value = t.value[1:-1] 
    return t

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_VAR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'VAR')
    return t

t_ignore = ' \t\n'

def t_error(t):
    print(f"Carácter ilegal: {t.value[0]}")
    t.lexer.skip(1)

lexer = lex()

# Definición de la clase Node antes de la gramática
class Node:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children if children else []
        self.value = value

# Precedencia de operadores
precedence = (
    ('left', 'SUM', 'RES'),
    ('left', 'MUL', 'DIV'),
)

# Definición de la gramática
def p_programa(p):
    'programa : declaraciones'
    print("--- Análisis sintáctico ---")
    p[0] = Node("PROGRAMA", [p[1]])

def p_declaraciones(p):
    '''declaraciones : declaraciones declaracion
                     | declaraciones asignacion
                     | declaraciones if_statement
                     | declaraciones while_statement
                     | declaracion
                     | asignacion
                     | if_statement
                     | while_statement'''
    if len(p) == 3:
        p[0] = Node("DECLARACIONES", p[1].children + [p[2]])
    else:
        p[0] = Node("DECLARACIONES", [p[1]])

def p_declaracion(p):
    '''declaracion : INT VAR PYC
                   | CHAR VAR PYC'''
    global id_contador
    if p[2] not in tabla_simbolos:
            tabla_simbolos[p[2]] = {"id": id_contador, "tipo": p[1], "valor": None}
            id_contador += 1
    print(f"Declaración de variable: {p[2]} (tipo {p[1]}, ID {tabla_simbolos[p[2]]['id']})")
    p[0] = Node("DECLARACION", value=f"{p[1]} {p[2]}")

#---------------------------------------
def evaluar_expresion(node):
    """Evalúa una expresión aritmética o variable y devuelve su valor."""
    if node.type == "NUM":
        return int(node.value)  # Asegurar conversión a número
    elif node.type == "VAR":
        if node.value in tabla_simbolos and tabla_simbolos[node.value]["valor"] is not None:
            return tabla_simbolos[node.value]["valor"]
        else:
            print(f"Error: La variable '{node.value}' no tiene un valor asignado.")
            return None
    elif node.type in ["+", "-", "*", "/"]:
        left = evaluar_expresion(node.children[0])
        right = evaluar_expresion(node.children[1])
        if left is not None and right is not None:
            if node.type == "+":
                return left + right
            elif node.type == "-":
                return left - right
            elif node.type == "*":
                return left * right
            elif node.type == "/":
                return left / right if right != 0 else None
    return None


#----------------------------------------

def p_asignacion(p):
    'asignacion : VAR IGUAL expresion PYC'
    valor = evaluar_expresion(p[3])

    if valor is not None:
        print(f"Asignación: {p[1]} = {valor}")
        # Actualizar o insertar en la tabla de símbolos
        if p[1] in tabla_simbolos:
            tabla_simbolos[p[1]]["valor"] = valor
        else:
            tabla_simbolos[p[1]] = {"tipo": "desconocido", "valor": valor}

    p[0] = Node("ASIGNACION", [Node("VAR", value=p[1]), p[3]])



def p_if_else_statement(p):
    'if_statement : IF PAR_L expresion PAR_R bloque ELSE bloque'
    print(f"Estructura if-else: {p[3].value if hasattr(p[3], 'value') else 'expresión'}")
    p[0] = Node("IF-ELSE", [p[3], p[5], p[7]])

def p_while_statement(p):
    'while_statement : WHILE PAR_L expresion PAR_R bloque'
    print(f"Estructura while: {p[3].value if hasattr(p[3], 'value') else 'expresión'}")
    p[0] = Node("WHILE", [p[3], p[5]])




def p_bloque(p):
    'bloque : LLAVE_L declaraciones LLAVE_R'
    p[0] = Node("BLOQUE", [p[2]])

def p_expresion(p):
    '''expresion : expresion SUM expresion
                 | expresion RES expresion
                 | expresion MUL expresion
                 | expresion DIV expresion'''
    print(f"Operación: {p[1].value if hasattr(p[1], 'value') else 'expresión'} {p[2]} {p[3].value if hasattr(p[3], 'value') else 'expresión'}")
    p[0] = Node(p[2], [p[1], p[3]])

def p_expresion_relacional(p):
    '''expresion : expresion MAYOR expresion
                 | expresion MENOR expresion'''
    print(f"Operación relacional: {p[1].value if hasattr(p[1], 'value') else 'expresión'} {p[2]} {p[3].value if hasattr(p[3], 'value') else 'expresión'}")
    p[0] = Node(p[2], [p[1], p[3]])

def p_expresion_numero(p):
    'expresion : NUM'
    print(f"Número: {p[1]}")
    p[0] = Node("NUM", value=p[1])

def p_expresion_var(p):
    'expresion : VAR'
    print(f"Uso de variable: {p[1]}")
    p[0] = Node("VAR", value=p[1])

def p_error(p):
    if p:
        print(f"Error de sintaxis en '{p.value}'")
    else:
        print("Error de sintaxis: código incompleto o inesperado.")

# Construcción del analizador sintáctico
parser = yacc.yacc()

def generar_arbol(node, graph=None, parent=None, count=[0]):
    if graph is None:
        graph = graphviz.Digraph()
    node_id = str(count[0])
    count[0] += 1
    label = node.type if node.value is None else f"{node.type}({node.value})"
    graph.node(node_id, label)
    if parent is not None:
        graph.edge(parent, node_id)
    for child in node.children:
        generar_arbol(child, graph, node_id, count)
    return graph

def prueba_sintactica(data):
    gram = parser.parse(data)
    if gram:
        arbol = generar_arbol(gram)
        arbol.render('arbol', format='png', cleanup=True)
        print("Árbol de análisis sintáctico generado y guardado como 'arbol.png'.")
        try:
            os.startfile("arbol.png")  
        except AttributeError:
            os.system("xdg-open arbol.png")
    else:
        print("Error en la sintaxis.")

def mostrar_tabla_simbolos():
    if not tabla_simbolos:
        print("\n La tabla de símbolos está vacía.")
        return
    print("\n--- Tabla de Símbolos ---")
    print("{:<5} {:<10} {:<10} {:<10}".format("ID", "VARIABLE", "TIPO", "VALOR"))
    print("-" * 40)
    for var, info in tabla_simbolos.items():
        id_var = info["id"]
        tipo = info["tipo"]
        valor = info["valor"] if info["valor"] is not None else "N/A"
        print("{:<5} {:<10} {:<10} {:<10}".format(id_var, var, tipo, valor))
    print("-" * 40)



# ---------------------- FUNCIONES DEL MENÚ ----------------------
def ingreso_datos():
    print("--------------------------------------------------")
    print("\t--- Ingreso de texto en el editor ---")
    global code
    lines = []
    while True:
        line = input()
        if line.lower() == "exit":
            break
        lines.append(line)
    code = "\n".join(lines)
    print("--------------------------------------------------")
    print("Código ingresado para análisis:\n", code)
    print("--------------------------------------------------")

def lexico():
    print("--------------------------------------------------")
    print("\t--- Análisis léxico ---")
    lexer.input(code)
    for tok in lexer:
        print(tok)
    print("--------------------------------------------------")

def sintactico():
    print("--------------------------------------------------")
    print("\t--- Análisis sintáctico en árbol ---")
    try:
        prueba_sintactica(code)  # Función que genera el árbol sintáctico
        print("Análisis sintáctico exitoso.")
    except Exception as e:
        print(f"Error de sintaxis: {e}")
    print("--------------------------------------------------")


def analizador_semantico():
    print("--------------------------------------------------")
    print("\t--- Analizador Semántico ---")
   # ejecutar_analizador_semantico(code)  # Función que analiza semánticamente el código
    print("--------------------------------------------------")

def codigo_intermedio():
    print("--------------------------------------------------")
    print("\t--- Código Intermedio ---")
    #generar_codigo_intermedio(code)  # Función que genera código intermedio
    print("--------------------------------------------------")

def salir():
    print("\t--- Feliz Día ---")
    print("--------------------------------------------------")
    exit()

opciones = {
    "1": ingreso_datos,
    "2": lexico,
    "3": sintactico,
    "4": mostrar_tabla_simbolos,
    "5": analizador_semantico,
    "6": codigo_intermedio,
    "7": salir
}

code = ""

if __name__ == "__main__":
    while True:
        print("\n--- MENU PRINCIPAL ---")
        print("1. Ingreso de texto en el editor")
        print("2. Análisis léxico")
        print("3. Análisis sintáctico en árbol")
        print("4. Tabla de símbolos")
        print("5. Analizador Semántico")
        print("6. Código intermedio")
        print("7. Salir")

        opcion = input("Escoja una opción: ")
        if opcion in opciones:
            opciones[opcion]()
        else:
            print("Opción incorrecta, por favor intente nuevamente.")
