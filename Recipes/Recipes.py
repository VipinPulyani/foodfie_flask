import requests
from collections import OrderedDict
from flask import Blueprint, render_template
from flask import request,jsonify
from flask_cors import CORS, cross_origin

import pymysql

import config
recipe_api = Blueprint('recipe_api', __name__)
CORS(recipe_api)


def connectDB():
    conn = pymysql.connect(host = config.host, port=config.port, user= config.user, password = config.password, db= config.db)
    cur = conn.cursor()
    return conn, cur


def getRawCategory(categoryId = 'Null'):

    conn, cur = connectDB()
    cur.execute("""select RecipeName 
                   from foodfie.Recipes
                   where RecipeId=IFNULL({},RecipeId)""".format(categoryId))
    rawCategory = cur.fetchall()
    l_rawCategory = [cat[0] for cat in rawCategory]
    return l_rawCategory


def getRawItems(itemId):

    conn, cur = connectDB()
    cur.execute("""select RecipeIngredients 
                   from foodfie.Recipes_Detail 
                   where RecipeId={}""".format(itemId))
    rawItem = cur.fetchall()
    l_rawItem = [cat[0] for cat in rawItem]
    return l_rawItem


@recipe_api.route("/Recipes", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def Recipes():
    rawCategory = getRawCategory()
    return render_template('Category.html', rawCategory = rawCategory, categoryName ='Recipes')


@recipe_api.route("/Paneer Momos", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def vegmomos():
    rawItem = getRawItems(1)
    commodityName = getRawCategory(1)[0]
    return render_template('Commodity.html', rawItem = rawItem, commodityName = commodityName )


@recipe_api.route("/getIngredient", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def getIngredient():
    itemId = 1
    itemQTY = 2

    conn, cur = connectDB()
    cur.execute("""Select RecipeIngredients, RecipeIngredientsWeight
                    from foodfie.Recipes_Detail
                    where RecipeId = {}""".format(itemId))
    t_allIngredient = cur.fetchall()
    dic_allIngredient = dict((x,y) for x, y in t_allIngredient)
    for key, value in dic_allIngredient.items():
        dic_allIngredient[key] = value * itemQTY
    return jsonify({})


@recipe_api.route("/api/v1.0/getVegMomosIngredient/<float:cabbage>", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def getVegMomosIngredient(cabbage):

    ingredient = OrderedDict()
    cabbage *= 1000
    totalSum = cabbage
    ingredient['carrot'], totalSum = [round(cabbage * 0.05), (totalSum + round(cabbage * 0.05))], (totalSum + round(cabbage * 0.05))
    ingredient['salt'], totalSum = [round(cabbage * 0.017), (totalSum + round(cabbage * 0.017))], (totalSum + round(cabbage * 0.017))
    ingredient['ginger_Garlic_Paste'], totalSum = [round(cabbage * 0.05), (totalSum + round(cabbage * 0.05))], (totalSum + round(cabbage * 0.05))
    ingredient['dalda'], totalSum = [round(cabbage * 0.027), (totalSum + round(cabbage * 0.027))], (totalSum + round(cabbage * 0.027))
    ingredient['hari_Mirch_Paste'], totalSum = [round(cabbage * 0.02), (totalSum + round(cabbage * 0.02))], (totalSum + round(cabbage * 0.02))
    ingredient['ajino'], totalSum = [round(cabbage * 0.05), (totalSum + round(cabbage * 0.05))], (totalSum + round(cabbage * 0.05))
    ingredient['dhaniya_Patta'], totalSum = [round(cabbage * 0.0167) , (totalSum + round(cabbage * 0.0167))], (totalSum + round(cabbage * 0.0167))

    return jsonify(ingredient)


@recipe_api.route("/api/v1.0/getPannerMomosIngredient/<float:paneer>", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def getPaneerMomosIngredient(paneer):

    ingredient = OrderedDict()
    paneer *= 1000
    ingredient['cabbage'] = paneer * 0.05
    ingredient['salt'] = paneer * 0.025
    ingredient['ginger_Garlic_Paste'] = paneer * 0.05
    ingredient['dalda'] = paneer * 0.055
    ingredient['hari_Mirch_Paste'] = paneer * 0.025
    ingredient['ajino'] = paneer * 0.055
    ingredient['dhaniya_Patta'] = paneer * 0.025

    return jsonify(ingredient)


@recipe_api.route("/api/v1.0/getChickenMomosIngredient/<float:chicken>", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def getChickenMomosIngredient(chicken):

    ingredient = OrderedDict()
    chicken *= 1000
    totalSum = chicken
    ingredient['onion'], totalSum = [round(chicken * 0.375), (totalSum + round(chicken * 0.375))], (totalSum + round(chicken * 0.375))
    ingredient['soyabean'], totalSum = [round(chicken * 0.0625), (totalSum + round(chicken * 0.0625))], (totalSum + round(chicken * 0.0625))
    ingredient['salt'], totalSum = [round(chicken * 0.05), (totalSum + round(chicken * 0.05))], (totalSum + round(chicken * 0.05))
    ingredient['ginger_Garlic_Paste'], totalSum = [round(chicken * 0.075), (totalSum + round(chicken * 0.075))], (totalSum + round(chicken * 0.075))
    ingredient['dalda'], totalSum = [round(chicken * 0.075), (totalSum + round(chicken * 0.075))],  (totalSum + round(chicken * 0.075))
    ingredient['hari_Mirch_Paste'], totalSum = [round(chicken * 0.025), (totalSum + round(chicken * 0.025))], (totalSum + round(chicken * 0.025))
    ingredient['ajino'], totalSum = [round(chicken * 0.05), (totalSum + round(chicken * 0.05))], (totalSum + round(chicken * 0.05))
    ingredient['dhaniya_Patta'], totalSum = [round(chicken * 0.025), (totalSum + round(chicken * 0.025))], (totalSum + round(chicken * 0.025))

    return jsonify(ingredient)


@recipe_api.route("/api/v1.0/testRecipe", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def testRecipe():
    return render_template('Recipe.html')
