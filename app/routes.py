from flask import Blueprint, render_template, request, jsonify
from .utils import get_planetary_positions, draw_astrological_chart, generate_astrological_summary
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/get_chart', methods=['POST'])
def get_chart():
    try:
        data = request.json
        date_time_str = data['date_time']  # Example format: '2025-01-06T12:34'
        date_time = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M')

        # Get the planetary positions using the provided date and time
        positions = get_planetary_positions(date_time)

        # Generate the astrological chart with those positions
        chart_base64 = draw_astrological_chart(positions)

        # Generate the astrological summary using T5
        summary = generate_astrological_summary(positions)

        # If chart generation is successful, return the positions, chart base64, and the summary
        return jsonify({'positions': positions, 'chart': chart_base64, 'summary': summary})

    except Exception as e:
        return jsonify({'error': str(e)}), 400
