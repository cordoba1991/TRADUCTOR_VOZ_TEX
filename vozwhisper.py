import os
import whisper
from tkinter import Tk, Button, Label, filedialog, messagebox, Text, Scrollbar, END
from pydub import AudioSegment
from deep_translator import GoogleTranslator
import threading

def adjuntar_audio():
    global ruta_audio
    ruta_audio = filedialog.askopenfilename(
        filetypes=[("Archivos de audio", "*.mp3 *.wav *.ogg *.flac *.m4a")]
    )
    if ruta_audio:
        label_info.config(text=f"Audio seleccionado:\n{os.path.basename(ruta_audio)}")
    else:
        label_info.config(text="No se seleccionó ningún audio.")

def convertir_audio_a_wav(ruta):
    """Convierte cualquier formato de audio a WAV si no es compatible directamente con Whisper."""
    try:
        audio = AudioSegment.from_file(ruta)
        ruta_wav = ruta.replace(os.path.splitext(ruta)[-1], ".wav")
        audio.export(ruta_wav, format="wav")
        return ruta_wav
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo convertir el audio: {e}")
        return None

def procesar_audio():
    if not ruta_audio:
        messagebox.showerror("Error", "Por favor, adjunta un archivo de audio primero.")
        return

    # Deshabilitar el botón mientras procesa
    btn_procesar.config(state="disabled")
    label_info.config(text="Procesando... Esto puede tardar un momento.")
    ventana.update_idletasks()

    # Ejecutar el procesamiento en un hilo separado para no bloquear la interfaz
    threading.Thread(target=procesar_audio_hilo).start()

def procesar_audio_hilo():
    global texto_en_ingles, texto_en_espanol

    try:
        # Convertir el archivo a WAV si es necesario
        ruta_wav = convertir_audio_a_wav(ruta_audio) if not ruta_audio.endswith(".wav") else ruta_audio

        if not ruta_wav:
            return

        # Cargar modelo Whisper AI (usa "base" para rapidez o "large" para mejor precisión)
        modelo = whisper.load_model("base")

        # Transcribir el audio en inglés
        resultado = modelo.transcribe(ruta_wav)
        texto_en_ingles = resultado["text"]

        # Traducir al español con deep-translator
        texto_en_espanol = GoogleTranslator(source='en', target='es').translate(texto_en_ingles)

        # Mostrar en la interfaz
        text_output.delete(1.0, END)
        text_output.insert(END, "📌 **Texto en inglés:**\n")
        text_output.insert(END, texto_en_ingles + "\n\n")
        text_output.insert(END, "📌 **Traducción en español:**\n")
        text_output.insert(END, texto_en_espanol)

        # Habilitar botón nuevamente
        btn_procesar.config(state="normal")

        # Guardar automáticamente el texto en un archivo
        guardar_texto()

        messagebox.showinfo("Éxito", "Texto extraído y traducido. Guardado en un archivo .txt.")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema: {e}")
        btn_procesar.config(state="normal")

def guardar_texto():
    """Guarda automáticamente el texto transcrito y traducido en un archivo .txt"""
    ruta_guardado = filedialog.asksaveasfilename(
        defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
    
    if ruta_guardado:
        with open(ruta_guardado, "w", encoding="utf-8") as archivo:
            archivo.write("📌 **Texto en inglés:**\n")
            archivo.write(texto_en_ingles + "\n\n")
            archivo.write("📌 **Traducción en español:**\n")
            archivo.write(texto_en_espanol)

# Crear la ventana principal
ventana = Tk()
ventana.title("Transcribir y Traducir Audio con Whisper AI")
ventana.geometry("600x400")

# Variables
ruta_audio = ""
texto_en_ingles = ""
texto_en_espanol = ""

# Widgets
label_titulo = Label(ventana, text="Audio a Texto y Traducción", font=("Arial", 14))
label_titulo.pack(pady=10)

btn_adjuntar = Button(ventana, text="Adjuntar Audio", command=adjuntar_audio)
btn_adjuntar.pack(pady=5)

label_info = Label(ventana, text="No se ha seleccionado ningún audio", wraplength=500, fg="gray")
label_info.pack(pady=5)

btn_procesar = Button(ventana, text="Procesar y Traducir", command=procesar_audio)
btn_procesar.pack(pady=20)

# Área de texto con scroll para mostrar el resultado
frame_texto = Scrollbar(ventana)
text_output = Text(ventana, height=10, wrap="word", yscrollcommand=frame_texto.set)
frame_texto.pack(side="right", fill="y")
text_output.pack(padx=10, pady=10, fill="both", expand=True)
frame_texto.config(command=text_output.yview)

# Ejecutar la aplicación
ventana.mainloop()
