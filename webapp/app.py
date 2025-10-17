#!/usr/bin/env python3
"""
Pico CMS Python Implementation
Flask-basierte Webapp mit Markdown-Rendering und Twig-Templates
"""

from flask import Flask, render_template_string, abort, send_from_directory
from pathlib import Path
import yaml
import markdown
from markdown.extensions.extra import ExtraExtension
from markdown.extensions.meta import MetaExtension
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from jinja2.ext import Extension
from datetime import datetime
import re

app = Flask(__name__)

# Pfade
BASE_DIR = Path(__file__).parent
CONFIG_DIR = BASE_DIR / 'config'
CONTENT_DIR = BASE_DIR / 'content'
THEMES_DIR = BASE_DIR / 'themes'
ASSETS_DIR = BASE_DIR / 'assets'


class PicoCMS:
    """Kern-Logik für Pico CMS"""
    
    def __init__(self):
        self.config = self.load_config()
        self.theme = self.config.get('theme', 'default')
        self.md = markdown.Markdown(extensions=[
            ExtraExtension(),
            MetaExtension()
        ])
        
        # Jinja2 Environment für Theme-Templates
        theme_path = THEMES_DIR / self.theme
        if not theme_path.exists():
            theme_path = THEMES_DIR / 'default'
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(theme_path)),
            autoescape=False  # Erlaubt HTML ohne |safe
        )
        
        # Twig-kompatible Filter hinzufügen
        def date_filter(value, format='%Y-%m-%d'):
            """Twig-kompatibler date-Filter"""
            if isinstance(value, str):
                if value.lower() == 'now':
                    dt = datetime.now()
                else:
                    try:
                        dt = datetime.fromisoformat(value)
                    except:
                        return value
            elif isinstance(value, datetime):
                dt = value
            else:
                dt = datetime.now()
            
            # PHP date format zu Python strftime
            format = format.replace('Y', '%Y').replace('m', '%m').replace('d', '%d')
            format = format.replace('H', '%H').replace('i', '%M').replace('s', '%S')
            
            return dt.strftime(format)
        
        self.jinja_env.filters['date'] = date_filter
        
        # Twig-kompatible Tests
        self.jinja_env.tests['empty'] = lambda x: not x if x is not None else True
    
    def load_config(self):
        """Lädt config.yml"""
        config_file = CONFIG_DIR / 'config.yml'
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def get_page(self, url_path):
        """Lädt und rendert eine Markdown-Seite"""
        # URL zu Dateipfad konvertieren
        if not url_path or url_path == '/':
            file_path = CONTENT_DIR / 'index.md'
        else:
            # Entferne führenden Slash
            clean_path = url_path.lstrip('/')
            file_path = CONTENT_DIR / f"{clean_path}.md"
            
            # Fallback: Prüfe ob es ein Verzeichnis mit index.md ist
            if not file_path.exists():
                dir_path = CONTENT_DIR / clean_path / 'index.md'
                if dir_path.exists():
                    file_path = dir_path
        
        if not file_path.exists():
            return None
        
        # Lese und parse Markdown
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reset Markdown-Parser
        self.md.reset()
        html_content = self.md.convert(content)
        
        # Extrahiere Meta-Daten
        meta = {}
        if hasattr(self.md, 'Meta'):
            for key, value in self.md.Meta.items():
                # Keys zu lowercase für Konsistenz
                meta[key.lower()] = value[0] if len(value) == 1 else value
        
        return {
            'title': meta.get('title', self.config.get('site_title', 'Pico')),
            'content': html_content,
            'meta': meta,
            'url': url_path,
            'date': meta.get('date', ''),
            'author': meta.get('author', ''),
            'description': meta.get('description', ''),
            'id': str(file_path)  # Eindeutige ID für Vergleiche
        }
    
    def get_pages(self):
        """Liste aller Seiten für Navigation"""
        pages = []
        
        for md_file in CONTENT_DIR.rglob('*.md'):
            rel_path = md_file.relative_to(CONTENT_DIR)
            
            # Lese Meta-Daten
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.md.reset()
            self.md.convert(content)
            
            meta = {}
            if hasattr(self.md, 'Meta'):
                for key, value in self.md.Meta.items():
                    # Keys zu lowercase für Konsistenz
                    meta[key.lower()] = value[0] if len(value) == 1 else value
            
            # Konstruiere URL
            if rel_path.name == 'index.md':
                if rel_path.parent == Path('.'):
                    url = '/'
                else:
                    url = f"/{rel_path.parent}"
            else:
                url = f"/{rel_path.with_suffix('')}"
            
            pages.append({
                'title': meta.get('title', rel_path.stem),
                'url': str(url).replace('\\', '/'),
                'meta': meta,
                'date': meta.get('date', ''),
                'author': meta.get('author', ''),
                'id': str(md_file)  # Eindeutige ID
            })
        
        # Sortierung
        order_by = self.config.get('pages_order_by', 'alpha')
        order = self.config.get('pages_order', 'asc')
        reverse = order == 'desc'
        
        if order_by == 'alpha':
            pages.sort(key=lambda p: p['title'], reverse=reverse)
        elif order_by == 'date':
            pages.sort(key=lambda p: p.get('date', ''), reverse=reverse)
        elif order_by == 'meta':
            meta_key = self.config.get('pages_order_by_meta', 'author')
            pages.sort(key=lambda p: p['meta'].get(meta_key, ''), reverse=reverse)
        
        # Zusätzlich: Sortiere nach Ordering falls vorhanden
        # Seiten mit Ordering kommen zuerst, sortiert nach Ordering-Wert
        pages_with_ordering = [p for p in pages if 'ordering' in p['meta']]
        pages_without_ordering = [p for p in pages if 'ordering' not in p['meta']]
        
        if pages_with_ordering:
            # Konvertiere Ordering zu int für korrekte Sortierung
            pages_with_ordering.sort(key=lambda p: int(p['meta'].get('ordering', 0)))
            pages = pages_with_ordering + pages_without_ordering
        
        return pages
    
    def render(self, page_data):
        """Rendert Seite mit Theme-Template"""
        # Wähle Template basierend auf Meta-Daten
        template_name = page_data.get('meta', {}).get('template', 'index')
        template_file = f"{template_name}.twig"
        
        try:
            template = self.jinja_env.get_template(template_file)
        except TemplateNotFound:
            # Fallback: index.twig
            try:
                template = self.jinja_env.get_template('index.twig')
            except TemplateNotFound:
                # Letzter Fallback: Einfaches HTML
                return f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>{page_data['title']}</title>
                    <meta charset="utf-8">
                </head>
                <body>
                    <h1>{page_data['title']}</h1>
                    {page_data['content']}
                </body>
                </html>
                """
        
        # DEBUG: Prüfe ob content vorhanden ist
        print(f"DEBUG: Title = {page_data.get('title')}")
        print(f"DEBUG: Template = {page_data.get('meta', {}).get('template', 'index')}")
        print(f"DEBUG: Content length = {len(page_data.get('content', ''))}")
        print(f"DEBUG: Content preview = {page_data.get('content', '')[:200]}")
        
        # Berechne prev/next für Navigation
        all_pages = self.get_pages()
        prev_page = None
        next_page = None
        
        current_id = page_data.get('id')
        current_index = -1
        
        for i, p in enumerate(all_pages):
            if p.get('id') == current_id:
                current_index = i
                if i > 0:
                    prev_page = all_pages[i - 1]
                if i < len(all_pages) - 1:
                    next_page = all_pages[i + 1]
                break
        
        print(f"DEBUG: Current page index = {current_index} of {len(all_pages)}")
        print(f"DEBUG: Prev page = {prev_page['title'] if prev_page else 'None'}")
        print(f"DEBUG: Next page = {next_page['title'] if next_page else 'None'}")
        
        # Bereite Context vor mit default-Werten
        context = {
            'config': self.config,
            'page': page_data,
            'pages': all_pages,
            'base_url': self.config.get('base_url', '/'),
            'theme_url': f"/themes/{self.theme}",
            'site_title': self.config.get('site_title', 'Pico'),
            'meta': page_data.get('meta', {}),
            'current_page': page_data,
            'now': datetime.now(),
            # Twig-Kompatibilität: Direkte Variablen
            'content': page_data.get('content', ''),
            'title': page_data.get('title', ''),
            # Navigation
            'prev_page': prev_page,
            'next_page': next_page
        }
        
        return template.render(**context)


# Initialisiere Pico
pico = PicoCMS()


@app.route('/')
@app.route('/<path:url_path>')
def page(url_path=''):
    """Hauptroute für alle Seiten"""
    page_data = pico.get_page('/' + url_path if url_path else '/')
    
    if page_data is None:
        abort(404)
    
    return pico.render(page_data)


@app.route('/assets/<path:filename>')
def assets(filename):
    """Statische Assets"""
    return send_from_directory(ASSETS_DIR, filename)


@app.route('/themes/<theme_name>/<path:filename>')
def theme_assets(theme_name, filename):
    """Theme-spezifische Assets"""
    theme_dir = THEMES_DIR / theme_name
    return send_from_directory(theme_dir, filename)


@app.errorhandler(404)
def not_found(error):
    """404 Handler"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>404 - Not Found</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>404 - Seite nicht gefunden</h1>
        <p>Die angeforderte Seite existiert nicht.</p>
        <a href="/">Zurück zur Startseite</a>
    </body>
    </html>
    """, 404


if __name__ == '__main__':
    # Entwicklungsserver
    app.run(host='0.0.0.0', port=5000, debug=True)
