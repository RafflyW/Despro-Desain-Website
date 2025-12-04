from flask import Blueprint, render_template

# Membuat blueprint bernama 'views'
views = Blueprint('views', __name__)

@views.route('/')
def home():
    # Ini akan mencari file 'dashboard.html' di folder website/templates
    return render_template("dashboard.html")