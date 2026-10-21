import os
import re

directories = [
    "/Users/k.trishal/Desktop/EduAgent AI/frontend/src/pages",
    "/Users/k.trishal/Desktop/EduAgent AI/frontend/src/components"
]

replacements = [
    (r'\btext-gray-400\b', 'text-gray-600'),
    (r'\btext-gray-500\b', 'text-gray-600'),
    (r'\bshadow-2xl\b', 'shadow-md'),
    (r'\bshadow-xl\b', 'shadow-md'),
    (r'\bshadow-lg\b', 'shadow-sm'),
]

for directory in directories:
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.jsx') or file.endswith('.js'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()

                original_content = content

                for old, new in replacements:
                    content = re.sub(old, new, content)

                if content != original_content:
                    with open(filepath, 'w') as f:
                        f.write(content)

print("Visual refinements applied.")
