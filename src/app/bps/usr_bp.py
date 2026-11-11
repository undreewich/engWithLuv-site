from flask import Blueprint, render_template


usr_bp = Blueprint('usr', __name__)


@usr_bp.route('/dashboard')
def student_dashboard():
	"""Страница-заглушка личного кабинета студента."""
	return render_template('student_dashboard.html')
