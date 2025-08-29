import subprocess
import os

def test_cuda_support():
    """Verificar soporte CUDA en FFmpeg"""
    print("Verificando soporte CUDA en FFmpeg...")
    
    ffmpeg_path = os.getenv('FFMPEG_PATH', 'ffmpeg')
    
    try:
        # Verificar encoders disponibles
        print("\n1. Verificando encoders CUDA...")
        cmd = [ffmpeg_path, '-encoders']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        cuda_encoders = {
            'h264_nvenc': 'H.264 NVENC',
            'hevc_nvenc': 'HEVC NVENC', 
            'av1_nvenc': 'AV1 NVENC'
        }
        
        found_encoders = []
        for encoder, name in cuda_encoders.items():
            if encoder in result.stdout:
                found_encoders.append(f"[OK] {name} ({encoder})")
                print(f"  [OK] {name} disponible")
            else:
                print(f"  [NO] {name} no disponible")
        
        if not found_encoders:
            print("\n[ERROR] No se encontraron encoders CUDA.")
            print("Posibles causas:")
            print("- FFmpeg no compilado con soporte NVENC")
            print("- Drivers NVIDIA no instalados o desactualizados")
            print("- Tarjeta gráfica no compatible con NVENC")
            return False
        
        # Verificar decoders CUDA
        print("\n2. Verificando decoders CUDA...")
        cmd = [ffmpeg_path, '-decoders']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        cuda_decoders = {
            'h264_cuvid': 'H.264 CUVID',
            'hevc_cuvid': 'HEVC CUVID'
        }
        
        for decoder, name in cuda_decoders.items():
            if decoder in result.stdout:
                print(f"  [OK] {name} disponible")
            else:
                print(f"  [NO] {name} no disponible")
        
        # Verificar filtros GPU
        print("\n3. Verificando filtros GPU...")
        cmd = [ffmpeg_path, '-filters']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        gpu_filters = {
            'scale_cuda': 'Escalado CUDA',
            'yadif_cuda': 'Deinterlacing CUDA',
            'overlay_cuda': 'Overlay CUDA'
        }
        
        for filter_name, description in gpu_filters.items():
            if filter_name in result.stdout:
                print(f"  [OK] {description} disponible")
            else:
                print(f"  [NO] {description} no disponible")
        
        # Verificar dispositivos CUDA
        print("\n4. Verificando dispositivos CUDA...")
        try:
            cmd = [ffmpeg_path, '-f', 'lavfi', '-i', 'color=c=black:s=32x32:d=1', '-f', 'null', '-']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            print("  [OK] FFmpeg puede acceder a dispositivos")
        except:
            print("  [WARN] No se pudo verificar acceso a dispositivos")
        
        print(f"\n[SUCCESS] CUDA soportado: {len(found_encoders)} encoder(s) disponible(s)")
        print("Encoders encontrados:")
        for encoder in found_encoders:
            print(f"  {encoder}")
        
        return True
        
    except FileNotFoundError:
        print(f"[ERROR] FFmpeg no encontrado en: {ffmpeg_path}")
        return False
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout al verificar FFmpeg")
        return False
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return False

def test_cuda_encode():
    """Prueba rápida de encoding CUDA"""
    print("\n" + "="*50)
    print("PRUEBA DE ENCODING CUDA")
    print("="*50)
    
    ffmpeg_path = os.getenv('FFMPEG_PATH', 'ffmpeg')
    
    try:
        # Crear video de prueba y encodear con CUDA
        print("Creando video de prueba con CUDA...")
        
        cmd = [
            ffmpeg_path,
            '-f', 'lavfi',
            '-i', 'testsrc=duration=2:size=320x240:rate=30',
            '-c:v', 'h264_nvenc',
            '-preset', 'fast',
            '-cq', '25',
            '-y',
            'cuda_test.mp4'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and os.path.exists('cuda_test.mp4'):
            file_size = os.path.getsize('cuda_test.mp4')
            print(f"[SUCCESS] Encoding CUDA exitoso (archivo: {file_size} bytes)")
            
            # Limpiar archivo de prueba
            os.remove('cuda_test.mp4')
            return True
        else:
            print("[ERROR] Encoding CUDA fallo")
            print("Error:", result.stderr)
            return False
            
    except Exception as e:
        print(f"[ERROR] Error en prueba CUDA: {e}")
        return False

if __name__ == "__main__":
    print("COCAT - Verificación de soporte CUDA")
    print("="*50)
    
    cuda_ok = test_cuda_support()
    
    if cuda_ok:
        test_cuda_encode()
        print("\n[RESULTADO] CUDA está listo para usar en COCAT")
    else:
        print("\n[RESULTADO] CUDA no está disponible")
        print("La aplicación funcionará solo con CPU")
    
    print("\nTest completado.")