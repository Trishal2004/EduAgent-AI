import re

def process_file(filepath, replacements, post_process=None):
    with open(filepath, "r") as f:
        content = f.read()
    
    for old, new in replacements:
        content = re.sub(old, new, content)
        
    if post_process:
        content = post_process(content)
        
    with open(filepath, "w") as f:
        f.write(content)


# 1. Sidebar.jsx
sidebar_replacements = [
    (r"bg-slate-900", "bg-white"),
    (r"border-slate-800", "border-gray-200"),
    (r"text-slate-500", "text-gray-500"),
    (r"text-slate-400", "text-gray-600"),
    (r"text-white", "text-gray-900"),
    (r"hover:text-white", "hover:text-gray-900"),
    (r"hover:bg-slate-800", "hover:bg-gray-100"),
    (r"bg-slate-800", "bg-gray-100"),
    (r"bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400", "text-blue-700"),
    (r"bg-blue-600/20 border border-blue-500/50", "bg-blue-50 border border-blue-200"),
    (r"group-hover:text-blue-400", "group-hover:text-blue-600"),
    (r"text-blue-400", "text-blue-600"),
]
process_file("/Users/k.trishal/Desktop/EduAgent AI/frontend/src/components/layout/Sidebar.jsx", sidebar_replacements)


# 2. MainLayout.jsx
def mainlayout_post(content):
    # Fix the wrapper text-white if we need. 
    # But wait, keeping `text-white` on the main container might be needed for dark pages.
    # We only change the header and dropdowns.
    return content

mainlayout_replacements = [
    (r"bg-slate-900/50", "bg-white/80"),
    (r"border-slate-800", "border-gray-200"),
    (r"text-slate-400", "text-gray-500"),
    (r"hover:text-white", "hover:text-gray-900"),
    (r"text-white", "text-gray-900"), # This replaces all text-white. Wait, the main container has text-white. 
    (r"bg-slate-800/80", "bg-gray-100/80"),
    (r"bg-slate-800/30", "bg-gray-50"),
    (r"bg-slate-800", "bg-white"),
    (r"border-slate-700/50", "border-gray-200"),
    (r"border-slate-700", "border-gray-200"),
    (r"text-slate-500", "text-gray-500"),
    (r"text-slate-200", "text-gray-800"),
    (r"placeholder-slate-500", "placeholder-gray-400"),
    (r"hover:bg-slate-700", "hover:bg-gray-100"),
    (r"text-blue-400", "text-blue-600"),
    (r"group-focus-within:text-blue-400", "group-focus-within:text-blue-600"),
]
# Wait, replacing all `text-white` in MainLayout.jsx to `text-gray-900` will change the main container text color to gray-900.
# That means all other pages will have gray-900 text on dark backgrounds!
# Let's refine MainLayout replacements to be safer.
mainlayout_replacements = [
    (r'header className="([^"]*)bg-slate-900/50([^"]*)"', r'header className="\1bg-white/80 border-gray-200\2"'),
    (r"border-slate-800", "border-gray-200"),
    (r'className="([^"]*)text-slate-400 hover:text-white([^"]*)"', r'className="\1text-gray-500 hover:text-gray-900\2"'),
    (r'text-white', 'text-gray-900'), # Actually wait, if we change the top-level min-h-screen text-white, it's safer to just change it to text-gray-900 but that affects dark pages.
    # Let's just do a blanket replace and fix the container.
]

def mainlayout_post2(content):
    c = content.replace("bg-[var(--color-bg-base)] text-white", "bg-[var(--color-bg-base)] text-[var(--color-text-main)]")
    c = re.sub(r"bg-slate-900/50", "bg-white/80", c)
    c = re.sub(r"border-slate-800", "border-gray-200", c)
    c = re.sub(r"bg-slate-800/80", "bg-gray-100", c)
    c = re.sub(r"bg-slate-800/30", "bg-gray-50", c)
    c = re.sub(r"bg-slate-800", "bg-white", c)
    c = re.sub(r"border-slate-700/50", "border-gray-200", c)
    c = re.sub(r"border-slate-700", "border-gray-200", c)
    c = re.sub(r"text-slate-400", "text-gray-500", c)
    c = re.sub(r"text-slate-200", "text-gray-800", c)
    c = re.sub(r"hover:text-white", "hover:text-gray-900", c)
    c = re.sub(r"text-white", "text-gray-900", c)
    c = re.sub(r"hover:bg-slate-700", "hover:bg-gray-50", c)
    # The header has user text. It's now text-gray-900.
    return c

