from flask import Blueprint, render_template,flash, request, url_for, current_app, session, jsonify, abort
from fly_bbs import db_utils, utils, forms, models
from fly_bbs.extensions import mongo
from flask_login import login_required
from flask_login import current_user
from bson.objectid import ObjectId
from bson.json_util import dumps
import pymongo
from random import randint
from datetime import datetime
post_collection = Blueprint("collection", __name__, url_prefix="", template_folder="templates")

@post_collection.route('/find/<ObjectId:post_id>', methods=['POST'])
@post_collection.route('/find/', methods=['POST'])
@login_required
def collection_find(post_id=None):
    collections = current_user.user.get('collections', [])
    if not post_id:
        collections = mongo.db.posts.find({'_id': {'$in': collections}})
        data = models.R().ok().put('rows', collections)
        return dumps(data)
    is_collected = False
    if collections and post_id in collections:
        is_collected = True
    return jsonify(models.BaseResult(data={'collection': is_collected}))

@post_collection.route('/<string:action>/<ObjectId:post_id>', methods=['POST'])
@login_required
def collection(action, post_id):
    update_action = '$pull'
    if action == 'add':
        update_action = '$push'
    mongo.db.users.update_one({'_id': current_user.user['_id']}, {update_action: {'collections': post_id}})
    return jsonify(models.BaseResult())

