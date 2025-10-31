#!/usr/bin/env python3
"""
Script para subir todos los PDFs del directorio data/ usando el endpoint /ingest.
Asegúrate de que el servidor FastAPI esté corriendo en http://localhost:8000

Uso: python upload_documents.py
"""
import requests
from pathlib import Path
import time


def upload_pdfs(api_url: str = "http://localhost:8000"):
    """Sube todos los PDFs del directorio data/ al endpoint /ingest"""
    
    DATA_DIR = Path("data")
    
    if not DATA_DIR.exists():
        print(f"✗ Directorio {DATA_DIR} no encontrado")
        return
    
    # Obtener todos los PDFs
    pdf_files = sorted(DATA_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print(f"✗ No se encontraron archivos PDF en {DATA_DIR}")
        return
    
    print(f"Encontrados {len(pdf_files)} archivos PDF:")
    for pdf in pdf_files:
        print(f"  - {pdf.name} ({pdf.stat().st_size / 1024 / 1024:.2f} MB)")
    
    print(f"\n📤 Subiendo archivos a {api_url}/ingest...\n")
    
    successful = 0
    failed = 0
    
    for pdf_path in pdf_files:
        print(f"Procesando: {pdf_path.name}...", end=" ", flush=True)
        
        try:
            with open(pdf_path, 'rb') as f:
                files = {'file': (pdf_path.name, f, 'application/pdf')}
                
                start_time = time.time()
                response = requests.post(
                    f"{api_url}/ingest",
                    files=files,
                    timeout=300  # 5 minutos de timeout para PDFs grandes
                )
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    chunks = result.get('chunks', 'N/A')
                    print(f"✓ {chunks} chunks en {elapsed:.1f}s")
                    successful += 1
                else:
                    print(f"✗ Error {response.status_code}: {response.text}")
                    failed += 1
                    
        except requests.exceptions.ConnectionError:
            print("✗ No se pudo conectar al servidor")
            print("\n⚠️  Asegúrate de que el servidor esté corriendo:")
            print("   python src/main.py")
            return
            
        except Exception as e:
            print(f"✗ Error: {e}")
            failed += 1
        
        # Pequeña pausa entre requests
        time.sleep(1)
    
    print(f"\n{'='*50}")
    print(f"✓ Exitosos: {successful}")
    print(f"✗ Fallidos: {failed}")
    print(f"{'='*50}")


if __name__ == "__main__":
    import sys
    
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"API URL: {api_url}")
    print("="*50)
    
    try:
        upload_pdfs(api_url)
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
