#Facturación Gasolinera

# Comprobar si es Octave
if (exist('OCTAVE_VERSION','builtin') ~= 0)
  pkg load signal;
  pkg load database;
end

# Ruta del archivo de facturas
archivo_facturas = "C:\\Users\\Alejandra\\Desktop\\980-Proyectos\\Parcial 01\\salida.txt";

# Conexión a la base de datos
conn = pq_connect(setdbopts( ...
    'dbname','gasolinera', ...
    'host','localhost', ...
    'port','5432', ...
    'user','postgres', ...
    'password','koala'));

# Crear tabla si no existe
create_table = [ ...
"CREATE TABLE IF NOT EXISTS facturas_gasolina (", ...
" cliente TEXT NOT NULL,", ...
" placa TEXT NOT NULL,", ...
" combustible TEXT NOT NULL,", ...
" litros REAL NOT NULL,", ...
" total REAL NOT NULL );" ];

pq_exec_params(conn, create_table);

#Funciones auxiliares

function nombre = pedir_nombre()
  valido = false;
  while ~valido
    nombre = strtrim(input("Ingrese nombre y apellido: ", "s"));
    if ~isempty(regexp(nombre, "^[A-Za-z]+( [A-Za-z]+)+$", "once"))
      valido = true;
    else
      disp("Formato inválido. Ejemplo: Juan Pérez");
    endif
  endwhile
endfunction

function placa = pedir_placa()
  valido = false;
  while ~valido
    placa = upper(strtrim(input("Ingrese placa (P123ABC): ", "s")));
    if ~isempty(regexp(placa, "^P[0-9]{3}[A-Z]{3}$", "once"))
      valido = true;
    else
      disp("Formato inválido. Ejemplo: P123ABC");
    endif
  endwhile
endfunction

function valor = pedir_entero(msg, minval, maxval)
  valido = false;
  while ~valido
    valor = str2num(input(msg, "s"));
    if isempty(valor) || ~isscalar(valor) || valor < minval || valor > maxval
      printf("Debe ingresar un entero válido entre %d y %d\n", minval, maxval);
    else
      valido = true;
    endif
  endwhile
endfunction

function valor = pedir_flotante(msg, minval)
  valido = false;
  while ~valido
    valor = str2double(input(msg, "s"));
    if isnan(valor) || valor < minval
      printf("Debe ingresar un número mayor que %.2f\n", minval);
    else
      valido = true;
    endif
  endwhile
endfunction

#Logica del programa

precios = {
  1, "Gasolina Regular", 7.84;
  2, "Gasolina Premium", 8.23;
  3, "Diesel", 7.39
};

function guardar_factura(conn, archivo_facturas, cliente, placa, combustible, litros, total)
  # Guardar en archivo
  fid = fopen(archivo_facturas, "a");
  fprintf(fid, "%s,%s,%s,%.2f,%.2f\n", cliente, placa, combustible, litros, total);
  fclose(fid);

  # Guardar en BD
  query = "INSERT INTO facturas_gasolina (cliente, placa, combustible, litros, total) VALUES ($1,$2,$3,$4,$5)";
  pq_exec_params(conn, query, {cliente, placa, combustible, litros, total});
  disp("Factura guardada correctamente.");
endfunction

function mostrar_historial(archivo_facturas)
  disp("\n--- HISTORIAL desde archivo ---");
  fid = fopen(archivo_facturas, "r");
  if fid != -1
    while !feof(fid)
      linea = fgetl(fid);
      if ischar(linea)
        disp([" - " linea]);
      endif
    endwhile
    fclose(fid);
  else
    disp("No hay facturas registradas en archivo.");
  endif
endfunction

