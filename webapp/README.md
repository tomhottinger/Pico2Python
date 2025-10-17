# Pico CMS Python - Flask Port

Eine Python/Flask-basierte Alternative zu Pico CMS mit vollständiger Docker-Unterstützung.

## Features

✅ **Flat-File CMS** - Keine Datenbank nötig, alles in Markdown  
✅ **Jinja2 Templates** - Fast identisch mit Twig (minimale Anpassungen nötig)  
✅ **YAML Frontmatter** - Wie bei Pico PHP  
✅ **Markdown Extra** - Erweiterte Markdown-Features  
✅ **Docker Ready** - Vollständig containerisiert  
✅ **Gunicorn Production Server** - Production-ready  
✅ **Nginx Reverse Proxy** - Optional für bessere Performance  

## Struktur

```
.
├── app.py                  # Haupt-Flask-Anwendung
├── requirements.txt        # Python-Dependencies
├── Dockerfile             # Container-Definition
├── docker-compose.yml     # Multi-Container Setup
├── nginx.conf            # Nginx Konfiguration
├── setup.sh              # Migrations-Script
└── volumes/              # Persistente Daten
    ├── content/          # Markdown-Dateien
    ├── themes/           # Templates & Assets
    ├── config/           # config.yml
    └── assets/           # Statische Files
```

## Quick Start

### 1. Migration von Pico PHP

Wenn du bereits Pico PHP verwendest:

```bash
# Setup-Script ausführen
./setup.sh
```

Das Script kopiert automatisch:
- Content aus `webrootPico/content/`
- Themes aus `webrootPico/themes/`
- Config aus `webrootPico/config/`
- Assets aus `webrootPico/assets/`

**Wichtig:** Das Script benennt `.twig` Dateien automatisch in `.html` um!

### 2. Manuelle Einrichtung

Falls du von Grund auf startest:

```bash
# Verzeichnisse erstellen
mkdir -p volumes/{content,themes,config,assets}

# Beispiel-Config erstellen
cat > volumes/config/config.yml << EOF
site_title: My Site
theme: default
pages_order_by: alpha
pages_order: asc
content_ext: .md
EOF
```

### 3. Container starten

```bash
# Build und Start
docker-compose up --build

# Oder im Hintergrund
docker-compose up -d --build
```

### 4. Zugriff

- **Mit Nginx:** http://localhost
- **Direkt Flask:** http://localhost:5000

## Template-Migration (Twig → Jinja2)

Die Templates sind **fast identisch**. Hauptunterschiede:

### ✅ Funktioniert ohne Änderung:

```jinja2
{% extends "base.html" %}
{% block content %}
    <h1>{{ meta.title }}</h1>
    {{ content }}
{% endblock %}

{% for page in pages %}
    <a href="{{ page.url }}">{{ page.title }}</a>
{% endfor %}

{% if meta.description %}
    <p>{{ meta.description }}</p>
{% endif %}
```

### ⚠️ Kleine Anpassungen nötig:

| Twig (PHP) | Jinja2 (Python) |
|------------|-----------------|
| `{% extends "base.twig" %}` | `{% extends "base.html" %}` |
| `{{ "now"\|date("Y") }}` | `{{ now().year }}` |
| Dateinamen: `*.twig` | Dateinamen: `*.html` |

### Deine Templates

Basierend auf deinen Dateien musst du anpassen:

**base.twig → base.html:**
```jinja2
{# Funktioniert fast unverändert! #}
{% extends "base.html" %}
```

**chapter.twig → chapter.html:**
```jinja2
{# Navigation bleibt gleich #}
{% for page in pages %}
    {% if page.id == current_page.id %}
        {# ... #}
    {% endif %}
{% endfor %}
```

## Content-Format

Markdown-Dateien mit YAML-Frontmatter (wie bei Pico):

```markdown
---
title: Mein Kapitel
template: chapter
date: 2024-01-15
description: Eine Beschreibung
---

# Content hier

Das ist der eigentliche Inhalt...
```

## Konfiguration

`volumes/config/config.yml`:

```yaml
site_title: Noah's Exodus
theme: roman
pages_order_by: alpha
pages_order: asc
content_ext: .md

# Theme-spezifische Einstellungen
theme_config:
    widescreen: false
```

## Docker Commands

```bash
# Build
docker-compose build

# Start
docker-compose up

# Stop
docker-compose down

# Logs ansehen
docker-compose logs -f

# Nur Flask ohne Nginx
docker-compose up pico-cms

# Container neu starten
docker-compose restart
```

## Development

Für lokale Entwicklung ohne Docker:

```bash
# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# Dependencies installieren
pip install -r requirements.txt

# Environment Variables setzen
export CONFIG_FILE=./volumes/config/config.yml
export CONTENT_DIR=./volumes/content
export THEMES_DIR=./volumes/themes

# App starten
python app.py
```

## Production Deployment

### Mit Docker Compose (empfohlen)

```bash
docker-compose up -d
```

### Nur Flask Container

```bash
docker build -t pico-cms .
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/volumes/content:/app/volumes/content:ro \
  -v $(pwd)/volumes/themes:/app/volumes/themes:ro \
  -v $(pwd)/volumes/config:/app/volumes/config:ro \
  pico-cms
```

## Performance-Tipps

1. **Nginx nutzen** - Besser für statische Dateien
2. **Gunicorn Workers anpassen** - In `Dockerfile`: `--workers 4`
3. **Template-Caching** - In production automatisch aktiv
4. **Static-Files** - Werden von Nginx direkt serviert

## Troubleshooting

### Port bereits belegt
```bash
# Andere Ports nutzen
docker-compose down
# In docker-compose.yml Ports ändern: "8080:5000"
docker-compose up
```

### Theme nicht gefunden
```bash
# Theme-Verzeichnis prüfen
ls -la volumes/themes/
# Sicherstellen dass theme: roman in config.yml gesetzt ist
```

### Templates nicht gefunden
```bash
# .twig in .html umbenennen
find volumes/themes -name "*.twig" -exec rename 's/\.twig$/.html/' {} \;
```

### Markdown wird nicht gerendert
```bash
# Frontmatter prüfen (muss mit --- beginnen und enden)
head -n 5 volumes/content/deine-datei.md
```

## Unterschiede zu Pico PHP

| Feature | Pico PHP | Pico Python |
|---------|----------|-------------|
| Templates | Twig | Jinja2 (fast identisch) |
| Server | Apache/Nginx + PHP-FPM | Gunicorn + Nginx |
| Performance | Gut | Besser bei vielen Requests |
| Setup | PHP installieren | Docker Container |
| Plugins | PHP Plugins | Python Packages |

## Nächste Schritte

1. ✅ Templates migrieren (.twig → .html)
2. ✅ Theme-spezifische Assets prüfen
3. ✅ Content testen
4. ⏭️ Eigene Features als Python-Module hinzufügen
5. ⏭️ SSL/HTTPS konfigurieren (nginx.conf)

## Support

Bei Problemen:
1. Logs prüfen: `docker-compose logs -f`
2. Config validieren: `cat volumes/config/config.yml`
3. Theme-Struktur prüfen: `ls -la volumes/themes/roman/`

## Lizenz

Wie das Original Pico CMS - MIT License
