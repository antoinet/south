import requests
import traceback
import time
from expiringdict import ExpiringDict
import os
import logging

class Fr24Poller:

  FR24_FEED_URL = 'http://data-live.flightradar24.com/zones/fcgi/feed.js'
  FR24_FLIGHT_DATA_URL = 'http://data-live.flightradar24.com/clickhandler/'
  HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0'
  }
  
  def __init__(self, bounds, sleep=5, max_altitude=6000, destination='ZRH'):
    self.bounds = bounds
    self.sleep = sleep
    self.max_altitude = max_altitude
    self.destination = destination
    self.cache = ExpiringDict(max_len=1000, max_age_seconds=3600)
    self.polling = False
    self.handlers = []
    self.__logger = logging.getLogger(self.__class__.__name__)

  def start(self):
    self.polling = True
    self.__poll()

  def __poll(self):
    while self.polling:
      try:
        feed = self.__get_feed()
        if feed:
          self.__logger.debug(feed)
          feed.pop('full_count', None)
          feed.pop('version', None)
        for fid in feed:
          if (feed[fid][4] < self.max_altitude and feed[fid][12] == self.destination):
            if fid not in self.cache:
              fdata = self.__get_flight_data(fid)
              self.cache[fid] = None
              for h in self.handlers:
                try:
                  h(fid, fdata)
                except Exception as e:
                  print e.__doc__
                  print e.message
      except Exception as e:
        print " EXCEPTION ***** "
        print e.__doc__
        print e.message     
        traceback.print_exc()
      time.sleep(self.sleep)

  def __get_feed(self):
    """
      Request the FR24 feed within the given bounds.
      Expected result is a JSON payload of the form:
      {
        "full_count": 12279,
        "version":4,
        "a8b761e": [
          "3C4872",  //  0 mode-s code (icao)
          47.3306,   //  1 lat
          8.4460,    //  2 lng
          30,        //  3 track (in degrees)
          34975,     //  4 altitude (in ft)
          436,       //  5 ground speed (in kts)
          "4074",    //  6 ?
          "F-LFST1", //  7 radar
          "A321",    //  8 aircraft type
          "D-ABCR",  //  9 registration
          1470169609,// 10 issue time
          "PMI",     // 11 departure
          "NUE",     // 12 destination
          "AB7531",  // 13 flight-nr
          0,         // 14 ?
          0,         // 15 ?
          "BER597E", // 16 alternate flight-nr
          0
        ],
        "a8b92d8": [ ... ],
        ...
      }

      Request:
      https://data-live.flightradar24.com/zones/fcgi/feed.js?bounds=47.297170,47.277958,8.638830,8.694534&faa=1&mlat=1&flarm=1&adsb=1&gnd=1&air=1&vehicles=1&estimated=1&maxage=7200&gliders=1&stats=1&selected=ad07c3a&ems=1
    """
    payload = {
      'bounds': self.bounds, 'mlat': 1, 'adsb': 1, 'estimated': 1, 'flarm': 1,
      'faa': 1, 'stats': 0, 'gliders': 1, 'vehicles': 1, 'maxage': 7200,
      'air': 1, 'gnd': 1, 'ems': 1
    }
    r = requests.get(Fr24Poller.FR24_FEED_URL, headers=Fr24Poller.HEADERS, params=payload)
    r.connection.close()
    return r.json()

  def __get_flight_data(self, fid):
    """
      Request the flight data for a given id.
      Expected result is a JSON payload of the form: 
      {
    "aircraft": {
        "age": null,
        "hex": "4b160b",
        "images": {
            "large": [
                {
                    "copyright": "stefano castelli",
                    "link": "https://external.flightradar24.com/redirect/?url=http%3A%2F%2Fwww.jetphotos.net%2Fphoto%2F8325621",
                    "source": "Jetphotos.net",
                    "src": "https://cdn.flightradar24.com/640cb/6/91776_1468260900.jpg?v=0"
                },
                {
                    "copyright": "Sebastian Schaffer",
                    "link": "https://external.flightradar24.com/redirect/?url=http%3A%2F%2Fwww.jetphotos.net%2Fphoto%2F8315443",
                    "source": "Jetphotos.net",
                    "src": "https://cdn.flightradar24.com/640cb/6/21350_1467297240.jpg?v=0"
                },
                {
                    "copyright": "Alexander Portas",
                    "link": "https://external.flightradar24.com/redirect/?url=http%3A%2F%2Fwww.jetphotos.net%2Fphoto%2F8308157",
                    "source": "Jetphotos.net",
                    "src": "https://cdn.flightradar24.com/640cb/6/38043_1466656210.jpg?v=0"
                }
            ],
            "medium": [
                {
                    "copyright": "stefano castelli",
                    "link": "https://external.flightradar24.com/redirect/?url=http%3A%2F%2Fwww.jetphotos.net%2Fphoto%2F8325621",
                    "source": "Jetphotos.net",
                    "src": "https://cdn.flightradar24.com/400/6/91776_1468260900.jpg?v=0"
                },
                {
                    "copyright": "Sebastian Schaffer",
                    "link": "https://external.flightradar24.com/redirect/?url=http%3A%2F%2Fwww.jetphotos.net%2Fphoto%2F8315443",
                    "source": "Jetphotos.net",
                    "src": "https://cdn.flightradar24.com/400/6/21350_1467297240.jpg?v=0"
                },
                {
                    "copyright": "Alexander Portas",
                    "link": "https://external.flightradar24.com/redirect/?url=http%3A%2F%2Fwww.jetphotos.net%2Fphoto%2F8308157",
                    "source": "Jetphotos.net",
                    "src": "https://cdn.flightradar24.com/400/6/38043_1466656210.jpg?v=0"
                }
            ],
            "thumbnails": [
                {
                    "copyright": "stefano castelli",
                    "link": "https://external.flightradar24.com/redirect/?url=http%3A%2F%2Fwww.jetphotos.net%2Fphoto%2F8325621",
                    "source": "Jetphotos.net",
                    "src": "https://cdn.flightradar24.com/200/6/91776_1468260900_tb.jpg?v=0"
                },
                {
                    "copyright": "Sebastian Schaffer",
                    "link": "https://external.flightradar24.com/redirect/?url=http%3A%2F%2Fwww.jetphotos.net%2Fphoto%2F8315443",
                    "source": "Jetphotos.net",
                    "src": "https://cdn.flightradar24.com/200/6/21350_1467297240_tb.jpg?v=0"
                },
                {
                    "copyright": "Alexander Portas",
                    "link": "https://external.flightradar24.com/redirect/?url=http%3A%2F%2Fwww.jetphotos.net%2Fphoto%2F8308157",
                    "source": "Jetphotos.net",
                    "src": "https://cdn.flightradar24.com/200/6/38043_1466656210_tb.jpg?v=0"
                }
            ]
        },
        "model": {
            "code": "A320",
            "text": "Airbus A320-214"
        },
        "msn": null,
        "registration": "HB-IJB"
    },
    "airline": {
        "code": {
            "iata": "LX",
            "icao": "SWR"
        },
        "name": "Swiss",
        "short": "Swiss",
        "url": "swiss-swr"
    },
    "airport": {
        "destination": {
            "code": {
                "iata": "ZRH",
                "icao": "LSZH"
            },
            "info": {
                "baggage": "29",
                "gate": null,
                "terminal": null
            },
            "name": "Zurich Airport",
            "position": {
                "altitude": "1416",
                "country": {
                    "code": "CH",
                    "name": "Switzerland"
                },
                "latitude": 47.464722,
                "longitude": 8.549167,
                "region": {
                    "city": "Zurich"
                }
            },
            "timezone": {
                "abbr": "CEST",
                "abbrName": "Central European Summer Time",
                "isDst": true,
                "name": "Europe/Zurich",
                "offset": 7200,
                "offsetHours": "2:00"
            },
            "visible": true,
            "website": "http://www.zurich-airport.com/"
        },
        "origin": {
            "code": {
                "iata": "FAO",
                "icao": "LPFR"
            },
            "info": {
                "baggage": null,
                "gate": null,
                "terminal": null
            },
            "name": "Faro Airport",
            "position": {
                "altitude": "24",
                "country": {
                    "code": "PT",
                    "name": "Portugal"
                },
                "latitude": 37.01442,
                "longitude": -7.96591,
                "region": {
                    "city": "Faro"
                }
            },
            "timezone": {
                "abbr": "WEST",
                "abbrName": "Western European Summer Time",
                "isDst": true,
                "name": "Europe/Lisbon",
                "offset": 3600,
                "offsetHours": "1:00"
            },
            "visible": true,
            "website": "http://www.faro-airport.org/"
        },
        "real": null
    },
    "airspace": null,
    "availability": [
        "AGE",
        "MSN"
    ],
    "ems": null,
    "firstTimestamp": 1470334333,
    "flightHistory": {
        "aircraft": null,
        "flight": null
    },
    "identification": {
        "callsign": "EDW299",
        "id": "a910501",
        "number": {
            "alternative": "LX299",
            "default": "WK299"
        },
        "row": 3225092022
    },
    "level": "limited",
    "owner": null,
    "s": "Ba4tWlyP6Zymny4NgUlkoovhqtvXjQi4cTy_KeohAnU",
    "status": {
        "ambiguous": false,
        "estimated": null,
        "generic": {
            "eventTime": {
                "local": 1470351136,
                "utc": 1470343936
            },
            "status": {
                "color": "green",
                "text": "estimated",
                "type": "arrival"
            }
        },
        "icon": "green",
        "live": true,
        "text": "Estimated- 22:52"
    },
    "time": {
        "estimated": {
            "arrival": 1470343936,
            "departure": null
        },
        "historical": {
            "delay": "-522",
            "flighttime": "8573"
        },
        "other": {
            "eta": 1470343936,
            "updated": 1470343636
        },
        "real": {
            "arrival": null,
            "departure": 1470334543
        },
        "scheduled": {
            "arrival": 1470343800,
            "departure": 1470333900
        }
    },
    "trail": [
        {
            "alt": 0,
            "hd": 334,
            "lat": 47.456001,
            "lng": 8.54955,
            "spd": 135,
            "ts": 1470343756
        },
        {
            "alt": 1250,
            "hd": 334,
            "lat": 47.452599,
            "lng": 8.5519,
            "spd": 148,
            "ts": 1470343750
        },
     ... ],
    }
    """
    payload = {
      'version': '1.5',
      'flight': fid
    }
    r = requests.get(Fr24Poller.FR24_FLIGHT_DATA_URL, headers=Fr24Poller.HEADERS, params=payload)
    r.connection.close()
    return r.json()
