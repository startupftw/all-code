#!/usr/bin/python

#!/usr/bin/python
from twython import Twython
import json
import cgi
import mysql.connector as conn
import sha, time, Cookie, os, socket
import pickle


consumer_key = "QZwOVsnTParlVIh0ratSHBwad"
consumer_secret = "KafCkTmyIlGOUiGFpqawPcVMZISzVXZW9J3thzlbcYyy9RY1I6"

host_ip_address = socket.gethostbyname(socket.gethostname())

def redirectToPage(url):
	print "Location: " + url 
	print

#this function takes in the twitter authenticated onject so that it can directly call the api for user data
def getUserData(twitter):
	return twitter.verify_credentials()

def connectDB():
	db = conn.connect(host='localhost' , user='root' , passwd='newpwd')
	cursor = db.cursor()
	return db,cursor

def readUserInfoTable(db , cursor):
	cursor.execute("use test")
	db.commit()
	cursor.execute("select * from user_info");

	people = cursor.fetchall()
	for each in people :
		print each[0] , "..." , each[1] , "..." , each[2]


#this function checks if the user is present in the Database
def old_user(user_info):
	db, cursor = connectDB()

	id = user_info["screen_name"]

	cursor.execute("use test")
	db.commit()

	cursor.execute("select * from user_prefs where id=\'" + id + '\''  )
	result = cursor.fetchall()

	cursor.close()
	db.close()
	return len(result) != 0


def creatUserInDB(user_info):
	db, cursor = connectDB()
	id = user_info["screen_name"]

	cursor.execute("use test")
	db.commit()

	#inserting News and Sports as the default Favourite categories for now!
	#and politics as the default dislike
	cursor.execute("insert into  user_prefs values (\'" + id +"\'" + ",\'[\"sports\" , \"news\"] \', \'[\"politics\"]\')"  )
	db.commit()
	cursor.close()
	db.close()

def getSessionData(sid):
	return pickle.load(open("session_data/" + sid))

def updateSessionData(sid , data):
	pickle.dump(data , open("session_data/" + sid , "w"))

def getCurrentSessionId():
	cookie = Cookie.SimpleCookie()
	string_cookie = os.environ.get('HTTP_COOKIE')
	if not string_cookie:
	   # The sid will be a hash of the server time
	   sid = sha.new(repr(time.time())).hexdigest()
	   # Set the sid in the cookie
	   cookie['sid'] = sid
	   # Will expire in a year
	   cookie['sid']['expires'] = 12 * 30 * 24 * 60 * 60

	   #creating a file that stores all the session information.
	   session_file = open("session_data/" + str(sid) , "w")
	   session_file.close()

	   print cookie
#	   print "Content-type: text/html"
	   print

	# If already existent session
	else:
	   cookie.load(string_cookie)
	   sid = cookie['sid'].value
#	   print "Content-type: text/html"
#	   print

	return sid

def auth_step1(form):
	sid = getCurrentSessionId()
	callback = 'http://'+host_ip_address + '/startupftw/login.cgi?command=auth_step2&sid='+sid
	
	print "Content-type: application/json"
	print

	twitter = Twython(consumer_key, consumer_secret)
	auth = twitter.get_authentication_tokens(callback_url=callback)

	session_data = {}
	session_data["oauth_token"] = auth["oauth_token"]
	session_data["oauth_token_secret"] = auth["oauth_token_secret"]

	session_data = updateSessionData( sid , session_data)

	data = {}
	json_data = json.dumps(auth)
	print json_data


def auth_step2(form):
	print "Content-type: application/json"
	print

	# so now in this step we shall not be taking too many things from the url but from the session, so for that we first get the sessionId
	sid = form.getvalue("sid")
	session_data = getSessionData(sid)
	
	#well this oauth_verifier , we still have to get from the url get params sent by twitter, so..go ahead
	oauth_pin = form.getvalue("oauth_verifier");

	OAUTH_TOKEN = session_data["oauth_token"]
	OAUTH_TOKEN_SECRET = session_data["oauth_token_secret"]

	twitter = Twython(consumer_key, consumer_secret ,OAUTH_TOKEN , OAUTH_TOKEN_SECRET)

	final_step = twitter.get_authorized_tokens(oauth_pin)
	OAUTH_TOKEN = final_step['oauth_token']
	OAUTH_TOKEN_SECRET = final_step['oauth_token_secret']

	twitter = Twython(consumer_key, consumer_secret ,OAUTH_TOKEN , OAUTH_TOKEN_SECRET)

	session_data["oauth_token"] = OAUTH_TOKEN
	session_data["oauth_token_secret"] = OAUTH_TOKEN_SECRET
	session_data["twitter"] = twitter
	updateSessionData(sid , session_data)

	#print json.dumps(twitter.verify_credentials())


	#now , when all is done, lets first get the user data, so that we can check if this guy is present in out DB
	user_info = getUserData(twitter)

	if old_user(user_info) == True :
#		print "An already existing user"
		redirectToPage("http://" + host_ip_address + "/startupftw/main.cgi?new_user=false")

	elif old_user(user_info) ==  False:
		#so incase he is not an old_user, we have to put his information in our DB, also send him to a page where he can set his 
		#prefs for the future
		#so here we go..........
		creatUserInDB(user_info)
		redirectToPage("http://" + host_ip_address + "/startupftw/main.cgi?new_user=true")
	session_data["oauth_token"] = OAUTH_TOKEN
	session_data["oauth_token_secret"] = OAUTH_TOKEN_SECRET
	session_data["twitter"] = twitter
	session_data["screen_name"] = user_info["screen_name"]
	updateSessionData(sid , session_data)


#this is a wrapper for the get_home_timeline function provided by twython
def get_home_timeline( count  = 50):
	sid = getCurrentSessionId()
	twitter = getSessionData(sid)["twitter"]
	
	print "Content-type: application/json"
	print

	print json.dumps(twitter.get_home_timeline(count = count))


#main program

if __name__ == "__main__":
	try:

		form = cgi.FieldStorage()
		
		command = form.getvalue("command")

		if command == "auth_step1":
			auth_step1(form)
		elif command == "auth_step2":
			auth_step2(form)
	except:
		cgi.print_exception()


