#FUNCIONES
#Ejemplo1
function hipo = hipotenusa (a, b)
  hipo = sqrt(a.^2 + b^2);
endfunction

x = hipotenusa (1,2)


#Ejemplo 2
function [hipo,a_cuadrada]= hipotenusa (a, b)
  hipo = sqrt(a.^2 + b^2);
  a_cuadrada = a.^2;
endfunction

[x,b] = hipotenusa(1,2)

# GRAFICAS
function y = f(x)
  y = 4*x.^3 + 10 * x.^2 + 6
endfunction

x = [-3:0.1:1];
plot(x, funcion(x))

#GRAFICAS

#CAMBIO DE COLOR
x = linspace(-3,1,50)
plot(x, funcion(x), 'Color','red')

#CAMBIO DE LINEA
x = linspace(-3,1,50)
plot(x, funcion(x), 'LineStyle',':');

x = linspace(-3,1,50)
stem(x, funcion(x), 'LineStyle',':');
title('Titulo')
ylabel('Eje y')
xlabel('Eje x')
legend('Funcion')

#GRAFICA CON DOS FUNCIONES
x = [0:0.1:4*pi];
y1 = sin(x);
y2 = cos(x);
hold on;
p1 = plot(x,y1);
p2 = plot(x,y2);
set(p1, 'Color','red','LineWidth',2);
set(p2, 'Color','blue','LineWidth',1);
ylabel('EJE Y');
xlabel('EJE X');
title('Seno y Coseno');
legend('Seno','Coseno');
hold off;

