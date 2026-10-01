import yt_dlp
import os
import threading
import queue
import sys
import time
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

# Intentamos importar PIL para el logo moderno
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ==========================================
# 1. ESTRUCTURA CENTRAL
# ==========================================

def limpiar_nombre(texto, limite=40):
    if not texto:
        return "Desconocido"
    ilegales = '<>:"/\\|?*'
    for char in ilegales:
        texto = texto.replace(char, '')
    return texto[:limite].strip()

def descargar_playlist(url, carpeta_destino="Lista_Descargada", formato_video="mp4", calidad_video="720p"):
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    ydl_opts_info = {'quiet': True, 'extract_flat': True}
    print(f"\nObteniendo información de la playlist...")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            playlist_title = info_dict.get('title', 'Playlist_Desconocida')
            carpeta_serie_segura = limpiar_nombre(playlist_title, 40)
    except Exception as e:
        print(f"Error al obtener info de la playlist: {e}")
        carpeta_serie_segura = "Playlist_Generica"

    ruta_base = os.path.join(carpeta_destino, carpeta_serie_segura, "Season 01")
    plantilla_salida = os.path.join(ruta_base, f"{carpeta_serie_segura} - S01E%(playlist_autonumber)02d - %(title).40s [%(id)s].%(ext)s")

    # Mapeo de opciones de calidad
    if calidad_video == "1080p":
        formato_cadena = 'bestvideo[height<=1080][vcodec^=avc]+bestaudio[ext=m4a]/best[height<=1080]/best'
    elif calidad_video == "720p":
        formato_cadena = 'bestvideo[height<=720][vcodec^=avc]+bestaudio[ext=m4a]/best[height<=720]/best'
    elif calidad_video == "480p":
        formato_cadena = 'bestvideo[height<=480]+bestaudio/best[height<=480]/best'
    elif calidad_video == "360p":
        formato_cadena = 'bestvideo[height<=360]+bestaudio/best[height<=360]/best'
    else:  # Máxima Calidad
        formato_cadena = 'bestvideo+bestaudio/best'

    opciones = {
        'format': formato_cadena,
        'outtmpl': plantilla_salida,
        'windowsfilenames': True,
        'trim_file_name': 220, 
        'ignoreerrors': True,
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        'ffmpeg_location': './ffmpeg/ffmpeg.exe' if os.path.exists('./ffmpeg/ffmpeg.exe') else None,
        'concurrent_fragment_downloads': 4,
        'buffersize': 1024 * 1024 * 2,
        'retries': 10,
        'fragment_retries': 10,
        'socket_timeout': 30,
        'sleep_interval': 6,
        'max_sleep_interval': 12,
        'sleep_requests': 3,        
        'sleep_subtitles': 8,       
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'download_archive': os.path.join(carpeta_destino, 'archivo_descargados.txt'),
        'writethumbnail': True,
        'convert_thumbnails': 'jpg',
        'writeautomaticsub': True,
        'writesubtitles': True,
        'subtitleslangs': ['es'], 
        'subtitlesformat': 'srt/best',
        'postprocessors': [
            {'key': 'FFmpegSubtitlesConvertor', 'format': 'srt'}, 
            {'key': 'FFmpegVideoConvertor', 'preferedformat': formato_video},
            {'key': 'FFmpegEmbedSubtitle'},                       
            {'key': 'FFmpegMetadata'},                            
            {'key': 'EmbedThumbnail'},                            
            {'key': 'SponsorBlock', 'categories': ['sponsor', 'intro', 'outro']},
        ],
        'keepvideo': False,
    }

    print(f"\nPreparando descarga acelerada: {url}")
    print(f"Ruta destino: {ruta_base}")
    print(f"Formato: .{formato_video} | Calidad seleccionada: {calidad_video}\n")
    
    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            ydl.download([url])
        print("\n¡Tarea completada!")
    except Exception as e:
        print(f"\nOcurrió un error inesperado: {e}")

# ==========================================
# 2. MOTOR EN SEGUNDO PLANO Y CONTROL DE PAUSA
# ==========================================
cola_descargas = queue.Queue()
estado_pausa = threading.Event()
estado_pausa.set()  # Inicia activo (no pausado)

