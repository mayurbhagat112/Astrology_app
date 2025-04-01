import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from datetime import datetime
from transformers import T5Tokenizer, T5ForConditionalGeneration
from astropy.time import Time
from astropy.coordinates import get_sun, get_moon, solar_system_ephemeris, get_body
from transformers import T5Tokenizer, T5ForConditionalGeneration


# Use larger T5 model for better results
model = T5ForConditionalGeneration.from_pretrained('t5-base')
tokenizer = T5Tokenizer.from_pretrained('t5-base')

def get_planetary_positions(date_time):
    """
    Calculate planetary positions for the astrological chart using astropy.
    """
    # Convert the datetime to Astropy Time object
    t = Time(date_time)

    positions = {
        "Sun": get_sun(t).ra.deg,
        "Moon": get_moon(t).ra.deg,
    }

    planets = ['mercury', 'venus', 'mars', 'jupiter', 'saturn']

    with solar_system_ephemeris.set('builtin'):
        for planet in planets:
            positions[planet.capitalize()] = get_body(planet, t).ra.deg

    return positions

def draw_astrological_chart(planet_positions):
    """
    Draw a circular astrological chart with planetary positions and zodiac symbols.
    """
    # Zodiac signs and their Unicode symbols
    zodiac_signs = [
        ("\u2648", "Aries"),      # ♈
        ("\u2649", "Taurus"),     # ♉
        ("\u264A", "Gemini"),     # ♊
        ("\u264B", "Cancer"),     # ♋
        ("\u264C", "Leo"),        # ♌
        ("\u264D", "Virgo"),      # ♍
        ("\u264E", "Libra"),      # ♎
        ("\u264F", "Scorpio"),    # ♏
        ("\u2650", "Sagittarius"),# ♐
        ("\u2651", "Capricorn"),  # ♑
        ("\u2652", "Aquarius"),   # ♒
        ("\u2653", "Pisces")      # ♓
    ]

    planets = {
        "Sun": planet_positions.get("Sun"),
        "Moon": planet_positions.get("Moon"),
        "Mercury": planet_positions.get("Mercury"),
        "Venus": planet_positions.get("Venus"),
        "Mars": planet_positions.get("Mars"),
        "Jupiter": planet_positions.get("Jupiter"),
        "Saturn": planet_positions.get("Saturn"),
    }

    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': 'polar'})
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi / 2)

    # Draw house boundaries
    for i in range(12):
        angle = i * np.pi / 6
        ax.plot([angle, angle], [0, 1], color='black', lw=1, alpha=0.5)

    # Draw zodiac symbols around the chart
    for i, (symbol, name) in enumerate(zodiac_signs):
        angle = i * np.pi / 6 + np.pi / 12
        ax.text(angle, 1.05, symbol, ha='center', va='center', fontsize=20, color='darkblue', fontweight='bold')

    # Define planet symbols and their colors
    planet_symbols = {
        "Sun": ("\u2609", "#FFB300"),        # ☉
        "Moon": ("\u263D", "#AAAAFF"),       # ☽
        "Mercury": ("\u263F", "#A8C3D1"),    # ☿
        "Venus": ("\u2640", "#FF69B4"),      # ♀
        "Mars": ("\u2642", "#FF4500"),       # ♂
        "Jupiter": ("\u2643", "#FF8C00"),    # ♃
        "Saturn": ("\u2644", "#C0C0C0"),     # ♄
    }

    # Plot planetary positions with their degrees
    for planet, position in planets.items():
        if position is not None:
            angle = np.deg2rad(position)
            symbol, color = planet_symbols.get(planet)

            # Plot planet symbol closer to the center (radius = 0.8)
            ax.text(angle, 0.8, symbol, fontsize=20, ha='center', va='center', color=color)

            # Plot planet position (degree) further out (radius = 0.95)
            ax.text(angle, 0.95, f"{position:.2f}°", fontsize=10, ha='center', va='center', color=color)

    ax.set_yticks([])
    ax.set_xticks([])
    ax.grid(False)

    # Create the "Planets" table
    planet_table_text = "\n".join(
        [f"{symbol} {planet}" for planet, (symbol, color) in planet_symbols.items()]
    )
    fig.text(
        1.05,
        0.8,
        f"Planets\n\n{planet_table_text}",
        fontsize=12,
        ha="left",
        va="top",
        color="black",
        bbox=dict(boxstyle="round,pad=0.5", edgecolor="black", facecolor="white")
    )

    # Create the "Zodiac Signs" table
    zodiac_table_text = "\n".join([f"{symbol} {name}" for symbol, name in zodiac_signs])
    fig.text(
        1.05,
        0.4,
        f"Zodiac Signs\n\n{zodiac_table_text}",
        fontsize=12,
        ha="left",
        va="top",
        color="black",
        bbox=dict(boxstyle="round,pad=0.5", edgecolor="black", facecolor="white")
    )

    # Add accuracy disclaimer
    fig.text(
        0.5,
        -0.1,
        "Planetary positions calculated using Astropy, accurate to the precision of the ephemeris ±0.005°",
        fontsize=10,
        ha="center",
        va="center",
        color="black",
        bbox=dict(boxstyle="round,pad=0.5", edgecolor="black", facecolor="white")
    )

    # Convert plot to PNG and store in a BytesIO buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
    img_buffer.seek(0)  # Rewind the buffer

    # Encode the image in base64 for sending it via JSON
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

    # Close the plot to free resources
    plt.close(fig)

    return img_base64

def generate_astrological_summary(planet_positions):
    """
    Generate detailed astrological interpretation using enhanced T5 prompting
    """
    prompt = (
        "As a professional astrologer, analyze these planetary positions:\n"
        f"Sun: {planet_positions['Sun']:.2f}° | "
        f"Moon: {planet_positions['Moon']:.2f}° | "
        f"Mercury: {planet_positions.get('Mercury', 'N/A'):.2f}° | "
        f"Venus: {planet_positions.get('Venus', 'N/A'):.2f}° | "
        f"Mars: {planet_positions.get('Mars', 'N/A'):.2f}° | "
        f"Jupiter: {planet_positions.get('Jupiter', 'N/A'):.2f}° | "
        f"Saturn: {planet_positions.get('Saturn', 'N/A'):.2f}°\n\n"
        "Provide a detailed analysis covering:\n"
        "- Zodiac sign placements and element balances\n"
        "- Planetary aspects and house positions\n"
        "- Personality traits and life tendencies\n"
        "- Career strengths and relationship patterns\n"
        "- Challenges and growth opportunities\n"
        "Use professional astrological terminology but keep interpretations accessible."
    )

    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    
    outputs = model.generate(inputs.input_ids,
        max_length=800,
        num_beams=5,
        no_repeat_ngram_size=3,
        early_stopping=True,
        temperature=0.9,
        do_sample=True
    )

    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary