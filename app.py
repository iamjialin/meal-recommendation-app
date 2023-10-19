import os
import re
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from sqlalchemy import ForeignKey, desc
from ast import literal_eval
import datetime
import random
from operator import itemgetter

# set working path
basedir = os.path.abspath(os.path.dirname(__file__))

# flask app configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# session key
app.config['SECRET_KEY'] = os.urandom(24)
app.debug = True
app.permanent_session_lifetime = timedelta(minutes=30)
db = SQLAlchemy(app)


# Database model
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False)
    user_name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    state = db.Column(db.Integer, nullable=False, default=0)
    admin = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"Email : {self.email}, Password:{self.password}"


class PersonalDetail(db.Model):
    __tablename__ = 'persondetail'
    id = db.Column(db.String(80), ForeignKey('user.id'), primary_key=True)
    Published_meals = db.Column(db.String(100), nullable=True, default='[]')
    favourite_meals = db.Column(db.String(100), nullable=True, default='[]')
    favourite_contributors = db.Column(db.String(100), nullable=True, default='[]')  # 存的名字
    rated_meals = db.Column(db.String(100), nullable=True)
    badge_list = db.Column(db.String(100), nullable=True)
    weekly_recipe = db.Column(db.String(100), nullable=True)
    last_modify = db.Column(db.String(100), nullable=True)


class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    comment_recipe = db.Column(db.Integer, nullable=False)
    comment_user = db.Column(db.Integer, nullable=False)
    comment_time = db.Column(db.String(80), nullable=False)
    comment_c = db.Column(db.String(80), nullable=False)


class Recipe(db.Model):
    __tablename__ = 'recipe'
    recipe_id = db.Column(db.Integer, primary_key=True)
    contributor_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    recipe_name = db.Column(db.String(80), nullable=False)
    recipe_detail = db.Column(db.String(80), nullable=False)
    ingredients = db.Column(db.String(100), nullable=False)
    recipe_tags = db.Column(db.String(100), nullable=True)
    recipe_img_name = db.Column(db.String(100), nullable=True)
    recipe_likes = db.Column(db.Integer, nullable=True)
    recipe_ratings = db.Column(db.Float, nullable=True)
    rated_numbers = db.Column(db.Integer, nullable=True)
    recipe_comments = db.Column(db.String(100), nullable=True)
    recipe_type = db.Column(db.String(100), nullable=True)
    recipe_method = db.Column(db.String(100), nullable=True)
    ingredients_num = db.Column(db.String(100), nullable=True)
    recipe_upload_time = db.Column(db.String(100), nullable=True)
    like_user = db.Column(db.String(100), nullable=True)


class Ingredient(db.Model):
    __tablename__ = 'ingredient'
    ingredient_name = db.Column(db.String(80), primary_key=True)
    recipe_list = db.Column(db.String(100), nullable=True)


class Badge(db.Model):
    __tablename__ = 'badge'
    badge_id = db.Column(db.Integer, primary_key=True)
    badge_detail = db.Column(db.String(100), nullable=False)
    badge_name = db.Column(db.String(100), nullable=False)
    badge_img = db.Column(db.String(100), nullable=False)


# each recipe card
def recipe_card(user_email, type):
    if type == 'recommended':
        recipe_dict = {
            'head_img': 'head_img/John Snow.png',
            'recipe_img': 'Food Images/yellow-squash-and-mozzarella-quiche-with-fresh-thyme-230610.jpg',
            'recipe_name': 'Yellow Squash and Mozzarell Aquiche with Fresh Thyme',
            'last_update': '3 days',
            'chef_name': 'John Snow'
        }
        return recipe_dict
    elif type == 'rated':
        recipe_dict = {
            'head_img': 'head_img/John Snow.png',
            'recipe_img': 'Food Images/yellow-squash-and-mozzarella-quiche-with-fresh-thyme-230610.jpg',
            'recipe_name': 'Yellow Squash and Mozzarell Aquiche with Fresh Thyme',
            'last_update': '3 days',
            'rating': 4.5,
            'chef_name': 'John Snow'
        }
        return recipe_dict


# string processing
def res(l):
    l = l.replace("['", '')
    l = l.replace("']", '')
    l = l.split("', '")
    for i in range(len(l)):
        l[i] = l[i].strip()
    return l


# comment method
def comment(recipe_id, num):
    comment = Comment.query.filter_by(comment_recipe=recipe_id).all()
    comments = []
    # check if recipe_id is uploaded by user
    if recipe_id > 520:
        comments = []
    else:
        for item in comment:
            c = dict()
            c['user_id'] = str(item.comment_user)
            if len(User.query.filter_by(id=item.comment_user).all()) > 0:
                c['user_name'] = User.query.filter_by(id=item.comment_user).all()[0].user_name
                c['comment_time'] = item.comment_time
                c['comment_c'] = item.comment_c
                comments.append(c)
        comments = comments[:num]
    return comments


# Earn badge by like recipes
def badge_likes(user_id, r_type):
    ## likes 5/20/50
    person = PersonalDetail.query.filter_by(id=user_id).all()[0]
    if r_type == 'dessert':
        badge_name = 'dessert_lv'
    elif r_type == 'meat':
        badge_name = 'meat_lv'
    elif r_type == 'veg':
        badge_name = 'veg_lv'
    else:
        return 0

    count = 0
    for r_id in literal_eval(person.favourite_meals):
        recipe = Recipe.query.filter_by(recipe_id=r_id).all()[0]
        if recipe.recipe_type == r_type:
            count += 1
    if count >= 50:
        update = [1, 2, 3]
    elif 50 > count >= 20:
        update = [1, 2]
    elif 20 > count >= 5:
        update = [1]
    else:
        update = None

    if update is not None:
        if person.badge_list is not None:
            badge_list = literal_eval(person.badge_list)
        else:
            badge_list = []

        for item in update:
            badge_name = badge_name + str(item)
            badge_id = Badge.query.filter_by(badge_name=badge_name).all()[0].badge_id
            if badge_id not in badge_list:
                badge_list.append(badge_id)
        PersonalDetail.query.filter_by(id=user_id).update({'badge_list': str(badge_list)})
        db.session.commit()
    return 1