def motor_de_descargas():
    numero = 1
    while True:
        paquete = cola_descargas.get() 
        if paquete == 'APAGAR':
            break 
            
        url, carpeta, formato, calidad = paquete
        
        # Verificación de pausa previa a la descarga
        if not estado_pausa.is_set():
            print("\n[PAUSA] El sistema está pausado. Esperando reanudación para la siguiente tarea...")
            estado_pausa.wait()
            print("[REANUDADO] Continuando con las descargas...")

        print(f"\n\n=======================================================")
        print(f"=== INICIANDO TAREA #{numero} ===")
        print(f"=======================================================")
        
        descargar_playlist(url, carpeta, formato, calidad)
        
        numero += 1
        print(f"\n[INFO] Tareas en espera restantes: {cola_descargas.qsize()}")
        cola_descargas.task_done()

hilo_trabajador = threading.Thread(target=motor_de_descargas, daemon=True)
hilo_trabajador.start()

# ==========================================
# 3. INTERFAZ GRÁFICA MULTI-TEMA (ZENIT-MX)
# ==========================================

# Catálogo de Temas Disponibles
TEMAS = {
    "Zenit (Oscuro)": {
        "bg": "#1a242f", "fg": "#ecf0f1", "accent": "#00a8e8", "accent_h": "#007bb5",
        "bg_panel": "#2c3e50", "bg_input": "#34495e", "c_bg": "#0b1015", "c_fg": "#00e5ff"
    },
    "Zenit (Claro)": {
        "bg": "#f0f4f8", "fg": "#2c3e50", "accent": "#00a8e8", "accent_h": "#007bb5",
        "bg_panel": "#ffffff", "bg_input": "#e1e8ed", "c_bg": "#ffffff", "c_fg": "#2c3e50"
    },
    "Terminal Hacker": {
        "bg": "#000000", "fg": "#00ff00", "accent": "#006600", "accent_h": "#009900",
        "bg_panel": "#0a0a0a", "bg_input": "#001100", "c_bg": "#000000", "c_fg": "#00ff00"
    },
    "Cyberpunk": {
        "bg": "#0d0221", "fg": "#00f0ff", "accent": "#ff007f", "accent_h": "#cc0066",
        "bg_panel": "#190440", "bg_input": "#26065c", "c_bg": "#05010d", "c_fg": "#ff00ff"
    }
}
PAUSE_COLOR = "#e74c3c"
PAUSE_HOVER = "#c0392b"

