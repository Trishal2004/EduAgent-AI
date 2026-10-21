import os
import glob

models_dir = 'app/models'
for filepath in glob.glob(os.path.join(models_dir, '*.py')):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace imports
    if 'from sqlalchemy.dialects.postgresql import' in content:
        content = content.replace('from sqlalchemy.dialects.postgresql import UUID, JSON', 'from sqlalchemy import JSON\nfrom sqlalchemy import Uuid as UUID')
        content = content.replace('from sqlalchemy.dialects.postgresql import UUID', 'from sqlalchemy import Uuid as UUID')
    
    # ProcessedChunk pgvector removal
    if 'pgvector.sqlalchemy' in content:
        content = content.replace('from pgvector.sqlalchemy import Vector\n', '')
        content = content.replace('Column(Vector(1536),', 'Column(JSON,')
        
    with open(filepath, 'w') as f:
        f.write(content)

print("Models rewritten successfully!")
