import os
from giotto.utils import better_base

Base = better_base()

project_path = os.path.dirname(os.path.abspath(__file__))
jinja2_template_dir = 'html'
auth_session_expire = 3600 * 24 * 7
error_template = None