# Earn badge by upload recipes
def badge_upload(user_id):
    person = PersonalDetail.query.filter_by(id=user_id).all()[0]
    upload_list = literal_eval(person.Published_meals)
    badge_name = 'upload_lv'
    len_ = len(upload_list)
    if len_ >= 50:
        update = [1, 2, 3]
    elif 50 > len_ >= 30:
        update = [1, 2]
    elif 30 > len_ >= 10:
        update = [1]
    else:
        update = None

    if update is not None:
        if person.badge_list is not None:
            badge_list = literal_eval(person.badge_list)
        else:
            badge_list = []

        for item in update:
            badge_name = badge_name + str(item)
            badge_id = Badge.query.filter_by(badge_name=badge_name).all()[0].badge_id
            if badge_id not in badge_list:
                badge_list.append(badge_id)
        PersonalDetail.query.filter_by(id=user_id).update({'badge_list': str(badge_list)})
        db.session.commit()

# earn badge by receive low rates from uploaded recipes
def badge_shit(user_id):
    person = PersonalDetail.query.filter_by(id=user_id).all()[0]
    upload_list = literal_eval(person.Published_meals)
    badge_name = 'shit_meal'
    badge_id = Badge.query.filter_by(badge_name=badge_name).all()[0].badge_id
    if len(upload_list) >= 10:
        rate = 0
        for item in upload_list:
            recipe = Recipe.query.filter_by(recipe_id=item).all()[0]
            rate += recipe.recipe_ratings
        avg_rate = rate / len(upload_list)
        if avg_rate <= 2:
            if person.badge_list is not None:
                badge_list = literal_eval(person.badge_list)
                if badge_id not in badge_list:
                    badge_list.append(badge_id)
            else:
                badge_list = [badge_id]
            PersonalDetail.query.filter_by(id=user_id).update({'badge_list': str(badge_list)})
            db.session.commit()


def badge(user_id, recipe_id, func):
    if recipe_id is not None:
        if func == 'likes':
            recipe_type = Recipe.query.filter_by(recipe_id=recipe_id).all()[0].recipe_type
            a = badge_likes(user_id, recipe_type)
    else:
        if func == 'upload':
            badge_upload(user_id)
        elif func == 'badge_page':
            badge_shit(user_id)


# recipe recommendation
def recipe_recom(name, num):
    recipe = Recipe.query.filter_by(recipe_name=name).all()[0]
    # recipe database format ['ingredient_1,ingredient_2,ingredient_3,...']
    ingredients = res(recipe.ingredients)
    recipe_sim = dict()
    for item in ingredients:
        ing = Ingredient.query.filter_by(ingredient_name=item).all()[0]
        # ingredient database format ['recipe_1,recipe_2,recipe_3,...']
        recipe_item = eval(ing.recipe_list)
        for j in recipe_item:
            if j in recipe_sim.keys():
                recipe_sim[j] += 1
            else:
                recipe_sim[j] = 1
    order = sorted(recipe_sim.items(), key=lambda x: x[1], reverse=True)

    order_l = []
    if len(order) < (num + 2):
        num = len(order) - 2
    for i in range(num + 2):
        if order[i][0] != name:
            order_l.append(order[i][0])

    # order_l first n similar recipes
    return order_l


def change_fav(id):
    person = PersonalDetail.query.filter_by(id = id).all()[0]
    fav_meal = eval(person.favourite_meals)

    for meal in fav_meal.copy():
        try:
            Recipe.query.filter_by(recipe_id=meal).all()[0]
        except:
            fav_meal.remove(meal)
    PersonalDetail.query.filter_by(id=id).update({'favourite_meals': str(fav_meal)})
    db.session.commit()
