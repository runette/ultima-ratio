# MIT License

# Copyright (c) 2019 Paul Harwood

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import types
import sys
from enum import Enum
from datetime import datetime
import logging
import googlemaps
from simplendb.ndb import Model, Query, Key, GeoPt, ndb
import simplendb.users
from simplendb.images import ndbImage, Blob
from simplendb.helpers import to_bool, to_int
import requests
import time


GUN_TYPES = ("Cast Iron", "Wrought Iron", "Bronze",
             "Not Known", "Combined Cast and Wrought Iron")
RECORD_QUALITIES = ('Observer', "Recorder", "Surveyor")
GUN_CATEGORIES = ("Not Known", "Muzzle Loading",
                  "Breech Loading", "Carronade")
GUN_STATUS = ('Unverified', 'Auto', 'Verified')
MATRIX = {'type': GUN_TYPES, 'quality': RECORD_QUALITIES,
          'category': GUN_CATEGORIES, 'status': GUN_STATUS}


class BNG():
    @staticmethod
    def convert_to_LL(eastings, northings):
        return BNG.BGS_api({'method': 'BNGtoLatLng', 'easting': eastings, "northing": northings})

    @staticmethod
    def convert_from_LL(lat, lon):
        return BNG.BGS_api({'method': 'LatLongToBNG', 'lat': str(lat), 'lon': str(lon)})

    @staticmethod
    def BGS_api(params):
        URL = "http://www.bgs.ac.uk/data/webservices/CoordConvert_LL_BNG.cfc"
        try:
            result = requests.get(URL, params=params)
            if result.status_code == requests.codes.ok:
                try:
                    return result.json()
                except:
                    raise Exception('ParseError' + result.text())
            else:
                raise Exception('ApiError' + str(result.status_code))
        except Exception as e:
            logging.error(str(e))
            return