class RedireccionConsola:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.after(0, self._escribir_seguro, string)

    def _escribir_seguro(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

# Función dinámica para cambiar los colores en vivo
def cambiar_tema(event=None):
    nombre_tema = var_tema.get()
    t = TEMAS[nombre_tema]
    
    # Actualizar Ventana y Logo
    ventana.configure(bg=t["bg"])
    if 'etiqueta_logo' in globals():
        etiqueta_logo.configure(bg=t["bg"])
        
    # Actualizar Estilos TTK Globales
    estilo.configure("TFrame", background=t["bg"])
    estilo.configure("TLabel", background=t["bg"], foreground=t["fg"])
    estilo.configure("Titulo.TLabel", background=t["bg"], foreground=t["accent"])
    estilo.configure("Panel.TLabel", background=t["bg_panel"], foreground=t["fg"])
    
    estilo.configure("TButton", background=t["accent"], foreground="white")
    estilo.map("TButton", background=[("active", t["accent_h"])])
    
    estilo.configure("Pausa.TButton", background=PAUSE_COLOR, foreground="white")
    estilo.map("Pausa.TButton", background=[("active", PAUSE_HOVER)])
    
    # Actualizar Widgets Nativos
    marco_controles.configure(bg=t["bg_panel"])
    entrada_carpeta.configure(bg=t["bg_input"], fg=t["fg"], insertbackground=t["fg"])
    entrada_urls.configure(bg=t["bg_input"], fg=t["fg"], insertbackground=t["fg"])
    consola_texto.configure(bg=t["c_bg"], fg=t["c_fg"])

def seleccionar_carpeta():
    ruta = filedialog.askdirectory(title="Seleccionar carpeta de destino")
    if ruta:
        var_carpeta.set(ruta)

def agregar_a_cola():
    texto_urls = entrada_urls.get("1.0", tk.END).strip()
    carpeta_final = var_carpeta.get().strip() or "Lista_Descargada"
    formato_final = var_formato.get().strip()
    calidad_final = var_calidad.get().strip()
    
    if not texto_urls:
        print("[-] Error: No ingresaste ningún enlace.")
        return

    entradas_corregidas = texto_urls.replace('\n', ',').replace(' ', ',')
    nuevos_enlaces = []
    
    for posible_url in entradas_corregidas.split(','):
        url_limpia = posible_url.strip()
        if not url_limpia:
            continue
        if "http" in url_limpia and not url_limpia.startswith("http"):
            url_limpia = url_limpia[url_limpia.find("http"):]
            
        if url_limpia.startswith("http") or url_limpia.startswith("www"):
            nuevos_enlaces.append(url_limpia)

    if nuevos_enlaces:
        for enlace in nuevos_enlaces:
            cola_descargas.put((enlace, carpeta_final, formato_final, calidad_final))
            
        print(f"[+] Se añadieron {len(nuevos_enlaces)} enlace(s) a la cola. (Total en fila: {cola_descargas.qsize()})")
        entrada_urls.delete("1.0", tk.END) 
    else:
        print("[-] No se detectó ningún enlace válido.")

def alternar_pausa():
    if estado_pausa.is_set():
        estado_pausa.clear()
        btn_pausa.config(text="▶ REANUDAR DESCARGAS", style="Pausa.TButton")
        print("\n[PAUSA SOLICITADA] Se pausará al terminar el elemento actual.")
    else:
        estado_pausa.set()
        btn_pausa.config(text="⏸ PAUSAR DESCARGAS", style="TButton")
        print("\n[SISTEMA REANUDADO] Procesando cola de descargas...")

def cerrar_programa():
    print("\nApagando sistema...")
    estado_pausa.set()
    cola_descargas.put('APAGAR')
    ventana.destroy()
    sys.exit()

# --- Configuración Principal de la Ventana ---
ventana = tk.Tk()
ventana.title("Tecnología ZENIT - Versión 2.0 Multi-Tema")
ventana.geometry("850x850")

# --- Inicialización de Estilos ---
estilo = ttk.Style()
estilo.theme_use('clam') 

marco_principal = ttk.Frame(ventana, padding="20")
marco_principal.pack(fill=tk.BOTH, expand=True)

# --- Sección 1: LOGO DE LA EMPRESA ---
marco_logo = ttk.Frame(marco_principal)
marco_logo.pack(fill=tk.X, pady=(0, 10))

if HAS_PIL and os.path.exists("ZENIT.jpg"):
    try:
        imagen_original = Image.open("ZENIT.jpg")
        ancho_deseado = 380
        proporcion = ancho_deseado / float(imagen_original.size[0])
        alto_calculado = int((float(imagen_original.size[1]) * float(proporcion)))
        imagen_redimensionada = imagen_original.resize((ancho_deseado, alto_calculado), Image.Resampling.LANCZOS)
        
        logo_tk = ImageTk.PhotoImage(imagen_redimensionada)
        etiqueta_logo = tk.Label(marco_logo, image=logo_tk)
        etiqueta_logo.image = logo_tk 
        etiqueta_logo.pack(anchor=tk.CENTER)
    except Exception as e:
        ttk.Label(marco_logo, text="TECNOLOGÍA ZENIT", style="Titulo.TLabel").pack(anchor=tk.CENTER)
else:
    ttk.Label(marco_logo, text="TECNOLOGÍA ZENIT", style="Titulo.TLabel").pack(anchor=tk.CENTER)

# --- Sección 2: CONTROLES ---
marco_controles = tk.Frame(marco_principal, padx=15, pady=15)
marco_controles.pack(fill=tk.X, pady=(0, 10))

# Ruta Destino
ttk.Label(marco_controles, text="📁 Ruta de Destino:", style="Panel.TLabel").grid(row=0, column=0, sticky=tk.W, pady=5)
var_carpeta = tk.StringVar(value="Lista_Descargada")
entrada_carpeta = tk.Entry(marco_controles, textvariable=var_carpeta, width=45, font=("Segoe UI", 10), relief=tk.FLAT)
entrada_carpeta.grid(row=0, column=1, padx=10, pady=5, ipady=3, columnspan=2, sticky=tk.W)
ttk.Button(marco_controles, text="Explorar...", command=seleccionar_carpeta).grid(row=0, column=3, pady=5, padx=5)

# Formato y Calidad
ttk.Label(marco_controles, text="🎬 Formato:", style="Panel.TLabel").grid(row=1, column=0, sticky=tk.W, pady=5)
var_formato = tk.StringVar(value="mkv")
combo_formato = ttk.Combobox(marco_controles, textvariable=var_formato, values=['mp4', 'mkv', 'webm', 'avi', 'mov', 'flv'], state="readonly", width=10, font=("Segoe UI", 10))
combo_formato.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

ttk.Label(marco_controles, text="📐 Calidad:", style="Panel.TLabel").grid(row=1, column=2, sticky=tk.W, pady=5)
var_calidad = tk.StringVar(value="720p")
combo_calidad = ttk.Combobox(marco_controles, textvariable=var_calidad, values=['1080p', '720p', '480p', '360p', 'Máxima Calidad'], state="readonly", width=14, font=("Segoe UI", 10))
combo_calidad.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)

