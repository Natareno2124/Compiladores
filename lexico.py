from ply.lex import lex
import ply.yacc as yacc
import graphviz
import os
from graphviz import Digraph
import re

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
def evaluar_expresion(nodo, contexto):
    if nodo.type == "NUM":
        return int(nodo.value)
    elif nodo.type == "VAR":
        # Se asume que 'nodo.value' es el nombre de la variable.
        if nodo.value in contexto and contexto[nodo.value]["valor"] is not None:
            return contexto[nodo.value]["valor"]
        else:
            print(f"Error: La variable '{nodo.value}' no tiene un valor asignado.")
            return None
    elif nodo.type in ["+", "-", "*", "/"]:
        left = evaluar_expresion(nodo.children[0], contexto)
        right = evaluar_expresion(nodo.children[1], contexto)
        if left is not None and right is not None:
            if nodo.type == "+":
                return left + right
            elif nodo.type == "-":
                return left - right
            elif nodo.type == "*":
                return left * right
            elif nodo.type == "/":
                return left / right if right != 0 else None
    return None


#----------------------------------------

def p_asignacion(p):
    'asignacion : VAR IGUAL expresion PYC'
    valor = evaluar_expresion(p[3], tabla_simbolos)

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


#---------------------------SEMANTICO------------------------------------------------
def decorar_nodo(original, contexto):

    # Caso 1: Declaración (se espera que original.value sea "int x" o "char y")
    if original.type == "DECLARACION":
        tokens = original.value.split()
        if len(tokens) == 2:
            tipo, var_name = tokens
            if var_name not in tabla_simbolos:
                tabla_simbolos[var_name] = {"tipo": tipo, "valor": None}
            else:
                print(f"Advertencia: La variable '{var_name}' ya ha sido declarada.")
            new_node = Node("VAR_DECL", value=f"{tipo} = {var_name}")
            tipo_node = Node("TIPO", value=tipo)
            id_node = Node("ID", value=var_name)
            new_node.children = [tipo_node, id_node]
        else:
            new_node = Node(original.type, value=original.value)
    
    # Caso 2: Asignación (se espera que original.children[0] sea una variable y la expresión)
    elif original.type == "ASIGNACION":
        var_node = original.children[0]  
        var_name = var_node.value
        if var_name not in tabla_simbolos:
            print(f"Error semántico: La variable '{var_name}' no ha sido declarada.")
            new_node = Node("ASIGNACION", value=f"{var_name} = Error")
        else:
            valor = evaluar_expresion(original.children[1], contexto)
            tabla_simbolos[var_name]["valor"] = valor
            tipo = tabla_simbolos[var_name]["tipo"]
            new_node = Node("ASIGNACION", value=f"{var_name} = {valor}")
            tipo_node = Node("TIPO", value=tipo)
            id_node = Node("ID", value=var_name)
            if valor is not None:
                valor_node = Node("VALOR", value=valor)
                id_node.children = [valor_node]
            new_node.children = [tipo_node, id_node]
    
    # Caso 3: Uso de variable en una expresión
    elif original.type == "VAR":
        var_name = original.value
        if var_name not in tabla_simbolos:
            print(f"Error semántico: Uso de variable '{var_name}' sin declarar.")
            new_node = Node("VAR", value=f"{var_name} (no declarada)")
            tipo_node = Node("TIPO", value="Desconocido")
            valor_node = Node("VALOR", value="Error")
            new_node.children = [tipo_node, valor_node]
        else:
            tipo = tabla_simbolos[var_name]["tipo"]
            valor = tabla_simbolos[var_name]["valor"]
            new_node = Node("VAR", value=f"{var_name} = {valor}")
            tipo_node = Node("TIPO", value=tipo)
            valor_node = Node("VALOR", value=valor)
            new_node.children = [tipo_node, valor_node]
    
    else:
        new_node = Node(original.type, value=original.value)
    
    for child in original.children:
        new_child = decorar_nodo(child, contexto)
        new_node.children.append(new_child)
    
    return new_node

def generar_arbol_semantico_decorado(sintactico_root):
    contexto = {}
    sem_tree = decorar_nodo(sintactico_root, contexto)
    return sem_tree