# Homepage
@app.route('/', methods=("GET", "POST"))
def home_page():
    if session.get('email') == None:
        sign_in_info = {"state": "sign in"}
    else:
        sign_in_info = {"state": "sign out", "admin": session.get('admin')}
        change_fav(session.get('id'))
    if request.method == "POST":
        search_by_name = request.form.get("Search_by_name")
        if search_by_name != "":
            result_by_name = Recipe.query.filter(
                Recipe.recipe_name.like('%{keyword}%'.format(keyword=search_by_name))).all()
            if len(result_by_name) == 0:
                result_by_name = 'cannot find'
                return render_template('search_result.html', recipe_list={}, sign_in_info=sign_in_info)
            search_by_name = ""
            result = {}
            for recipe in result_by_name:
                user_name = User.query.filter_by(id=recipe.contributor_id).all()[0].user_name
                result[recipe.recipe_name] = {'recipe_img': recipe.recipe_img_name, 'id': str(recipe.contributor_id),
                                              'rating': recipe.recipe_ratings, 'contributor_name': user_name}
            return render_template('search_result.html', recipe_list=result, sign_in_info=sign_in_info)

        search_by_other = request.form.get("Search_by_other")
        if search_by_other != "":
            result_by_other = set()
            search_by_other_list = search_by_other.split("; ")
            for item in search_by_other_list[:-1]:
                temp_result = Ingredient.query.filter_by(ingredient_name=item).all()[0].recipe_list
                temp_result = set(literal_eval(temp_result))
                if result_by_other != set():
                    result_by_other = result_by_other.intersection(temp_result)
                else:
                    result_by_other = temp_result
            search_by_other = ""
            result_by_other = [Recipe.query.filter_by(recipe_name=recipe).all()[0] for recipe in result_by_other]
            result = {}
            for recipe in result_by_other:
                user_name = User.query.filter_by(id=recipe.contributor_id).all()[0].user_name
                result[recipe.recipe_name] = {'recipe_img': recipe.recipe_img_name, 'id': str(recipe.contributor_id),
                                              'rating': recipe.recipe_ratings, 'contributor_name': user_name}
            return render_template('search_result.html', recipe_list=result, sign_in_info=sign_in_info)
    if session.get('id') == None:
        sign_in_info = {"state": "sign in"}
        recipe_rated = Recipe.query.order_by(Recipe.recipe_ratings.desc()).all()[:6]

        result = {}
        for recipe in recipe_rated:
            user_name = User.query.filter_by(id=recipe.contributor_id).all()[0].user_name
            result[recipe.recipe_name] = {'recipe_img': recipe.recipe_img_name, 'id': str(recipe.contributor_id),
                                          'rating': recipe.recipe_ratings, 'contributor_name': user_name}
        return render_template('home_page.html', sign_in_info=sign_in_info, recipe_rated=result,
                               recipe_recommended=None)
    else:
        sign_in_info = {"state": "sign out", 'admin': session.get('admin')}
        favo_meals = eval(PersonalDetail.query.filter_by(id=session.get('id')).all()[0].favourite_meals)
        length = len(favo_meals)
        if length > 1:
            favo_name = [Recipe.query.filter_by(recipe_id=meal).all()[0].recipe_name for meal in favo_meals]
            refer = [favo_name[random.randint(0, length - 1)] for i in range(2)]
            recommend_1 = recipe_recom(refer[0], 5)
            recommend_2 = recipe_recom(refer[1], 5)
            recommend = set(recommend_1 + recommend_2)
            recommend = list(recommend)[0:6]
            result = {}
            recommend = [Recipe.query.filter_by(recipe_name=recipe).all()[0] for recipe in recommend]
            for recipe in recommend:
                user_name = User.query.filter_by(id=recipe.contributor_id).all()[0].user_name
                result[recipe.recipe_name] = {'recipe_img': recipe.recipe_img_name, 'id': str(recipe.contributor_id),
                                              'rating': recipe.recipe_ratings, 'contributor_name': user_name}
        else:
            result = None
        recipe_rated = Recipe.query.order_by(Recipe.recipe_ratings.desc()).all()[:6]
        result_rated = {}
        for recipe in recipe_rated:
            user_name = User.query.filter_by(id=recipe.contributor_id).all()[0].user_name
            result_rated[recipe.recipe_name] = {'recipe_img': recipe.recipe_img_name, 'id': str(recipe.contributor_id),
                                                'rating': recipe.recipe_ratings, 'contributor_name': user_name}
        return render_template('home_page.html', sign_in_info=sign_in_info, recipe_recommended=result,
                               recipe_rated=result_rated)


# password strength checker
def password_check(password):
    '''
    A password should be at least 6 character, 1 letter or more, 1 digit or more
    '''

    length_checker = len(password) > 5
    letter_checker = re.search(r"[a-zA-Z]", password)
    digit_checker = re.search(r"\d", password)
    password_ok = all([length_checker, letter_checker, digit_checker])
    return password_ok


# sign in page
@app.route("/sign_up/", methods=("GET", "POST"))
def sign_up():
    if request.method == "POST":
        form_data = request.form.to_dict(flat=False)
        email_address = form_data['email'][0]
        password = form_data['password'][0]
        confirm_password = form_data['confirm_password'][0]
        username = form_data['username'][0]
        if password == confirm_password:
            # if user input email
            if len(email_address) == 0:
                return 'Please input your email address'
            elif len(password) == 0:
                return 'Please input your password'

            elif len(username) == 0:
                return 'Please input your username'
            elif not password_check(password):
                return 'A password should be at least 6 character, 1 letter or more, 1 digit or more'
            else:
                user = User.query.filter_by(email=email_address).all()
                if len(user) == 0:
                    new_user = User(email=email_address, password=password, user_name=username)
                    db.session.add(new_user)
                    db.session.commit()
                    user_id = User.query.filter_by(email=email_address).all()[0].id
                    new_person = PersonalDetail(id=user_id)
                    db.session.add(new_person)
                    db.session.commit()
                else:
                    return 'User name already exists'
            return redirect(url_for('sign_in'))
        else:
            return 'Please confirm your password'

    return render_template('sign_up.html')


# Sign in Page
@app.route("/sign_in/", methods=("GET", "POST"))
def sign_in():
    if session.get('email') != None:
        User.query.filter_by(email=session.get('email')).update({'state': 0})
        db.session.commit()
        session.clear()
        return redirect(url_for("home_page"))
    if request.method == "POST":
        form_data = request.form.to_dict(flat=False)
        email_address = form_data['email'][0]
        password = form_data['password'][0]
        user = User.query.filter_by(email=email_address).all()
        if len(user) == 0:
            return 'wrong username, please sign up first'
        else:
            user = user[0]
            if user.password == password and password != '':
                if user.email == session.get('email') or user.state == 1:
                    return 'already login'
                else:
                    session['email'] = user.email
                    session['id'] = user.id
                    session['admin'] = user.admin
                    User.query.filter_by(email=session.get('email')).update({'state': 1})
                    db.session.commit()
                    session.permanent = True
                    return redirect(url_for('home_page'))
                # return redirect(url_for('home_page'))
            else:
                return 'wrong password, try again later'
    return render_template('sign_in.html')


@app.route("/Recipe_details/<string:name>", methods=("GET", "POST"))
def Recipe_details(name):
    recipe_name = name
    recipe_detail = Recipe.query.filter_by(recipe_name=recipe_name).all()[0]
    liked_img = "unliked.png"
    comment_list = comment(recipe_id=recipe_detail.recipe_id, num=10)
    order = recipe_recom(name=recipe_name, num=3)
    food_img = [Recipe.query.filter_by(recipe_name=name).all()[0].recipe_img_name for name in order]
    order_dict = dict(zip(order, food_img))
    if session.get('email') == None:
        sign_in_info = {"state": "sign in"}
    else:
        sign_in_info = {"state": "sign out", "admin": session.get('admin')}
        if recipe_detail.recipe_id in eval(
                PersonalDetail.query.filter_by(id=session.get('id')).all()[0].favourite_meals):
            liked_img = "liked.png"
        else:
            liked_img = "unliked.png"
    rating = recipe_detail.recipe_ratings
    rating_list = ['unstarred.png', 'unstarred.png', 'unstarred.png', 'unstarred.png', 'unstarred.png']
    rating_list[0:int(rating)] = ['starred.png' for i in range(0, round(rating))]
    contributor_id = recipe_detail.contributor_id
    contributor_name = User.query.filter_by(id=contributor_id).all()[0].user_name

    return render_template('Recipe_details.html', sign_in_info=sign_in_info, recipe_name=recipe_detail.recipe_name,
                           recipe_img_name=recipe_detail.recipe_img_name, recipe_detail=recipe_detail.recipe_detail,
                           ingredients=eval(recipe_detail.ingredients), method=recipe_detail.recipe_detail,
                           number_like=recipe_detail.recipe_likes, liked_img=liked_img, rating_list=rating_list,
                           rate=rating, comment_list=comment_list, order_dict=order_dict,
                           contributor_id=str(contributor_id), contributor_name=contributor_name,
                           meal_type=recipe_detail.recipe_type)


