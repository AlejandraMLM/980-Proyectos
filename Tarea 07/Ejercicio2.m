#Estructuras de control de flujo
x = 1
y = 0

if(x > y)
  'X es mayor a Y'
elseif (x == y)
  'X y Y son iguales'
else
  'Y es mayor a X'
endif

#ejemplo 2
x = 1
y = 0
z = -5

if(x > y & z < 0)
  'X es mayor a Y y Z es menor a 0'
elseif (x == y | z < 0)
  'X y Y son iguales'
else
  'Y es mayor a X'
endif


#Estructuras de control while

x = 1
y = 0
z = -5

while(z < y )
    'Valor de z'
    z
    ++z
endwhile

#Estructuras de control for
fib = ones(1, 10);
for i = 3:10
  fib(i) = fib(i-1) + fib(i-2);
endfor
fib

#Estructuras de control try catch

try
  m = [1:5;10:15]
catch
  'NO SE PUDO EJERCUTAR, se continua con la ejecucion normal del codigo'
end_try_catch
#Operaciones basicas con matrices
M = [1,2,7; 4,5,11 ; 0.1,0.2,0.3]
N =  double([0,1,2; 8,10,12; 0x177,0x176,0x125])
M + N
M - N
M * N
cross(M,N) #M X N
dot(M, N) #Producto punto
M' #Matriz traspuesta




