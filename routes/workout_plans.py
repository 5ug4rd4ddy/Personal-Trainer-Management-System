from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from models import Client, WorkoutPlan, WorkoutPlanDetail, Exercise, Session, db
from datetime import datetime
from sqlalchemy import desc
import math

workout_plans_bp = Blueprint('workout_plans', __name__)

@workout_plans_bp.route('/client/<int:client_id>')
@login_required
def index(client_id):
    """
    Daftar semua workout plan untuk klien tertentu
    """
    client = Client.query.get_or_404(client_id)
    workout_plans = WorkoutPlan.query.filter_by(client_id=client_id).order_by(desc(WorkoutPlan.created_at)).all()
    
    return render_template('workout_plans/index.html', client=client, workout_plans=workout_plans)

@workout_plans_bp.route('/client/<int:client_id>/add', methods=['GET', 'POST'])
@login_required
def add(client_id):
    """
    Tambah workout plan baru untuk klien
    """
    client = Client.query.get_or_404(client_id)
    exercises = Exercise.query.order_by(Exercise.name).all()
    
    if request.method == 'POST':
        try:
            plan_name = request.form.get('plan_name', '').strip()
            if not plan_name:
                flash('Nama program latihan harus diisi.', 'error')
                return render_template('workout_plans/add.html', client=client, exercises=exercises)
            
            # Parse form data
            duration = request.form.get('duration')
            days_per_week = request.form.get('days_per_week')
            start_date = request.form.get('start_date')
            
            # Create new workout plan
            workout_plan = WorkoutPlan(
                client_id=client_id,
                plan_name=plan_name,
                notes=request.form.get('notes', '').strip(),
                duration=int(duration) if duration else None,
                days_per_week=int(days_per_week) if days_per_week else None,
                start_date=datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
            )
            
            db.session.add(workout_plan)
            db.session.flush()  # Get the ID
            
            # Process selected days
            selected_days = request.form.getlist('selected_days[]')
            print(f"Selected days: {selected_days}")
            
            # Ambil data latihan yang dipilih dari form
            exercise_ids = request.form.getlist('exercise_id[]')
            sets_list = request.form.getlist('sets[]')
            weight_values = request.form.getlist('weight[]')
            reps_values = request.form.getlist('reps[]')
            
            # Simpan data latihan yang dipilih untuk digunakan nanti
            selected_exercises = []
            for i in range(len(exercise_ids)):
                if i < len(exercise_ids) and exercise_ids[i] and exercise_ids[i] != '0':
                    # Simpan weight sebagai string asli, bukan mencoba mengkonversi ke float
                    weight_value = None
                    if i < len(weight_values) and weight_values[i]:
                        weight_value = weight_values[i]  # Simpan nilai asli
                    
                    exercise_data = {
                        'exercise_id': int(exercise_ids[i]),
                        'sets': int(sets_list[i]) if i < len(sets_list) and sets_list[i] else 0,
                        'weight': weight_value,
                        'reps': reps_values[i] if i < len(reps_values) and reps_values[i] else None
                    }
                    # Ambil nama latihan dari database
                    exercise = db.session.get(Exercise, exercise_data['exercise_id'])
                    if exercise:
                        exercise_data['exercise_name'] = exercise.name
                        selected_exercises.append(exercise_data)
            
            # Create sessions automatically based on workout plan
            if workout_plan.start_date and workout_plan.duration and workout_plan.days_per_week and selected_days:
                from models import Session, SessionDetail
                from datetime import timedelta
                
                # Map day names to day numbers (0 = Sunday, 1 = Monday, etc.)
                day_name_to_number = {
                    'Minggu': 0,
                    'Senin': 1,
                    'Selasa': 2,
                    'Rabu': 3,
                    'Kamis': 4,
                    'Jumat': 5,
                    'Sabtu': 6
                }
                
                # Convert selected days to day numbers
                selected_day_numbers = [day_name_to_number[day] for day in selected_days]
                selected_day_numbers.sort()
                
                # Generate sessions
                total_sessions = workout_plan.duration * workout_plan.days_per_week
                session_date = workout_plan.start_date
                session_count = 0
                
                while session_count < total_sessions:
                    current_day_number = session_date.weekday()  # 0 = Monday in Python
                    if current_day_number == 6:  # Convert to 0 = Sunday format
                        current_day_number = 0
                    else:
                        current_day_number += 1
                    
                    if current_day_number in selected_day_numbers:
                        # Create new session
                        session = Session(
                            client_id=client_id,
                            date=session_date,
                            workout_plan_id=workout_plan.id,
                            completed=False,
                            notes=""
                        )
                        db.session.add(session)
                        db.session.flush()  # Dapatkan ID sesi
                        
                        # Tambahkan detail latihan ke sesi
                        for exercise_data in selected_exercises:
                            # Periksa nilai weight, jika nan, ubah menjadi None
                            weight_value = exercise_data['weight']
                            if isinstance(weight_value, float) and math.isnan(weight_value):
                                weight_value = None
                                
                            session_detail = SessionDetail(
                                session_id=session.id,
                                exercise_id=exercise_data['exercise_id'],
                                exercise_name=exercise_data['exercise_name'],
                                sets=exercise_data['sets'],
                                weight=weight_value,
                                reps=exercise_data['reps']
                            )
                            db.session.add(session_detail)
                        
                        session_count += 1
                    
                    # Move to next day
                    session_date += timedelta(days=1)
            
            db.session.commit()
            
            flash(f'Program latihan "{workout_plan.plan_name}" berhasil ditambahkan dengan sesi otomatis!', 'success')
            return redirect(url_for('workout_plans.view', id=workout_plan.id))
            
        except ValueError as e:
            flash(f'Data tidak valid: {str(e)}. Periksa kembali input Anda.', 'error')
        except Exception as e:
            db.session.rollback()
            print(f"Error: {str(e)}")
            flash('Terjadi kesalahan saat menyimpan data.', 'error')
    
    # Jika tidak ada latihan tersedia, tampilkan pesan
    if not exercises:
        flash('Belum ada data latihan. Silakan tambahkan latihan terlebih dahulu.', 'warning')
        
    return render_template('workout_plans/add.html', client=client, exercises=exercises)

