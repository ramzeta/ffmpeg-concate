import subprocess
import os

def test_ffmpeg():
    """Verificar instalación de FFmpeg"""
    print("Probando FFmpeg...")
    
    # Probar diferentes ubicaciones comunes
    ffmpeg_paths = [
        'ffmpeg',
        'ffmpeg.exe',
        r'C:\ffmpeg\bin\ffmpeg.exe',
        r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
        r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe'
    ]
    
    ffmpeg_found = None
    
    for path in ffmpeg_paths:
        try:
            result = subprocess.run([path, '-version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                ffmpeg_found = path
                print(f"[OK] FFmpeg encontrado en: {path}")
                print(f"     Version: {result.stdout.split('\\n')[0] if result.stdout else 'Unknown'}")
                break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    if not ffmpeg_found:
        print("\n[ERROR] FFmpeg NO ENCONTRADO")
        print("\nPara instalar FFmpeg:")
        print("1. Descarga desde: https://www.ffmpeg.org/download.html")
        print("2. Extrae los archivos")
        print("3. Agrega la carpeta 'bin' al PATH del sistema")
        print("   O configura la variable de entorno FFMPEG_PATH")
    else:
        # Probar concatenación simple
        print("\nProbando funcionalidad de concatenación...")
        test_file = "test_concat.txt"
        try:
            with open(test_file, 'w') as f:
                f.write("# Test file for FFmpeg concat\n")
            
            cmd = [ffmpeg_found, '-f', 'concat', '-safe', '0', '-i', test_file, '-f', 'null', '-']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if "At least one output file must be specified" in result.stderr or result.returncode == 1:
                print("[OK] FFmpeg concat demuxer funciona correctamente")
            else:
                print("[WARN] FFmpeg concat puede tener problemas")
        except Exception as e:
            print(f"[WARN] Error al probar concat: {e}")
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
    
    return ffmpeg_found

if __name__ == "__main__":
    found_path = test_ffmpeg()
    if found_path and found_path != 'ffmpeg':
        print(f"\nConfigura la variable de entorno:")
        print(f"set FFMPEG_PATH={found_path}")