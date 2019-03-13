from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Data_Setup import Base, GadgetCompanyName, GadgetName, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///Gadget.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Gadget Store"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
tb_Gadget = session.query(GadgetCompanyName).all()


# login
@app.route('/login')
def showLogin():

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    tb_Gadget = session.query(GadgetCompanyName).all()
    Gds = session.query(GadgetName).all()
    return render_template('login.html',
                           STATE=state, tb_Gadget=tb_Gadget, Gds=Gds)
    # return render_template('myhome.html', STATE=state
    # tbs_cat=tbs_cat,tbes=tbes)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    U1 = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(U1)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

#####
# Home


@app.route('/')
@app.route('/home')
def home():
    tb_Gadget = session.query(GadgetCompanyName).all()
    return render_template('myhome.html', tb_Gadget=tb_Gadget)

#####
# Gadget Category for admins


@app.route('/GadgetStore')
def GadgetStore():
    try:
        if login_session['username']:
            name = login_session['username']
            tb_Gadget = session.query(GadgetCompanyName).all()
            tb = session.query(GadgetCompanyName).all()
            Gds = session.query(GadgetName).all()
            return render_template('myhome.html', tb_Gadget=tb_Gadget,
                                   tb=tb, Gds=Gds, uname=name)
    except:
        return redirect(url_for('showLogin'))

######
# Showing Gadget based on Gadget category


@app.route('/GadgetStore/<int:Gdid>/AllCompanys')
def showGadget(Gdid):
    tb_Gadget = session.query(GadgetCompanyName).all()
    tb = session.query(GadgetCompanyName).filter_by(id=Gdid).one()
    Gds = session.query(GadgetName).filter_by(Gadgetcompanynameid=Gdid).all()
    try:
        if login_session['username']:
            return render_template('showGadget.html', tb_Gadget=tb_Gadget,
                                   tb=tb, Gds=Gds,
                                   uname=login_session['username'])
    except:
        return render_template('showGadget.html',
                               tb_Gadget=tb_Gadget, tb=tb, Gds=Gds)

#####
# Add New Gadget


@app.route('/GadgetStore/addGadgetCompany', methods=['POST', 'GET'])
def addGadgetCompany():
    if request.method == 'POST':
        company = GadgetCompanyName(name=request.form['name'],
                                    user_id=login_session['user_id'])
        session.add(company)
        session.commit()
        return redirect(url_for('GadgetStore'))
    else:
        return render_template('addGadgetCompany.html', tb_Gadget=tb_Gadget)

########
# Edit Gadget Category


@app.route('/GadgetStore/<int:Gdid>/edit', methods=['POST', 'GET'])
def editGadgetCategory(Gdid):
    editGadget = session.query(GadgetCompanyName).filter_by(id=Gdid).one()
    creator = getUserInfo(editGadget.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this Gadget Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('GadgetStore'))
    if request.method == "POST":
        if request.form['name']:
            editGadget.name = request.form['name']
        session.add(editGadget)
        session.commit()
        flash("Gadget Category Edited Successfully")
        return redirect(url_for('GadgetStore'))
    else:
        # tbs_cat is global variable we can them in entire application
        return render_template('editGadgetCategory.html',
                               Gd=editGadget, tb_Gadget=tb_Gadget)

######
# Delete Gadget Category


@app.route('/GadgetStore/<int:Gdid>/delete', methods=['POST', 'GET'])
def deleteGadgetCategory(Gdid):
    Gd = session.query(GadgetCompanyName).filter_by(id=Gdid).one()
    creator = getUserInfo(Gd.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this Gadget Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('GadgetStore'))
    if request.method == "POST":
        session.delete(Gd)
        session.commit()
        flash("Gadget Category Deleted Successfully")
        return redirect(url_for('GadgetStore'))
    else:
        return render_template('deleteGadgetCategory.html',
                               Gd=Gd, tb_Gadget=tb_Gadget)

######
# Add New Gadget Name Details


@app.route('/GadgetStore/addCompany/addGadgetDetails/<string:Gdname>/add',
           methods=['GET', 'POST'])
def addGadgetDetails(Gdname):
    tb = session.query(GadgetCompanyName).filter_by(name=Gdname).one()
    # See if the logged in user is not the owner of Gadget
    creator = getUserInfo(tb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't add new Gadget edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showGadget', Gdid=tb.id))
    if request.method == 'POST':
        name = request.form['name']
        color = request.form['color']
        price = request.form['price']
        Gadgettype = request.form['Gadgettype']
        Gadgetdetails = GadgetName(name=name,
                                   color=color,
                                   price=price,
                                   Gadgettype=Gadgettype,
                                   date=datetime.datetime.now(),
                                   Gadgetcompanynameid=tb.id,
                                   user_id=login_session['user_id'])
        session.add(Gadgetdetails)
        session.commit()
        return redirect(url_for('showGadget', Gdid=tb.id))
    else:
        return render_template('addGadgetDetails.html',
                               Gdname=tb.name, tb_Gadget=tb_Gadget)

