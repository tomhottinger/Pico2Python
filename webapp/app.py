#!/usr/bin/env python3
"""
Flask-based Pico CMS Alternative
A flat-file CMS using Markdown files and Jinja2 templates
"""

import os
import yaml
import markdown
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, abort
from markdown.extensions.extra import ExtraExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension

# Initialize Flask app
app = Flask(__name__)

# Configuration
CONFIG_FILE = os.environ.get('CONFIG_FILE', '/app/volumes/config/config.yml')
CONTENT_DIR = os.environ.get('CONTENT_DIR', '/app/volumes/content')
THEMES_DIR = os.environ.get('THEMES_DIR', '/app/volumes/themes')


class PicoConfig:
    """Load and manage Pico configuration"""
    
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path):
        """Load YAML configuration file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"Warning: Config file not found at {config_path}, using defaults")
            return {}
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)


class Page:
    """Represents a single page/content file"""
    
    def __init__(self, file_path, base_url='', content_dir=''):
        self.file_path = file_path
        self.content_dir = Path(content_dir)
        self.base_url = base_url
        self.meta = {}
        self.content = ''
        self.raw_content = ''
        self._parse_file()
        
    def _parse_file(self):
        """Parse markdown file with YAML frontmatter"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Split frontmatter and content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    # Parse YAML frontmatter
                    try:
                        self.meta = yaml.safe_load(parts[1]) or {}
                    except yaml.YAMLError:
                        self.meta = {}
                    self.raw_content = parts[2].strip()
                else:
                    self.raw_content = content
            else:
                self.raw_content = content
                
            # Convert markdown to HTML
            md = markdown.Markdown(extensions=[
                ExtraExtension(),
                CodeHiliteExtension(css_class='highlight'),
                TocExtension(permalink=True)
            ])
            self.content = md.convert(self.raw_content)
            
            # Generate URL from file path
            self.url = self._generate_url()
            
            # Set page ID (relative path without extension)
            self.id = str(Path(self.file_path).relative_to(self.content_dir).with_suffix(''))
            
            # Add file modification date if not in meta
            if 'date' not in self.meta:
                mtime = os.path.getmtime(self.file_path)
                self.meta['date'] = datetime.fromtimestamp(mtime)
                
        except Exception as e:
            print(f"Error parsing file {self.file_path}: {e}")
            self.content = ''
            
    def _generate_url(self):
        """Generate URL from file path"""
        rel_path = Path(self.file_path).relative_to(self.content_dir)
        
        # Handle index files
        if rel_path.stem == 'index':
            if rel_path.parent == Path('.'):
                return self.base_url + '/'
            return self.base_url + '/' + str(rel_path.parent) + '/'
        
        # Regular files
        url_path = str(rel_path.with_suffix(''))
        return self.base_url + '/' + url_path
    
    @property
    def title(self):
        """Get page title from meta or generate from filename"""
        return self.meta.get('title', Path(self.file_path).stem.replace('-', ' ').title())
    
    @property
    def template(self):
        """Get template name from meta or use default"""
        return self.meta.get('template', 'index')
    
    @property
    def date(self):
        """Get page date"""
        return self.meta.get('date')
    
    @property
    def description(self):
        """Get page description"""
        return self.meta.get('description', '')


class PageManager:
    """Manage all pages/content files"""
    
    def __init__(self, content_dir, base_url='', config=None):
        self.content_dir = Path(content_dir)
        self.base_url = base_url
        self.config = config or {}
        self.pages = []
        self._load_pages()
        
    def _load_pages(self):
        """Load all markdown files from content directory"""
        content_ext = self.config.get('content_ext', '.md')
        
        if not self.content_dir.exists():
            print(f"Warning: Content directory not found: {self.content_dir}")
            return
            
        # Find all markdown files
        for md_file in self.content_dir.rglob(f'*{content_ext}'):
            if md_file.is_file():
                page = Page(str(md_file), self.base_url, str(self.content_dir))
                self.pages.append(page)
        
        # Sort pages
        self._sort_pages()
        
    def _sort_pages(self):
        """Sort pages according to configuration"""
        pages_order_by = self.config.get('pages_order_by', 'alpha')
        pages_order = self.config.get('pages_order', 'asc')
        
        reverse = (pages_order == 'desc')
        
        if pages_order_by == 'date':
            self.pages.sort(key=lambda p: p.date or datetime.min, reverse=reverse)
        elif pages_order_by == 'meta':
            meta_key = self.config.get('pages_order_by_meta', 'title')
            self.pages.sort(key=lambda p: p.meta.get(meta_key, ''), reverse=reverse)
        else:  # alpha
            self.pages.sort(key=lambda p: p.title, reverse=reverse)
    
    def get_page_by_url(self, url):
        """Get page by URL"""
        # Normalize URL
        if not url.startswith('/'):
            url = '/' + url
        if not url.endswith('/') and url != '/':
            url = url + '/'
            
        base_url = self.base_url if self.base_url else ''
        
        for page in self.pages:
            page_url = page.url
            if not page_url.endswith('/'):
                page_url = page_url + '/'
                
            if page_url == base_url + url:
                return page
        return None
    
    def get_all_pages(self):
        """Get all pages"""
        return self.pages


# Initialize configuration and page manager
config = PicoConfig(CONFIG_FILE)
base_url = config.get('base_url', '').rstrip('/')

# Configure Flask
app.config['THEME'] = config.get('theme', 'default')
app.config['SITE_TITLE'] = config.get('site_title', 'Pico')
app.config['DEBUG'] = config.get('debug', False)

# Set template folder to themes directory
theme_name = app.config['THEME']
theme_path = os.path.join(THEMES_DIR, theme_name)
app.template_folder = theme_path

# Set static folder
app.static_folder = os.path.join(theme_path, 'assets')
app.static_url_path = '/assets'

# Initialize page manager
page_manager = PageManager(CONTENT_DIR, base_url, config.config)


@app.context_processor
def inject_globals():
    """Inject global variables into all templates"""
    return {
        'site_title': app.config['SITE_TITLE'],
        'base_url': base_url,
        'theme_url': f'{base_url}/assets',
        'pages': page_manager.get_all_pages(),
        'config': config.config
    }


@app.route('/')
def index():
    """Serve index page"""
    page = page_manager.get_page_by_url('/')
    
    if not page:
        # Try to find index.md
        for p in page_manager.get_all_pages():
            if p.id == 'index' or p.id.endswith('/index'):
                page = p
                break
    
    if not page:
        abort(404)
    
    template_name = page.template + '.html'
    
    return render_template(
        template_name,
        current_page=page,
        meta=page.meta,
        content=page.content
    )


@app.route('/<path:url>')
def serve_page(url):
    """Serve any page by URL"""
    page = page_manager.get_page_by_url('/' + url)
    
    if not page:
        abort(404)
    
    template_name = page.template + '.html'
    
    # Check if template file exists, fallback to index.html
    template_path = os.path.join(app.template_folder, template_name)
    if not os.path.exists(template_path):
        template_name = 'index.html'
    
    return render_template(
        template_name,
        current_page=page,
        meta=page.meta,
        content=page.content
    )


@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 error page"""
    return render_template(
        'error.html' if os.path.exists(os.path.join(app.template_folder, 'error.html')) else 'index.html',
        meta={'title': '404 - Page Not Found'},
        content='<h1>404 - Page Not Found</h1><p>The requested page could not be found.</p>'
    ), 404


if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)
