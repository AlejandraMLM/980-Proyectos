import cv2
import tensorflow as tf
import numpy as np

# Cargar el modelo entrenado
model = tf.keras.models.load_model(r"C:\Users\Alejandra\Desktop\980-Proyectos\Tarea TensorFlow\mnist_model.keras")


# Iniciar la captura del video
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if ret == False:
        break
     
    # Crear una imagen vacía donde se mostrará la predicción
    image_prediction = np.zeros(shape=(250, 200, 3))

    # Convertir el frame a escala de grises, aplicar umbral binario inverso,
    # detectar contornos externos y seleccionar los 5 más grandes por área 
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(frame_gray, 127, 255, cv2.THRESH_BINARY_INV) 
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
   
    # cv2.drawContours(frame, contours, -1, (255, 0, 0), 3)
    for cnt in contours:
        # Filtrar contornos pequeños
        if cv2.contourArea(cnt) > 3000:
            x, y, w, h = cv2.boundingRect(cnt)

            # Considerar los contornos más altos que anchos (dígitos)
            if w / h < 1:
                # Ampliar el rectángulo de recorte verticalmente
                y_ini = y - h//10
                y_fin = y + h + h//10
                
                # Calcular el margen horizontal para centrar el recorte
                w_portion = (int(y_fin - y_ini) - w) // 2

                # Validar que el recorte esté dentro de la imagen
                if y_ini > 0 and (x - w_portion) > 0:
                    # Reiniciar la imagen de predicción
                    image_prediction = np.zeros(shape=(250, 200, 3))

                    # Recortar la región de interés del dígito y 
                    # redimensionarlo a 28 x 28
                    crop_image = binary[y_ini: y_fin, x - w_portion: x + w + w_portion]
                    crop_resize_image = cv2.resize(crop_image, (28, 28))

                    # Normalizar los valores de píxel entre 0 y 1, 
                    # luego aplanarla, como se hizo en el entrenamiento del modelo
                    input_image = crop_resize_image.astype("float32") / 255.0
                    input_image = input_image.reshape(1, 28 * 28)

                    # Realizar la predicción con el modelo
                    prediction = model.predict(input_image)
                    predicted_class = prediction.argmax(axis=1)[0]

                    # Dibujar rectángulos en el frame: el original y el extendido
                    cv2.rectangle(frame, (x, y), (x + w, y+ h), (255, 0, 0), 1)
                    cv2.rectangle(frame, (x - w_portion, y_ini), (x + w + w_portion, y_fin), (0, 255, 0), 1)

                    # Visualizar el resultado en la imagen de predicción
                    cv2.putText(image_prediction, 
                                f"Prediction ({prediction[0][predicted_class]*100:.1f}%):", 
                                (5, 20), 
                                1, 
                                1.2, 
                                (0, 255, 255), 
                                1)
                    cv2.putText(image_prediction, 
                                str(predicted_class), 
                                (5, 240), 
                                1, 
                                20,
                                (0, 255, 255),
                                3)

                    # Visualizar las ventanas de recorte
                    cv2.imshow("crop_image", crop_image)
                    cv2.imshow("crop_resize_image", crop_resize_image)

    cv2.imshow("Frame", frame)
    cv2.imshow("image_prediction", image_prediction)
    cv2.imshow("binary", binary)
    
    # Salir con la tecla ESC (código ASCII 27)
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Liberar la cámara y cerrar todas las ventanas
cap.release()
cv2.destroyAllWindows()