process_file("/Users/k.trishal/Desktop/EduAgent AI/frontend/src/components/layout/MainLayout.jsx", [], mainlayout_post2)

# 3. Dashboard.jsx
def dashboard_post(content):
    # Remove blur-3xl divs
    content = re.sub(r'<div className="absolute[^"]*blur-3xl[^"]*" />', "", content)
    
    # Banner
    content = re.sub(r'bg-gradient-to-br from-blue-600 to-indigo-900 border border-blue-400/30 p-10 shadow-2xl', 'bg-blue-50 border border-blue-100 p-10 shadow-sm rounded-3xl', content)
    content = re.sub(r'text-white mb-3 tracking-tight drop-shadow-sm', 'text-blue-900 mb-3 tracking-tight', content)
    content = re.sub(r'text-blue-100 text-lg font-medium max-w-2xl drop-shadow-sm', 'text-blue-700 text-lg font-medium max-w-2xl', content)
    content = re.sub(r'shadow-lg shadow-blue-900/50', 'shadow-sm', content)
    
    # Cards and general
    content = re.sub(r'bg-slate-800/40', 'bg-white', content)
    content = re.sub(r'bg-slate-800/60', 'bg-white', content)
    content = re.sub(r'bg-slate-800/80', 'bg-white', content)
    content = re.sub(r'bg-slate-800/30', 'bg-gray-50', content)
    content = re.sub(r'bg-slate-800', 'bg-white', content)
    
    content = re.sub(r'border-slate-700/50', 'border-gray-200', content)
    content = re.sub(r'border-slate-700', 'border-gray-200', content)
    content = re.sub(r'border-slate-600', 'border-gray-300', content)
    
    content = re.sub(r'text-white', 'text-gray-900', content)
    content = re.sub(r'text-slate-400', 'text-gray-500', content)
    content = re.sub(r'text-slate-300', 'text-gray-600', content)
    content = re.sub(r'text-slate-500', 'text-gray-400', content)
    content = re.sub(r'hover:text-blue-300', 'hover:text-blue-700', content)
    content = re.sub(r'text-blue-400', 'text-blue-600', content)
    content = re.sub(r'text-blue-100', 'text-blue-700', content)
    content = re.sub(r'bg-blue-500/10', 'bg-blue-50', content)
    content = re.sub(r'hover:bg-blue-500/20', 'hover:bg-blue-100', content)
    
    content = re.sub(r'stroke="#334155"', 'stroke="#e2e8f0"', content)
    content = re.sub(r'stroke="#94a3b8"', 'stroke="#64748b"', content)
    content = re.sub(r'fill="#94a3b8"', 'fill="#64748b"', content)

    # Wrap the entire return inside Dashboard
    wrapper = '<div className="-m-6 lg:-m-10 p-6 lg:p-10 bg-[#F7F8FA] text-gray-900 min-h-[calc(100vh-5rem)]" style={{ "--color-bg-card": "#FFFFFF", "--color-border-subtle": "#E5E7EB", "--color-text-main": "#1F2937", "--color-text-muted": "#6B7280" }}>'
    content = re.sub(r'return \(\s*<div className="space-y-8">', f'return (\\n    {wrapper}\\n      <div className="space-y-8">', content)
    content = re.sub(r'</div>\s*\);\s*};\s*export default Dashboard;', '</div>\\n    </div>\\n  );\\n};\\n\\nexport default Dashboard;', content)

    return content

process_file("/Users/k.trishal/Desktop/EduAgent AI/frontend/src/pages/Dashboard.jsx", [], dashboard_post)

print("Modifications applied successfully.")
