import os
import re

from pathlib import Path

BASE_DIR = Path(r"e:\SeatSense")
TEMPLATES_DIR = BASE_DIR / "templates" / "seatsense_app"

STATIC_DIRS = ['css', 'images', 'js', 'plugins', 'fonts']

def to_view_name(filename):
    name = filename.replace('.html', '')
    if name == 'index':
        return 'index'
    name = name.replace('-', '_').lower()
    if name[0].isdigit():
        name = f"page_{name}"
    return name

def convert_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Ensure {% load static %} is at the top
    if '{% load static %}' not in content:
        content = '{% load static %}\n' + content

    # 1. Replace static links
    # Match href="css/...", src="images/...", etc.
    # We do a smart replacement.
    for folder in STATIC_DIRS:
        # Match quotes and optional leading slash or relative traverse
        pattern = r'(href|src)=([\'"])((?:\.\./)*/*)(' + folder + r'/.*?)\2'
        
        def static_repl(match):
            attr = match.group(1) # href or src
            folder_path = match.group(4)
            # if already has static tag, leave it alone (it wouldn't match anyway because of the curly braces)
            return f'{attr}="{{% static \'seatsense_app/{folder_path}\' %}}"'
        
        content = re.sub(pattern, static_repl, content)

    # 2. Replace .html links
    # Match href="some-page.html"
    def url_repl(match):
        html_file = match.group(3)
        view_name = to_view_name(html_file)
        # Avoid double replacing if it's somehow already in a django tag
        if html_file in [f.name for f in TEMPLATES_DIR.glob('*.html')]:
            # if we are linking to a valid template file!
            return f'{match.group(1)}="{{% url \'{view_name}\' %}}"'
        return match.group(0)

    # Note: we shouldn't replace href="#" or similar
    pattern_html = r'(href|action)=([\'"])(.*?\.html)\2'
    content = re.sub(pattern_html, url_repl, content)

    # Also handle things like style="background-image: url(images/...)"
    for folder in STATIC_DIRS:
        # Match url('images/...'), url("images/..."), url(images/...)
        pattern_bg = r'url\(([\'"]?)((?:\.\./)*/*)(' + folder + r'/.*?)\1\)'
        
        def bg_repl(match):
            folder_path = match.group(3)
            return f"url('{{% static \"seatsense_app/{folder_path}\" %}}')"
            
        content = re.sub(pattern_bg, bg_repl, content)

    # Fix the incorrectly generated 404 url pattern
    content = content.replace("{% url '404' %}", "{% url 'page_404' %}")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def generate_views_and_urls():
    html_files = [f.name for f in TEMPLATES_DIR.glob('*.html')]
    
    views_code = "from django.shortcuts import render\n\n"
    urls_code = "from django.urls import path\nfrom . import views\n\nurlpatterns = [\n"
    
    for f in html_files:
        view_name = to_view_name(f)
        
        # View
        views_code += f"def {view_name}(request):\n"
        views_code += f"    return render(request, 'seatsense_app/{f}')\n\n"
        
        # URL
        url_path = "''" if f == 'index.html' else f"'{f.replace('.html', '')}/'"
        urls_code += f"    path({url_path}, views.{view_name}, name='{view_name}'),\n"
        
    urls_code += "]\n"

    with open(BASE_DIR / 'seatsense_app' / 'views.py', 'w', encoding='utf-8') as f:
        f.write(views_code)
        
    with open(BASE_DIR / 'seatsense_app' / 'urls.py', 'w', encoding='utf-8') as f:
        f.write(urls_code)

if __name__ == "__main__":
    for html_file in TEMPLATES_DIR.glob('*.html'):
        convert_html(html_file)
        
    generate_views_and_urls()
    print("Conversion complete!")
