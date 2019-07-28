from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from database_setup import Base, Category, Item
import json
import requests

NO_RESPONSE = ''

app = Flask(__name__)
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# This is the function used to verify authorization from google id_token
def verify_id_token(request):
    if not request.cookies:
        return False, None

    if 'id_token' not in request.cookies:
        return False, None

    id_token = request.cookies['id_token']
    response = requests.get(
        'https://oauth2.googleapis.com/tokeninfo?id_token=%s' % id_token
        )
    return id_token if response.status_code == 200 else None


'''
Below are a series of standard flask routes.
Variables defined are usually SQL queries, which are then passed
into the render template page for use with SQLAlchemy to order
some CRUD on, which then passes to the appropriate route/method
such as edit, delete, and new to perform it

Instances of if user_id check to see if user has permission
to perform operations on the item. If not, operation is aborted.

user_id is created with the verify_id function above in each instance
'''


@app.route('/')
@app.route('/catalog/')
def showCategories():
    categories = session.query(Category).all()
    return render_template('catalog.html', categories=categories)


@app.route('/catalog/JSON/')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])


@app.route('/catalog/<int:category_id>/')
@app.route('/catalog/<int:category_id>/items/')
def showItems(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template('items.html', category=category, items=items)


@app.route('/catalog/<int:category_id>/items/JSON/')
def itemsJSON(category_id):
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalog/<int:category_id>/items/<int:item_id>/')
def showItem(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('item.html', item=item)


@app.route('/catalog/<int:category_id>/items/<int:item_id>/JSON/')
def itemJSON(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=[item.serialize])


@app.route('/catalog/<int:category_id>/item/new/', methods=['GET', 'POST'])
def newItem(category_id):
    category = session.query(Category).filter_by(id=category_id).one()

    if request.method == 'POST':
        user_id = verify_id_token(request)

        if user_id is None:
            abort(401)

        if not user_id:
            abort(401)

        newItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            category_id=category_id
            )
        newItem.user_id = user_id
        session.add(newItem)
        session.commit()
        return redirect(url_for('showItems', category_id=category_id))

    else:
        user_id = verify_id_token(request)

        if user_id is None:
            abort(401)

        if not user_id:
            abort(401)
        return render_template('newItem.html', category=category)


@app.route('/catalog/<int:category_id>/items/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    itemToEdit = session.query(Item).filter_by(id=item_id).one()

    if request.method == 'POST':

        user_id = verify_id_token(request)

        if user_id is None:
            return redirect(url_for('loginPage'))
        if user_id != itemToEdit.user_id:
            abort(401)

        if request.form['name'] != '':
            itemToEdit.name = request.form['name']
        if request.form['description'] != '':
            itemToEdit.description = request.form['description']
        session.add(itemToEdit)
        session.commit()
        return redirect(url_for('showItems',
                                category_id=itemToEdit.category_id))

    else:
        user_id = verify_id_token(request)

        if user_id is None:
            return redirect(url_for('loginPage'))
        if user_id != itemToEdit.user_id:
            abort(401)

        return render_template('editItem.html', item=itemToEdit)


@app.route('/catalog/<int:category_id>/items/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    itemToDelete = session.query(Item).filter_by(id=item_id).one()

    if request.method == 'POST':
        user_id = verify_id_token(request)

        if user_id is None:
            return redirect(url_for('loginPage'))
        if user_id != itemToDelete.user_id:
            abort(401)
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showItems', category_id=category_id))

    else:
        user_id = verify_id_token(request)

        if user_id is None:
            return redirect(url_for('loginPage'))
        if user_id != itemToDelete.user_id:
            abort(401)
        return render_template('deleteItem.html', item=itemToDelete)


@app.route('/login', methods=['GET', 'POST'])
def loginPage():
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        data = json.loads(request.data)
        print (data['id'])
        print (data['email'])
        print (data['id_token'])
        print ('Successfully logged in %s: %s' % (data['email'],
                                                  data['id_token']))

        return NO_RESPONSE, 200


# The signout page sets "id_token='", clearing it and removing authorization
@app.route('/logout', methods=['GET'])
def signoutPage():
    return render_template('signout.html')


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=5000)
