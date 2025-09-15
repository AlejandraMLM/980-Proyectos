#OBJETOS NUMERICOS
375
3.75e2
3.75E2
0x177

#numero_inicial:salto:numero_final
1:10
1:0.5:10
1:0.6:10

#matrices
M = [1, 2, 3; 4, 5, 6; 7, 8, 9]
M = [1:4;5:8]

#Cadena de caracteres
'Cadena de string'
"Cadena de string"
"\\"
"\a"

#Estructuras
x = {}
x.secuencia = 1:5
x.matriz = [1,2;44,5]
x.string = 'Secuencia '

#Estructuras dentro de estructuras
x.estructura = {}
x.estructura.numero = 0x177
x.estructura.letra = 'A'
x

#OPERADORES
#operadores aritmeticos
z = 2
y = 3

z + y
z - y
z * y
z / y
++z # z = z + 1
--z # z = z - 1

#operadores de comparacion
a = 2
b = 3

a < b
a <= b
a == b
a > b
a >= b
a != b

#operadores booleanos
j = 1
k = 0

j & k   #and
j | k   #or
not (j) #not

