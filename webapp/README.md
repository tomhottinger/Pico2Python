# Pico CMS - Python Implementation

Python-basierte Implementierung von Pico CMS mit Flask und Gunicorn.

## Installation

```bash
pip install -r requirements.txt
```

## Entwicklung

Flask Development Server:
```bash
python app.py
```

Öffne: http://localhost:5000

## Produktion

Mit Gunicorn:
```bash
gunicorn -c gunicorn.conf.py app:app
```

Öffne: http://localhost:8000

## Struktur

```
webapp/
├── app.py                 # Hauptanwendung
├── requirements.txt       # Python-Dependencies
├── gunicorn.conf.py      # Gunicorn-Config
├── config/
│   └── config.yml        # CMS-Konfiguration
├── content/              # Markdown-Seiten
│   └── index.md
├── themes/               # Themes (Twig + CSS)
│   └── roman/
│       ├── index.twig
│       └── style.css
└── assets/               # Statische Assets
```

## Content erstellen

Neue Seite: `content/meine-seite.md`

```markdown
---
title: Meine Seite
author: Name
date: 2025-10-17
description: Beschreibung
---

# Überschrift

Content hier...
```

URL: `/meine-seite`

### Unterseiten

Erstelle: `content/blog/erster-post.md`
URL: `/blog/erster-post`

## Theme anpassen

1. Theme-Ordner: `themes/dein-theme/`
2. Template: `index.twig` (Jinja2-Syntax)
3. Styles: `style.css`
4. In `config/config.yml` setzen: `theme: dein-theme`

### Verfügbare Template-Variablen

- `config` - Komplette Config
- `page.title` - Seitentitel
- `page.content` - HTML-Content
- `page.meta` - Meta-Daten
- `page.author` - Autor
- `page.date` - Datum
- `pages` - Liste aller Seiten
- `base_url` - Basis-URL
- `theme_url` - Theme-URL

## Konfiguration

`config/config.yml`:

```yaml
site_title: Meine Website
theme: roman
pages_order_by: alpha  # alpha, date, meta
pages_order: asc       # asc, desc
```

## Kompatibilität

Kompatibel mit:
- Pico CMS Content-Dateien (.md)
- Pico CMS Themes (Twig-Templates)
- Pico CMS Config-Format (YAML)

**Unterschiede zu PHP-Pico:**
- Jinja2 statt Twig (sehr ähnlich)
- Python-Markdown statt PHP-Parsedown
- Flask statt PHP

## Lizenz

MIT
