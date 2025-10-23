from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from models import Session, Client, db
from forms import SessionForm
from datetime import datetime, date
from sqlalchemy import desc, asc
import json
from extensions import csrf

sessions_bp = Blueprint('sessions', __name__)

@sessions_bp.route('/client/<int:client_id>')
@login_required
def index(client_id):
    """
    Daftar semua sesi latihan untuk klien tertentu
    """
    client = Client.query.get_or_404(client_id)
    
    # Pagination and filtering
    page = request.args.get('page', 1, type=int)
    month = request.args.get('month', '', type=str)
    
    query = Session.query.filter_by(client_id=client_id)
    
    # Filter by month if provided
    if month:
        try:
            month_date = datetime.strptime(month, '%Y-%m')
            start_date = month_date.date()
            if month_date.month == 12:
                end_date = date(month_date.year + 1, 1, 1)
            else:
                end_date = date(month_date.year, month_date.month + 1, 1)
            
            query = query.filter(Session.date >= start_date, Session.date < end_date)
        except ValueError:
            pass
    
    sessions = query.order_by(desc(Session.date)).paginate(
        page=page, per_page=15, error_out=False
    )
    
    return render_template('sessions/index.html', client=client, sessions=sessions, selected_month=month)

@sessions_bp.route('/client/<int:client_id>/add', methods=['GET', 'POST'])
@login_required
def add(client_id):
    """
    Tambah sesi latihan baru untuk klien
    """
    client = Client.query.get_or_404(client_id)
    form = SessionForm()
    form.client_id.data = client_id
    
    if form.validate_on_submit():
        try:
            # Create new session
            session = Session(
                client_id=client_id,
                date=form.date.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                session_type=form.session_type.data,
                exercises_performed=form.exercises_performed.data,
                client_feedback=form.client_feedback.data,
                trainer_notes=form.trainer_notes.data,
                rating=int(form.rating.data) if form.rating.data else None
            )
            
            db.session.add(session)
            db.session.commit()
            
            flash(f'Sesi latihan untuk {client.name} berhasil ditambahkan!', 'success')
            return redirect(url_for('sessions.view', id=session.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan saat menyimpan data.', 'error')
    
    return render_template('sessions/add.html', client=client, form=form)

@sessions_bp.route('/<int:id>')
@login_required
def view(id):
    """
    Lihat detail sesi latihan
    """
    session = Session.query.get_or_404(id)
    
    # Mencari sesi sebelumnya dan selanjutnya untuk klien yang sama
    prev_session = Session.query.filter(
        Session.client_id == session.client_id,
        Session.date < session.date
    ).order_by(desc(Session.date)).first()
    
    next_session = Session.query.filter(
        Session.client_id == session.client_id,
        Session.date > session.date
    ).order_by(asc(Session.date)).first()
    
    return render_template('sessions/view.html', session=session, prev_session=prev_session, next_session=next_session)

@sessions_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Edit sesi latihan
    """
    session = Session.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Validasi tanggal
            date_str = request.form.get('date')
            if not date_str:
                flash('Tanggal harus diisi.', 'error')
                return render_template('sessions/edit.html', session=session)
            
            session_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Validasi exercises_done
            exercises_done = request.form.get('exercises_done', '').strip()
            if not exercises_done:
                flash('Latihan yang dilakukan harus diisi.', 'error')
                return render_template('sessions/edit.html', session=session)
            
            # Update session data
            session.date = session_date
            session.exercises_done = exercises_done
            session.comments = request.form.get('comments', '').strip()
            
            db.session.commit()
            
            flash('Sesi latihan berhasil diperbarui!', 'success')
            return redirect(url_for('sessions.view', id=session.id))
            
        except ValueError:
            flash('Data tidak valid. Periksa kembali input Anda.', 'error')
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan saat menyimpan data.', 'error')
    
    return render_template('sessions/edit.html', session=session)

@sessions_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """
    Hapus sesi latihan
    """
    session = Session.query.get_or_404(id)
    client_id = session.client_id
    
    try:
        db.session.delete(session)
        db.session.commit()
        
        flash('Sesi latihan berhasil dihapus.', 'success')
        return redirect(url_for('sessions.index', client_id=client_id))
        
    except Exception as e:
        db.session.rollback()
        flash('Terjadi kesalahan saat menghapus data.', 'error')
        return redirect(url_for('sessions.view', id=id))

@sessions_bp.route('/client/<int:client_id>/calendar')
@login_required
def calendar(client_id):
    """
    Tampilan kalender sesi latihan klien
    """
    client = Client.query.get_or_404(client_id)
    
    # Get current month or requested month
    month_str = request.args.get('month', datetime.now().strftime('%Y-%m'))
    try:
        current_month = datetime.strptime(month_str, '%Y-%m')
    except ValueError:
        current_month = datetime.now().replace(day=1)
    
    # Get sessions for the month
    start_date = current_month.date()
    if current_month.month == 12:
        end_date = date(current_month.year + 1, 1, 1)
    else:
        end_date = date(current_month.year, current_month.month + 1, 1)
    
    sessions = Session.query.filter_by(client_id=client_id)\
        .filter(Session.date >= start_date, Session.date < end_date)\
        .order_by(asc(Session.date)).all()
    
    return render_template('sessions/calendar.html', 
                         client=client, 
                         sessions=sessions, 
                         current_month=current_month)

@sessions_bp.route('/<int:id>/toggle_complete', methods=['POST'])
@login_required
def toggle_complete(id):
    """
    Mengubah status sesi menjadi selesai atau belum selesai
    """
    session = Session.query.get_or_404(id)
    
    try:
        # Toggle status completed
        session.completed = not session.completed
        db.session.commit()
        
        status = "selesai" if session.completed else "belum selesai"
        flash(f'Status sesi berhasil diubah menjadi {status}.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Terjadi kesalahan saat mengubah status sesi.', 'error')
    
    return redirect(url_for('sessions.view', id=id))
    
    if start_date:
        query = query.filter(Session.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Session.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    sessions = query.order_by(asc(Session.date)).all()
    
    # Format data for calendar
    events = []
    for session in sessions:
        events.append({
            'id': session.id,
            'title': f'Sesi Latihan - {session.client.name}',
            'date': session.date.strftime('%Y-%m-%d'),
            'exercises': session.exercises_done[:100] + '...' if len(session.exercises_done) > 100 else session.exercises_done,
            'comments': session.comments[:100] + '...' if session.comments and len(session.comments) > 100 else session.comments,
            'url': url_for('sessions.view', id=session.id)
        })
    
    return jsonify(events)

@sessions_bp.route('/today')
@login_required
def today():
    """
    Sesi latihan hari ini untuk semua klien
    """
    today_date = date.today()
    today_sessions = Session.query.filter_by(date=today_date)\
        .join(Client)\
        .order_by(Client.name).all()
    
    return render_template('sessions/today.html', 
                         today_sessions=today_sessions, 
                         today_date=today_date)

# Endpoint untuk update actual reps secara inline dari AJAX
@sessions_bp.route('/update_actual_reps', methods=['POST'])
@csrf.exempt
@login_required
def update_actual_reps():
    """
    Menerima update reps dari AJAX dan menyimpan ke database sebagai string
    """
    from models import SessionDetail, db
    import sys
    data = request.get_json()
    print('DEBUG update_actual_reps:', data, file=sys.stderr)
    detail_id = data.get('detail_id')
    reps_num = data.get('reps_num')
    value = data.get('value')

    # Validasi input
    if not detail_id or not reps_num:
        print('DEBUG: Data tidak lengkap', file=sys.stderr)
        return {'success': False, 'message': 'Data tidak lengkap'}, 400
    if reps_num not in ['1', '2', '3', '4']:
        print('DEBUG: Nomor reps tidak valid', file=sys.stderr)
        return {'success': False, 'message': 'Nomor reps tidak valid'}, 400

    detail = db.session.get(SessionDetail, detail_id)
    if not detail:
        print('DEBUG: Detail tidak ditemukan', file=sys.stderr)
        return {'success': False, 'message': 'Detail tidak ditemukan'}, 404

    try:
        # Jika value kosong, simpan sebagai None
        if value == '' or value is None:
            setattr(detail, f'actual_reps_{reps_num}', None)
        else:
            setattr(detail, f'actual_reps_{reps_num}', str(value))
        db.session.commit()
        print('DEBUG: Berhasil update actual reps', file=sys.stderr)
        return {'success': True, 'message': 'Berhasil update actual reps'}
    except Exception as e:
        db.session.rollback()
        print(f'DEBUG: Gagal update: {str(e)}', file=sys.stderr)
        return {'success': False, 'message': f'Gagal update: {str(e)}'}, 500

@sessions_bp.route('/<int:id>/update_notes', methods=['POST'])
@login_required
@csrf.exempt
def update_notes(id):
    """
    Endpoint untuk update notes pada sesi latihan
    """
    session = Session.query.get_or_404(id)
    notes = request.form.get('notes', '').strip()
    session.notes = notes
    db.session.commit()
    flash('Notes berhasil diperbarui!', 'success')
    return redirect(url_for('sessions.view', id=session.id))

# Endpoint untuk update rest_time secara inline dari AJAX
@sessions_bp.route('/update_rest_time', methods=['POST'])
@csrf.exempt
@login_required
def update_rest_time():
    """
    Menerima update rest_time dari AJAX dan menyimpan ke database
    """
    from models import SessionDetail, db
    import sys
    data = request.get_json()
    print('DEBUG update_rest_time:', data, file=sys.stderr)
    detail_id = data.get('detail_id')
    rest_time = data.get('rest_time')

    # Validasi input
    if not detail_id:
        print('DEBUG: Data tidak lengkap', file=sys.stderr)
        return {'success': False, 'message': 'Data tidak lengkap'}, 400

    detail = db.session.get(SessionDetail, detail_id)
    if not detail:
        print('DEBUG: Detail tidak ditemukan', file=sys.stderr)
        return {'success': False, 'message': 'Detail tidak ditemukan'}, 404

    try:
        # Jika rest_time kosong, simpan sebagai None
        if rest_time == '' or rest_time is None:
            detail.rest_time = None
        else:
            detail.rest_time = rest_time
        db.session.commit()
        print('DEBUG: Berhasil update rest time', file=sys.stderr)
        return {'success': True, 'message': 'Berhasil update rest time'}
    except Exception as e:
        db.session.rollback()
        print(f'DEBUG: Gagal update: {str(e)}', file=sys.stderr)
        return {'success': False, 'message': f'Gagal update: {str(e)}'}, 500

@sessions_bp.route('/update_exercise_notes', methods=['POST'])
@csrf.exempt
@login_required
def update_exercise_notes():
    """
    Menerima update notes untuk exercise dari AJAX dan menyimpan ke database
    """
    from models import SessionDetail, db
    import sys
    data = request.get_json()
    print('DEBUG update_exercise_notes:', data, file=sys.stderr)
    detail_id = data.get('detail_id')
    notes = data.get('notes')

    # Validasi input
    if not detail_id:
        print('DEBUG: Data tidak lengkap', file=sys.stderr)
        return {'success': False, 'message': 'Data tidak lengkap'}, 400

    detail = db.session.get(SessionDetail, detail_id)
    if not detail:
        print('DEBUG: Detail tidak ditemukan', file=sys.stderr)
        return {'success': False, 'message': 'Detail tidak ditemukan'}, 404

    try:
        detail.notes = notes
        db.session.commit()
        print('DEBUG: Berhasil update notes', file=sys.stderr)
        return {'success': True, 'message': 'Berhasil update notes'}
    except Exception as e:
        db.session.rollback()
        print(f'DEBUG: Gagal update: {str(e)}', file=sys.stderr)
        return {'success': False, 'message': f'Gagal update: {str(e)}'}, 500