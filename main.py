from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from . import db
from .models import Scan
from .network_scanner import run_scan
from .scheduler import schedule_scan

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    """Render the user's profile page."""
    return render_template('profile.html', name=current_user.username)

@main.route('/scan', methods=['GET', 'POST'])
@login_required
def scan():
    """Handle scan requests."""
    if request.method == 'POST':
        target = request.form.get('target')
        scan_type = request.form.get('scan_type')
        if not target or not scan_type:
            flash('Invalid scan parameters', 'error')
            return redirect(url_for('main.scan'))
        try:
            new_scan = Scan(target=target, scan_type=scan_type, user_id=current_user.id)
            db.session.add(new_scan)
            db.session.commit()
            run_scan(new_scan.id)
            flash('Scan started successfully', 'success')
            return redirect(url_for('main.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error starting scan: {str(e)}', 'error')
            return redirect(url_for('main.scan'))
    return render_template('scan.html')

@main.route('/schedule_scan', methods=['POST'])
@login_required
def schedule_scan_route():
    """Schedule a new scan."""
    cron_expression = request.form.get('cron_expression')
    if not cron_expression:
        flash('Invalid cron expression', 'error')
        return redirect(url_for('main.profile'))
    try:
        schedule_scan(cron_expression)
        flash('Scan scheduled successfully', 'success')
    except Exception as e:
        flash(f'Error scheduling scan: {str(e)}', 'error')
    return redirect(url_for('main.profile'))

@main.route('/results')
@login_required
def results():
    """Display scan results with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    scans = Scan.query.filter_by(user_id=current_user.id).order_by(Scan.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    if not scans.items and page != 1:
        abort(404)
    return render_template('results.html', scans=scans)
