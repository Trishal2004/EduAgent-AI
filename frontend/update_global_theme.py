import os
import re

directories = [
    "/Users/k.trishal/Desktop/EduAgent AI/frontend/src/pages",
    "/Users/k.trishal/Desktop/EduAgent AI/frontend/src/components"
]

replacements = [
    (r'bg-slate-900/50', 'bg-gray-50'),
    (r'bg-slate-900/80', 'bg-gray-50/80'),
    (r'bg-slate-900', 'bg-white'),
    (r'bg-slate-800/50', 'bg-gray-100'),
    (r'bg-slate-800/80', 'bg-gray-100/80'),
    (r'bg-slate-800', 'bg-gray-50'),
    (r'bg-slate-700', 'bg-gray-100'),
    (r'border-slate-800', 'border-gray-200'),
    (r'border-slate-700', 'border-gray-200'),
    (r'border-slate-600', 'border-gray-300'),
    (r'border-slate-500', 'border-gray-300'),
    (r'text-slate-200', 'text-gray-800'),
    (r'text-slate-300', 'text-gray-700'),
    (r'text-slate-400', 'text-gray-600'),
    (r'text-slate-500', 'text-gray-500'),
    (r'hover:bg-slate-800', 'hover:bg-gray-100'),
    (r'hover:bg-slate-700', 'hover:bg-gray-200'),
    (r'hover:text-white', 'hover:text-gray-900'),
    (r'placeholder-slate-500', 'placeholder-gray-400'),
    (r'placeholder-slate-400', 'placeholder-gray-500'),
    (r'bg-slate-600', 'bg-gray-200'),
    (r'shadow-\[0_0_30px_rgba\(37,99,235,0\.4\)\]', 'shadow-md'),
    (r'shadow-\[0_0_20px_rgba\(37,99,235,0\.3\)\]', 'shadow-sm'),
    (r'shadow-\[0_0_15px_rgba\(37,99,235,0\.3\)\]', 'shadow-sm'),
]

for directory in directories:
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.jsx') or file.endswith('.js'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()

                original_content = content
                
                # 1. First we replace `text-white` with `text-gray-900` EXCEPT if it's on a primary button
                # A safe way is to replace `text-white` -> `text-gray-900`, then fix known buttons.
                content = content.replace('text-white', 'text-gray-900')
                
                # Restore text-white for blue backgrounds, red, green, gradients etc
                content = re.sub(r'(bg-blue-[456]00[^"]*)text-gray-900', r'\1text-white', content)
                content = re.sub(r'text-gray-900([^"]*bg-blue-[456]00)', r'text-white\1', content)
                content = re.sub(r'(bg-gradient-to-[a-z]+ from-[a-z]+-[456]00[^"]*)text-gray-900', r'\1text-white', content)
                content = re.sub(r'text-gray-900([^"]*bg-gradient-to-[a-z]+ from-[a-z]+-[456]00)', r'text-white\1', content)
                content = re.sub(r'(bg-emerald-[456]00[^"]*)text-gray-900', r'\1text-white', content)
                content = re.sub(r'(bg-red-[456]00[^"]*)text-gray-900', r'\1text-white', content)
                content = re.sub(r'(bg-purple-[456]00[^"]*)text-gray-900', r'\1text-white', content)
                
                # Also restore for Button.jsx definitions
                if file == 'Button.jsx':
                    content = content.replace('text-gray-900 hover:bg-blue-500', 'text-white hover:bg-blue-500')
                    content = content.replace('hover:text-gray-900 border border-[var(--color-danger)]', 'hover:text-white border border-[var(--color-danger)]')

                for old, new in replacements:
                    content = re.sub(old, new, content)

                if content != original_content:
                    with open(filepath, 'w') as f:
                        f.write(content)

print("Global theme replacements applied.")
