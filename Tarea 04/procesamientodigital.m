#Comprobar si es Octave
if (exist('OCTAVE_VERSION','builtin')~=0)
  pkg load signal;
  pkg load database;
end

#Conexión a la base de datos
conn = pq_connect(setdbopts('dbname','postgres','host','localhost','port','5432','user','postgres','password','koala'));

opcion = 0;

while opcion ~= 5
  disp('========== Menú Principal ==========');
  disp('1) Grabar audio');
  disp('2) Reproducir audio');
  disp('3) Graficar señal');
  disp('4) Graficar espectro de frecuencia');
  disp('5) Salir');

  opcion = input('Ingrese su eleccion: ');

  switch opcion
      case 1
          try
              duracion = input('Ingrese la duracion de la grabacion en segundos: ');
              disp('Comenzando la grabacion...');
              recObj = audiorecorder;
              recordblocking(recObj, duracion);
              disp('Grabación finalizada.');
              data = getaudiodata(recObj);
              nombreArchivo = 'audio.wav';
              audiowrite(nombreArchivo, data, recObj.SampleRate);
              disp('Archivo de audio guardado correctamente');

              #Guardar en la base de datos
              fid = fopen(nombreArchivo, 'rb');
              audioBytes = fread(fid, '*uint8');
              fclose(fid);
              query = sprintf("INSERT INTO audios (nombre, audio) VALUES ('%s', decode('%s','base64'))", ...
                  nombreArchivo, base64_encode(audioBytes));
              pq_exec_params(conn, query);
              disp('Audio guardado en la base de datos.');

          catch
              disp(['Error al grabar el audio: ', e.message]);
          end

      case 2
          try
              disp('Reproduciendo audio...');
              [data, fs] = audioread('audio.wav');
              sound(data, fs);
          catch
              disp('Error al reproducir el audio.');
          end

      case 3
          try
              disp('Graficando señal...');
              [data, fs] = audioread('audio.wav');
              tiempo = linspace(0, length(data)/fs, length(data));
              plot(tiempo, data);
              xlabel('Tiempo (s)');
              ylabel('Amplitud');
              title('Audio');
          catch
              disp('Error al graficar el audio.');
          end

      case 4
          try
              disp('Graficando espectro de frecuencia...');
              [audio, fs] = audioread('audio.wav');
              N = length(audio);
              f = linspace(0, fs/2, N/2+1);
              ventana = hann(N);
              Sxx = pwelch(audio, ventana, 0, N, fs);
              plot(f, 10*log10(Sxx(1:N/2+1)));
              xlabel('Frecuencia (Hz)');
              ylabel('Densidad espectral de potencia (dB/Hz)');
              title('Espectro de Frecuencia de la señal grabada');
          catch
              disp('Error al graficar el audio.');
          end

      case 5
          disp('Saliendo del programa...');
      otherwise
          disp('Opción no válida.');
  end
end
