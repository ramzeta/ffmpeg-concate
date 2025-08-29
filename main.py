import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import os
import psutil
import time
from pathlib import Path
import json

class VideoConcat:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Concatenator")
        self.root.geometry("900x750")
        self.root.minsize(800, 600)  # Tamaño mínimo
        self.root.resizable(True, True)  # Permitir redimensionar
        
        self.video_files = []
        self.output_path = ""
        self.is_processing = False
        self.current_process = None
        self.current_thread = None
        self.stop_requested = False
        self.ffmpeg_path = os.getenv('FFMPEG_PATH', 'ffmpeg')
        self.max_cpu_usage = float(os.getenv('MAX_CPU_USAGE', '80'))
        self.cuda_available = self.check_cuda_support()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Video files section
        ttk.Label(main_frame, text="Videos a concatenar:", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Listbox for videos
        self.video_listbox = tk.Listbox(main_frame, height=12, width=80)
        self.video_listbox.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.video_listbox.yview)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.video_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=3, pady=(0, 15))
        
        ttk.Button(buttons_frame, text="Agregar Videos", command=self.add_videos).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Quitar Seleccionado", command=self.remove_video).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Limpiar Lista", command=self.clear_videos).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Subir", command=self.move_up).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Bajar", command=self.move_down).pack(side=tk.LEFT, padx=5)
        
        # Output section
        ttk.Label(main_frame, text="Archivo de salida:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky=tk.W, pady=(15, 5))
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.output_var = tk.StringVar()
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var, width=60)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(output_frame, text="Seleccionar", command=self.select_output).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Settings section
        settings_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        settings_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(settings_frame, text="Uso máximo de CPU (%):").grid(row=0, column=0, sticky=tk.W)
        self.cpu_var = tk.StringVar(value=str(self.max_cpu_usage))
        cpu_entry = ttk.Entry(settings_frame, textvariable=self.cpu_var, width=10)
        cpu_entry.grid(row=0, column=1, padx=(5, 0))
        
        ttk.Label(settings_frame, text="Ruta FFmpeg:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.ffmpeg_var = tk.StringVar(value=self.ffmpeg_path)
        ffmpeg_entry = ttk.Entry(settings_frame, textvariable=self.ffmpeg_var, width=50)
        ffmpeg_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(5, 0), pady=(5, 0))
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progreso", padding="10")
        progress_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.progress_var = tk.StringVar(value="Listo")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack()
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        # CPU usage display
        self.cpu_usage_var = tk.StringVar(value="CPU: 0%")
        ttk.Label(progress_frame, textvariable=self.cpu_usage_var).pack(pady=(5, 0))
        
        # Process buttons frame
        process_frame = ttk.Frame(main_frame)
        process_frame.grid(row=7, column=0, columnspan=3, pady=15)
        
        # Main action buttons
        self.concat_button = ttk.Button(process_frame, text="Concatenar Videos", command=self.start_concatenation)
        self.concat_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.frame_button = ttk.Button(process_frame, text="Extraer Último Frame", command=self.start_frame_extraction)
        self.frame_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.enhance_button = ttk.Button(process_frame, text="Mejorar Calidad", command=self.start_quality_enhancement)
        self.enhance_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(process_frame, text="🛑 Detener", command=self.stop_processing, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame options
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=8, column=0, columnspan=3, pady=(0, 15))
        
        # Checkbox for frame capture during concatenation
        self.capture_frame_var = tk.BooleanVar(value=True)
        capture_check = ttk.Checkbutton(options_frame, text="También capturar frame al concatenar", variable=self.capture_frame_var)
        capture_check.pack(side=tk.LEFT, padx=(0, 10))
        
        # Quality selector
        ttk.Label(options_frame, text="Calidad frame:").pack(side=tk.LEFT, padx=(10, 5))
        self.quality_var = tk.StringVar(value="alta")
        quality_combo = ttk.Combobox(options_frame, textvariable=self.quality_var, values=["alta", "media", "baja"], width=8, state="readonly")
        quality_combo.pack(side=tk.LEFT)
        
        # GPU/CUDA options
        gpu_frame = ttk.Frame(main_frame)
        gpu_frame.grid(row=9, column=0, columnspan=3, pady=(0, 15))
        
        # CUDA checkbox
        self.use_cuda_var = tk.BooleanVar(value=self.cuda_available[0])
        cuda_check = ttk.Checkbutton(gpu_frame, text="Usar aceleración GPU (CUDA)", variable=self.use_cuda_var)
        cuda_check.pack(side=tk.LEFT, padx=(0, 10))
        
        # Modo de concatenación
        ttk.Label(gpu_frame, text="Modo:").pack(side=tk.LEFT, padx=(10, 5))
        self.concat_mode_var = tk.StringVar(value="rapido" if not self.cuda_available[0] else "gpu")
        mode_values = ["rapido", "gpu", "calidad", "turbo"] if self.cuda_available[0] else ["rapido", "calidad", "turbo"]
        mode_combo = ttk.Combobox(gpu_frame, textvariable=self.concat_mode_var, values=mode_values, width=8, state="readonly")
        mode_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # CUDA status
        cuda_status = "Disponible" if self.cuda_available[0] else "No disponible"
        self.cuda_status_label = ttk.Label(gpu_frame, text=f"GPU: {cuda_status}")
        self.cuda_status_label.pack(side=tk.LEFT)
        
        # Tooltip info
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=10, column=0, columnspan=3, pady=(0, 5))
        info_text = "Modos: rápido=sin pérdida, gpu=CUDA optimizado, calidad=máxima compatibilidad, turbo=90% recursos"
        ttk.Label(info_frame, text=info_text, font=("Arial", 8), foreground="gray").pack()
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Start CPU monitoring
        self.monitor_cpu()
        
    def add_videos(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar videos",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
                ("All files", "*.*")
            ]
        )
        
        for file in files:
            if file not in self.video_files:
                self.video_files.append(file)
                self.video_listbox.insert(tk.END, os.path.basename(file))
    
    def remove_video(self):
        selection = self.video_listbox.curselection()
        if selection:
            index = selection[0]
            self.video_listbox.delete(index)
            del self.video_files[index]
    
    def clear_videos(self):
        self.video_listbox.delete(0, tk.END)
        self.video_files.clear()
    
    def move_up(self):
        selection = self.video_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            # Swap in list
            self.video_files[index], self.video_files[index-1] = self.video_files[index-1], self.video_files[index]
            # Update listbox
            item = self.video_listbox.get(index)
            self.video_listbox.delete(index)
            self.video_listbox.insert(index-1, item)
            self.video_listbox.selection_set(index-1)
    
    def move_down(self):
        selection = self.video_listbox.curselection()
        if selection and selection[0] < self.video_listbox.size() - 1:
            index = selection[0]
            # Swap in list
            self.video_files[index], self.video_files[index+1] = self.video_files[index+1], self.video_files[index]
            # Update listbox
            item = self.video_listbox.get(index)
            self.video_listbox.delete(index)
            self.video_listbox.insert(index+1, item)
            self.video_listbox.selection_set(index+1)
    
    def select_output(self):
        file_path = filedialog.asksaveasfilename(
            title="Guardar video como",
            defaultextension=".mp4",
            filetypes=[
                ("MP4 files", "*.mp4"),
                ("AVI files", "*.avi"),
                ("MOV files", "*.mov"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.output_var.set(file_path)
    
    def monitor_cpu(self):
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage_var.set(f"CPU: {cpu_percent:.1f}%")
        except:
            self.cpu_usage_var.set("CPU: N/A")
        
        self.root.after(2000, self.monitor_cpu)
    
    def stop_processing(self):
        """Detener el proceso actual en ejecución"""
        if not self.is_processing:
            return
        
        # Marcar que se solicitó detener
        self.stop_requested = True
        
        # Intentar terminar el proceso FFmpeg
        if self.current_process:
            try:
                # Terminar proceso y subprocesos
                import psutil
                parent = psutil.Process(self.current_process.pid)
                for child in parent.children(recursive=True):
                    try:
                        child.terminate()
                    except:
                        pass
                parent.terminate()
                
                # Esperar un poco para terminación limpia
                try:
                    parent.wait(timeout=3)
                except:
                    # Si no termina, forzar
                    try:
                        parent.kill()
                        for child in parent.children(recursive=True):
                            child.kill()
                    except:
                        pass
            except Exception as e:
                print(f"Error terminando proceso: {e}")
        
        # Actualizar interfaz
        self.progress_var.set("Proceso detenido por el usuario")
        self.progress_bar.stop()
        
        # Restaurar botones
        self.reset_ui_state()
        
        messagebox.showwarning("Proceso Detenido", "El procesamiento ha sido cancelado por el usuario.")
    
    def reset_ui_state(self):
        """Restaurar estado de la interfaz"""
        self.is_processing = False
        self.current_process = None
        self.current_thread = None
        self.stop_requested = False
        
        # Habilitar botones
        self.concat_button.config(state="normal")
        self.frame_button.config(state="normal") 
        self.enhance_button.config(state="normal")
        self.stop_button.config(state="disabled")
    
    def check_cuda_support(self):
        """Verificar si CUDA está disponible en FFmpeg"""
        try:
            cmd = [self.ffmpeg_path, '-encoders']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            # Buscar encoders CUDA
            cuda_encoders = ['h264_nvenc', 'hevc_nvenc', 'av1_nvenc']
            available_encoders = []
            
            for encoder in cuda_encoders:
                if encoder in result.stdout:
                    available_encoders.append(encoder)
            
            return len(available_encoders) > 0, available_encoders
            
        except Exception:
            return False, []
    
    def capture_last_frame(self, video_path, output_dir):
        """Captura el último frame de un video con configuración de calidad"""
        try:
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            frame_path = os.path.join(output_dir, f"{video_name}_last_frame.png")
            
            # Configuraciones de calidad
            quality_settings = {
                "alta": {
                    "q:v": "1",  # Máxima calidad
                    "compression_level": "0",  # Sin compresión
                    "pix_fmt": "rgb24"  # RGB 24-bit
                },
                "media": {
                    "q:v": "5",  # Calidad media
                    "compression_level": "6",  # Compresión media
                    "pix_fmt": "rgb24"
                },
                "baja": {
                    "q:v": "15",  # Calidad baja
                    "compression_level": "9",  # Máxima compresión
                    "pix_fmt": "yuv420p"  # Formato más comprimido
                }
            }
            
            # Obtener configuración actual
            quality = self.quality_var.get() if hasattr(self, 'quality_var') else "alta"
            settings = quality_settings.get(quality, quality_settings["alta"])
            
            # Extraer último frame con configuración de calidad
            cmd_last = [
                self.ffmpeg_path,
                '-sseof', '-1',  # Seek to 1 second before end
                '-i', video_path,
                '-vframes', '1',
                '-q:v', settings["q:v"],
                '-compression_level', settings["compression_level"],
                '-pix_fmt', settings["pix_fmt"],
                '-vf', 'scale=iw:ih',  # Mantener resolución original
                '-f', 'png',
                '-y',
                frame_path
            ]
            
            process = subprocess.run(cmd_last, capture_output=True, text=True)
            
            if process.returncode == 0 and os.path.exists(frame_path):
                return frame_path
            else:
                return None
                
        except Exception as e:
            print(f"Error capturando frame: {e}")
            return None
    
    def start_concatenation(self):
        if self.is_processing:
            messagebox.showwarning("Advertencia", "Ya se está procesando un video")
            return
        
        if not self.video_files:
            messagebox.showerror("Error", "No hay videos seleccionados")
            return
        
        output_file = self.output_var.get().strip()
        if not output_file:
            messagebox.showerror("Error", "Debe especificar un archivo de salida")
            return
        
        # Validar que el archivo de salida tenga una extensión válida
        valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
        file_ext = os.path.splitext(output_file.lower())[1]
        
        if not file_ext or file_ext not in valid_extensions:
            result = messagebox.askyesno(
                "Extensión no válida", 
                f"El archivo de salida '{output_file}' no tiene una extensión de video válida.\n\n"
                f"¿Desea agregar '.mp4' automáticamente?"
            )
            if result:
                output_file += '.mp4'
                self.output_var.set(output_file)
            else:
                return
        
        self.max_cpu_usage = float(self.cpu_var.get())
        self.ffmpeg_path = self.ffmpeg_var.get()
        
        self.is_processing = True
        self.stop_requested = False
        self.concat_button.config(state="disabled")
        self.frame_button.config(state="disabled")
        self.enhance_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress_bar.start()
        self.progress_var.set("Iniciando concatenación...")
        
        thread = threading.Thread(target=self.process_videos)
        thread.daemon = True
        self.current_thread = thread
        thread.start()
    
    def start_frame_extraction(self):
        """Iniciar extracción de último frame de videos seleccionados"""
        if self.is_processing:
            messagebox.showwarning("Advertencia", "Ya se está procesando")
            return
        
        if not self.video_files:
            messagebox.showerror("Error", "No hay videos seleccionados")
            return
        
        # Preguntar dónde guardar los frames
        output_dir = filedialog.askdirectory(title="Seleccionar carpeta para guardar frames")
        if not output_dir:
            return
        
        self.is_processing = True
        self.stop_requested = False
        self.concat_button.config(state="disabled")
        self.frame_button.config(state="disabled")
        self.enhance_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress_bar.start()
        self.progress_var.set("Extrayendo últimos frames...")
        
        thread = threading.Thread(target=self.extract_frames_only, args=(output_dir,))
        thread.daemon = True
        self.current_thread = thread
        thread.start()
    
    def extract_frames_only(self, output_dir):
        """Extraer último frame de cada video seleccionado"""
        try:
            extracted_frames = []
            failed_extractions = []
            total_videos = len(self.video_files)
            
            for i, video_file in enumerate(self.video_files):
                # Verificar si se solicitó cancelación
                if self.stop_requested:
                    self.progress_var.set("Extracción cancelada por el usuario")
                    return
                
                self.progress_var.set(f"Extrayendo frame {i+1}/{total_videos}...")
                
                # Verificar que el archivo existe
                if not os.path.exists(video_file):
                    failed_extractions.append(f"{os.path.basename(video_file)} - Archivo no encontrado")
                    continue
                
                frame_path = self.capture_last_frame(video_file, output_dir)
                
                if frame_path:
                    extracted_frames.append(frame_path)
                else:
                    failed_extractions.append(f"{os.path.basename(video_file)} - Error al extraer frame")
            
            # Mostrar resultados
            if extracted_frames:
                success_msg = f"Frames extraídos exitosamente: {len(extracted_frames)}\n\n"
                success_msg += "Archivos generados:\n"
                for frame in extracted_frames[:5]:  # Mostrar máximo 5
                    success_msg += f"• {os.path.basename(frame)}\n"
                if len(extracted_frames) > 5:
                    success_msg += f"... y {len(extracted_frames) - 5} más"
                    
                if failed_extractions:
                    success_msg += f"\n\nAdvertencias ({len(failed_extractions)} fallos):\n"
                    for failure in failed_extractions[:3]:
                        success_msg += f"• {failure}\n"
                    if len(failed_extractions) > 3:
                        success_msg += f"... y {len(failed_extractions) - 3} más"
                
                self.progress_var.set("Extracción completada")
                messagebox.showinfo("Éxito", success_msg)
            else:
                self.progress_var.set("Error en la extracción")
                error_msg = "No se pudo extraer ningún frame.\n\nErrores:\n"
                for failure in failed_extractions[:5]:
                    error_msg += f"• {failure}\n"
                messagebox.showerror("Error", error_msg)
                
        except Exception as e:
            self.progress_var.set("Error inesperado")
            import traceback
            error_details = traceback.format_exc()
            with open('app_error.log', 'w') as f:
                f.write(error_details)
            messagebox.showerror("Error", f"Error inesperado: {str(e)}\n\nRevisa app_error.log para más detalles")
        
        finally:
            self.reset_ui_state()
    
    def start_quality_enhancement(self):
        """Iniciar mejora de calidad de videos seleccionados"""
        if self.is_processing:
            messagebox.showwarning("Advertencia", "Ya se está procesando")
            return
        
        if not self.video_files:
            messagebox.showerror("Error", "No hay videos seleccionados")
            return
        
        # Preguntar dónde guardar los videos mejorados
        output_dir = filedialog.askdirectory(title="Seleccionar carpeta para guardar videos mejorados")
        if not output_dir:
            return
        
        # Mostrar opciones de mejora
        options = messagebox.askyesnocancel(
            "Opciones de Mejora",
            "¿Qué tipo de mejora deseas?\n\n"
            "SÍ: Mejora completa (upscaling 2x + filtros avanzados)\n"
            "NO: Mejora básica (solo filtros de nitidez y color)\n"
            "CANCELAR: Cancelar operación"
        )
        
        if options is None:  # Cancelar
            return
        
        self.is_processing = True
        self.stop_requested = False
        self.concat_button.config(state="disabled")
        self.frame_button.config(state="disabled")
        self.enhance_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress_bar.start()
        self.progress_var.set("Mejorando calidad de videos...")
        
        thread = threading.Thread(target=self.enhance_videos_quality, args=(output_dir, options))
        thread.daemon = True
        self.current_thread = thread
        thread.start()
    
    def enhance_videos_quality(self, output_dir, full_enhancement):
        """Mejorar calidad de videos seleccionados"""
        try:
            enhanced_videos = []
            failed_enhancements = []
            total_videos = len(self.video_files)
            
            for i, video_file in enumerate(self.video_files):
                # Verificar si se solicitó cancelación
                if self.stop_requested:
                    self.progress_var.set("Mejora cancelada por el usuario")
                    return
                
                self.progress_var.set(f"Mejorando video {i+1}/{total_videos}...")
                
                # Verificar que el archivo existe
                if not os.path.exists(video_file):
                    failed_enhancements.append(f"{os.path.basename(video_file)} - Archivo no encontrado")
                    continue
                
                video_name = os.path.splitext(os.path.basename(video_file))[0]
                enhanced_path = os.path.join(output_dir, f"{video_name}_enhanced.mp4")
                
                # Determinar si usar CUDA
                use_cuda = self.use_cuda_var.get() and self.cuda_available[0]
                
                if full_enhancement:
                    # Mejora completa con upscaling y filtros avanzados
                    if use_cuda:
                        cmd = [
                            self.ffmpeg_path,
                            '-hwaccel', 'cuda',  # Aceleración hardware
                            '-hwaccel_output_format', 'cuda',  # Formato de salida GPU
                            '-i', video_file,
                            '-vf', 'scale_cuda=iw*2:ih*2,hwdownload,format=nv12,unsharp=5:5:1.0:5:5:0.0,eq=contrast=1.1:brightness=0.05:saturation=1.2,hwupload_cuda',
                            '-c:v', 'h264_nvenc',  # Encoder CUDA
                            '-preset', 'slow',
                            '-cq', '18',  # Calidad constante para NVENC
                            '-c:a', 'aac',
                            '-b:a', '192k',
                            '-y',
                            enhanced_path
                        ]
                    else:
                        cmd = [
                            self.ffmpeg_path,
                            '-i', video_file,
                            '-vf', 'scale=iw*2:ih*2:flags=lanczos,unsharp=5:5:1.0:5:5:0.0,eq=contrast=1.1:brightness=0.05:saturation=1.2',
                            '-c:v', 'libx264',
                            '-preset', 'slow',
                            '-crf', '18',  # Calidad muy alta
                            '-c:a', 'aac',
                            '-b:a', '192k',
                            '-y',
                            enhanced_path
                        ]
                else:
                    # Mejora básica solo con filtros
                    if use_cuda:
                        cmd = [
                            self.ffmpeg_path,
                            '-hwaccel', 'cuda',
                            '-hwaccel_output_format', 'cuda',
                            '-i', video_file,
                            '-vf', 'hwdownload,format=nv12,unsharp=5:5:1.0:5:5:0.0,eq=contrast=1.05:brightness=0.02:saturation=1.1,hwupload_cuda',
                            '-c:v', 'h264_nvenc',
                            '-preset', 'medium',
                            '-cq', '20',  # Buena calidad
                            '-c:a', 'copy',  # Mantener audio original
                            '-y',
                            enhanced_path
                        ]
                    else:
                        cmd = [
                            self.ffmpeg_path,
                            '-i', video_file,
                            '-vf', 'unsharp=5:5:1.0:5:5:0.0,eq=contrast=1.05:brightness=0.02:saturation=1.1',
                            '-c:v', 'libx264',
                            '-preset', 'medium',
                            '-crf', '20',  # Buena calidad
                            '-c:a', 'copy',  # Mantener audio original
                            '-y',
                            enhanced_path
                        ]
                
                try:
                    # Ejecutar con control de CPU
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    ps_process = psutil.Process(process.pid)
                    
                    while process.poll() is None and not self.stop_requested:
                        current_cpu = psutil.cpu_percent(interval=0.1)
                        if current_cpu > self.max_cpu_usage:
                            try:
                                ps_process.suspend()
                                time.sleep(0.5)
                                ps_process.resume()
                            except:
                                pass
                        time.sleep(0.1)
                    
                    stdout, stderr = process.communicate()
                    
                    if process.returncode == 0 and os.path.exists(enhanced_path):
                        enhanced_videos.append(enhanced_path)
                    else:
                        failed_enhancements.append(f"{os.path.basename(video_file)} - Error en mejora")
                        
                except Exception as e:
                    failed_enhancements.append(f"{os.path.basename(video_file)} - {str(e)}")
            
            # Mostrar resultados
            if enhanced_videos:
                success_msg = f"Videos mejorados exitosamente: {len(enhanced_videos)}\n\n"
                success_msg += "Archivos generados:\n"
                for video in enhanced_videos[:3]:  # Mostrar máximo 3
                    success_msg += f"• {os.path.basename(video)}\n"
                if len(enhanced_videos) > 3:
                    success_msg += f"... y {len(enhanced_videos) - 3} más"
                    
                if failed_enhancements:
                    success_msg += f"\n\nAdvertencias ({len(failed_enhancements)} fallos):\n"
                    for failure in failed_enhancements[:2]:
                        success_msg += f"• {failure}\n"
                    if len(failed_enhancements) > 2:
                        success_msg += f"... y {len(failed_enhancements) - 2} más"
                
                self.progress_var.set("Mejora de calidad completada")
                messagebox.showinfo("Éxito", success_msg)
            else:
                self.progress_var.set("Error en la mejora")
                error_msg = "No se pudo mejorar ningún video.\n\nErrores:\n"
                for failure in failed_enhancements[:3]:
                    error_msg += f"• {failure}\n"
                messagebox.showerror("Error", error_msg)
                
        except Exception as e:
            self.progress_var.set("Error inesperado")
            import traceback
            error_details = traceback.format_exc()
            with open('app_error.log', 'w') as f:
                f.write(error_details)
            messagebox.showerror("Error", f"Error inesperado: {str(e)}\n\nRevisa app_error.log para más detalles")
        
        finally:
            self.reset_ui_state()
    
    def process_videos(self):
        try:
            # Verificar que FFmpeg esté disponible
            try:
                test_cmd = [self.ffmpeg_path, '-version']
                subprocess.run(test_cmd, capture_output=True, check=False)
            except FileNotFoundError:
                self.progress_var.set("FFmpeg no encontrado")
                messagebox.showerror("Error", f"FFmpeg no encontrado en: {self.ffmpeg_path}\n\nPor favor, instala FFmpeg o configura la ruta correcta.")
                return
            
            # Verificar cancelación antes de empezar
            if self.stop_requested:
                self.progress_var.set("Concatenación cancelada")
                return
            
            # Verificar que todos los archivos existen
            missing_files = []
            for video_file in self.video_files:
                if not os.path.exists(video_file):
                    missing_files.append(os.path.basename(video_file))
            
            if missing_files:
                self.progress_var.set("Archivos faltantes detectados")
                messagebox.showerror("Error", f"Los siguientes archivos no se encontraron:\n" + "\n".join(missing_files))
                return
            
            temp_file = os.path.abspath("temp_concat_list.txt")
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                for video_file in self.video_files:
                    # Convertir a ruta absoluta y usar formato correcto para FFmpeg
                    abs_path = os.path.abspath(video_file).replace('\\', '/')
                    f.write(f"file '{abs_path}'\n")
            
            self.progress_var.set("Concatenando videos...")
            
            output_path = self.output_var.get().strip()
            
            # Determinar modo de concatenación
            concat_mode = self.concat_mode_var.get()
            use_cuda = self.use_cuda_var.get() and self.cuda_available[0]
            
            if concat_mode == "gpu" and use_cuda:
                # Modo GPU: recodifica con CUDA para máxima velocidad
                cmd = [
                    self.ffmpeg_path,
                    '-hwaccel', 'cuda',
                    '-hwaccel_output_format', 'cuda',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', temp_file,
                    '-c:v', 'h264_nvenc',  # Encoder GPU
                    '-preset', 'p1',  # Máxima velocidad NVENC
                    '-tune', 'hq',  # Optimizar para calidad
                    '-cq', '20',  # Calidad visual excelente
                    '-b:v', '0',  # Rate control por CQ
                    '-c:a', 'copy',  # Audio sin cambios
                    '-avoid_negative_ts', 'make_zero',
                    '-fflags', '+genpts',
                    '-threads', '0',
                    '-y',
                    output_path
                ]
            elif concat_mode == "calidad":
                # Modo calidad: recodifica con CPU para máxima compatibilidad
                cmd = [
                    self.ffmpeg_path,
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', temp_file,
                    '-c:v', 'libx264',  # Encoder CPU de alta calidad
                    '-preset', 'medium',
                    '-crf', '18',  # Calidad muy alta
                    '-c:a', 'aac',  # Recodificar audio para compatibilidad
                    '-b:a', '192k',
                    '-avoid_negative_ts', 'make_zero',
                    '-fflags', '+genpts',
                    '-threads', '0',  # Usar todos los cores
                    '-y',
                    output_path
                ]
            elif concat_mode == "turbo":
                # Modo TURBO: 100% de recursos, sin verificaciones
                if use_cuda:
                    cmd = [
                        self.ffmpeg_path,
                        '-hwaccel', 'cuda',
                        '-hwaccel_output_format', 'cuda',
                        '-f', 'concat',
                        '-safe', '0',
                        '-i', temp_file,
                        '-c:v', 'h264_nvenc',
                        '-preset', 'p1',  # Máxima velocidad
                        '-tune', 'ull',  # Ultra low latency
                        '-cq', '18',  # Calidad alta
                        '-2pass', '0',  # Sin 2-pass
                        '-b_ref_mode', '0',  # Sin frames de referencia extra
                        '-spatial_aq', '1',  # AQ espacial activado
                        '-temporal_aq', '1',  # AQ temporal activado
                        '-c:a', 'copy',
                        '-threads', '0',
                        '-thread_queue_size', '1024',  # Buffer grande
                        '-max_muxing_queue_size', '9999',
                        '-y',
                        output_path
                    ]
                else:
                    cmd = [
                        self.ffmpeg_path,
                        '-f', 'concat',
                        '-safe', '0',
                        '-i', temp_file,
                        '-c', 'copy',
                        '-threads', '0',
                        '-thread_queue_size', '1024',  # Buffer grande
                        '-max_muxing_queue_size', '9999',
                        '-max_interleave_delta', '0',  # Sin límite de entrelazado
                        '-avoid_negative_ts', 'disabled',  # Desactivar verificaciones
                        '-fflags', '+genpts+igndts+ignidx',  # Ignorar índices y timestamps
                        '-y',
                        output_path
                    ]
            else:  # modo "rapido" por defecto
                # Modo rápido: sin pérdida, máxima velocidad
                cmd = [
                    self.ffmpeg_path,
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', temp_file,
                    '-c', 'copy',  # Sin recodificación
                    '-avoid_negative_ts', 'make_zero',
                    '-fflags', '+genpts',
                    '-threads', '0',
                    '-max_muxing_queue_size', '9999',
                    '-y',
                    output_path
                ]
            
            # Usar subprocess.STARTUPINFO para Windows
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                startupinfo=startupinfo
            )
            
            # Almacenar referencia del proceso para poder detenerlo
            self.current_process = process
            
            # Verificar cancelación después de iniciar proceso
            if self.stop_requested:
                try:
                    process.terminate()
                except:
                    pass
                return
            
            # Control de proceso optimizado
            ps_process = psutil.Process(process.pid)
            
            # Configurar prioridad y control según el modo
            try:
                if concat_mode == "turbo":
                    # TURBO: máxima prioridad, sin limitaciones
                    ps_process.nice(psutil.REALTIME_PRIORITY_CLASS if os.name == 'nt' else -20)
                elif concat_mode == "gpu" and use_cuda:
                    # GPU: prioridad alta para aprovechar al máximo
                    ps_process.nice(psutil.HIGH_PRIORITY_CLASS if os.name == 'nt' else -10)
                elif concat_mode == "calidad":
                    # CPU intensivo: prioridad normal con control estricto
                    ps_process.nice(psutil.NORMAL_PRIORITY_CLASS if os.name == 'nt' else 0)
                else:
                    # Modo rápido: prioridad alta, menos control
                    ps_process.nice(psutil.HIGH_PRIORITY_CLASS if os.name == 'nt' else -5)
            except:
                pass
            
            # Control de CPU adaptativo según el modo
            if concat_mode == "turbo":
                # MODO TURBO: usar hasta 90% de CPU/GPU
                while process.poll() is None and not self.stop_requested:
                    current_cpu = psutil.cpu_percent(interval=0.01)
                    if current_cpu > 90:  # Límite del 90%
                        time.sleep(0.01)  # Pausa muy corta
                    else:
                        time.sleep(0.001)  # Mínimo sleep
            else:
                # Modos normales con control de CPU
                cpu_checks = 0
                check_interval = 10 if concat_mode == "rapido" else 3
                
                while process.poll() is None and not self.stop_requested:
                    if cpu_checks % check_interval == 0:
                        current_cpu = psutil.cpu_percent(interval=0.1)
                        
                        # Umbral dinámico según el modo
                        if concat_mode == "gpu" and use_cuda:
                            # Con GPU, permitir más CPU para transferencias
                            cpu_limit = min(self.max_cpu_usage + 10, 95)
                        elif concat_mode == "rapido":
                            # Modo rápido: ser más permisivo
                            cpu_limit = min(self.max_cpu_usage + 5, 90)
                        else:
                            cpu_limit = self.max_cpu_usage
                        
                        if current_cpu > cpu_limit:
                            try:
                                ps_process.suspend()
                                time.sleep(0.1 if concat_mode == "rapido" else 0.3)
                                ps_process.resume()
                            except:
                                pass
                    else:
                        time.sleep(0.02 if concat_mode == "gpu" else 0.05)
                    
                    cpu_checks += 1
            
            stdout, stderr = process.communicate()
            
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if process.returncode == 0:
                success_msg = "Videos concatenados exitosamente"
                
                # Capturar último frame si está habilitado
                if self.capture_frame_var.get():
                    self.progress_var.set("Capturando último frame...")
                    output_dir = os.path.dirname(output_path)
                    frame_path = self.capture_last_frame(output_path, output_dir)
                    
                    if frame_path:
                        success_msg += f"\n\nÚltimo frame guardado en:\n{frame_path}"
                    else:
                        success_msg += "\n\nAdvertencia: No se pudo capturar el último frame"
                
                self.progress_var.set("Concatenación completada exitosamente")
                messagebox.showinfo("Éxito", success_msg)
            else:
                self.progress_var.set("Error en la concatenación")
                error_msg = stderr if stderr else stdout
                # Guardar log de error para debug
                with open('ffmpeg_error.log', 'w') as f:
                    f.write(f"Command: {' '.join(cmd)}\n")
                    f.write(f"Return code: {process.returncode}\n")
                    f.write(f"Stdout: {stdout}\n")
                    f.write(f"Stderr: {stderr}\n")
                messagebox.showerror("Error", f"Error al concatenar videos:\n{error_msg[:500]}\n\nRevisa ffmpeg_error.log para más detalles")
        
        except Exception as e:
            self.progress_var.set("Error inesperado")
            import traceback
            error_details = traceback.format_exc()
            with open('app_error.log', 'w') as f:
                f.write(error_details)
            messagebox.showerror("Error", f"Error inesperado: {str(e)}\n\nRevisa app_error.log para más detalles")
        
        finally:
            self.reset_ui_state()
            # Limpiar archivo temporal si existe
            if 'temp_file' in locals() and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConcat(root)
    root.mainloop()