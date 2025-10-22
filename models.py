from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Numeric

# Initialize db instance here to avoid circular imports
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    Model untuk user/admin (Personal Trainer) dan klien
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('admin', 'client'), default='admin', nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)  # Untuk role client
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship untuk client user
    linked_client = db.relationship('Client', backref='user_account', foreign_keys=[client_id])
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def is_client(self):
        """Check if user is client"""
        return self.role == 'client'
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

class Client(db.Model):
    """
    Model untuk data klien
    """
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    gender = db.Column(db.Enum('Male', 'Female'), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    photo = db.Column(db.String(255))  # Path ke file foto
    height = db.Column(Numeric(5, 2))  # dalam cm
    start_weight = db.Column(Numeric(5, 2))  # dalam kg
    medical_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessments = db.relationship('Assessment', backref='client', lazy=True, cascade='all, delete-orphan')
    workout_plans = db.relationship('WorkoutPlan', backref='client', lazy=True, cascade='all, delete-orphan')

    sessions = db.relationship('Session', backref='client', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Client {self.name}>'

class Exercise(db.Model):
    """
    Model untuk menyimpan daftar latihan yang tersedia
    """
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)  # Kategori latihan (contoh: 'Chest', 'Legs', 'Back', dll)
    weight_options = db.Column(db.JSON, nullable=True)  # Menyimpan opsi weight dalam format JSON
    reps_options = db.Column(db.JSON, nullable=True)  # Menyimpan opsi reps dalam format JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Exercise {self.name}>'

class Assessment(db.Model):
    """
    Model untuk assessment awal klien
    """
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    weight = db.Column(Numeric(5, 2))  # dalam kg
    height = db.Column(Numeric(5, 2))  # dalam cm
    muscle_mass = db.Column(Numeric(5, 2))  # dalam kg
    neck = db.Column(Numeric(5, 2))  # dalam cm
    date = db.Column(db.Date, nullable=True)
    body_fat = db.Column(Numeric(5, 2))  # dalam %
    chest = db.Column(Numeric(5, 2))  # dalam cm
    waist = db.Column(Numeric(5, 2))  # dalam cm
    hips = db.Column(Numeric(5, 2))  # dalam cm
    arm = db.Column(Numeric(5, 2))  # dalam cm
    thigh = db.Column(Numeric(5, 2))  # dalam cm
    squat_max = db.Column(Numeric(5, 2))  # dalam kg
    bench_max = db.Column(Numeric(5, 2))  # dalam kg
    deadlift_max = db.Column(Numeric(5, 2))  # dalam kg
    pushup_test = db.Column(db.Integer)  # jumlah pushup
    pullup_test = db.Column(db.Integer)  # jumlah pullup
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Assessment {self.client.name} - {self.created_at.strftime("%Y-%m-%d")}>'

class WorkoutPlan(db.Model):
    """
    Model untuk rencana latihan
    """
    __tablename__ = 'workout_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)
    duration = db.Column(db.Integer, nullable=True)  # Durasi dalam minggu
    days_per_week = db.Column(db.Integer, nullable=True)  # Jumlah hari latihan per minggu
    start_date = db.Column(db.Date, nullable=True)  # Tanggal mulai program
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    details = db.relationship('WorkoutPlanDetail', backref='workout_plan', lazy=True, cascade='all, delete-orphan')
    sessions = db.relationship('Session', back_populates='workout_plan', lazy=True, cascade='all, delete-orphan', foreign_keys='Session.workout_plan_id')
    
    def __repr__(self):
        return f'<WorkoutPlan {self.plan_name}>'

class WorkoutPlanDetail(db.Model):
    """
    Model untuk detail rencana latihan per hari
    """
    __tablename__ = 'workout_plan_details'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('workout_plans.id'), nullable=False)
    day_name = db.Column(db.String(20), nullable=False)  # Senin, Selasa, dst
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=True)  # Referensi ke model Exercise
    exercise = db.Column(db.String(100), nullable=False)  # Tetap simpan nama latihan untuk kompatibilitas
    sets = db.Column(db.Integer)
    reps = db.Column(db.String(20))  # Mengubah dari Integer ke String untuk mendukung format "6-8", "AMRAP", dll
    weight = db.Column(Numeric(5, 2))  # dalam kg
    rest_time = db.Column(db.String(20), nullable=True)  # contoh: "60 detik"
    notes = db.Column(db.Text)
    
    # Relationship dengan Exercise
    exercise_ref = db.relationship('Exercise', foreign_keys=[exercise_id])
    
    def __repr__(self):
        return f'<WorkoutPlanDetail {self.exercise} - {self.day_name}>'



class Session(db.Model):
    """
    Model untuk sesi latihan
    """
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # dalam menit
    workout_plan_id = db.Column(db.Integer, db.ForeignKey('workout_plans.id'), nullable=True)
    completed = db.Column(db.Boolean, default=False)
    total_weight = db.Column(Numeric(8, 2), nullable=True)  # Total berat yang diangkat dalam sesi
    total_reps = db.Column(db.Integer, nullable=True)  # Total repetisi dalam sesi
    calories_burned = db.Column(db.Integer, nullable=True)  # Estimasi kalori yang terbakar
    notes = db.Column(db.Text, nullable=True)
    session_type = db.Column(db.String(50), nullable=True)  # Tipe sesi (strength, cardio, dll)
    client_feedback = db.Column(db.Text, nullable=True)  # Feedback dari klien
    trainer_notes = db.Column(db.Text, nullable=True)  # Catatan dari trainer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    workout_plan = db.relationship('WorkoutPlan', foreign_keys=[workout_plan_id], back_populates='sessions')
    details = db.relationship('SessionDetail', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Session {self.client.name} - {self.date}>'

class SessionDetail(db.Model):
    """
    Model untuk detail latihan yang dilakukan dalam sesi
    """
    __tablename__ = 'session_details'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=True)
    exercise_name = db.Column(db.String(100), nullable=False)  # Nama latihan
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.String(20), nullable=True)  # String untuk mendukung format "6-8", "AMRAP", dll
    weight = db.Column(db.String(50), nullable=True)  # bisa berupa nilai numerik atau string (seperti "UNGU" untuk band)
    rest_time = db.Column(db.String(20), nullable=True)  # contoh: "60 detik"
    notes = db.Column(db.Text, nullable=True)
    actual_reps_1 = db.Column(db.Integer, nullable=True)
    actual_reps_2 = db.Column(db.Integer, nullable=True)
    actual_reps_3 = db.Column(db.Integer, nullable=True)
    actual_reps_4 = db.Column(db.Integer, nullable=True)
    
    # Relationship dengan Exercise
    exercise = db.relationship('Exercise', foreign_keys=[exercise_id])
    
    def __repr__(self):
        return f'<SessionDetail {self.exercise_name} - {self.session_id}>'