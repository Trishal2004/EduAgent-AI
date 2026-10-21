import re
import os

filepath = "/Users/k.trishal/Desktop/EduAgent AI/frontend/src/pages/Quiz.jsx"

with open(filepath, "r") as f:
    content = f.read()

replacements = [
    (r"bg-slate-900/50", "bg-white border border-gray-200 shadow-sm"),
    (r"bg-slate-900", "bg-white"),
    (r"bg-slate-800", "bg-gray-50"),
    (r"border-slate-800", "border-gray-200"),
    (r"border-slate-700", "border-gray-200"),
    (r"hover:bg-slate-700", "hover:bg-gray-100"),
    (r"text-white", "text-gray-900"),
    (r"text-slate-400", "text-gray-500"),
    (r"text-slate-300", "text-gray-600"),
    (r"text-emerald-400", "text-emerald-600"),
    (r"text-emerald-500/70", "text-emerald-700"),
    (r"text-emerald-500", "text-emerald-600"),
    (r"text-blue-400", "text-blue-600"),
    (r"text-purple-400", "text-purple-600"),
    (r"bg-emerald-500/10", "bg-emerald-50"),
    (r"border-emerald-500/20", "border-emerald-200"),
    (r"border-emerald-500/30", "border-emerald-200"),
    (r"bg-blue-500/20", "bg-blue-50"),
    (r"bg-blue-500/10", "bg-blue-50"),
    (r"border-red-500/30", "border-red-200"),
    (r"bg-red-500/10", "bg-red-50"),
    (r"border-red-500/20", "border-red-200"),
    (r"text-red-400", "text-red-600"),
    (r"text-red-500", "text-red-600"),
    (r"bg-indigo-500/10", "bg-indigo-50"),
    (r"border-indigo-500/20", "border-indigo-200"),
    (r"text-indigo-200", "text-indigo-800"),
    (r"border-orange-500/30", "border-orange-200"),
    (r"text-orange-400", "text-orange-600"),
    (r"text-orange-500", "text-orange-600"),
    (r"shadow-\[0_0_30px_rgba\(37,99,235,0\.4\)\]", "shadow-sm"),
    (r"bg-gradient-to-br from-blue-500 to-indigo-600", "bg-blue-100"),
    (r"text-4xl text-gray-900 shadow-sm", "text-4xl text-blue-600 shadow-sm"), # fixing the previous replace if any
]

new_content = content
for old, new in replacements:
    new_content = re.sub(old, new, new_content)

# We also need to add a wrapper or ensure the main layout is light theme
# The Quiz returns `<div className={mode === 'daily_only' ? "" : "pb-12"}>`
# We can replace this with `<div className={(mode === 'daily_only' ? "" : "pb-12") + " text-gray-900 bg-gray-50 min-h-screen"}>`
new_content = new_content.replace(
    '<div className={mode === \'daily_only\' ? "" : "pb-12"}>',
    '<div className={(mode === \'daily_only\' ? "" : "pb-12") + " text-gray-900 bg-gray-50 min-h-screen p-6"} style={{ "--color-bg-card": "#FFFFFF", "--color-border-subtle": "#E5E7EB", "--color-text-main": "#1F2937", "--color-text-muted": "#6B7280" }}>'
)

# And fix the text-4xl text-gray-900 shadow-sm from the award icon
new_content = new_content.replace(
    'bg-blue-100 rounded-full flex items-center justify-center text-4xl text-gray-900 shadow-sm',
    'bg-blue-100 rounded-full flex items-center justify-center text-4xl text-blue-600 shadow-sm'
)

with open(filepath, "w") as f:
    f.write(new_content)

print("Modifications applied successfully.")