@app.route('/like_function/', methods=['POST'])
def like_function():
    if session.get('email') == None:
        return "Not logged"
    else:
        if request.method == "POST":
            recipe_name = request.get_json()
            recipe = Recipe.query.filter_by(recipe_name=recipe_name).all()[0]
            fav_meals = eval(PersonalDetail.query.filter_by(id=session.get('id')).all()[0].favourite_meals)
            if recipe.recipe_id in fav_meals:
                recipe.recipe_likes -= 1
                fav_meals.remove(recipe.recipe_id)
                PersonalDetail.query.filter_by(id=session.get('id')).update({'favourite_meals': str(fav_meals)})
                Recipe.query.filter_by(recipe_name=recipe_name).update({'recipe_likes': recipe.recipe_likes})
                db.session.commit()
                badge(user_id=session.get('id'), recipe_id=recipe.recipe_id, func='likes')
                return "Existed"
            else:
                recipe.recipe_likes += 1
                fav_meals.append(recipe.recipe_id)
                PersonalDetail.query.filter_by(id=session.get('id')).update({'favourite_meals': str(fav_meals)})
                like_user = eval(recipe.like_user)
                like_user.append(session.get('id'))
                Recipe.query.filter_by(recipe_name=recipe_name).update(
                    {'recipe_likes': recipe.recipe_likes, 'like_user': str(like_user)})
                db.session.commit()
                badge(user_id=session.get('id'), recipe_id=recipe.recipe_id, func='likes')
                return str(recipe.recipe_likes)
    return "100"


@app.route('/add_week_function/', methods=['POST'])
def add_week_function():
    if session.get('email') == None:
        return "Not logged"
    else:
        if request.method == "POST":
            recipe_name = request.get_json()
            recipe = Recipe.query.filter_by(recipe_name=recipe_name).all()[0]
            user = User.query.filter_by(email=session.get('email')).all()[0]
            person = PersonalDetail.query.filter_by(id=user.id).all()[0]
            wkl_list = person.weekly_recipe
            if wkl_list is None:
                wkl_list = [recipe.recipe_id]
            else:
                wkl_list = literal_eval(wkl_list)
                if recipe.recipe_id in wkl_list:
                    return 'already exist'
                else:
                    wkl_list.append(recipe.recipe_id)
            PersonalDetail.query.filter_by(id=user.id).update({'weekly_recipe': str(wkl_list)})
            db.session.commit()

    return "100"


@app.route('/rating_function/', methods=['POST'])
def rating_function():
    if session.get('email') == None:
        return "Not logged"
    else:
        if request.method == "POST":
            info = request.get_json()
            rating = int(info[:1])
            recipe_name = info[1:]
            recipe = Recipe.query.filter_by(recipe_name=recipe_name).all()[0]
            rated_meals = PersonalDetail.query.filter_by(id=session.get('id')).all()[0].rated_meals
            if rated_meals:
                rated_meals = eval(rated_meals)
            else:
                rated_meals = []
            if recipe.recipe_id in rated_meals:
                return "Rated"
            else:
                rated_meals.append(recipe.recipe_id)
                rated_number = recipe.rated_numbers
                total_rating = rated_number * recipe.recipe_ratings
                rated_number += 1
                new_rating = round((total_rating + rating) / rated_number, 2)
                PersonalDetail.query.filter_by(id=session.get('id')).update({'rated_meals': str(rated_meals)})
                Recipe.query.filter_by(recipe_name=recipe_name).update(
                    {'rated_numbers': rated_number, 'recipe_ratings': new_rating})
                db.session.commit()
                return str(new_rating)


@app.route('/comment_function/', methods=['POST'])
def comment_function():
    if session.get('email') == None:
        return "Not logged"
    else:
        if request.method == "POST":
            comment_dict = request.get_json()
            recipe_name = comment_dict['recipe_name']
            comment = comment_dict['comment']
            recipe = Recipe.query.filter_by(recipe_name=recipe_name).all()[0]

            time = str(datetime.datetime.now().year) + '.' + str(datetime.datetime.now().month) + '.' + str(
                datetime.datetime.now().day)
            new_comment = Comment(comment_c=comment, comment_time=time, comment_user=session.get('id'),
                                  comment_recipe=recipe.recipe_id)

            db.session.add(new_comment)
            db.session.commit()
            return "success"


