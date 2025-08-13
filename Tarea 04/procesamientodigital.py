import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import psycopg2
import base64
import wave

# Conexión a la base de datos
conn = psycopg2.connect("dbname=postgres user=postgres password=koala host=localhost port=5432")
cur = conn.cursor()

opcion = 0
while opcion != 5:
    print("\n========== Menú Principal ==========")
    print("1) Grabar audio")
    print("2) Reproducir audio")
    print("3) Graficar señal")
    print("4) Graficar espectro de frecuencia")
    print("5) Salir")

    try:
        opcion = int(input("Ingrese su elección: "))
    except ValueError:
        opcion = 0

    if opcion == 1:
        duracion = int(input("Ingrese la duración de la grabación (segundos): "))
        print("Comenzando la grabación...")
        audio = sd.rec(int(duracion * 44100), samplerate=44100, channels=1, dtype='int16')
        sd.wait()
        print("Grabación finalizada.")

        nombre_archivo = "audio.wav"
        with wave.open(nombre_archivo, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(audio.tobytes())

        print("Archivo guardado correctamente.")

        with open(nombre_archivo, "rb") as f:
            audio_bytes = f.read()
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        cur.execute("INSERT INTO audios (nombre, audio) VALUES (%s, decode(%s, 'base64'))",
                    (nombre_archivo, audio_base64))
        conn.commit()
        print("Audio guardado en la base de datos.")

    elif opcion == 2:
        try:
            print("Reproduciendo audio...")
            with wave.open("audio.wav", 'rb') as wf:
                data = wf.readframes(wf.getnframes())
                audio = np.frombuffer(data, dtype='int16')
                sd.play(audio, wf.getframerate())
                sd.wait()
        except:
            print("Error al reproducir el audio.")

    elif opcion == 3:
        try:
            with wave.open("audio.wav", 'rb') as wf:
                data = wf.readframes(wf.getnframes())
                audio = np.frombuffer(data, dtype='int16')
                tiempo = np.linspace(0, len(audio) / wf.getframerate(), num=len(audio))
            plt.plot(tiempo, audio)
            plt.xlabel("Tiempo (s)")
            plt.ylabel("Amplitud")
            plt.title("Audio")
            plt.show()
        except:
            print("Error al graficar la señal.")

    elif opcion == 4:
        try:
            with wave.open("audio.wav", 'rb') as wf:
                data = wf.readframes(wf.getnframes())
                audio = np.frombuffer(data, dtype='int16')
                fs = wf.getframerate()
            N = len(audio)
            freqs = np.fft.rfftfreq(N, 1/fs)
            espectro = np.abs(np.fft.rfft(audio))**2
            plt.plot(freqs, 10 * np.log10(espectro))
            plt.xlabel("Frecuencia (Hz)")
            plt.ylabel("Potencia (dB)")
            plt.title("Espectro de Frecuencia")
            plt.show()
        except:
            print("Error al graficar el espectro.")

    elif opcion == 5:
        print("Saliendo del programa...")
    else:
        print("Opción no válida.")