def generar_arbol_semantico(dot_root):
    dot = Digraph(format="png")
    dot.attr(rankdir='TB', ordering='out')
    
    def recorrer(n, padre_id=None):
        n_id = str(id(n))
        label = n.type
        if n.value is not None:
            label += f"\n{n.value}"
        dot.node(n_id, label, shape="box", style="filled", fillcolor="lightblue")
        if padre_id:
            dot.edge(padre_id, n_id)
        for child in n.children:
            recorrer(child, n_id)
    
    recorrer(dot_root)
    dot.render('arbol_semantico', format='png', cleanup=True)
    return dot


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
        prueba_sintactica(code)  
        print("Análisis sintáctico exitoso.")
    except Exception as e:
        print(f"Error de sintaxis: {e}")
    print("--------------------------------------------------")


def analizador_semantico(code):
    print("--------------------------------------------------")
    print("\t--- Análisis Semántico en árbol ---")
    gram = parser.parse(code)
    if not gram:
        print("Error de sintaxis. No se puede realizar el análisis semántico.")
        return
    semantico_root = generar_arbol_semantico_decorado(gram)
    arbol_semantico = generar_arbol_semantico(semantico_root)
    arbol_semantico.render('arbol_semantico', format='png', cleanup=True)
    print("Árbol semántico generado y guardado como 'arbol_semantico.png'.")
    try:
        os.startfile("arbol_semantico.png")
    except AttributeError:
        os.system("xdg-open arbol_semantico.png")
    print("--------------------------------------------------")


def codigo_intermedio():
    print("--------------------------------------------------")
    print("\t--- Generando Código Intermedio ---")
    print("--------------------------------------------------")
    
    temp_count = 1  
    variable_map = {}  

    def procesar_expresion(expr):
        nonlocal temp_count
        tokens = re.split(r'(\+|\-|\*|/)', expr)
        operadores = []
        operandos = []

        # Separar operandos y operadores
        for token in tokens:
            token = token.strip()
            if token.isdigit() or token in variable_map:
                operandos.append(token)
            elif token in "+-*/":
                while (operadores and
                       precedence[operadores[-1]] >= precedence[token]):
                    op2 = operandos.pop()
                    op1 = operandos.pop()
                    operador = operadores.pop()
                    temp_var = f"t{temp_count}"
                    temp_count += 1
                    print(f"{temp_var} = {op1} {operador} {op2}")
                    operandos.append(temp_var)
                operadores.append(token)

        # Procesar los operadores restantes
        while operadores:
            op2 = operandos.pop()
            op1 = operandos.pop()
            operador = operadores.pop()
            temp_var = f"t{temp_count}"
            temp_count += 1
            print(f"{temp_var} = {op1} {operador} {op2}")
            operandos.append(temp_var)

        return operandos[0]

    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

    lines = code.splitlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith("//"):  
            continue

        
        if "int" in line or "char" in line:
            var = line.split()[1].replace(";", "")
            variable_map[var] = None
            continue

        
        if "=" in line:
            var, expr = line.split("=")
            var = var.strip()
            expr = expr.strip().replace(";", "")

            
            resultado = procesar_expresion(expr)
            print(f"{var} = {resultado}")
            variable_map[var] = resultado

    print("--------------------------------------------------")

