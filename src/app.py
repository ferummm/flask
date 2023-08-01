from flask import Flask, flash, get_flashed_messages, \
    make_response, redirect, render_template, request, \
    session, url_for
import json
from validation import validate, validate_mail
#from repository import UsersRepository

# Это callable WSGI-приложение
app = Flask(__name__)

app.secret_key = '2e18421321a9d10e19427b5e3214ed46fc92c42dc78b27cb852c4301cbbfe029'
#source = 'users_repo.json'
#repo = UsersRepository(source)

users = ['mike', 'mishel', 'adel', 'keks', 'kamila']

@app.before_request
def before_request():
    if 'email' not in session and request.endpoint != 'login':
        return redirect(url_for('login'), code=302)


@app.route('/')
def index():
    return render_template(
        'index.html',
        logout_url=url_for('logout') if session.get('email') else None,
        search_url=url_for('get_search'),
        users_url=url_for('get_users')
    )


@app.post('/')
def logout():
    session['email']
    session.clear()
    return redirect(url_for('login'), code=302)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        if validate_mail(email):
           session['email'] = email
           return redirect(url_for('index'), code=302)
    return render_template('login.html',
                           form_destination=url_for('login'))


@app.get('/search')
def get_search():
    term = request.args.get("term", default=None, type=str)

    search_res = users if term is None else [name for name in users if term in name]

    return render_template(
        'search/index.html',
        logout_url=url_for('logout') if session.get('email') else None,
        back_url=url_for('index'),
        search_res=search_res,
        search= "" if term is None else term,
        form_destination=url_for('get_search')
        )


@app.post('/search')
def post_search():
    return 'Page not found', 404


@app.route('/users')
def get_users():
    messages = get_flashed_messages(with_categories=True)
    users = json.loads(request.cookies.get('users', json.dumps([])))
    encoded_users = json.dumps(users)

    
    response = make_response(render_template(
        'users/users_list.html',
        back_url=url_for('index'),
        logout_url=url_for('logout') if session.get('email') else None,
        users=users,
        messages=messages,
        new_user_url=url_for('get_new_user'),
        user_handler='get_user'
    ))
    response.set_cookie('users', encoded_users)
    return response



@app.route('/users/new')
def get_new_user():
    return render_template(
        'users/new.html',
        errors={},
        user={},
        form_destination=url_for('get_users')
        )


@app.post('/users')
def post_new_user():
    user = {}
    user['name'] = request.form.get('name', default=None, type=str)
    user['email'] = request.form.get('email', default=None, type=str)

    if errors:=validate(user):
        return render_template(
            'users/new.html',
            errors=errors,
            user=user
        ), 422
    else:
        users = json.loads(request.cookies.get('users', json.dumps([])))
        last_id = users[-1]['id'] + 1 if len(users) != 0 else 1
        user['id'] = last_id
        users.append(user)
        
        encoded_users = json.dumps(users)

        response = make_response(redirect(url_for('get_users'), code=302))
        response.set_cookie('users', encoded_users)
        flash('User was added successfully', 'success')
        return response


@app.get('/users/<int:id>')
def get_user(id):
    messages = get_flashed_messages(with_categories=True)
    users = json.loads(request.cookies.get('users', json.dumps([])))
    user = next((user for user in users if user['id'] == id))
    if user:
        return render_template(
            'users/show.html',
            messages=messages,
            user=user,
            edit_url=url_for('edit_user', id=id),
            delete_url=url_for('delete_user', id=id),
            back_url=url_for('get_users')
        )
    else:
        return 'Page not found', 404
    

@app.get('/users/<int:id>/edit')    
def edit_user(id):
    users = json.loads(request.cookies.get('users', json.dumps([])))
    user = next((user for user in users if user['id'] == id))
    if user:
        return render_template(
            'users/edit.html',
            user=user,
            errors={},
            form_destination=url_for('patch_user',id=id)
        )
    else:
        return 'Page not found', 404


@app.post('/users/<int:id>/edit')
def patch_user(id):
    updated_user = {}
    updated_user['name'] = request.form.get('name', default=None, type=str)
    updated_user['email'] = request.form.get('email', default=None, type=str)
    users = json.loads(request.cookies.get('users', json.dumps([])))
    user = next((user for user in users if user['id'] == id))

    if errors:=validate(updated_user):
        return render_template(
            'users/edit.html',
            errors=errors,
            user=updated_user,
            form_destination=url_for('patch_user',id=id)
        ), 422
    else:
        user['name'] = updated_user['name']
        user['email'] = updated_user['email']

        encoded_users = json.dumps(users)

        response = make_response(redirect(url_for('get_user',id=id), code=302))
        response.set_cookie('users', encoded_users)

        flash('User was updated successfully', 'success')

        return response


@app.route('/users/<int:id>/delete', methods=['POST'])
def delete_user(id):
    users = json.loads(request.cookies.get('users', json.dumps([])))
    users = [user for user in users if user['id'] != id]
    encoded_users = json.dumps(users)

    response = make_response(redirect(url_for('get_users',id=id), code=302))
    response.set_cookie('users', encoded_users)

    flash('User has been deleted', 'success')
    return response
