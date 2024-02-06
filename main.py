from flask import Flask, render_template, request, abort, flash, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, URL
from sqlalchemy.exc import IntegrityError
import os


# Init Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['FLASK_KEY']


# Init Boostrap
Bootstrap5(app)


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy()
db.init_app(app)

to_do_dict = {"sweep": "sweep the floor", "mop": "mop the floor", "brush": "brush the dog"}


class TodoForm(FlaskForm):
    name = StringField('Task Name', validators=[DataRequired()])
    desc = StringField('Description')
    duedate = StringField('Due Date')
    submit = SubmitField('Submit')


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    desc = db.Column(db.String(500), nullable=True)
    duedate = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    result = db.session.execute(db.select(Todo).order_by(Todo.id))
    all_todos = result.scalars().all()
    list_of_todos = []
    for todo in all_todos:
        list_of_todos.append(todo.to_dict())
    print(list_of_todos)
    return render_template("index.html", todos=list_of_todos)


@app.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    todo = db.get_or_404(Todo, todo_id)
    if todo:
        db.session.delete(todo)
        db.session.commit()
        result = db.session.execute(db.select(Todo).order_by(Todo.id))
        all_todos = result.scalars().all()
        list_of_todos = []
        for todo in all_todos:
            list_of_todos.append(todo.to_dict())
        return redirect(url_for('home'))
    else:
        result = db.session.execute(db.select(Todo).order_by(Todo.id))
        all_todos = result.scalars().all()
        list_of_todos = []
        for todo in all_todos:
            list_of_todos.append(todo.to_dict())
        return redirect(url_for('home'))


@app.route('/add', methods=['POST', 'GET'])
def add():
    form = TodoForm()
    if form.validate_on_submit():
        try:
            new_todo = Todo(
                name=request.form.get("name"),
                desc=request.form.get("desc"),
                duedate=request.form.get("duedate"),
            )
            db.session.add(new_todo)
            db.session.commit()
            result = db.session.execute(db.select(Todo).order_by(Todo.id))
            all_todos = result.scalars().all()
            list_of_todos = []
            for todo in all_todos:
                list_of_todos.append(todo.to_dict())
            return redirect(url_for('home'))
        except IntegrityError:
            # Handle the case where there's a duplicate name
            db.session.rollback()
            flash('Error: Task with this name already exists.')
        # result = db.session.execute(db.select(Todo).order_by(Todo.id))
        # all_todos = result.scalars().all()
        # list_of_todos = []
        # for todo in all_todos:
        #     list_of_todos.append(todo.to_dict())
        # return render_template('index.html', todos=list_of_todos)
    return render_template('add.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)