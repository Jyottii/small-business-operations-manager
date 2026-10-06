import os
import re

env_py_path = 'alembic/env.py'
with open(env_py_path, 'r') as f:
    content = f.read()

import_str = """
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.models.base import Base
from app.models import *
"""

content = re.sub(r'target_metadata = None', 'target_metadata = Base.metadata', content)
content = content.replace('target_metadata = Base.metadata', import_str + '\ntarget_metadata = Base.metadata')

override_str = """
    url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    config.set_main_option("sqlalchemy.url", url)
"""
content = content.replace('def run_migrations_offline():', override_str + '\n\ndef run_migrations_offline():')

with open(env_py_path, 'w') as f:
    f.write(content)
