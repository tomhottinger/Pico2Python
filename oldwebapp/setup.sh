#!/bin/bash

echo "==================================="
echo "Pico CMS Python Migration Setup"
echo "==================================="
echo ""

# Create volumes directory structure
echo "Creating volume directories..."
mkdir -p volumes/content
mkdir -p volumes/themes
mkdir -p volumes/config
mkdir -p volumes/assets

# Copy content from PHP Pico if available
if [ -d "webrootPico/content" ]; then
    echo "Copying content from PHP Pico..."
    cp -r webrootPico/content/* volumes/content/ 2>/dev/null || echo "No content files found"
fi

# Copy themes from PHP Pico if available
if [ -d "webrootPico/themes" ]; then
    echo "Copying themes from PHP Pico..."
    cp -r webrootPico/themes/* volumes/themes/ 2>/dev/null || echo "No theme files found"
    
    # Rename .twig files to .html in themes
    echo "Renaming Twig templates to HTML..."
    find volumes/themes -name "*.twig" -type f | while read file; do
        mv "$file" "${file%.twig}.html"
    done
fi

# Copy config from PHP Pico if available
if [ -f "webrootPico/config/config.yml" ]; then
    echo "Copying configuration..."
    cp webrootPico/config/config.yml volumes/config/
else
    # Create default config if none exists
    echo "Creating default configuration..."
    cat > volumes/config/config.yml << 'EOF'
##
# Basic
#
site_title: My Pico Site
base_url: ~
rewrite_url: true
debug: false
timezone: Europe/Zurich
locale: de_CH

##
# Theme
#
theme: default
theme_config:
    widescreen: false

##
# Content
#
date_format: "%d.%m.%Y"
pages_order_by: alpha
pages_order: asc
content_dir: ~
content_ext: .md
content_config:
    extra: true
    breaks: false
    escape: false
    auto_urls: true
assets_dir: assets/

##
# Custom
#
my_custom_setting: Hello World!
EOF
fi

# Copy assets if available
if [ -d "webrootPico/assets" ]; then
    echo "Copying assets..."
    cp -r webrootPico/assets/* volumes/assets/ 2>/dev/null || echo "No asset files found"
fi

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Review volumes/config/config.yml"
echo "2. Check your themes in volumes/themes/"
echo "3. Verify content in volumes/content/"
echo "4. Build and run: docker-compose up --build"
echo ""
echo "Access your site at: http://localhost"
echo "Direct Flask access: http://localhost:5000"
echo ""