# Selector de Temas Visuales (NUEVO)
ttk.Label(marco_controles, text="🎨 Tema Visual:", style="Panel.TLabel").grid(row=2, column=0, sticky=tk.W, pady=5)
var_tema = tk.StringVar(value="Zenit (Oscuro)")
combo_tema = ttk.Combobox(marco_controles, textvariable=var_tema, values=list(TEMAS.keys()), state="readonly", width=20, font=("Segoe UI", 10))
combo_tema.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5, columnspan=2)
combo_tema.bind("<<ComboboxSelected>>", cambiar_tema)

# --- Sección 3: ENLACES Y BOTONES ---
ttk.Label(marco_principal, text="🔗 Pegar Enlaces (separados por espacios, comas o saltos de línea):").pack(anchor=tk.W)
entrada_urls = tk.Text(marco_principal, height=3, font=("Segoe UI", 10), relief=tk.FLAT, padx=8, pady=8)
entrada_urls.pack(fill=tk.X, pady=5)

marco_acciones = ttk.Frame(marco_principal)
marco_acciones.pack(fill=tk.X, pady=5)

btn_agregar = ttk.Button(marco_acciones, text="➕ AÑADIR A LA COLA", command=agregar_a_cola)
btn_agregar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

btn_pausa = ttk.Button(marco_acciones, text="⏸ PAUSAR DESCARGAS", command=alternar_pausa)
btn_pausa.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

# --- Sección 4: CONSOLA CIBERNÉTICA ---
ttk.Label(marco_principal, text="🖥 Terminal de Operaciones:").pack(anchor=tk.W)
consola_texto = scrolledtext.ScrolledText(marco_principal, height=14, font=("Consolas", 9), relief=tk.FLAT, padx=10, pady=10)
consola_texto.pack(fill=tk.BOTH, expand=True, pady=5)

# Redirigir el output
sys.stdout = RedireccionConsola(consola_texto)
sys.stderr = sys.stdout 

# Mensaje corporativo
print("================================================================")
print(" SISTEMA DE DESCARGA: TECNOLOGÍA ZENIT [ACTIVO]")
print("================================================================")
print("[+] Conectado al motor asíncrono.")
print("[+] En espera de directrices de descarga...")
print("[TIP] Puedes cambiar el aspecto del programa en 'Tema Visual'.\n")

# Forzar la pintura del tema inicial antes de mostrar la ventana
cambiar_tema()

ventana.protocol("WM_DELETE_WINDOW", cerrar_programa)
ventana.mainloop()
