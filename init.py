import os
import csv
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from sqlalchemy import ForeignKey, desc



basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 绑session用的key
app.config['SECRET_KEY'] = os.urandom(24)
app.debug = True
app.permanent_session_lifetime = timedelta(minutes=30)

db = SQLAlchemy(app)
# 定义User：email是primary key
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
    id = db.Column(db.String(80), ForeignKey('user.id'),primary_key=True)
    # 以下三个都存 [recipe_id1,recipe_id2,recipe_id2] 按照id存
    Published_meals = db.Column(db.String(100), nullable=True, default='[]')
    favourite_meals = db.Column(db.String(100), nullable=True, default='[]')
    favourite_contributors = db.Column(db.String(100), nullable=True,default='[]')   # 存的名字
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





# init recipe db
with open('./final_data.csv','r',encoding='utf-8') as f:
    with app.app_context():
        reader = csv.reader(f)
        count = 0
        
        if reader != None:
            for i in reader:
                count += 1
                if count > 1:
                    # id starts from 2
                    recipe = Recipe(recipe_name=i[3],recipe_detail=i[5],recipe_img_name=i[6],ingredients=i[8],recipe_likes=i[10],recipe_ratings=i[9],rated_numbers=i[11], contributor_id=i[16],like_user='[]',recipe_type = i[13],recipe_method=i[14],recipe_upload_time=i[12],ingredients_num=i[15])
                    db.session.add(recipe)
                    db.session.commit()

# init ingredients db
with open('./recipe_name.csv','r',encoding='utf-8') as f:
    with app.app_context():
        reader = csv.reader(f)
        count = 0
        if reader != None:
            for i in reader:
                count += 1
                if count > 1:
                    ing = Ingredient(ingredient_name=i[0],recipe_list=i[1])
                    db.session.add(ing)
                    db.session.commit()
# init user db
with open('./user.csv','r',encoding='utf-8') as f:
    with app.app_context():
        reader = csv.reader(f)
        count = 0
        if reader != None:
            for i in reader:
                count += 1
                if count > 1:
                    user = User(email=i[0],user_name=i[1],password=i[2],state=i[3],admin=1)
                    db.session.add(user)
                    db.session.commit()

# init comment db
with open('./comment.csv','r',encoding='utf-8') as f:
    with app.app_context():
        reader = csv.reader(f)
        count = 0
        if reader != None:
            for i in reader:
                count += 1
                if count > 1:
                    comment = Comment(comment_recipe=i[2],comment_user=i[1],comment_time=i[4],comment_c=i[3])
                    db.session.add(comment)
                    db.session.commit()


with open('./badge.csv','r',encoding='utf-8') as f:
    with app.app_context():
        reader = csv.reader(f)
        count = 0
        if reader != None:
            for i in reader:
                count += 1
                if count > 1:
                    badge = Badge(badge_name=i[0],badge_detail=i[1],badge_img=i[2])
                    db.session.add(badge)
                    db.session.commit()


with open('./persondetail.csv','r',encoding='utf-8') as f:
    with app.app_context():
        reader = csv.reader(f)
        count = 0
        badge_list = ['1','3','6']
        if reader != None:
            for i in reader:
                count += 1
                if count > 1:
                    person = PersonalDetail(id=i[0],Published_meals=i[1], favourite_meals=i[2],badge_list=str(badge_list))
                    db.session.add(person)
                    db.session.commit()

print("initialization complete!")