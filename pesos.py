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

def analyze_directory(path, indent=0, max_depth=None, current_depth=0):
    """Analizar directorio recursivamente y mostrar estructura con tamaños"""
    try:
        entries = sorted(os.scandir(path), key=lambda x: (-get_dir_size(x.path) if x.is_dir() else -x.stat().st_size, x.name))
    except (PermissionError, FileNotFoundError):
        return

    for i, entry in enumerate(entries):
        if max_depth is not None and current_depth >= max_depth:
            continue
            
        is_last = i == len(entries) - 1
        prefix = "└── " if is_last else "├── "
        
        try:
            if entry.is_dir():
                size = get_dir_size(entry.path)
                print(f"{'    ' * indent}{prefix}[{entry.name}] (dir) - {convert_size(size)}")
                analyze_directory(entry.path, indent + 1, max_depth, current_depth + 1)
            elif entry.is_file():
                print(f"{'    ' * indent}{prefix}{entry.name} - {convert_size(entry.stat().st_size)}")
        except (PermissionError, FileNotFoundError):
            print(f"{'    ' * indent}{prefix}{entry.name} [error al acceder]")

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
    print(f"\nAnálisis de: {path}\n")
    print(f"Tamaño total: {convert_size(total_size)}\n")
    print("Contenido ordenado por tamaño (de mayor a menor):\n")
    analyze_directory(path)
    print()

if __name__ == "__main__":
    main()