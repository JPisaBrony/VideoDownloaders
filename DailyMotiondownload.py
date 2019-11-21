import requests
import json

def DailyMotionSpliceId(url):
	regions=str(url).split("?")
	id = regions[0].split("/")[-1]
	return id

def DailyMotionGetMaps(url):
	DailyMotionBaseProbe = "https://www.dailymotion.com/player/metadata/video/"

	id = DailyMotionSpliceId(url)
	req = requests.get(DailyMotionBaseProbe+str(id));
	req.raise_for_status()
	req = req.text
	dat = json.loads(req)
	return dat

def DailyMotionSaveToFile(url, name):
	#https://stackoverflow.com/questions/14114729/save-a-large-file-using-the-python-requests-library
	req = requests.get(url, stream=True)
	req.raise_for_status()
	with open(str(name)+".mp4", 'wb') as handle:
		for block in req.iter_content(65536):
			handle.write(block)

def DailyMotionRip(url,quality=360):
	jdat = DailyMotionGetMaps(url)
	regions = jdat["qualities"]
	id = DailyMotionSpliceId(url)
	
	quality = int(quality)
	
	lastval = 999999
	selkey = "auto"
	for key in regions.keys():
		try:
			val = int(key)
			sval = abs(quality-val)
			if lastval > sval:
				lastval = sval
				selkey = key
			else:
				#take the quality here, will take the lower quality if evenly inbetween upper and lower qualities
				break
			
		except:
			pass
	
	print("Closes Quality Found: "+str(selkey))
	
	for thing in jdat['qualities'][selkey]:
		d = dict(thing)
		if "mp4" in str(d["type"]):
			url = d["url"]
			print(url)
			DailyMotionSaveToFile(url,id)

#EXAMPLE: 
#DailyMotionRip("https://dai.ly/SOMEVIDEO",260) #closest to 260p
#DailyMotionRip("https://www.dailymotion.com/video/SOMEVIDEO",0) #smallest quality available
