import os
import re
import sys

# Configuration
SOURCE_DIR = "raw"
TARGET_DIR = "reference"  # This will be used by the GitHub Action to sync to www
MAPPING = {
    "1.": "01-variables-constants.md",
    "2.": "02-primitive-types.md",
    "3.": "03-aggregate-types.md",
    "4.": "04-functions-lambdas.md",
    "5.": "05-control-flow.md",
    "6.": "06-operators.md",
    "7.": "07-printing-interpolation.md",
    "8.": "08-memory-management.md",
    "9.": "09-oop.md",
    "10.": "10-generics.md",
    "11.": "11-concurrency.md",
    "12.": "12-advanced.md",
    "13.": "12-advanced.md",
    "14.": "12-advanced.md",
    "15.": "12-advanced.md",
    "16.": "12-advanced.md",
    "17.": "13-interop.md",
    "18.": "14-unit-testing-framework.md",
}

WEIGHTS = {
    "01-variables-constants.md": 1,
    "02-primitive-types.md": 2,
    "03-aggregate-types.md": 3,
    "04-functions-lambdas.md": 4,
    "05-control-flow.md": 5,
    "06-operators.md": 6,
    "07-printing-interpolation.md": 7,
    "08-memory-management.md": 8,
    "09-oop.md": 9,
    "10-generics.md": 10,
    "11-concurrency.md": 11,
    "12-advanced.md": 12,
    "13-interop.md": 13,
    "14-unit-testing-framework.md": 14,
}

LANG_MAP = {
    "README.md": "en",
    "README_DE.md": "de",
    "README_ES.md": "es",
    "README_IT.md": "it",
    "README_PT_BR.md": "pt",
    "README_RU.md": "ru",
    "README_ZH_CN.md": "zh-cn",
    "README_ZH_TW.md": "zh-tw",
}

def convert_alerts(content):
    def replace_alert(match):
        alert_type = match.group(1).lower()
        body = match.group(2)
        # remove '> ' or '>' from start of lines
        body_clean = re.sub(r'^>\s?', '', body, flags=re.MULTILINE)
        return f'{{% alert(type="{alert_type}") %}}\n{body_clean}{{% end %}}\n'

    pattern = r'>\s*\[!(NOTE|TIP|WARNING|IMPORTANT|CAUTION)\]\s*\n((?:>.*\n?)+)'
    return re.sub(pattern, replace_alert, content)

def process_file(filename):
    lang = LANG_MAP.get(filename)
    if not lang:
        return

    filepath = os.path.join(SOURCE_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        full_content = f.read()

    # Split by ### headers
    # We look for "### N. Title"
    sections = re.split(r'\n###\s+(\d+\.)\s+(.*?)\n', full_content)
    # sections[0] is preamble
    # sections[1] is "1."
    # sections[2] is "Variables and Constants"
    # sections[3] is the content of section 1
    
    file_contents = {} # target_filename -> list of (title, body)

    for i in range(1, len(sections), 3):
        num = sections[i]
        title = sections[i+1]
        body = sections[i+2]
        
        target_filename = MAPPING.get(num)
        if not target_filename:
            continue
            
        if target_filename not in file_contents:
            file_contents[target_filename] = []
        
        file_contents[target_filename].append((num + " " + title, body))

    # Write split files
    for target_filename, parts in file_contents.items():
        # Final filename needs lang suffix if not English
        if lang == "en":
            out_name = target_filename
        else:
            out_name = target_filename.replace(".md", f".{lang}.md")
            
        out_path = os.path.join(TARGET_DIR, out_name)
        
        # Combine parts for grouped files (like 12-advanced)
        combined_body = ""
        main_title = parts[0][0] # use first title as main title for now
        
        if target_filename == "12-advanced.md":
            main_title = "12. Advanced & Metaprogramming"
            # Special case for 12-16 grouping
            for title, body in parts:
                combined_body += f"\n### {title.split('. ', 1)[1]}\n{body}"
        else:
            combined_body = parts[0][1]

        # Clean up combined_body
        combined_body = convert_alerts(combined_body)

        # Build final content with Zola frontmatter
        weight = WEIGHTS.get(target_filename, 100)
        final_content = f"+++\ntitle = \"{main_title}\"\nweight = {weight}\n+++\n\n# {main_title}\n\n{combined_body}"

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(final_content)

if __name__ == "__main__":
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        
    for filename in os.listdir(SOURCE_DIR):
        if filename.startswith("README"):
            print(f"Processing {filename}...")
            process_file(filename)
