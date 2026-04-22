from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func
from forms import WorkoutForm
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    notes = db.Column(db.String(500), nullable=True)
    date_logged = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Workout %r>' % self.exercise_name


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/assignment/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/assignment/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)


@app.route('/assignment/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/assignment/')
    except:
        return 'There was a problem deleting that task'

@app.route('/assignment/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/assignment/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)


# ── Workout Log Routes ──────────────────────────────────────────────────────

@app.route('/workouts/', methods=['GET', 'POST'])
def workouts():
    form = WorkoutForm()
    if form.validate_on_submit():
        new_workout = Workout(
            exercise_name=form.exercise_name.data,
            category=form.category.data,
            duration=form.duration.data,
            sets=form.sets.data,
            reps=form.reps.data,
            weight=form.weight.data,
            notes=form.notes.data
        )
        try:
            db.session.add(new_workout)
            db.session.commit()
            return redirect('/workouts/')
        except:
            return 'There was an issue adding your workout'

    sort = request.args.get('sort', 'date')
    category_filter = request.args.get('category', '')

    query = Workout.query
    if category_filter:
        query = query.filter_by(category=category_filter)

    if sort == 'exercise':
        query = query.order_by(Workout.exercise_name)
    elif sort == 'category':
        query = query.order_by(Workout.category)
    elif sort == 'duration':
        query = query.order_by(Workout.duration.desc())
    else:
        query = query.order_by(Workout.date_logged.desc())

    all_workouts = query.all()
    categories = ['strength', 'cardio', 'flexibility', 'sports', 'other']
    return render_template('workouts/index.html', workouts=all_workouts, form=form,
                           sort=sort, category_filter=category_filter, categories=categories)


@app.route('/workouts/delete/<int:id>')
def delete_workout(id):
    workout = Workout.query.get_or_404(id)
    try:
        db.session.delete(workout)
        db.session.commit()
        return redirect('/workouts/')
    except:
        return 'There was a problem deleting that workout'


@app.route('/workouts/update/<int:id>', methods=['GET', 'POST'])
def update_workout(id):
    workout = Workout.query.get_or_404(id)
    form = WorkoutForm(obj=workout)
    if form.validate_on_submit():
        workout.exercise_name = form.exercise_name.data
        workout.category = form.category.data
        workout.duration = form.duration.data
        workout.sets = form.sets.data
        workout.reps = form.reps.data
        workout.weight = form.weight.data
        workout.notes = form.notes.data
        try:
            db.session.commit()
            return redirect('/workouts/')
        except:
            return 'There was an issue updating your workout'
    return render_template('workouts/update.html', form=form, workout=workout)


@app.route('/workouts/stats/')
def workout_stats():
    category_data = db.session.query(
        Workout.category, func.count(Workout.id)
    ).group_by(Workout.category).all()

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_data = db.session.query(
        func.date(Workout.date_logged), func.count(Workout.id)
    ).filter(Workout.date_logged >= seven_days_ago).group_by(
        func.date(Workout.date_logged)
    ).all()

    total_workouts = Workout.query.count()
    total_duration = db.session.query(func.sum(Workout.duration)).scalar() or 0

    return render_template('workouts/stats.html',
                           category_labels=json.dumps([r[0].capitalize() for r in category_data]),
                           category_counts=json.dumps([r[1] for r in category_data]),
                           date_labels=json.dumps([str(r[0]) for r in recent_data]),
                           date_counts=json.dumps([r[1] for r in recent_data]),
                           total_workouts=total_workouts,
                           total_duration=total_duration)


if __name__ == "__main__":
    app.run(debug=True)
