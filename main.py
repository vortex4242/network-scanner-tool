from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import Scan
from .network_scanner import run_scan
from .scheduler import schedule_scan

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.username)

@main.route('/scan', methods=['GET', 'POST'])
@login_required
def scan():
    if request.method == 'POST':
        target = request.form.get('target')
        scan_type = request.form.get('scan_type')
        new_scan = Scan(target=target, scan_type=scan_type, user_id=current_user.id)
        db.session.add(new_scan)
        db.session.commit()
        run_scan(new_scan.id)
        flash('Scan started successfully')
        return redirect(url_for('main.profile'))
    return render_template('scan.html')

@main.route('/schedule_scan', methods=['POST'])
@login_required
def schedule_scan_route():
    cron_expression = request.form.get('cron_expression')
    schedule_scan(cron_expression)
    flash('Scan scheduled successfully')
    return redirect(url_for('main.profile'))

@main.route('/results')
@login_required
def results():
    scans = Scan.query.filter_by(user_id=current_user.id).all()
    return render_template('results.html', scans=scans)
