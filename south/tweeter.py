import re
import tweepy
import urllib
import os
import bunch
import traceback
import random

class Tweeter:
  
  def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    self.api = tweepy.API(auth)
  
  def tweet(self, fid, fdata):
    pic_url = random.choice(fdata['aircraft']['images']['large'])['src'].split('?', 1)[0]
    pic_url = re.sub('^https', 'http', pic_url)
    try:
      tfile = '/tmp/' + pic_url.split('/')[-1]
      urllib.urlretrieve(pic_url, tfile)
      text = Tweeter.assemble_tweet(fdata)
      self.api.update_with_media(tfile, text)
      os.remove(tfile)
    except Exception as e:
      print traceback.format_exc()
      text = Tweeter.assemble_tweet(fdata)
      self.api.update_status(text)
    print text

  @staticmethod
  def assemble_tweet(fdata):
    o = bunch.bunchify(fdata)
    airline = Tweeter.getaltattr(o, 'airline.short', 'airline.name')
    
    defid = Tweeter.getaltattr(o, 'identification.number.default')
    altid = Tweeter.getaltattr(o, 'identification.number.alternative')
    if defid is None:
      if altid is None:
        id = None
      else:
        id = altid
    elif altid is None:
      id = defid
    elif defid == altid:
      id = defid
    else:
      id = defid + "/" + altid
    
    if (airline is None) and (id is None):
      airline = "UFO"

    city = Tweeter.getaltattr(o, 'airport.origin.position.region.city')
    country = Tweeter.getaltattr(o, 'airport.origin.position.country.name')
    if city is None:
      if country is None:
        origin = None
      else:
        origin = country
    elif country is None:
      origin = city
    elif city == country:
      origin = city
    else:
      origin = city + ", " + country
    if origin is not None:
      origin = "arriving from " + origin

    model = Tweeter.getaltattr(o, 'aircraft.model.text')
    if model is not None:
      if model[0].lower() in 'aeiou':
        model = "in an " + model
      else:
        model = "in a " + model
    
    return " ".join(('Hello %s %s %s %s' % tuple(map(lambda x: '' if x is None else x, (airline, id, origin, model)))).split())

  
  @staticmethod
  def rgetattr(obj, attr):
    left, _, right = attr.partition('.')      
    if right is '':
      return getattr(obj, left)
    else:
      return Tweeter.rgetattr(getattr(obj, left), right)

  @staticmethod
  def getaltattr(obj, *args):
    for arg in args:
      try:
        return Tweeter.rgetattr(obj, arg)
      except AttributeError:
        pass
    return None
