from flask import Blueprint

exam_bp = Blueprint('exam', __name__, template_folder='templates')

from . import routes 