@app.route("/Personal_profile/", methods=("GET", "POST"))
def Personal_profile():
    if session.get('email') == None:
        return redirect(url_for('sign_in'))
    else:
        change_fav(session.get('id'))
        sign_in_info = {"state": "sign out", "admin": session.get('admin')}
    user = User.query.filter_by(email=session.get('email')).all()[0]
    # get user_img and user name
    user_img = user.id
    user_name = user.user_name

    person = PersonalDetail.query.filter_by(id=user.id).all()[0]

    if person.Published_meals is not None:
        published_meals = [(meal.recipe_name, meal.recipe_img_name) for meal in
                           [Recipe.query.filter_by(recipe_id=int(id)).all()[0] for id in eval(person.Published_meals)]]
    else:
        published_meals = []

    if person.favourite_meals is not None:
        favourite_meals = [(meal.recipe_name, meal.recipe_img_name) for meal in
                           [Recipe.query.filter_by(recipe_id=int(id)).all()[0] for id in eval(person.favourite_meals)]]
    else:
        favourite_meals = []

    if person.favourite_contributors is not None:
        favourite_contributor = [(user.user_name, str(user.id)) for user in
                                 [User.query.filter_by(id=int(id)).all()[0] for id in
                                  eval(person.favourite_contributors)]]

    else:
        favourite_contributor = []

    if person.badge_list is not None:
        badge_list = [(badge.badge_name, badge.badge_img) for badge in
                      [Badge.query.filter_by(badge_id=int(id)).all()[0] for id in eval(person.badge_list)]]
    else:
        badge_list = []

    return render_template('personal_profile.html', sign_in_info=sign_in_info, user_img=str(user_img),
                           user_name=user_name,
                           user_badge='green_lover', published_meals=published_meals, favourite_meals=favourite_meals,
                           favourite_contributors=favourite_contributor, badge_list=badge_list)


@app.route("/Contributor_profile/<string:name>", methods=("GET", "POST"))
def Contributor_profile(name):
    if session.get('email') == None:
        sign_in_info = {"state": "sign in"}
    else:
        sign_in_info = {"state": "sign out", "admin": session.get('admin')}
    contributor = User.query.filter_by(user_name=name).all()[0]
    if session.get('id'):
        fav_contributor = PersonalDetail.query.filter_by(id=session.get('id')).all()[0].favourite_contributors

        fav_contributor = literal_eval(fav_contributor) if fav_contributor else []
        sub_status = "unsubscribe" if contributor.id in fav_contributor else "subscribe"

    else:
        sub_status = "subscribe"
    # get user_img and user name
    user_img = contributor.id
    user_name = contributor.user_name
    person = PersonalDetail.query.filter_by(id=contributor.id).all()[0]
    if person.badge_list is not None:
        badge_list = [(badge.badge_name, badge.badge_img) for badge in
                      [Badge.query.filter_by(badge_id=int(id)).all()[0] for id in eval(person.badge_list)]]
    else:
        badge_list = []
    published_meals = [(meal.recipe_name, meal.recipe_img_name) for meal in
                       [Recipe.query.filter_by(recipe_id=int(id)).all()[0] for id in eval(person.Published_meals)]]
    return render_template('Contributor_profile.html', sign_in_info=sign_in_info, user_img=str(user_img),
                           user_name=user_name, user_badge='green_lover', published_meals=published_meals,
                           subscribe=sub_status, badge_list=badge_list)


@app.route('/add_contributor_function/', methods=['POST'])
def add_contributor():
    if session.get('email') == None:
        return "Not logged"
    else:
        status = ''
        if request.method == "POST":
            contributor_name = request.get_json()
            contributor_id = User.query.filter_by(user_name=contributor_name).all()[0].id
            user = PersonalDetail.query.filter_by(id=session.get('id')).all()[0]
            if user.favourite_contributors is None:
                contributor_list = [contributor_id]
                status = '100'
            else:
                contributor_list = literal_eval(user.favourite_contributors)
                # check if user subscribed
                if contributor_id in contributor_list:
                    contributor_list.remove(contributor_id)
                    status = 'already subscribe'
                else:
                    contributor_list.append(contributor_id)
                    status = "100"
            PersonalDetail.query.filter_by(id=user.id).update({'favourite_contributors': str(contributor_list)})
            db.session.commit()
    return status


@app.route("/Weekly_recipe/", methods=("GET", "POST"))
def Weekly_recipe():
    if session.get('id') == None:
        return redirect(url_for('sign_in'))
    else:
        if session.get('email') == None:
            sign_in_info = {"state": "sign in"}
        else:
            sign_in_info = {"state": "sign out", "admin": session.get('admin')}
        user_id = session.get('id')
        person = PersonalDetail.query.filter_by(id=user_id).all()[0]
        if person.weekly_recipe is not None:
            weekly_recipe = person.weekly_recipe
            weekly_recipe = literal_eval(weekly_recipe)
            ing = dict()
            recipe_list = []
            for item in weekly_recipe:
                recipe_dict = dict()
                recipe = Recipe.query.filter_by(recipe_id=item).all()[0]
                recipe_dict['recipe_name'] = recipe.recipe_name
                recipe_dict['recipe_img_name'] = recipe.recipe_img_name
                recipe_dict['contributor_name'] = User.query.filter_by(id=recipe.contributor_id).all()[0].user_name
                recipe_dict['contributor_id'] = str(recipe.contributor_id)
                recipe_dict['last_updated'] = recipe.recipe_upload_time
                recipe_dict['likes'] = recipe.recipe_likes
                recipe_list.append(recipe_dict)
                # ing_num format：[[ing1_name, ing1_num],[ing2_name, ing2_num]]
                ing_list = literal_eval(recipe.ingredients_num)
                for i in ing_list:
                    if i[0] in ing.keys():
                        ing[i[0]] += i[1]
                    else:
                        ing[i[0]] = i[1]
        else:
            return 'No weekly recipe'
        return render_template('weekly_recipe.html', sign_in_info=sign_in_info, recipe_list=recipe_list,
                               ingredients=ing)