######
# Edit Gadget details


@app.route('/GadgetStore/<int:Gdid>/<string:Gdsname>/edit',
           methods=['GET', 'POST'])
def editGadget(Gdid, Gdsname):
    Gd = session.query(GadgetCompanyName).filter_by(id=Gdid).one()
    Gadgetdetails = session.query(GadgetName).filter_by(name=Gdsname).one()
    # See if the logged in user is not the owner of Gadget
    creator = getUserInfo(Gd.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't edit this Gadget edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showGadget', Gdid=Gd.id))
    # POST methods
    if request.method == 'POST':
        Gadgetdetails.name = request.form['name']
        Gadgetdetails.color = request.form['color']
        Gadgetdetails.price = request.form['price']
        Gadgetdetails.Gadgettype = request.form['Gadgettype']
        Gadgetdetails.date = datetime.datetime.now()
        session.add(Gadgetdetails)
        session.commit()
        flash("Gadget Edited Successfully")
        return redirect(url_for('showGadget', Gdid=Gdid))
    else:
        return render_template('editGadget.html',
                               Gdid=Gdid, Gadgetdetails=Gadgetdetails,
                               tb_Gadget=tb_Gadget)

#####
# Delte Gadget Edit


@app.route('/GadgetStore/<int:Gdid>/<string:Gdsname>/delete',
           methods=['GET', 'POST'])
def deleteGadget(Gdid, Gdsname):
    Gd = session.query(GadgetCompanyName).filter_by(id=Gdid).one()
    Gadgetdetails = session.query(GadgetName).filter_by(name=Gdsname).one()
    # See if the logged in user is not the owner of Gadget
    creator = getUserInfo(Gd.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't delete this Gadget edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showGadget', Gdid=Gd.id))
    if request.method == "POST":
        session.delete(Gadgetdetails)
        session.commit()
        flash("Deleted Gadget Successfully")
        return redirect(url_for('showGadget', Gdid=Gd.id))
    else:
        return render_template('deleteGadget.html',
                               Gdid=Gdid, Gadgetdetails=Gadgetdetails,
                               tb_Gadget=tb_Gadget)

####
# Logout from current user


@app.route('/logout')
def logout():
    access_token = login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type':
                           'application/x-www-form-urlencoded'})[0]

    print (result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps
                                 ('Successfully disconnected user..'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#####
# Json


@app.route('/GadgetStore/JSON')
def allGadgetJSON():
    Gadgetcategories = session.query(GadgetCompanyName).all()
    category_dict = [c.serialize for c in Gadgetcategories]
    for c in range(len(category_dict)):
        Gadget = [i.serialize for i in session.query(GadgetName).
                  filter_by(Gadgetcompanynameid=category_dict[c]["id"]).all()]
        if Gadget:
            category_dict[c]["Gadget"] = Gadget
    return jsonify(GadgetCompanyName=category_dict)

####


@app.route('/GadgetStore/GadgetCategories/JSON')
def categoriesJSON():
    Gadget = session.query(GadgetCompanyName).all()
    return jsonify(GadgetCategories=[c.serialize for c in Gadget])

####


@app.route('/GadgetStore/Gadget/JSON')
def itemsJSON():
    items = session.query(GadgetName).all()
    return jsonify(Gadget=[i.serialize for i in items])

#####


@app.route('/GadgetStore/<path:Gadget_name>/Gadget/JSON')
def categoryItemsJSON(Gadget_name):
    GadgetCategory = session.query(GadgetCompanyName).filter_by(
        name=Gadget_name).one()
    Gadget = session.query(GadgetName).filter_by(
        Gadgetcompanyname=GadgetCategory).all()
    return jsonify(GadgetEdtion=[i.serialize for i in Gadget])

#####


@app.route('/GadgetStore/<path:Gadget_name>/<path:edition_name>/JSON')
def ItemJSON(Gadget_name, edition_name):
    GadgetCategory = session.query
    (GadgetCompanyName).filter_by(name=Gadget_name).one()
    GadgetEdition = session.query(GadgetName).filter_by(
           name=edition_name, Gadgetcompanyname=GadgetCategory).one()
    return jsonify(GadgetEdition=[GadgetEdition.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=5555)
