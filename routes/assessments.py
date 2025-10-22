from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
from models import Assessment, Client, db
from forms import AssessmentForm
from datetime import datetime
from sqlalchemy import desc

assessments_bp = Blueprint('assessments', __name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@assessments_bp.route('/client/<int:client_id>')
@login_required
def index(client_id):
    """
    Daftar semua assessment untuk klien tertentu
    """
    client = Client.query.get_or_404(client_id)
    assessments = Assessment.query.filter_by(client_id=client_id).order_by(desc(Assessment.created_at)).all()
    
    return render_template('assessments/index.html', client=client, assessments=assessments)

@assessments_bp.route('/client/<int:client_id>/add', methods=['GET', 'POST'])
@login_required
def add(client_id):
    """
    Tambah assessment baru untuk klien
    """
    client = Client.query.get_or_404(client_id)
    form = AssessmentForm()
    
    if form.validate_on_submit():
        try:
            # Create new assessment
            assessment = Assessment(
                client_id=client_id,
                weight=form.weight.data,
                height=form.height.data,
                muscle_mass=form.muscle_mass.data,
                neck=form.neck.data,
                date=form.date.data,
                body_fat=form.body_fat.data,
                chest=form.chest.data,
                waist=form.waist.data,
                hips=form.hips.data,
                arm=form.arm.data,
                thigh=form.thigh.data,
                squat_max=form.squat_max.data,
                bench_max=form.bench_max.data,
                deadlift_max=form.deadlift_max.data,
                pushup_test=form.pushup_test.data,
                pullup_test=form.pullup_test.data,
                notes=form.notes.data
            )
            db.session.add(assessment)
            db.session.commit()
            flash(f'Assessment untuk {client.name} berhasil ditambahkan!', 'success')
            return redirect(url_for('assessments.view', id=assessment.id))
        except Exception as e:
            import logging
            logging.exception("Error saat menyimpan assessment baru:")
            db.session.rollback()
            flash('Terjadi kesalahan saat menyimpan data.', 'error')
    
    return render_template('assessments/add.html', client=client, form=form)

@assessments_bp.route('/<int:id>')
@login_required
def view(id):
    """
    Lihat detail assessment
    """
    assessment = Assessment.query.get_or_404(id)
    client = assessment.client
    return render_template('assessments/view.html', assessment=assessment, client=client)

@assessments_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit assessment
    """
    assessment = Assessment.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Handle file upload
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename != '' and allowed_file(file.filename):
                    # Delete old photo if exists
                    if assessment.photo:
                        old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], assessment.photo)
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                    
                    # Save new photo
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    assessment.photo = filename
            
            # Update assessment data
            assessment.weight = float(request.form.get('weight')) if request.form.get('weight') else None
            assessment.height = float(request.form.get('height')) if request.form.get('height') else None
            assessment.muscle_mass = float(request.form.get('muscle_mass')) if request.form.get('muscle_mass') else None
            assessment.neck = float(request.form.get('neck')) if request.form.get('neck') else None
            date_str = request.form.get('date')
            if date_str:
                assessment.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            assessment.body_fat = float(request.form.get('body_fat')) if request.form.get('body_fat') else None
            assessment.chest = float(request.form.get('chest')) if request.form.get('chest') else None
            assessment.waist = float(request.form.get('waist')) if request.form.get('waist') else None
            assessment.hips = float(request.form.get('hips')) if request.form.get('hips') else None
            assessment.arm = float(request.form.get('arm')) if request.form.get('arm') else None
            assessment.thigh = float(request.form.get('thigh')) if request.form.get('thigh') else None
            assessment.squat_max = float(request.form.get('squat_max')) if request.form.get('squat_max') else None
            assessment.bench_max = float(request.form.get('bench_max')) if request.form.get('bench_max') else None
            assessment.deadlift_max = float(request.form.get('deadlift_max')) if request.form.get('deadlift_max') else None
            assessment.pushup_test = int(request.form.get('pushup_test')) if request.form.get('pushup_test') else None
            assessment.pullup_test = int(request.form.get('pullup_test')) if request.form.get('pullup_test') else None
            assessment.notes = request.form.get('notes', '').strip()
            db.session.commit()
            flash('Assessment berhasil diperbarui!', 'success')
            return redirect(url_for('assessments.view', id=assessment.id))
        except ValueError:
            flash('Data tidak valid. Periksa kembali input Anda.', 'error')
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan saat menyimpan data.', 'error')
    
    return render_template('assessments/edit.html', assessment=assessment)

@assessments_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """
    Hapus assessment
    """
    assessment = Assessment.query.get_or_404(id)
    client_id = assessment.client_id
    
    try:
        # Delete photo file if exists
        if assessment.photo:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], assessment.photo)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(assessment)
        db.session.commit()
        
        flash('Assessment berhasil dihapus.', 'success')
        return redirect(url_for('assessments.index', client_id=client_id))
        
    except Exception as e:
        db.session.rollback()
        flash('Terjadi kesalahan saat menghapus data.', 'error')
        return redirect(url_for('assessments.view', id=id))