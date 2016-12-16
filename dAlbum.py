from gmusicapi import Mobileclient
import gMusicLogin

from tqdm import tqdm
import sys , os , time , requests

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import mutagen.id3


EasyID3.RegisterTextKey("albumartist", "TPE2")
EasyID3.RegisterTextKey("media", "TMED")

r_albumID = 'Bmzku73mo3yicub2vnes43wv52y'

api = Mobileclient()
try:
	api.login( gMusicLogin.getUser() , gMusicLogin.getPass() , Mobileclient.FROM_MAC_ADDRESS )		
except:
	sys.exit("Login Failed")

while api.is_authenticated() == False:
	time.sleep(.1)

def removeNonASCII(text):
    return ''.join(i for i in text if ord(i)<128)

def runMainBody():

	r_album = api.get_album_info(r_albumID)

	w_Album = {}
	w_Album['name'] = r_album['name']
	print(w_Album['name'])
	w_Album['songs'] = []

	for item in r_album['tracks']:
		w_Item = {}
		w_Item['nid'] = item['nid']
		w_Item['trackNumber'] = item['trackNumber']
		w_Item['title'] = removeNonASCII(item['title'])
		w_Item['artist'] = removeNonASCII(item['artist'])
		w_Item['artURL'] = item['albumArtRef'][0]['url']
		w_Album['songs'].append( w_Item )

	c_Length = len(w_Album['songs'])
	w_Index = 1
	for item in w_Album['songs']:

		print( "Downloading [" + str(w_Index) + "] of " + str(c_Length ) )

		w_URL = api.get_stream_url( item['nid'] , api.android_id , 'hi' )
		fN = os.path.join( os.getcwd() , item['title'] + ".mp3" )

		response1 = requests.get( w_URL , stream=True )
		
		with open( fN , 'wb' ) as f:
			for data in tqdm( response1.iter_content(chunk_size=524288) ):
				f.write(data)		

		m3 = MP3( fN , ID3=EasyID3 )
		m3.add_tags( ID3=EasyID3 )

		m3["title"] = item['title']
		m3['artist'] = item['artist']
		m3['albumartist'] = item['artist']
		m3['album'] = w_Album['name']
		m3['media'] = item['artURL'] 
		m3.save()

		w_Index = w_Index + 1


runMainBody()
