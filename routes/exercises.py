from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from models import Exercise, db
from sqlalchemy import desc
from datetime import datetime

exercises_bp = Blueprint('exercises', __name__)

@exercises_bp.route('/')
@login_required
def index():
    """
    Halaman daftar semua latihan
    """
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Exercise.query
    
    if search:
        query = query.filter(Exercise.name.contains(search))
    
    exercises = query.order_by(Exercise.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('exercises/index.html', exercises=exercises, search=search)

@exercises_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """
    Tambah latihan baru
    """
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        
        # Ambil data opsi weight
        weight_units = request.form.getlist('weight_units[]')
        
        # Ambil data opsi reps
        reps_units = request.form.getlist('reps_units[]')
        
        # Filter unit yang tidak kosong
        weight_options = [unit for unit in weight_units if unit.strip()]
        reps_options = [unit for unit in reps_units if unit.strip()]
        
        if not name:
            flash('Nama latihan wajib diisi.', 'error')
            return redirect(url_for('exercises.add'))
        
        # Cek apakah latihan dengan nama yang sama sudah ada
        existing_exercise = Exercise.query.filter_by(name=name).first()
        if existing_exercise:
            flash(f'Latihan dengan nama "{name}" sudah ada.', 'error')
            return redirect(url_for('exercises.add'))
        
        # Buat latihan baru
        exercise = Exercise(
            name=name,
            description=description,
            category=category,
            weight_options=weight_options if weight_options else None,
            reps_options=reps_options if reps_options else None
        )
        
        db.session.add(exercise)
        db.session.commit()
        
        flash(f'Latihan "{name}" berhasil ditambahkan.', 'success')
        return redirect(url_for('exercises.index'))
    
    return render_template('exercises/add.html')

@exercises_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit latihan
    """
    exercise = Exercise.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        
        # Ambil data opsi weight
        weight_units = request.form.getlist('weight_units[]')
        
        # Ambil data opsi reps
        reps_units = request.form.getlist('reps_units[]')
        
        # Filter unit yang tidak kosong
        weight_options = [unit for unit in weight_units if unit.strip()]
        reps_options = [unit for unit in reps_units if unit.strip()]
        
        if not name:
            flash('Nama latihan wajib diisi.', 'error')
            return redirect(url_for('exercises.edit', id=id))
        
        # Cek apakah latihan dengan nama yang sama sudah ada (selain latihan ini)
        existing_exercise = Exercise.query.filter(Exercise.name == name, Exercise.id != id).first()
        if existing_exercise:
            flash(f'Latihan dengan nama "{name}" sudah ada.', 'error')
            return redirect(url_for('exercises.edit', id=id))
        
        # Update latihan
        exercise.name = name
        exercise.description = description
        exercise.category = category
        exercise.weight_options = weight_options if weight_options else None
        exercise.reps_options = reps_options if reps_options else None
        exercise.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Latihan "{name}" berhasil diperbarui.', 'success')
        return redirect(url_for('exercises.index'))
    
    return render_template('exercises/edit.html', exercise=exercise)

@exercises_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """
    Hapus latihan
    """
    exercise = Exercise.query.get_or_404(id)
    
    # Cek apakah latihan sedang digunakan di workout plan
    # Jika ya, jangan izinkan penghapusan
    from models import WorkoutPlanDetail
    used_in_workout = WorkoutPlanDetail.query.filter_by(exercise_id=id).first()
    
    if used_in_workout:
        flash(f'Latihan "{exercise.name}" tidak dapat dihapus karena sedang digunakan dalam program latihan.', 'error')
        return redirect(url_for('exercises.index'))
    
    db.session.delete(exercise)
    db.session.commit()
    
    flash(f'Latihan "{exercise.name}" berhasil dihapus.', 'success')
    return redirect(url_for('exercises.index'))