@app.route("/Badge_page/", methods=("GET", "POST"))
def Badge_page():
    if session.get('id') == None:
        return redirect(url_for('sign_in'))
    else:
        if session.get('email') == None:
            sign_in_info = {"state": "sign in"}
        else:
            sign_in_info = {"state": "sign out", "admin": session.get('admin')}
        user_id = session.get('id')
        user_name = User.query.filter_by(id=user_id).all()[0].user_name
        badge(user_id=user_id, recipe_id=None, func='badge_page')
        person = PersonalDetail.query.filter_by(id=user_id).all()[0]
        if person.badge_list is not None:
            badges = literal_eval(person.badge_list)
            badge_l = []
            unachieve_badge = list(set([str(i) for i in range(1, 14)]) - set(badges))
            for item in badges:
                details = dict()
                badge_i = Badge.query.filter_by(badge_id=item).all()[0]
                details['badge_name'] = badge_i.badge_name
                details['badge_detail'] = badge_i.badge_detail
                details['badge_img'] = badge_i.badge_img
                badge_l.append(details)

        else:
            badge_l = []
            unachieve_badge = [i for i in range(1, 14)]

        badge_un = []
        for item in unachieve_badge:
            details = dict()
            badge_i = Badge.query.filter_by(badge_id=item).all()[0]
            details['badge_name'] = badge_i.badge_name
            details['badge_detail'] = badge_i.badge_detail
            details['badge_img'] = badge_i.badge_img
            badge_un.append(details)
        return render_template('badge_page.html', sign_in_info=sign_in_info, badge_list=badge_l,
                               unachieve_badge=badge_un, user_img=str(user_id), user_name=user_name)


@app.route("/My_personal_news_feed/", methods=("GET", "POST"))
def My_personal_news_feed():
    if session.get('id') == None:
        return redirect(url_for('sign_in'))
    else:
        if session.get('email') == None:
            sign_in_info = {"state": "sign in"}
        else:
            sign_in_info = {"state": "sign out", "admin": session.get('admin')}
        user_id = session.get('id')
        person = PersonalDetail.query.filter_by(id=user_id).all()[0]
        if person.favourite_contributors is not None:
            fav_contributors = literal_eval(person.favourite_contributors)
            meal_l = []
            for item in fav_contributors:
                pub_meal = PersonalDetail.query.filter_by(id=item).all()[0].Published_meals
                pub_meal = literal_eval(pub_meal)
                for meal in pub_meal:
                    meal_dict = dict()
                    recipe = Recipe.query.filter_by(recipe_id=meal).all()[0]
                    meal_dict['recipe_name'] = recipe.recipe_name
                    meal_dict['recipe_img_name'] = recipe.recipe_img_name
                    time = datetime.datetime.strptime(recipe.recipe_upload_time, '%Y.%m.%d')
                    meal_dict['recipe_upload_time'] = time
                    meal_dict['contributor_name'] = User.query.filter_by(id=item).all()[0].user_name
                    meal_dict['contributor_id'] = str(item)
                    meal_dict['likes'] = recipe.recipe_likes
                    meal_l.append(meal_dict)
            meal_l_sort = sorted(meal_l, key=itemgetter('recipe_upload_time', 'likes'), reverse=1)


        else:
            return render_template('my_personal_newsfeed.html', sign_in_info=sign_in_info, recipe_list=None,
                                   unachived=None)
        return render_template('my_personal_newsfeed.html', sign_in_info=sign_in_info, recipe_list=meal_l_sort,
                               unachived=None)


@app.route("/recipe_manage/<string:pagenum>", methods=("GET", "POST"))
def recipe_manage(pagenum):
    if session.get('id') == None:
        return redirect(url_for('sign_in'))
    else:
        if session.get('email') == None:
            # check if admin
            sign_in_info = {"state": "sign in"}
        else:
            sign_in_info = {"state": "sign out", "admin": session.get('admin')}
        if request.method == "POST":
            link = "http://127.0.0.1:5000/recipe_manage/"
            search_by_name = request.form.get("Search_by_name")
            if search_by_name != "":
                recipe_list = Recipe.query.filter(
                    Recipe.recipe_name.like('%{keyword}%'.format(keyword=search_by_name))).all()
                search_by_name = ''
                if not recipe_list:
                    page = {'page_prev': "", 'page_num': str(1), 'page_next': link + str(int(pagenum) + 1)}
                    return render_template('recipe_manage.html', sign_in_info=sign_in_info, recipe_list=None, page=page)

                res_list = []
                for recipe in recipe_list:
                    recipe_dict = dict()
                    contributor_name = User.query.filter_by(id=recipe.contributor_id).all()[0].user_name
                    recipe_dict['recipe_name'] = recipe.recipe_name
                    recipe_dict['recipe_id'] = recipe.recipe_id
                    recipe_dict['upload_time'] = recipe.recipe_upload_time
                    recipe_dict['recipe_rating'] = recipe.recipe_ratings
                    recipe_dict['contributor'] = contributor_name
                    res_list.append(recipe_dict)
                return render_template('recipe_manage.html', sign_in_info=sign_in_info, recipe_list=res_list, page=None)
        else:
            recipe_list = Recipe.query.filter(Recipe.recipe_ratings < 4).all()
        res_list = []
        for recipe in recipe_list:
            recipe_dict = dict()
            contributor_name = User.query.filter_by(id=recipe.contributor_id).all()[0].user_name
            recipe_dict['recipe_name'] = recipe.recipe_name
            recipe_dict['recipe_id'] = recipe.recipe_id
            recipe_dict['upload_time'] = recipe.recipe_upload_time
            recipe_dict['recipe_rating'] = recipe.recipe_ratings
            recipe_dict['contributor'] = contributor_name
            res_list.append(recipe_dict)
        link = "http://127.0.0.1:5000/recipe_manage/"
        if int(pagenum) == 1:
            page = {'page_prev': "", 'page_num': pagenum, 'page_next': link + str(int(pagenum) + 1)}
        else:
            page = {'page_prev': "http://127.0.0.1:5000/recipe_manage/" + str(int(pagenum) - 1), 'page_num': pagenum,
                    'page_next': link + str(int(pagenum) + 1)}
        res_list = res_list[(int(pagenum) - 1) * 20:(int(pagenum)) * 20]
        return render_template('recipe_manage.html', sign_in_info=sign_in_info, recipe_list=res_list, page=page)


