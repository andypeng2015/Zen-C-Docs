import os
import re

SOURCE_DIR = "raw"
TARGET_DIR = "../zenc"
TRANSLATIONS_DIR = "../zenc/translations"

HEADERS_REF = {
    "README.md": "## Language Reference",
    "README_DE.md": "## Sprachreferenz",
    "README_ES.md": "## Referencia del Lenguaje",
    "README_IT.md": "## Riferimenti Del Linguaggio",
    "README_PT_BR.md": "## Referência da Linguagem",
    "README_RU.md": "## Справочник",
    "README_ZH_CN.md": "## 语言参考",
    "README_ZH_TW.md": "## 語言參考",
}

HEADERS_STD = {
    "README.md": "## Standard Library",
    "README_DE.md": "## Standardbibliothek",
    "README_ES.md": "## Biblioteca Estándar",
    "README_IT.md": "## Libreria Standard",
    "README_PT_BR.md": "## Biblioteca Padrão",
    "README_RU.md": "## Стандартная библиотека",
    "README_ZH_CN.md": "## 标准库",
    "README_ZH_TW.md": "## 標準庫",
}

LINKS = {
    "README.md": "See the official [Language Reference](https://docs.zenc-lang.org/tour/01-variables-constants/) for more details.",
    "README_DE.md": "Weitere Details finden Sie in der offiziellen [Sprachreferenz](https://docs.zenc-lang.org/tour/01-variables-constants/).",
    "README_ES.md": "Consulte la [Referencia del Lenguaje](https://docs.zenc-lang.org/tour/01-variables-constants/) oficial para obtener más detalles.",
    "README_IT.md": "Consulta il [Riferimento del linguaggio](https://docs.zenc-lang.org/tour/01-variables-constants/) ufficiale per maggiori dettagli.",
    "README_PT_BR.md": "Consulte a [Referência da Linguagem](https://docs.zenc-lang.org/tour/01-variables-constants/) oficial para mais detalhes.",
    "README_RU.md": "Для получения более подробной информации см. официальный [Справочник по языку](https://docs.zenc-lang.org/tour/01-variables-constants/).",
    "README_ZH_CN.md": "有关更多详细信息，请参阅官方[语言参考](https://docs.zenc-lang.org/tour/01-variables-constants/)。",
    "README_ZH_TW.md": "有關更多詳細資訊，請參閲官方[語言參考](https://docs.zenc-lang.org/tour/01-variables-constants/)。",
}

LANGUAGES = [
    ("README.md", "English", ""),
    ("README_DE.md", "Deutsch", "translations/"),
    ("README_RU.md", "Русский", "translations/"),
    ("README_ZH_CN.md", "简体中文", "translations/"),
    ("README_ZH_TW.md", "繁體中文", "translations/"),
    ("README_ES.md", "Español", "translations/"),
    ("README_IT.md", "Italiano", "translations/"),
    ("README_PT_BR.md", "Português Brasileiro", "translations/"),
]

def build_lang_block(is_main):
    items = []
    for filename, label, rel_path in LANGUAGES:
        if is_main:
            path = rel_path + filename
        else:
            path = ("../" if filename == "README.md" else "") + filename
        items.append(f'    <a href="{path}">{label}</a>')
    
    return '<div align="center">\n  <p>\n' + ' •\n'.join(items) + '\n  </p>\n</div>'

def simplify(filename):
    filepath = os.path.join(SOURCE_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    is_main = filename == "README.md"
    
    # 1. Update language links block
    # Matches <div align="center">\n  <p>\n  <a href="...">...</a> • ...\n  </p>\n</div>
    lang_pattern = r'<div align="center">\s*<p>.*?</p>\s*</div>'
    new_lang_block = build_lang_block(is_main)
    content = re.sub(lang_pattern, new_lang_block, content, flags=re.DOTALL, count=1)

    # 2. Update Index table
    # We want to replace the second column's <ul> with a documentation link
    index_pattern = r'(<th width="50%">.*?Language Reference.*?</th>.*?<td valign="top">)\s*<ul>.*?</ul>(\s*</td>)'
    # Note: Need to handle translations in the mapping
    lang = filename.split('_')[1].split('.')[0].lower() if '_' in filename else 'en'
    docs_tour_url = f"https://docs.zenc-lang.org/tour/" # base tour url
    
    # Use a broader pattern for the index table contents to catch across translations
    # Find the table, then look for the second column
    table_match = re.search(r'(## (Index|Índice|Содержание|Inhaltsverzeichnis|Indice|Conteúdo|目录|目錄).*?)<table.*?>.*?</table>', content, re.DOTALL | re.IGNORECASE)
    if table_match:
        table_content = table_match.group(0)
        # Identify the second <td> (which contains the Language Reference list)
        # We look for the <td> that follows another </td>
        new_table_content = re.sub(r'(<td valign="top">.*?</td>\s*<td valign="top">)\s*<ul>.*?</ul>(\s*</td>)', 
                                f'\\1\n      <p><a href="{docs_tour_url}"><b>Browse the Language Reference</b></a></p>\\2', 
                                table_content, flags=re.DOTALL)
        content = content.replace(table_content, new_table_content)

    ref_header = HEADERS_REF.get(filename)
    std_header = HEADERS_STD.get(filename)
    link_text = LINKS.get(filename)

    if not ref_header or not std_header:
        print(f"Skipping {filename} (no headers found)")
        return

    # Find start of Language Reference
    ref_start = content.find(ref_header)
    if ref_start == -1:
        print(f"Start not found in {filename}")
        return

    # Find start of Standard Library (to include it and what follows)
    std_start = content.find(std_header)
    if std_start == -1:
        std_start = content.find("## Tool")
        if std_start == -1:
            std_start = len(content)

    preamble = content[:ref_start]
    footer = content[std_start:]

    new_content = preamble + ref_header + "\n\n" + link_text + "\n\n" + footer

    if is_main:
        dest_path = os.path.join(TARGET_DIR, filename)
    else:
        if not os.path.exists(TRANSLATIONS_DIR):
            os.makedirs(TRANSLATIONS_DIR)
        dest_path = os.path.join(TRANSLATIONS_DIR, filename)

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Created simplified {filename} at {dest_path}")

if __name__ == "__main__":
    for filename in os.listdir(SOURCE_DIR):
        if filename.startswith("README"):
            simplify(filename)
