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

def get_directories_sorted(path):
    """Obtener todos los directorios ordenados por tamaño (descendente)"""
    dirs = []
    for entry in os.scandir(path):
        if entry.is_dir() and not entry.is_symlink():
            try:
                size = get_dir_size(entry.path)
                dirs.append((entry.name, size, entry.path))
            except (PermissionError, FileNotFoundError):
                dirs.append((entry.name, 0, entry.path))
    
    # Ordenar por tamaño (descendente), luego alfabéticamente
    dirs.sort(key=lambda x: (-x[1], x[0]))
    return dirs

def print_directory_tree(dirs, indent=0, parent_path=None):
    """Imprimir árbol de directorios con tamaños"""
    for i, (name, size, full_path) in enumerate(dirs):
        is_last = i == len(dirs) - 1
        prefix = "└── " if is_last else "├── "
        
        # Solo procesar subdirectorios del directorio actual
        if parent_path is not None and not full_path.startswith(parent_path):
            continue
            
        print(f"{'    ' * indent}{prefix}[{name}] - {convert_size(size)}")
        
        # Obtener subdirectorios de este directorio
        sub_dirs = get_directories_sorted(full_path)
        if sub_dirs:
            print_directory_tree(sub_dirs, indent + 1, full_path)

def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "."

    path = Path(path).resolve()
    
    if not path.exists():
        print(f"Error: El directorio {path} no existe")
        sys.exit(1)
    elif not path.is_dir():
        print(f"Error: {path} no es un directorio")
        sys.exit(1)

    total_size = get_dir_size(path)
    print(f"\nAnálisis de directorios en: {path}\n")
    print(f"Tamaño total: {convert_size(total_size)}\n")
    print("Directorios ordenados por tamaño (de mayor a menor):\n")
    
    dirs = get_directories_sorted(path)
    print_directory_tree(dirs, 0)

if __name__ == "__main__":
    main()