@app.route("/user_manage/<string:pagenum>", methods=("GET", "POST"))
def user_manage(pagenum):
    if session.get('id') == None:
        return redirect(url_for('sign_in'))
    else:
        if session.get('email') == None:
            # check if admin
            sign_in_info = {"state": "sign in"}
        else:
            sign_in_info = {"state": "sign out", "admin": session.get('admin')}
        link = "http://127.0.0.1:5000/user_manage/"
        if request.method == "POST":
            search_by_name = request.form.get("Search_by_name")
            if search_by_name != "":
                name_list = User.query.filter(User.user_name.like('%{keyword}%'.format(keyword=search_by_name))).all()
                search_by_name = ''
                if len(name_list) == 0:
                    page = {'page_prev': "", 'page_num': str(1), 'page_next': link + str(int(pagenum) + 1)}
                    return render_template('user_manage.html', sign_in_info=sign_in_info, name_list=None, page=page)
                res_list = []
                for name in name_list:
                    user_dict = dict()
                    user_dict['user_name'] = name.user_name
                    user_dict['user_id'] = name.id
                    user_dict['user_email'] = name.email
                    res_list.append(user_dict)
                return render_template('user_manage.html', sign_in_info=sign_in_info, name_list=res_list, page=None)
        else:
            name_list = User.query.all()
        res_list = []
        for name in name_list:
            user_dict = dict()
            user_dict['user_name'] = name.user_name
            user_dict['user_id'] = name.id
            user_dict['user_email'] = name.email
            res_list.append(user_dict)
        link = "http://127.0.0.1:5000/user_manage/"
        if int(pagenum) == 1:
            page = {'page_prev': "", 'page_num': pagenum, 'page_next': link + str(int(pagenum) + 1)}
        else:
            page = {'page_prev': "http://127.0.0.1:5000/user_manage/" + str(int(pagenum) - 1), 'page_num': pagenum,
                    'page_next': link + str(int(pagenum) + 1)}
        res_list = res_list[(int(pagenum) - 1) * 20:(int(pagenum)) * 20]
        return render_template('user_manage.html', sign_in_info=sign_in_info, name_list=res_list, page=page)


def delete_info(recipe_id):
    recipe = Recipe.query.filter_by(recipe_id=recipe_id).all()[0]
    for ingredient in eval(recipe.ingredients):
        recipe_list = eval(Ingredient.query.filter_by(ingredient_name=ingredient).all()[0].recipe_list)
        recipe_list.remove(recipe.recipe_name)
        Ingredient.query.filter_by(ingredient_name=ingredient).update({'recipe_list': str(recipe_list)})
    meal_type = recipe.recipe_type
    type_List = eval(Ingredient.query.filter_by(ingredient_name=meal_type).all()[0].recipe_list)
    type_List.remove(recipe.recipe_name)
    recipe_method = recipe.recipe_method
    method_list = eval(Ingredient.query.filter_by(ingredient_name=recipe_method).all()[0].recipe_list)
    method_list.remove(recipe.recipe_name)
    Ingredient.query.filter_by(ingredient_name=meal_type).update({'recipe_list': str(type_List)})
    Ingredient.query.filter_by(ingredient_name=recipe_method).update({'recipe_list': str(method_list)})
    for user in eval(recipe.like_user):
        u = PersonalDetail.query.filter_by(id=user).all()[0]
        fav_list = eval(u.favourite_meals)
        if int(recipe_id) in fav_list:
            fav_list.remove(int(recipe_id))
        pub_list = eval(u.Published_meals)
        if int(recipe_id) in pub_list:
            pub_list.remove(recipe_id)
        PersonalDetail.query.filter_by(id=user).update(
            {'favourite_meals': str(fav_list), 'Published_meals': str(pub_list)})
    db.session.delete(recipe)
    db.session.commit()


@app.route("/delete_func/", methods=['POST'])
def delete_func():
    if session.get('email') == None:
        return "Not logged"
    else:
        if request.method == "POST":
            recipe_id = request.get_json()
            delete_info(recipe_id)
    return '100'


@app.route("/delete_user/", methods=['POST'])
def delete_user():
    if session.get('email') == None:
        return "Not logged"
    else:
        if request.method == "POST":
            user_id = request.get_json()
            user = User.query.filter_by(id=user_id).all()[0]
            recipe_list = eval(PersonalDetail.query.filter_by(id=user_id).all()[0].Published_meals)
            if recipe_list:
                for recipe_id in recipe_list:
                    delete_info(recipe_id)
            db.session.delete(user)
            db.session.commit()
    return '100'


# 菜谱上传页
@app.route("/recipe_upload_page/", methods=("GET", "POST"))
def recipe_upload_page():
    if session.get('id') == None:
        return redirect(url_for('sign_in'))
    else:
        if session.get('email') == None:
            sign_in_info = {"state": "sign in"}
        else:
            sign_in_info = {"state": "sign out", "admin": session.get('admin')}

        user_id = session.get('id')
        if request.method == "POST":
            recipe_data = request.form.to_dict(flat=False)
            recipe_image = request.files['recipe_image']
            # image_name = secure_filename(recipe_image.filename)
            recipe_name = recipe_data['recipe_name'][0]

            recipe_image.save(os.path.join(app.root_path, 'static/Food Images', recipe_name + '.jpg'))
            meal_type = recipe_data['meal_type'][0]
            cooking_method = recipe_data['cooking_method'][0]
            recipe_steps = recipe_data['recipe_steps'][0]
            ingredient_list = recipe_data['ingredients'][0].split(',')

            ingredients = []
            ingredients_unit = {}
            final_ingredients_unit = []
            for item in ingredient_list:
                first = item.find(' ')
                second = item.find(' ', first + 1) + 1
                ingredients.append(item[second:])
                ingredients_unit[item[second:]] = item[:first]
            ingredients = list(set(ingredients))
            for k, v in ingredients_unit.items():
                final_ingredients_unit.append([k, v])
            for item in ingredients:
                temp_result = Ingredient.query.filter_by(ingredient_name=item).first().recipe_list
                temp_result = eval(temp_result)
                temp_result.append(recipe_name)
                Ingredient.query.filter_by(ingredient_name=item).update({'recipe_list': str(temp_result)})
            temp_result = Ingredient.query.filter_by(ingredient_name=meal_type).first().recipe_list
            temp_result = eval(temp_result)
            temp_result.append(recipe_name)
            Ingredient.query.filter_by(ingredient_name=meal_type).update({'recipe_list': str(temp_result)})
            temp_result = Ingredient.query.filter_by(ingredient_name=cooking_method).first().recipe_list
            temp_result = eval(temp_result)
            temp_result.append(recipe_name)
            Ingredient.query.filter_by(ingredient_name=cooking_method).update({'recipe_list': str(temp_result)})
            db.session.commit()
            time = str(datetime.datetime.now().year) + '.' + str(datetime.datetime.now().month) + '.' + str(
                datetime.datetime.now().day)

            new_recipe = Recipe(contributor_id=user_id, recipe_name=recipe_name, recipe_detail=recipe_steps,
                                ingredients=str(ingredients), ingredients_num=str(final_ingredients_unit),
                                recipe_type=meal_type, recipe_method=cooking_method,
                                recipe_upload_time=time, recipe_img_name=recipe_name,
                                recipe_likes=0, recipe_ratings=0, rated_numbers=0, like_user='[]')

            db.session.add(new_recipe)
            db.session.commit()
            published_meals = eval(PersonalDetail.query.filter_by(id=session.get('id')).all()[0].Published_meals)
            recipe = Recipe.query.filter_by(recipe_name=recipe_name).all()[0]
            if recipe.recipe_id not in published_meals:
                published_meals.append(recipe.recipe_id)
                PersonalDetail.query.filter_by(id=session.get('id')).update({'Published_meals': str(published_meals)})
                db.session.commit()

        return render_template('recipe_upload_page.html', sign_in_info=sign_in_info)


