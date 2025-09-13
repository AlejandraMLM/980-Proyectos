import tkinter as tk
from tkinter import ttk, messagebox
import smtplib
import imaplib
import email

# Configuración de Gmail
GMAIL_SMTP = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587
GMAIL_IMAP = "imap.gmail.com"
GMAIL_IMAP_PORT = 993

EMAIL_ADDRESS = "alejandramglmr@gmail.com"        # Tu correo
EMAIL_PASSWORD = "ftqwxxucxgjgnrki"               # Tu contraseña de aplicación (sin espacios)


# Función para enviar correos

def enviar_correo():
    destinatario = entry_destinatario.get()
    asunto = entry_asunto.get()
    mensaje = text_mensaje.get("1.0", tk.END)

    try:
        with smtplib.SMTP(GMAIL_SMTP, GMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            mensaje_email = f"Subject: {asunto}\n\n{mensaje}"
            server.sendmail(EMAIL_ADDRESS, destinatario, mensaje_email)
        messagebox.showinfo("Éxito", "Correo enviado correctamente")
    except Exception as e:
        messagebox.showerror("Error", f"Error al enviar el correo: {e}")


# Función para recibir correos

def recibir_correos():
    try:
        mail = imaplib.IMAP4_SSL(GMAIL_IMAP, GMAIL_IMAP_PORT)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")

        _, data = mail.search(None, "ALL")
        mail_ids = data[0].split()

        mensajes = ""
        for num in mail_ids[-5:]:  # Solo últimos 5 correos
            _, data = mail.fetch(num, "(RFC822)")
            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    asunto = msg["subject"]
                    remitente = msg["from"]
                    cuerpo = ""

                    if msg.is_multipart():
                        for part in msg.walk():
                            ctype = part.get_content_type()
                            cdispo = str(part.get("Content-Disposition"))
                            if ctype == "text/plain" and "attachment" not in cdispo:
                                cuerpo = part.get_payload(decode=True).decode(errors="ignore")
                                break
                    else:
                        cuerpo = msg.get_payload(decode=True).decode(errors="ignore")

                    mensajes += f"De: {remitente}\nAsunto: {asunto}\nCuerpo:\n{cuerpo}\n{'-'*50}\n"

        text_recibidos.delete("1.0", tk.END)
        text_recibidos.insert(tk.END, mensajes if mensajes else "No hay correos nuevos.")

        mail.close()
        mail.logout()
    except Exception as e:
        messagebox.showerror("Error", f"Error al recibir correos: {e}")


# Interfaz gráfica con Tkinter

ventana = tk.Tk()
ventana.title("Correo Gmail")

# Remitente (fijo, solo lectura)
label_remitente = ttk.Label(ventana, text="Remitente (tu cuenta):")
label_remitente.grid(row=0, column=0, sticky=tk.W)
entry_remitente = ttk.Entry(ventana, width=50)
entry_remitente.insert(0, EMAIL_ADDRESS)
entry_remitente.config(state="readonly")
entry_remitente.grid(row=0, column=1)

# Destinatario
label_destinatario = ttk.Label(ventana, text="Destinatario:")
label_destinatario.grid(row=1, column=0, sticky=tk.W)
entry_destinatario = ttk.Entry(ventana, width=50)
entry_destinatario.grid(row=1, column=1)

# Asunto
label_asunto = ttk.Label(ventana, text="Asunto:")
label_asunto.grid(row=2, column=0, sticky=tk.W)
entry_asunto = ttk.Entry(ventana, width=50)
entry_asunto.grid(row=2, column=1)

# Mensaje
label_mensaje = ttk.Label(ventana, text="Mensaje:")
label_mensaje.grid(row=3, column=0, sticky=tk.W)
text_mensaje = tk.Text(ventana, width=50, height=10)
text_mensaje.grid(row=3, column=1)

# Botón enviar
boton_enviar = ttk.Button(ventana, text="Enviar", command=enviar_correo)
boton_enviar.grid(row=4, column=1, sticky=tk.E)

# Botón recibir correos
boton_recibir = ttk.Button(ventana, text="Recibir Correos", command=recibir_correos)
boton_recibir.grid(row=5, column=0, sticky=tk.W)

# Área de correos recibidos
text_recibidos = tk.Text(ventana, width=80, height=20)
text_recibidos.grid(row=6, column=0, columnspan=2)

ventana.mainloop()
