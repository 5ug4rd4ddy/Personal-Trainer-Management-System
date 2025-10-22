"""
Forms untuk aplikasi Personal Trainer Client Management System
Menggunakan Flask-WTF untuk validasi form dan keamanan CSRF
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, IntegerField, FloatField, 
    SelectField, DateField, TimeField, PasswordField,
    SubmitField, HiddenField, FieldList, FormField, BooleanField
)
from wtforms.validators import (
    DataRequired, Email, Optional, Length, NumberRange,
    ValidationError
)
from datetime import date, datetime
from models import Client, Assessment, Session


class LoginForm(FlaskForm):
    """Form untuk login Personal Trainer"""
    username = StringField('Username', validators=[
        DataRequired(message='Username wajib diisi'),
        Length(min=3, max=50, message='Username harus 3-50 karakter')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password wajib diisi')
    ])
    submit = SubmitField('Login')


class ClientForm(FlaskForm):
    """Form untuk menambah/edit klien"""
    name = StringField('Nama Lengkap', validators=[
        DataRequired(message='Nama wajib diisi'),
        Length(min=2, max=100, message='Nama harus 2-100 karakter')
    ])
    email = StringField('Email', validators=[
        Optional(),
        Email(message='Format email tidak valid')
    ])
    phone = StringField('Nomor Telepon', validators=[
        DataRequired(message='Nomor telepon wajib diisi'),
        Length(min=10, max=15, message='Nomor telepon harus 10-15 digit')
    ])
    birth_date = DateField('Tanggal Lahir', validators=[
        Optional()
    ])
    gender = SelectField('Jenis Kelamin', choices=[
        ('', 'Pilih Jenis Kelamin'),
        ('Male', 'Laki-laki'),
        ('Female', 'Perempuan')
    ], validators=[DataRequired(message='Jenis kelamin wajib dipilih')])
    
    height = FloatField('Tinggi Badan (cm)', validators=[
        Optional(),
        NumberRange(min=100, max=250, message='Tinggi badan harus antara 100-250 cm')
    ])
    start_weight = FloatField('Berat Badan Awal (kg)', validators=[
        Optional(),
        NumberRange(min=30, max=300, message='Berat badan harus antara 30-300 kg')
    ])
    medical_notes = TextAreaField('Catatan Medis', validators=[Optional()])
    
    photo = FileField('Foto Profil', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Hanya file JPG dan PNG yang diizinkan')
    ])
    
    submit = SubmitField('Simpan')


class AssessmentForm(FlaskForm):
    """Form untuk assessment klien"""
    client_id = HiddenField()
    date = DateField('Tanggal Assessment', validators=[
        DataRequired(message='Tanggal wajib diisi')
    ], default=date.today)
    
    # Body measurements
    weight = FloatField('Berat Badan (kg)', validators=[
        DataRequired(message='Berat badan wajib diisi'),
        NumberRange(min=30, max=300, message='Berat badan harus antara 30-300 kg')
    ])
    height = FloatField('Tinggi Badan (cm)', validators=[
        DataRequired(message='Tinggi badan wajib diisi'),
        NumberRange(min=100, max=250, message='Tinggi badan harus antara 100-250 cm')
    ])
    body_fat = FloatField('Body Fat (%)', validators=[
        Optional(),
        NumberRange(min=0, max=50, message='Body fat harus antara 0-50%')
    ])
    muscle_mass = FloatField('Massa Otot (kg)', validators=[
        Optional(),
        NumberRange(min=0, max=100, message='Massa otot harus antara 0-100 kg')
    ])
    
    # Body measurements
    chest = FloatField('Lingkar Dada (cm)', validators=[Optional()])
    waist = FloatField('Lingkar Pinggang (cm)', validators=[Optional()])
    hips = FloatField('Lingkar Pinggul (cm)', validators=[Optional()])
    arm = FloatField('Lingkar Lengan (cm)', validators=[Optional()])
    thigh = FloatField('Lingkar Paha (cm)', validators=[Optional()])
    neck = FloatField('Lingkar Leher (cm)', validators=[Optional()])
    
    # Strength tests
    squat_max = FloatField('Squat Max (kg)', validators=[
        Optional(),
        NumberRange(min=0, max=500, message='Squat max harus antara 0-500 kg')
    ])
    bench_max = FloatField('Bench Press Max (kg)', validators=[
        Optional(),
        NumberRange(min=0, max=500, message='Bench press max harus antara 0-500 kg')
    ])
    deadlift_max = FloatField('Deadlift Max (kg)', validators=[
        Optional(),
        NumberRange(min=0, max=500, message='Deadlift max harus antara 0-500 kg')
    ])
    
    # Fitness tests
    pushup_test = IntegerField('Push-up Test (reps)', validators=[
        Optional(),
        NumberRange(min=0, max=200, message='Push-up test harus antara 0-200')
    ])
    pullup_test = IntegerField('Pull-up Test (reps)', validators=[
        Optional(),
        NumberRange(min=0, max=100, message='Pull-up test harus antara 0-100')
    ])
    
    notes = TextAreaField('Catatan', validators=[Optional()])
    
    photo = FileField('Foto Assessment', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Hanya file JPG dan PNG yang diizinkan')
    ])
    
    submit = SubmitField('Simpan Assessment')
    
    def validate_date(self, field):
        """Validasi tanggal tidak boleh di masa depan"""
        if field.data > date.today():
            raise ValidationError('Tanggal assessment tidak boleh di masa depan')


class WorkoutPlanDetailForm(FlaskForm):
    """Form untuk detail workout plan (exercise)"""
    day = SelectField('Hari', choices=[
        ('1', 'Senin'),
        ('2', 'Selasa'),
        ('3', 'Rabu'),
        ('4', 'Kamis'),
        ('5', 'Jumat'),
        ('6', 'Sabtu'),
        ('7', 'Minggu')
    ], validators=[DataRequired(message='Hari wajib dipilih')])
    
    exercise_name = StringField('Nama Latihan', validators=[
        DataRequired(message='Nama latihan wajib diisi'),
        Length(min=2, max=100, message='Nama latihan harus 2-100 karakter')
    ])
    sets = IntegerField('Sets', validators=[
        DataRequired(message='Jumlah set wajib diisi'),
        NumberRange(min=1, max=20, message='Sets harus antara 1-20')
    ])
    reps = StringField('Reps', validators=[
        DataRequired(message='Reps wajib diisi'),
        Length(max=20, message='Reps maksimal 20 karakter')
    ])
    weight = FloatField('Beban (kg)', validators=[
        Optional(),
        NumberRange(min=0, max=500, message='Beban harus antara 0-500 kg')
    ])
    rest_time = StringField('Waktu Istirahat', validators=[
        Optional(),
        Length(max=20, message='Waktu istirahat maksimal 20 karakter')
    ])
    notes = TextAreaField('Catatan', validators=[Optional()])


class WorkoutPlanForm(FlaskForm):
    """Form untuk workout plan"""
    client_id = HiddenField()
    name = StringField('Nama Program', validators=[
        DataRequired(message='Nama program wajib diisi'),
        Length(min=2, max=100, message='Nama program harus 2-100 karakter')
    ])
    description = TextAreaField('Deskripsi', validators=[Optional()])
    start_date = DateField('Tanggal Mulai', validators=[
        DataRequired(message='Tanggal mulai wajib diisi')
    ], default=date.today)
    end_date = DateField('Tanggal Selesai', validators=[
        Optional()
    ])
    
    # Dynamic field list for exercises
    exercises = FieldList(FormField(WorkoutPlanDetailForm), min_entries=1)
    
    submit = SubmitField('Simpan Program')
    
    def validate_end_date(self, field):
        """Validasi tanggal selesai harus setelah tanggal mulai"""
        if field.data and self.start_date.data:
            if field.data <= self.start_date.data:
                raise ValidationError('Tanggal selesai harus setelah tanggal mulai')




class SessionForm(FlaskForm):
    """Form untuk session logging"""
    client_id = HiddenField()
    date = DateField('Tanggal', validators=[
        DataRequired(message='Tanggal wajib diisi')
    ], default=date.today)
    start_time = TimeField('Waktu Mulai', validators=[
        DataRequired(message='Waktu mulai wajib diisi')
    ])
    end_time = TimeField('Waktu Selesai', validators=[
        DataRequired(message='Waktu selesai wajib diisi')
    ])
    duration = IntegerField('Durasi', validators=[
        Optional(),
        NumberRange(min=15, max=240, message='Durasi harus antara 15-240 menit')
    ])
    
    workout_plan_id = SelectField('Program Latihan', validators=[Optional()], coerce=int)
    
    completed = BooleanField('Sesi Selesai')
    
    # Performance metrics
    total_weight = FloatField('Total Beban', validators=[Optional()])
    total_reps = IntegerField('Total Repetisi', validators=[Optional()])
    calories_burned = IntegerField('Kalori Terbakar', validators=[Optional()])
    
    notes = TextAreaField('Catatan Sesi', validators=[Optional()])
    
    session_type = SelectField('Jenis Sesi', choices=[
        ('', 'Pilih Jenis Sesi'),
        ('strength', 'Strength Training'),
        ('cardio', 'Cardio'),
        ('flexibility', 'Flexibility'),
        ('functional', 'Functional Training'),
        ('assessment', 'Assessment'),
        ('consultation', 'Konsultasi')
    ], validators=[DataRequired(message='Jenis sesi wajib dipilih')])
    
    exercises_performed = TextAreaField('Latihan yang Dilakukan', validators=[
        DataRequired(message='Latihan yang dilakukan wajib diisi')
    ])
    
    client_feedback = TextAreaField('Feedback Klien', validators=[Optional()])
    trainer_notes = TextAreaField('Catatan Trainer', validators=[Optional()])
    
    rating = SelectField('Rating Sesi', choices=[
        ('', 'Pilih Rating'),
        ('1', '1 - Sangat Buruk'),
        ('2', '2 - Buruk'),
        ('3', '3 - Cukup'),
        ('4', '4 - Baik'),
        ('5', '5 - Sangat Baik')
    ], validators=[Optional()])
    
    submit = SubmitField('Simpan Sesi')
    
    def validate_end_time(self, field):
        """Validasi waktu selesai harus setelah waktu mulai"""
        if field.data and self.start_time.data:
            if field.data <= self.start_time.data:
                raise ValidationError('Waktu selesai harus setelah waktu mulai')
    
    def validate_date(self, field):
        """Validasi tanggal tidak boleh di masa depan"""
        if field.data > date.today():
            raise ValidationError('Tanggal sesi tidak boleh di masa depan')


class SearchForm(FlaskForm):
    """Form untuk pencarian"""
    search = StringField('Cari', validators=[Optional()])
    submit = SubmitField('Cari')


class CopyWorkoutPlanForm(FlaskForm):
    """Form untuk copy workout plan ke klien lain"""
    target_client_id = SelectField('Klien Tujuan', validators=[
        DataRequired(message='Klien tujuan wajib dipilih')
    ])
    new_name = StringField('Nama Program Baru', validators=[
        DataRequired(message='Nama program baru wajib diisi'),
        Length(min=2, max=100, message='Nama program harus 2-100 karakter')
    ])
    submit = SubmitField('Copy Program')