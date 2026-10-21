import sys

with open("app/services/document_processing.py", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if i >= 33 and i <= 149: # Lines after `try:` up to `return ProcessingResponse` (excluding except block)
        if line.strip() != "":
            # Indent by 4 spaces
            new_lines.append("    " + line)
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open("app/services/document_processing.py", "w") as f:
    f.writelines(new_lines)
