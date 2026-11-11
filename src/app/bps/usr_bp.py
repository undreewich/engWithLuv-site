from flask import Blueprint, jsonify, render_template


usr_bp = Blueprint('usr', __name__)


@usr_bp.route('/dashboard')
def student_dashboard():
	"""Страница-заглушка личного кабинета студента."""
	return render_template('student_dashboard.html')


@usr_bp.route('/api/dashboard/<section>', methods=['GET'])
def student_dashboard_data(section):
	"""Заглушка API: данные разделов кабинета пока отсутствуют."""
	if section not in {'lesson_history', 'upcoming_lessons', 'homework', 'available_materials'}:
		return jsonify({'error': 'unknown_section'}), 404
	return jsonify([])
