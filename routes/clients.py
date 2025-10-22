from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from models import Client, Assessment, Session, WorkoutPlan, db, Exercise, SessionDetail
from forms import ClientForm
from datetime import datetime
from sqlalchemy import desc, func
from werkzeug.datastructures import FileStorage

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/')
@login_required
def index():
    """
    Halaman daftar semua klien
    """
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = Client.query
    
    if search:
        query = query.filter(Client.name.contains(search))
    
    clients_data = query.order_by(desc(Client.created_at)).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Hitung umur untuk setiap klien
    for client in clients_data.items:
        if client.birth_date:
            today = datetime.now().date()
            client.age = today.year - client.birth_date.year - ((today.month, today.day) < (client.birth_date.month, client.birth_date.day))
        else:
            client.age = None
    
    return render_template('clients/index.html', clients=clients_data, search=search)

@clients_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """
    Tambah klien baru
    """
    form = ClientForm()
    
    if form.validate_on_submit():
        try:
            # Buat klien baru
            client = Client(
                name=form.name.data,
                birth_date=form.birth_date.data,
                gender=form.gender.data,
                phone=form.phone.data,
                email=form.email.data,
                height=form.height.data,
                start_weight=form.start_weight.data,
                medical_notes=form.medical_notes.data
            )
            
            # Proses upload foto jika ada
            if form.photo.data and hasattr(form.photo.data, 'filename') and form.photo.data.filename:
                import os
                from werkzeug.utils import secure_filename
                import uuid
                from werkzeug.datastructures import FileStorage
                
                # Pastikan direktori uploads ada
                upload_folder = os.path.join('static', 'uploads')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                # Simpan file dengan nama unik
                filename = secure_filename(form.photo.data.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                
                # Simpan file ke path yang benar
                save_path = os.path.join(upload_folder, unique_filename)
                form.photo.data.save(save_path)
                
                # Simpan nama file ke database
                client.photo = unique_filename
            
            db.session.add(client)
            db.session.commit()
            
            flash(f'Klien {client.name} berhasil ditambahkan!', 'success')
            return redirect(url_for('clients.view', id=client.id))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error saat menyimpan data: {str(e)}")
            flash('Terjadi kesalahan saat menyimpan data.', 'error')
    
    return render_template('clients/add.html', form=form)

@clients_bp.route('/<int:id>')
@login_required
def view(id):
    """
    Lihat detail klien
    """
    client = Client.query.get_or_404(id)
    
    # Ambil data terkait
    latest_assessment = Assessment.query.filter_by(client_id=id).order_by(desc(Assessment.created_at)).first()
    recent_sessions = Session.query.filter_by(client_id=id).order_by(desc(Session.date)).limit(5).all()
    workout_plans = WorkoutPlan.query.filter_by(client_id=id).order_by(desc(WorkoutPlan.created_at)).all()
    
    # Hitung umur jika ada tanggal lahir
    age = None
    if client.birth_date:
        today = datetime.now().date()
        age = today.year - client.birth_date.year - ((today.month, today.day) < (client.birth_date.month, client.birth_date.day))
    
    return render_template('clients/view.html',
                         client=client,
                         age=age,
                         latest_assessment=latest_assessment,
                         recent_sessions=recent_sessions,
                         workout_plans=workout_plans,
                         now=datetime.now())

@clients_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit data klien
    """
    client = Client.query.get_or_404(id)
    form = ClientForm(obj=client)
    
    if form.validate_on_submit():
        try:
            # Update data dari form
            form.populate_obj(client)
            
            # Proses upload foto jika ada
            if form.photo.data:
                # Cek apakah ini adalah objek file yang valid
                from werkzeug.datastructures import FileStorage
                if isinstance(form.photo.data, FileStorage) and form.photo.data.filename:
                    import os
                    from werkzeug.utils import secure_filename
                    import uuid
                    
                    # Pastikan direktori uploads ada
                    upload_folder = os.path.join('static', 'uploads')
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    
                    # Simpan file dengan nama unik
                    filename = secure_filename(form.photo.data.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    
                    # Simpan file ke path yang benar
                    save_path = os.path.join(upload_folder, unique_filename)
                    form.photo.data.save(save_path)
                    
                    # Hapus foto lama jika ada
                    if client.photo and isinstance(client.photo, str) and not client.photo.startswith('<FileStorage'):
                        old_photo_path = os.path.join(upload_folder, client.photo)
                        if os.path.exists(old_photo_path):
                            try:
                                os.remove(old_photo_path)
                            except:
                                pass
                    
                    # Simpan nama file baru ke database (pastikan ini string)
                    client.photo = unique_filename
            
            client.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash(f'Data klien {client.name} berhasil diperbarui!', 'success')
            return redirect(url_for('clients.view', id=client.id))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error saat menyimpan data: {str(e)}")
            flash('Terjadi kesalahan saat menyimpan data.', 'error')
    
    return render_template('clients/edit.html', client=client, form=form)

@clients_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """
    Hapus klien (dengan konfirmasi)
    """
    client = Client.query.get_or_404(id)
    
    try:
        client_name = client.name
        db.session.delete(client)
        db.session.commit()
        
        flash(f'Klien {client_name} berhasil dihapus.', 'success')
        return redirect(url_for('clients.index'))
        
    except Exception as e:
        db.session.rollback()
        flash('Terjadi kesalahan saat menghapus data.', 'error')
        return redirect(url_for('clients.view', id=id))

@clients_bp.route('/api/search')
@login_required
def api_search():
    """
    API untuk pencarian klien (untuk autocomplete)
    """
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    clients = Client.query.filter(Client.name.contains(query)).limit(10).all()
    
    results = []
    for client in clients:
        results.append({
            'id': client.id,
            'name': client.name,
            'phone': client.phone,
            'email': client.email
        })
    
    return jsonify(results)

@clients_bp.route('/api/<int:client_id>/exercises')
@login_required
def api_client_exercises(client_id):
    """
    API untuk mendapatkan daftar exercise yang pernah digunakan oleh client
    berdasarkan data session_details
    """
    # Cek apakah client ada
    client = Client.query.get_or_404(client_id)
    
    # Query untuk mendapatkan exercise yang pernah digunakan oleh client
    exercises = db.session.query(Exercise.id, Exercise.name)\
        .join(SessionDetail, SessionDetail.exercise_id == Exercise.id)\
        .join(Session, Session.id == SessionDetail.session_id)\
        .filter(Session.client_id == client_id)\
        .group_by(Exercise.id, Exercise.name)\
        .order_by(Exercise.name)\
        .all()
    
    # Format hasil query
    result = [{'id': 'all', 'name': 'Semua Exercise'}]
    for exercise_id, exercise_name in exercises:
        result.append({
            'id': exercise_id,
            'name': exercise_name
        })
    
    return jsonify(result)