@workout_plans_bp.route('/<int:id>')
@login_required
def view(id):
    """
    Lihat detail workout plan
    """
    workout_plan = WorkoutPlan.query.get_or_404(id)
    
    # Mengambil semua sesi latihan yang terkait dengan workout plan ini
    # Mengurutkan berdasarkan tanggal terdekat (tanggal yang akan datang dulu, kemudian yang sudah lewat)
    from datetime import date
    today = date.today()
    
    # Ambil sesi yang belum lewat (tanggal >= hari ini), urutkan dari terdekat
    upcoming_sessions = Session.query.filter_by(workout_plan_id=id).filter(Session.date >= today).order_by(Session.date.asc()).all()
    
    # Ambil sesi yang sudah lewat (tanggal < hari ini), urutkan dari yang paling baru
    past_sessions = Session.query.filter_by(workout_plan_id=id).filter(Session.date < today).order_by(Session.date.desc()).all()
    
    # Gabungkan keduanya: upcoming dulu, baru past
    sessions = upcoming_sessions + past_sessions
    
    return render_template('workout_plans/view.html', 
                         workout_plan=workout_plan,
                         sessions=sessions)

@workout_plans_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit workout plan
    """
    workout_plan = WorkoutPlan.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            plan_name = request.form.get('plan_name', '').strip()
            if not plan_name:
                flash('Nama program latihan harus diisi.', 'error')
                return render_template('workout_plans/edit.html', workout_plan=workout_plan)
            
            # Update workout plan
            workout_plan.plan_name = plan_name
            workout_plan.notes = request.form.get('notes', '').strip()
            
            # Update new fields
            duration = request.form.get('duration')
            days_per_week = request.form.get('days_per_week')
            start_date = request.form.get('start_date')
            
            workout_plan.duration = int(duration) if duration else None
            workout_plan.days_per_week = int(days_per_week) if days_per_week else None
            workout_plan.start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
            
            db.session.commit()
            
            flash('Program latihan berhasil diperbarui!', 'success')
            return redirect(url_for('workout_plans.view', id=workout_plan.id))
            
        except ValueError:
            flash('Data tidak valid. Periksa kembali input Anda.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan saat menyimpan data: {str(e)}', 'error')
    
    return render_template('workout_plans/edit.html', workout_plan=workout_plan)

@workout_plans_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """
    Hapus workout plan dan update sesi terkait
    """
    workout_plan = WorkoutPlan.query.get_or_404(id)
    client_id = workout_plan.client_id
    
    try:
        plan_name = workout_plan.plan_name
        
        # Cari semua sesi yang terkait dengan workout plan ini
        related_sessions = Session.query.filter_by(workout_plan_id=id).all()
        session_count = len(related_sessions)
        
        # Hapus workout plan (akan otomatis menghapus sesi terkait karena cascade='all, delete-orphan')
        db.session.delete(workout_plan)
        db.session.commit()
        
        flash(f'Program latihan "{plan_name}" berhasil dihapus. {session_count} sesi terkait telah dihapus.', 'success')
        return redirect(url_for('workout_plans.index', client_id=client_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan saat menghapus data: {str(e)}', 'error')
        return redirect(url_for('workout_plans.view', id=id))

@workout_plans_bp.route('/<int:id>/copy', methods=['POST'])
@login_required
def copy_plan(id):
    """
    Copy workout plan untuk klien lain
    """
    original_plan = WorkoutPlan.query.get_or_404(id)
    target_client_id = request.form.get('target_client_id')
    
    if not target_client_id:
        flash('Pilih klien tujuan.', 'error')
        return redirect(url_for('workout_plans.view', id=id))
    
    target_client = Client.query.get_or_404(target_client_id)
    
    try:
        # Create new workout plan
        new_plan = WorkoutPlan(
            client_id=target_client_id,
            plan_name=f"{original_plan.plan_name} (Copy)",
            notes=original_plan.notes
        )
        
        db.session.add(new_plan)
        db.session.flush()
        
        # Copy all details
        for detail in original_plan.details:
            new_detail = WorkoutPlanDetail(
                plan_id=new_plan.id,
                day_name=detail.day_name,
                exercise=detail.exercise,
                sets=detail.sets,
                reps=detail.reps,
                weight=detail.weight,
                rest_time=detail.rest_time,
                notes=detail.notes
            )
            db.session.add(new_detail)
        
        db.session.commit()
        
        flash(f'Program latihan berhasil disalin ke {target_client.name}!', 'success')
        return redirect(url_for('workout_plans.view', id=new_plan.id))
        
    except Exception as e:
        db.session.rollback()
        flash('Terjadi kesalahan saat menyalin program latihan.', 'error')
        return redirect(url_for('workout_plans.view', id=id))