# Recipe edit page
@app.route("/edit_recipe_page/<string:name>", methods=("GET", "POST"))
def edit_recipe_page(name):
    if session.get('email') == None:
        sign_in_info = {"state": "sign in"}
    else:
        sign_in_info = {"state": "sign out", "admin": session.get('admin')}
    user_id = session.get('id')
    recipe_to_edit = Recipe.query.filter_by(recipe_name=name).all()[0]
    ingredients_num_e = eval(recipe_to_edit.ingredients_num)
    if request.method == "POST":
        recipe_data = request.form.to_dict(flat=False)
        recipe_name = recipe_data['recipe_name'][0]
        image_name = name
        old_recipe_name = name
        old_type = recipe_to_edit.recipe_type
        old_method = recipe_to_edit.recipe_method
        old_ing = eval(recipe_to_edit.ingredients)
        old_ing.append(old_type)
        old_ing.append(old_method)
        for ing in old_ing:
            recipe_list = eval(Ingredient.query.filter_by(ingredient_name=ing).all()[0].recipe_list)
            recipe_list.remove(old_recipe_name)
            Ingredient.query.filter_by(ingredient_name=ing).update({'recipe_list': str(recipe_list)})
        db.session.commit()

        if 'recipe_image' in recipe_data:
            if recipe_data['recipe_image'][0] == '0':
                old_path = os.path.join(app.root_path, 'static/Food Images', recipe_to_edit.recipe_name + '.jpg')
                os.rename(old_path, os.path.join(app.root_path, 'static/Food Images', name + '.jpg'))
            else:
                recipe_image = request.files['recipe_image']
                recipe_image.save(os.path.join(app.root_path, 'static/Food Images', recipe_name + '.jpg'))

        meal_type = recipe_data['meal_type'][0]
        cooking_method = recipe_data['cooking_method'][0]
        recipe_steps = recipe_data['recipe_steps'][0]
        ingredient_list = recipe_data['ingredients'][0].split(',')
        ingredients = []
        ingredients_unit = {}
        final_ingredients_unit = []
        for item in ingredient_list:
            first = item.find(' ')
            second = item.find(' ', first + 1) + 1
            ingredients.append(item[second:])
            ingredients_unit[item[second:]] = item[:first]
        ingredients = list(set(ingredients))
        for k, v in ingredients_unit.items():
            final_ingredients_unit.append([k, v])
        for item in ingredients:
            temp_result = Ingredient.query.filter_by(ingredient_name=item).first().recipe_list
            temp_result = eval(temp_result)
            temp_result.append(recipe_name)
            Ingredient.query.filter_by(ingredient_name=item).update({'recipe_list': str(temp_result)})
            db.session.commit()
        temp_result = Ingredient.query.filter_by(ingredient_name=meal_type).first().recipe_list
        temp_result = eval(temp_result)
        temp_result.append(recipe_name)
        Ingredient.query.filter_by(ingredient_name=meal_type).update({'recipe_list': str(temp_result)})
        temp_result = Ingredient.query.filter_by(ingredient_name=cooking_method).first().recipe_list
        temp_result = eval(temp_result)
        temp_result.append(recipe_name)
        Ingredient.query.filter_by(ingredient_name=cooking_method).update({'recipe_list': str(temp_result)})
        db.session.commit()
        time = str(datetime.datetime.now().year) + '.' + str(datetime.datetime.now().month) + '.' + str(
            datetime.datetime.now().day)

        Recipe.query.filter_by(recipe_id=recipe_to_edit.recipe_id).update({'recipe_name': recipe_name,
                                                                           'recipe_detail': recipe_steps,
                                                                           'ingredients': str(ingredients),
                                                                           'ingredients_num': str(
                                                                               final_ingredients_unit),
                                                                           'recipe_type': meal_type,
                                                                           'recipe_method': cooking_method,
                                                                           'recipe_upload_time': time,
                                                                           'recipe_img_name': image_name})
        db.session.commit()
    return render_template('edit_recipe_page.html', sign_in_info=sign_in_info,
                           recipe_name=recipe_to_edit.recipe_name,
                           recipe_steps=recipe_to_edit.recipe_detail,
                           recipe_type=recipe_to_edit.recipe_type,
                           recipe_method=recipe_to_edit.recipe_method,
                           image_name=recipe_to_edit.recipe_img_name,
                           ingredients_num=ingredients_num_e)


if __name__ == '__main__':
    app.run()