class Gun(Model):
    class Types(Enum):
        CAST = 0
        WROUGHT = 1
        BRONZE = 2
        NOT_KNOWN = 3
        COMBINATION = 4

    class Quality(Enum):
        GOLD = 2
        SILVER = 1
        BRONZE = 0

    class Status(Enum):
        UNVERIFIED = 0
        AUTO = 1
        VERIFIED = 2

    class Categories(Enum):
        NOT_KNOWN = 0
        MUZZLE_LOAD = 1
        BREECH_LOAD = 2
        CARRONADE = 3

    def schema(self):
        super().schema()
        self.Property("gunid", ndb.IntegerProperty)
        self.Property("location", ndb.GeoPtProperty)
        self.Property("type", ndb.EnumProperty, enum=Gun.Types)
        self.Property("quality", ndb.EnumProperty,
                      enum=Gun.Quality, default=Gun.Quality.BRONZE)
        self.Property("description", ndb.StringProperty)
        self.Property("name", ndb.StringProperty)
        self.Property("date", ndb.DateTimeProperty, auto_now=True)
        self.Property("site", ndb.StringProperty)
        self.Property('display_name', ndb.StringProperty)
        self.Property("context", ndb.StringProperty)
        self.Property("collection", ndb.BooleanProperty)
        self.Property("coll_name", ndb.StringProperty)
        self.Property("coll_ref", ndb.StringProperty)
        self.Property("images", ndb.TextProperty, repeated=True)
        self.Property("markings", ndb.BooleanProperty)
        self.Property("mark_details", ndb.StringProperty)
        self.Property("interpretation", ndb.BooleanProperty)
        self.Property("inter_details", ndb.StringProperty)
        self.Property("country", ndb.StringProperty, default="none")
        self.Property("geocode", ndb.JsonProperty)
        self.Property("user_id", ndb.StringProperty)
        self.Property("status", ndb.EnumProperty,
                      enum=Gun.Status, default=Gun.Status.UNVERIFIED)
        self.Property("measurements", ndb.DictProperty)
        self.Property("moulding_code", ndb.StringProperty, repeated=True)
        self.Property("muzzle_code", ndb.StringProperty)
        self.Property("cas_code", ndb.StringProperty)
        self.Property("button_code", ndb.StringProperty)
        self.Property('category', ndb.EnumProperty,
                      enum=Gun.Categories, default=Gun.Categories.NOT_KNOWN)

    @classmethod
    def map_data(cls, namespace):
        result = cls.query(order=['gunid'], namespace=namespace).fetch()
        users = User.query().fetch()
        map_data = []
        for gun in result:
            try:
                thumbnail = gun.get_images()[0].get("s32")
            except:
                thumbnail = "/img/32x32.png"
            try:
                name = [user for user in users if user.user_id
                        == gun.user_id][0].fire_user['name']
            except Exception as e:
                id = ""
                for user in users:
                    fu = user.fire_user
                    if fu['email'] in gun.name:
                        id = fu['user_id']
                if id != "":
                    gun.user_id = id
                    gun.put()
                    name = User.get_by_id(gun.user_id).fire_user['name']
                else:
                    name = gun.name
            try:
                map_data.append({
                    "anchor_id": gun.gunid,
                    "description": gun.description,
                    "latitude": gun.location.latitude,
                    "longitude": gun.location.longitude,
                    "anchor_type": GUN_TYPES[gun.type.value],
                    "location": gun.context,
                    "names": name,
                    'filename': thumbnail,
                    'quality': gun.quality.value,
                    'nationality': gun.country,
                    'site': gun.display_name,
                    'category': GUN_CATEGORIES[gun.category.value],
                })
            except Exception as e:
                logging.error(str(e))
        return map_data

    @classmethod
    def map_data_2(cls, namespace):
        result = cls.query(order=['gunid'], namespace=namespace).fetch()
        users = User.query().fetch()
        map_data = []
        for gun in result:
            try:
                thumbnail = gun.get_images()[0].get("s32")
            except:
                thumbnail = "/img/32x32.png"
            try:
                name = [user for user in users if user.user_id
                        == gun.user_id][0].fire_user['name']
            except Exception as e:
                id = ""
                for user in users:
                    fu = user.fire_user
                    if fu['email'] in gun.name:
                        id = fu['user_id']
                if id != "":
                    gun.user_id = id
                    gun.put()
                    name = User.get_by_id(gun.user_id).fire_user['name']
                else:
                    name = gun.name
            try:
                line = {}
                line.update({'thumbnail': thumbnail, 'author': name})
                for item in gun.items():
                    if item[0] == 'location':
                        line.update(
                            {'lat': item[1].latitude, 'lng': gun.location.longitude})
                    elif item[0] in MATRIX:
                        line.update({item[0]: MATRIX[item[0]][item[1]]})
                    elif item[0] == 'date':
                        line.update({'date': gun.date.strftime('%d %b %Y')})
                    else:
                        line.update({item[0]: item[1]})
                map_data.append(line)
            except Exception as e:
                logging.error(str(e))
        return map_data

    @classmethod
    def get_next(cls, namespace):
        all = cls.query(order=["-gunid"], namespace=namespace).fetch()
        if all:
            return all[0].gunid + 1
        else:
            return 1

    @classmethod
    def get_id(cls, id, namespace):
        return cls.query(filters=[("gunid", "=", id)], namespace=namespace).get()

    def get_images(self):
        IMAGE_DEFAULTS = [{"s200": "/img/70x70.png", "original": ""}]
        images = []
        try:
            test = self.images[0]
            for image in self.images:
                try:
                    images.append(json.loads(image))
                except:
                    images.append(
                        {"original": image, "s32": image + '=s32', "s200": image + "=s200"})
            return images
        except:
            return IMAGE_DEFAULTS