def generador_ensamblador():
    print("--------------------------------------------------")
    print("\t--- Generador de Código Ensamblador ---")
    print("--------------------------------------------------")
    
    temp_count = 1  
    variable_map = {}  

    def procesar_expresion_ensamblador(expr):
        nonlocal temp_count
        tokens = re.split(r'(\+|\-|\*|/)', expr)
        operadores = []
        operandos = []

        for token in tokens:
            token = token.strip()
            if token.isdigit() or token in variable_map:
                operandos.append(token)
            elif token in "+-*/":
                while (operadores and
                       precedence[operadores[-1]] >= precedence[token]):
                    op2 = operandos.pop()
                    op1 = operandos.pop()
                    operador = operadores.pop()
                    temp_var = f"t{temp_count}"
                    temp_count += 1

                    if operador == "+":
                        ensamblador.append(f"MOV AX, {op1}")
                        ensamblador.append(f"ADD AX, {op2}")
                    elif operador == "-":
                        ensamblador.append(f"MOV AX, {op1}")
                        ensamblador.append(f"SUB AX, {op2}")
                    elif operador == "*":
                        ensamblador.append(f"MOV AX, {op1}")
                        ensamblador.append(f"MUL {op2}")
                    elif operador == "/":
                        ensamblador.append(f"MOV AX, {op1}")
                        ensamblador.append(f"DIV {op2}")

                    ensamblador.append(f"MOV {temp_var}, AX")
                    operandos.append(temp_var)
                operadores.append(token)

        while operadores:
            op2 = operandos.pop()
            op1 = operandos.pop()
            operador = operadores.pop()
            temp_var = f"t{temp_count}"
            temp_count += 1

            if operador == "+":
                ensamblador.append(f"MOV AX, {op1}")
                ensamblador.append(f"ADD AX, {op2}")
            elif operador == "-":
                ensamblador.append(f"MOV AX, {op1}")
                ensamblador.append(f"SUB AX, {op2}")
            elif operador == "*":
                ensamblador.append(f"MOV AX, {op1}")
                ensamblador.append(f"MUL {op2}")
            elif operador == "/":
                ensamblador.append(f"MOV AX, {op1}")
                ensamblador.append(f"DIV {op2}")

            ensamblador.append(f"MOV {temp_var}, AX")
            operandos.append(temp_var)

        return operandos[0]

    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
    ensamblador = []  

    lines = code.splitlines()  

    for line in lines:
        line = line.strip()
        if not line or line.startswith("//"):  
            continue

        # Procesar declaraciones
        if "int" in line or "char" in line:
            var = line.split()[1].replace(";", "")
            ensamblador.append(f"{var} DW ?")  
            variable_map[var] = var
            continue

        if "=" in line:
            var, expr = line.split("=")
            var = var.strip()
            expr = expr.strip().replace(";", "")

            # Procesar la expresión respetando la jerarquía
            resultado = procesar_expresion_ensamblador(expr)
            ensamblador.append(f"MOV {var}, {resultado}")
            variable_map[var] = var

    print("\n--- Código Ensamblador Generado ---")
    for instr in ensamblador:
        print(instr)
    print("--------------------------------------------------")

def ejecutar_codigo():
    print("--------------------------------------------------")
    print("\t--- Ejecución de Código .EXE---")
    print("--------------------------------------------------")
    try:
        gram = parser.parse(code)
        if not gram:
            print("Error de sintaxis. No se puede ejecutar el código.")
            return
        print("Resultado de ejecución:")

        def recorrer_y_ejecutar(nodo):
            if nodo.type == "DECLARACION":
                # Ya manejado en la declaración
                pass
            elif nodo.type == "ASIGNACION":
                var_name = nodo.children[0].value
                valor = evaluar_expresion(nodo.children[1], tabla_simbolos)
                if var_name in tabla_simbolos:
                    tabla_simbolos[var_name]["valor"] = valor
                else:
                    tabla_simbolos[var_name] = {"tipo": "desconocido", "valor": valor}
                print(f"{var_name} = {valor}")
            for child in nodo.children:
                recorrer_y_ejecutar(child)

        recorrer_y_ejecutar(gram)
        print("--------------------------------------------------")
    except Exception as e:
        print(f"Error durante la ejecución: {e}")


def salir():
    print("\t--- Feliz Día ---")
    print("--------------------------------------------------")
    exit()

opciones = {
                "1": ingreso_datos,
                "2": lexico,
                "3": sintactico,
                "4": mostrar_tabla_simbolos,
                "5": lambda: analizador_semantico(code),
                "6": codigo_intermedio,
                "7": generador_ensamblador,
                "8": ejecutar_codigo,
                "9": salir
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
        print("7. Generador de Código Ensamblador")
        print("8. Ejecutar Código .EXE")
        print("9. Salir")
        print("--------------------------------------------------")

        opcion = input("Escoja una opción: ")
        if opcion in opciones:
            opciones[opcion]()
        else:
            print("Opción incorrecta, por favor intente nuevamente.")
#--------------------------------------------------------------------


