from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Database config — uses DATABASE_URL env var (set by Docker), falls back to SQLite locally
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///todos.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
        }


@app.route('/')
def index():
    filter_by = request.args.get('filter', 'all')
    if filter_by == 'active':
        todos = Todo.query.filter_by(completed=False).order_by(Todo.created_at.desc()).all()
    elif filter_by == 'completed':
        todos = Todo.query.filter_by(completed=True).order_by(Todo.created_at.desc()).all()
    else:
        todos = Todo.query.order_by(Todo.created_at.desc()).all()

    total = Todo.query.count()
    completed_count = Todo.query.filter_by(completed=True).count()
    active_count = total - completed_count

    return render_template('index.html',
                           todos=todos,
                           filter_by=filter_by,
                           total=total,
                           completed_count=completed_count,
                           active_count=active_count)


@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title', '').strip()
    if title:
        todo = Todo(title=title)
        db.session.add(todo)
        db.session.commit()
    return redirect(url_for('index', filter=request.form.get('filter', 'all')))


@app.route('/toggle/<int:todo_id>', methods=['POST'])
def toggle(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for('index', filter=request.args.get('filter', 'all')))


@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index', filter=request.args.get('filter', 'all')))


@app.route('/clear-completed', methods=['POST'])
def clear_completed():
    Todo.query.filter_by(completed=True).delete()
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get('FLASK_DEBUG', 'false') == 'true')
