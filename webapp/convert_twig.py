#!/usr/bin/env python3
"""
Konvertiert Twig-Templates zu Jinja2-kompatiblen Templates
"""

import re
from pathlib import Path
import sys


def convert_twig_to_jinja2(content):
    """
    Konvertiert Twig-Syntax zu Jinja2-Syntax
    """
    
    # 1. Null coalescing operator ?? zu default-Filter
    # {{ var ?? 'default' }} -> {{ var|default('default') }}
    content = re.sub(
        r'{{\s*(\w+(?:\.\w+)*)\s*\?\?\s*([^}]+)\s*}}',
        r'{{ \1|default(\2) }}',
        content
    )
    
    # 2. Komplexere null coalescing mit mehreren Variablen
    # {{ meta.author ?? site_title }} -> {{ meta.author|default(site_title) }}
    content = re.sub(
        r'{{\s*(\w+\.\w+)\s*\?\?\s*(\w+)\s*}}',
        r'{{ \1|default(\2) }}',
        content
    )
    
    # 3. Twig date filter: "now"|date("Y") -> now|date("Y")
    content = re.sub(
        r'"now"\|date',
        r'now|date',
        content
    )
    
    # 4. is empty -> is undefined or not
    content = re.sub(
        r'is\s+empty',
        r'is undefined or not',
        content
    )
    
    # 5. is not empty -> is defined and
    content = re.sub(
        r'is\s+not\s+empty',
        r'is defined and',
        content
    )
    
    return content


def convert_file(file_path):
    """Konvertiert eine einzelne Twig-Datei"""
    print(f"Konvertiere: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    converted = convert_twig_to_jinja2(content)
    
    # Backup erstellen
    backup_path = file_path.with_suffix('.twig.bak')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Backup: {backup_path}")
    
    # Konvertierte Version speichern
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(converted)
    print(f"  ✓ Konvertiert")


def main():
    if len(sys.argv) > 1:
        # Spezifische Dateien
        for path_str in sys.argv[1:]:
            path = Path(path_str)
            if path.exists():
                convert_file(path)
            else:
                print(f"Datei nicht gefunden: {path}")
    else:
        # Alle .twig Dateien im themes-Verzeichnis
        themes_dir = Path(__file__).parent / 'themes'
        
        if not themes_dir.exists():
            print("themes/ Verzeichnis nicht gefunden")
            return
        
        twig_files = list(themes_dir.rglob('*.twig'))
        
        if not twig_files:
            print("Keine .twig Dateien gefunden")
            return
        
        print(f"Gefunden: {len(twig_files)} .twig Dateien\n")
        
        for twig_file in twig_files:
            convert_file(twig_file)
            print()


if __name__ == '__main__':
    main()
