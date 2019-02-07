#!/usr/bin/env python
#
# Copyright 2018 Paul Harwood
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import jinja2, os, json, logging
from update import UpdateSchema
from data import Gun, GUN_TYPES, RECORD_QUALITIES, to_bool, UserStatus, to_int, BNG, geolocate, GeoPt
from flask import Flask, render_template, send_from_directory, request
from datetime import datetime

app = Flask(__name__)
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")



@app.route('/')
def main_handler():
    user_data = UserStatus()
    return render_template("index.html", 
                user_data= user_data,
                index= 1)

@app.route('/about')
def about():
    user_data = UserStatus()
    return render_template('about.html',
                           index= 2,
                           user_data= user_data
                           )

@app.route('/database')
def database():
    user_data = UserStatus()
    return render_template("database.html",
                           user_data= user_data,
                           gun_types= GUN_TYPES,
                           index= 3                           
                           )


@app.route('/map_fetch', methods=['POST'])
def fetch_map():
    map = {
        "defaultThumb" : "/img/70x70.png",
        "icons" : {
            "bronze" : '/img/cannon_bronze.png',
            "silver" : "/img/cannon_silver.png",
            'gold' : "/img/cannon_gold.png",
            'none' : '/img/cannon_bronze.png',
        },
        "pageSize": 10,
        "entryPath" : "/database/entry?gun_id=",
        "sort":{"asc": 4, "desc": 3},
    }
    entries = Gun.map_data()
    map.update({
        "entries":entries
    })
    return json.dumps(map)

@app.route('/database/entry')
def fetch_entry():
    user_data = UserStatus()
    user = user_data['user']
    gun_id = to_int(request.args.get('gun_id'))
    if gun_id > 0:
        gun = Gun.get_id(gun_id)
        index = 3
    else:
        if user:
            gun = Gun(
                gunid=Gun.get_next(),
                description="",
                type=Gun.Types.NOT_KNOWN,
                name=user.email(),
                location= GeoPt(52,0),
                date= datetime.now()
            )
            index = 4
        else :
            gun = Gun(
                gunid=Gun.get_next(),
                description="",
                type=Gun.Types.NOT_KNOWN,
                name="",
                location=GeoPt(52, 0),
                date=datetime.now()
            )
            index = 4
    return render_template('detail.html',
                           user_data=user_data,
                           gun= gun,
                           gun_types= GUN_TYPES,
                           qualities_text= RECORD_QUALITIES,
                           qualities= Gun.Quality,
                           index= index                           
                           )

@app.route('/set_entry', methods=['POST'])
def set_entry():
    user_data=UserStatus()
    user = user_data['user']
    if user:
        gun_id = to_int(request.form.get('id'))
        new_location = GeoPt(request.form.get('lat'), request.form.get('lon'))
        gun = Gun.get_id(gun_id)
        if not gun :
            gun = Gun(
                gunid=gun_id,
                name=user.email(),
                images=""
            )
        gun.populate(
            description= request.form.get('description'),
            type= Gun.Types[request.form.get('type')],
            name= request.form.get('name'),
            site=request.form.get('site'),
            context=request.form.get('context'),
            collection=to_bool(request.form.get('collection')),
            coll_name=request.form.get('coll_name'),
            coll_ref=request.form.get('coll_ref'),
            markings=to_bool(request.form.get('markings')),
            mark_details=request.form.get('mark_details'),
            interpretation=to_bool(request.form.get('interpretation')),
            inter_details=request.form.get('inter_details'),
            quality=Gun.Quality[request.form.get('quality')]
        )
        if  gun.country == 'none' or new_location != gun.location:
            gun.location = new_location
            address = geolocate(gun.location)
            gun.geocode = json.dumps(address)
            for location in address:
                if "country" in location['types']:
                    gun.country = location['formatted_address']
        gun.put()
        return render_template('detail.html',
                               user_data= user_data,
                               gun= gun,
                               gun_types= GUN_TYPES,
                               qualities_text= RECORD_QUALITIES,
                               qualities= Gun.Quality,
                               index= 4,                               
                               )

@app.route('/get_upload_key')
def GetKey():
    def post(self):
        user_data = UserStatus(self.request.uri)
        user = user_data['user']
        if user:
            logging.info("Creating key for " + user.email() + (" to upload"))
            auth = Auth('https://www.googleapis.com/auth/cloud-platform')
            key = auth.get_token()
            url = auth.get_url()
            response = json.dumps({
                'key': key,
                'url': url
            })
            self.response.write(response)
        return

@app.route('/add_photo')
def add_photo():
    def post(self):
        user_data = UserStatus(self.request.uri)
        user = user_data['user']
        if user:
            data = json.loads(self.request.body)
            logging.info( user.email() + " added Object " + data['name'] + "." )
            name = data['name']
            bucket = data['bucket']
            gun_id = to_int(self.request.get('id'))
            url = images.get_serving_url(None, filename='/gs/{}/{}'.format(bucket, name), secure_url=True)
            gun = Gun.get_id(gun_id)
            if gun :
                image_list = gun.images
                if len(image_list) == 1 and image_list[0] == "":
                    gun.images = [url]
                else :
                    gun.images.append(url)
                gun.put()
            self.response.write(url)
        return

@app.route('/bng_convert')
def bng_convert():
    def post(self):
        eastings = to_int(self.request.get('eastings'))
        northings = to_int(self.request.get('northings'))
        bng = BNG(
            eastings=eastings,
            northings=northings
        )
        convert = bng.convert_to_LL()
        response = json.dumps({
            "LATITUDE" : convert["LATITUDE"],
            "LONGITUDE" : convert["LONGITUDE"]
        })
        self.response.write(response)
        return

@app.route('/ll_convert', methods=['POST'])
def LlConvert():
    lat = self.request.get('lat')
    lon = self.request.get('lon')
    convert = BNG.convert_from_LL(lat,lon)
    response = json.dumps({
        "EASTING" : convert["EASTING"],
        "NORTHING" : convert["NORTHING"]
    })
    self.response.write(response)
    return
    
@app.route('/img/<path:path>', methods=['GET'])
def img(path):
    return send_from_directory(root, path)
    


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)