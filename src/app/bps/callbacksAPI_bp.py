from flask import Blueprint, current_app, jsonify, request

from src.app.invoiceManager import save_invoice_data


# Создаем blueprint
callbacksAPI_bp = Blueprint('callbacksAPI', __name__)


@callbacksAPI_bp.route("/invoicecallback", methods=['POST'])
def invoice_callback():
    """Обработка callback от CryptoCloud"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

        save_invoice_data(data)

        return jsonify({'status': 'success', 'message': 'Callback received'}), 200
    except Exception:
        current_app.logger.exception("Не удалось обработать callback платёжной системы")
        return jsonify({'status': 'error', 'message': 'Server error'}), 500

