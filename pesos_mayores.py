
#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import math

def convert_size(size_bytes):
    """Convertir bytes a formato legible (KB, MB, GB, etc.)"""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def get_dir_size(path):
    """Calcular tamaño total de un directorio recursivamente"""
    total = 0
    for entry in os.scandir(path):
        try:
            if entry.is_symlink():
                continue
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
        except (PermissionError, FileNotFoundError):
            continue
    return total

def is_large_file(size_bytes, threshold_mb=98):
    """Verificar si un archivo es mayor al umbral especificado en MB"""
    threshold_bytes = threshold_mb * 1024 * 1024  # Convertir MB a bytes
    return size_bytes > threshold_bytes

def find_large_files(path, threshold_mb=98):
    """Encontrar recursivamente todos los archivos mayores al umbral especificado"""
    large_files = []
    
    try:
        for entry in os.scandir(path):
            if entry.is_symlink():
                continue
                
            if entry.is_file():
                try:
                    size = entry.stat().st_size
                    if is_large_file(size, threshold_mb):
                        large_files.append((entry.name, size, entry.path))
                except (PermissionError, FileNotFoundError):
                    continue
            elif entry.is_dir():
                # Recursión para subdirectorios
                large_files.extend(find_large_files(entry.path, threshold_mb))
    except (PermissionError, FileNotFoundError):
        pass
    
    return large_files

def group_files_by_directory(large_files, base_path):
    """Agrupar archivos por directorio para mostrar estructura de árbol"""
    dir_structure = {}
    
    for name, size, full_path in large_files:
        # Obtener el directorio relativo
        rel_path = os.path.relpath(os.path.dirname(full_path), base_path)
        if rel_path == '.':
            rel_path = ''
        
        if rel_path not in dir_structure:
            dir_structure[rel_path] = []
        
        dir_structure[rel_path].append((name, size, full_path))
    
    # Ordenar archivos dentro de cada directorio por tamaño (descendente)
    for rel_path in dir_structure:
        dir_structure[rel_path].sort(key=lambda x: -x[1])
    
    return dir_structure

def print_filtered_tree(dir_structure, base_path):
    """Imprimir árbol solo con archivos grandes"""
    # Ordenar directorios
    sorted_dirs = sorted(dir_structure.keys())
    
    for i, rel_path in enumerate(sorted_dirs):
        files = dir_structure[rel_path]
        
        if not files:
            continue
        
        # Mostrar directorio (si no es el directorio raíz)
        if rel_path:
            # Dividir el path en componentes para mostrar jerarquía
            path_parts = rel_path.split(os.sep)
            for j, part in enumerate(path_parts):
                indent = "    " * j
                if j == len(path_parts) - 1:
                    # Último componente del path
                    prefix = "└── " if i == len(sorted_dirs) - 1 and j == len(path_parts) - 1 else "├── "
                else:
                    prefix = "├── "
                
                print(f"{indent}{prefix}[{part}]/")
        else:
            print("[Directorio raíz]/")
        
        # Mostrar archivos en este directorio
        path_depth = len(rel_path.split(os.sep)) if rel_path else 0
        for k, (name, size, full_path) in enumerate(files):
            is_last_file = k == len(files) - 1
            file_prefix = "└── " if is_last_file else "├── "
            file_indent = "    " * (path_depth + 1) if rel_path else "    "
            
            print(f"{file_indent}{file_prefix}→ {name} - {convert_size(size)}")
        
        print()  # Línea en blanco entre directorios

def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "."

    # Umbral personalizable (por defecto 98MB)
    threshold_mb = 98
    if len(sys.argv) > 2:
        try:
            threshold_mb = float(sys.argv[2])
        except ValueError:
            print("Advertencia: El segundo parámetro debe ser un número para el umbral en MB")

    path = Path(path).resolve()
    
    if not path.exists():
        print(f"Error: El directorio {path} no existe")
        sys.exit(1)
    elif not path.is_dir():
        print(f"Error: {path} no es un directorio")
        sys.exit(1)

    print(f"\nAnálisis de archivos grandes en: {path}")
    print(f"Mostrando solo archivos mayores a {threshold_mb} MB\n")
    
    # Encontrar archivos grandes
    large_files = find_large_files(path, threshold_mb)
    
    if not large_files:
        print(f"No se encontraron archivos mayores a {threshold_mb} MB en el directorio especificado.")
        return
    
    # Calcular tamaño total de archivos grandes
    total_large_size = sum(size for _, size, _ in large_files)
    print(f"Total de archivos grandes encontrados: {len(large_files)}")
    print(f"Tamaño total de archivos grandes: {convert_size(total_large_size)}")
    print(f"Tamaño total del directorio: {convert_size(get_dir_size(path))}\n")
    
    # Agrupar por directorio y mostrar
    dir_structure = group_files_by_directory(large_files, str(path))
    print_filtered_tree(dir_structure, str(path))

if __name__ == "__main__":
    main()