from urllib.request import urlopen
import xml.etree.ElementTree
#

class Artist:
    def __init__(self, name, image, url):
        self.name = name
        self.image = image
        self.url = url

class Track:
    def __init__(self, artist, name, image, url):
        self.artist = artist
        self.name = name
        self.image = image
        self.url = url

def getSimilarArtists(apikey, artist, track =""):
    method = "artist"
    query = "http://ws.audioscrobbler.com/2.0/?method=" + method + ".getsimilar&artist="
    query = query + artist + "&track=" + track + "&api_key=" + apikey
    print(query)
    try:
        req = urlopen(query)
    except BaseException:
        return []

    tree = xml.etree.ElementTree.parse(req)
    root = tree.getroot()

    if "ok" != root.get('status') or len(root) < 1:
        return []

    res_array = []
    for child in root[0]:
        name = child.find("name").text
        url = child.find("url").text
        image_list = child.findall('.//image[@size="large"]')
        if len(image_list):
            image = image_list[0].text
        else:
            image = child.find("image").text
        artist = Artist(name, image, url)
        res_array.append(artist)

    return res_array

def getSimilarTracks(apikey, artist, track=""):
    method = "track"
    query = "http://ws.audioscrobbler.com/2.0/?method=" + method + ".getsimilar&artist="
    query = query + artist + "&track=" + track + "&api_key=" + apikey

    print(query)

    try:
        req = urlopen(query)
    except BaseException:
        return []

    tree = xml.etree.ElementTree.parse(req)
    root = tree.getroot()


    if "ok" != root.get('status') or len(root) < 1:
        return []

    res_array = []
    for child in root[0]:
        name = child.find("name").text
        url = child.find("url").text
        artist = child.find("artist").find("name").text
        image_list = child.findall('.//image[@size="large"]')
        if len(image_list):
            image = image_list[0].text
        else:
            image = child.find("image").text
        track = Track(artist, name, image, url)
        res_array.append(track)

    return res_array


# def getSimilarArtist(apikey, artist, track = ""):
#     pass