function borrar_historial(conn, archivo_facturas)
  disp("\n--- BORRAR HISTORIAL ---");
  disp("1. Borrar una factura específica (por placa)");
  disp("2. Borrar todas las facturas");
  disp("3. Borrar todas las facturas de una placa");
  disp("4. Cancelar");

  opcion = pedir_entero("Seleccione una opción: ", 1, 4);

  if opcion == 1
    placa = pedir_placa();

    # borrar en archivo (solo la primera coincidencia)
    if exist(archivo_facturas, "file")
      fid = fopen(archivo_facturas, "r");
      lineas = {};
      eliminado = false;
      while !feof(fid)
        linea = fgetl(fid);
        if ischar(linea)
          if ~eliminado && ~isempty(strfind(linea, placa))
            eliminado = true; # omitimos esta línea
          else
            lineas{end+1} = linea;
          endif
        endif
      endwhile
      fclose(fid);
      fid = fopen(archivo_facturas, "w");
      for i=1:length(lineas)
        fprintf(fid, "%s\n", lineas{i});
      endfor
      fclose(fid);
      if eliminado
        printf("Factura con placa %s borrada del archivo.\n", placa);
      else
        printf("No se encontró factura con placa %s en el archivo.\n", placa);
      endif
    endif

    # borrar en BD (solo una fila usando CTE)
    query = ["WITH cte AS (SELECT ctid FROM facturas_gasolina WHERE placa=$1 LIMIT 1) ", ...
             "DELETE FROM facturas_gasolina WHERE ctid IN (SELECT ctid FROM cte)"];
    pq_exec_params(conn, query, {placa});
    disp("Factura borrada de la base de datos (si existía).");

  elseif opcion == 2
    # borrar todo
    fid = fopen(archivo_facturas, "w"); fclose(fid);
    disp("Archivo borrado correctamente.");
    pq_exec_params(conn, "DELETE FROM facturas_gasolina");
    disp("Historial en base de datos borrado.");

  elseif opcion == 3
    placa = pedir_placa();
    # borrar todas las facturas de esa placa en archivo
    if exist(archivo_facturas, "file")
      fid = fopen(archivo_facturas, "r");
      lineas = {};
      while !feof(fid)
        linea = fgetl(fid);
        if ischar(linea) && isempty(strfind(linea, placa))
          lineas{end+1} = linea;
        endif
      endwhile
      fclose(fid);
      fid = fopen(archivo_facturas, "w");
      for i=1:length(lineas)
        fprintf(fid, "%s\n", lineas{i});
      endfor
      fclose(fid);
      printf("Facturas con placa %s borradas del archivo (si existían).\n", placa);
    endif
    # borrar en BD
    pq_exec_params(conn, "DELETE FROM facturas_gasolina WHERE placa=$1", {placa});
    printf("Facturas con placa %s borradas de la base de datos (si existían).\n", placa);

  else
    disp("Cancelando borrado. Regresando al menú principal...");
  endif
endfunction

#MENU PRINCIPAL

while true
  disp("\n========== MENÚ PRINCIPAL ==========");
  disp("1. Registrar factura");
  disp("2. Ver historial");
  disp("3. Borrar historial");
  disp("4. Salir");

  opcion = pedir_entero("Seleccione una opción (1-4): ", 1, 4);

  if opcion == 1
    cliente = pedir_nombre();
    placa = pedir_placa();

    disp("\n----- Tipos de combustible -----");
    for i=1:rows(precios)
      printf("%d. %s - Q%.2f por litro\n", precios{i,1}, precios{i,2}, precios{i,3});
    endfor

    tipo = pedir_entero("Seleccione el tipo (1-3): ", 1, 3);
    litros = pedir_flotante("Litros a despachar: ", 0.1);

    combustible = precios{tipo,2};
    total = litros * precios{tipo,3};

    disp("\n--- FACTURA ---");
    printf("Cliente: %s\n", cliente);
    printf("Vehículo: %s\n", placa);
    printf("Combustible: %s\n", combustible);
    printf("Litros: %.2f\n", litros);
    printf("Total a pagar: Q%.2f\n", total);
    disp("---------------------");

    guardar_factura(conn, archivo_facturas, cliente, placa, combustible, litros, total);

  elseif opcion == 2
    mostrar_historial(archivo_facturas);

  elseif opcion == 3
    borrar_historial(conn, archivo_facturas);

  elseif opcion == 4
    disp("Gracias por usar el sistema. Saliendo...");
    break;
  endif
endwhile

# Cerrar conexión
pq_close(conn);