class User(Model):
    class Standing(Enum):
        OBSERVER = 0
        RECORDER = 1
        SURVEYOR = 2
        ADMIN = 3

    def schema(self):
        super().schema()
        self.Property("user_id", ndb.StringProperty)
        self.Property("standing", ndb.EnumProperty,
                      enum=User.Standing, default=User.Standing.OBSERVER)
        self.Property('created', ndb.DateTimeProperty, auto_now=True)
        self.Property("fire_user", ndb.JsonProperty)
        self.Property('test_user', ndb.BooleanProperty)
        self.Property('train_user', ndb.BooleanProperty)

    @classmethod
    def get_by_id(cls, id):
        return User.query(filters=[('user_id', '=', id)]).get()


def geolocate(location):
    gmaps = googlemaps.Client(key='AIzaSyDZcNCn8CzpdFG58rzRxQBORIWPN9LOVYg')
    reverse_geocode_result = gmaps.reverse_geocode(
        (location.latitude, location.longitude))
    for radius in [100, 300, 600, 1000]:
        places_result = gmaps.places_nearby(
            location=(location.latitude, location.longitude), radius=radius)
        token = places_result.get('next_page_token')
        results = places_result["results"]
        while token:
            try:
                places_result = gmaps.places_nearby(page_token=token)
            except Exception as e:
                logging.error(str(e))
                if 'INVALID_REQUEST' in str(e):
                    time.sleep(2)
                    continue
                raise
            results += places_result['results']
            token = places_result.get('next_page_token')
        if len(results) > 10:
            break
    level = 0
    if len(reverse_geocode_result) < 2:
        try:
            default = reverse_geocode_result[0]['formatted_address']
        except:
            default = "None"
        country = default
    else:
        for location in reverse_geocode_result:
            if "country" in location['types']:
                country = location['formatted_address']
                if level == 0:
                    default = location['formatted_address']
            if 'neighborhood' in location['types']:
                level = 10
                default = location['formatted_address']
                continue
            try:
                admin = [item for item in location['types']
                         if 'administrative_area' in item][0]
                admin_level = to_int(admin[-1])
                if admin_level > level:
                    level = admin_level
                    default = location['formatted_address']
            except:
                pass
    return {"geolocation": reverse_geocode_result, "places": results, 'default': default, 'country': country}


def get_serving_url(upload_metadata):
    bucket_name = upload_metadata.get('bucket')
    full_path = upload_metadata.get('fullPath')
    folder = full_path.replace('/original', '')
    original = ndbImage(full_path, bucket_name)
    original.get()
    original.content_format = original.image.format
    if original.image.format == 'TIFF':
        rgb = original.image.convert('RGB')
        original.image = rgb
        original.put(content_type='image/jpeg', content_format='JPEG')
    thumb_32 = original.thumbnail((32, 32), folder + "/32x32")
    thumb_32.put()
    thumb_200 = original.thumbnail((200, 200), folder + "/200x200")
    thumb_200.put()
    mediaLink = {"original": original.get_media_link(
    ), "s32": thumb_32.get_media_link(), "s200": thumb_200.get_media_link()}
    del original
    del thumb_32
    del thumb_200
    return mediaLink


def UserStatus(id_token):
    result = simplendb.users.UserStatus(id_token)
    if result['user']:
        user = User.get_by_id(result['user'].user_id)
        if user is None:
            user = User(
                user_id=result['user'].user_id,
                fire_user= json.dumps(result['user'])
            )
            user.put()
        if user.fire_user['name'] != result['user']['name']:
            user.fire_user = json.dumps(result['user'])
            a = user.put()
        result['local_user'] = user
        result['test'] = user.test_user
        result['train'] = user.train_user
        result['namespace'] = None
        if result['test']:
            result['namespace'] = 'test'
        if result['train']:
            result["namespace"] = 'train'
    return result


def get_posts():
    URL = "https://public-api.wordpress.com/rest/v1.2/sites/ultimaproject.org/posts"
    params = {'number': 5}
    try:
        result = requests.get(URL, params=params)
        if result.status_code == requests.codes.ok:
            try:
                return result.json()
            except:
                raise Exception('ParseError' + result.text())
        else:
            raise Exception('ApiError' + str(result.status_code))
    except Exception as e:
        logging.error(str(e))
        return

