import os
import json
import urllib2
import re

#####################################################
#Settings
#####################################################
#The directory where your movies are stored
#They can be files or folders within that dir
MOVIE_DIR = "/Volumes/My_Book/Movies"
#MOVIE_DIR = "/Users/kim/Downloads/complete/Movies"

#The maximum number of movies to search through
#Use a small number for testing, default: 1000
LIMIT = 1000

#True for fancy HTML output
#False for simple output with only the rating
HTML_OUTPUT = True

#Match this regex pattern
movie_match_regex = "^[A-Za-z0-9' -]+"
#####################################################




#stores a list of titles from the local drive
movies_list = []

#dictionary of movies with all details from IMDB
#key is the title
#value is the list of attributes from IMDB
movie_dict = {}

#structure for storing movies which we couldn't find
not_found_dict = {}

#open the directory containing all of the movies.
os.chdir(MOVIE_DIR)



#If the last four chars of a string are a number, remove it
#This might cause a problem with some movies...
def removeTrailingNumber(string):
    last4chars = string[-4:]
    if last4chars.isdigit():
        #remove the string
        return string[:-4]
    else:
        #keep the whole string
        return string

#Given a nice IMDB movie dictionary (which this program generates) output a nice html page
def generateHTMLOutput(movie_dict, not_found_dict):
    
    print "<html>"

    print "<head>"
    print "<title>Movie Info Output</title>"
    print ""
    print "<script type=\"text/javascript\" charset=\"utf-8\" src=\"http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js\"></script>"
    print "<script type=\"text/javascript\" charset=\"utf-8\" src=\"scripts/jquery.dataTables.js\"></script>"
    print "<script type=\"text/javascript\" charset=\"utf-8\" src=\"scripts/scripts.js\"></script>"
    print ""
    print "<style type=\"text/css\" title=\"currentStyle\">@import \"css/style.css\";</style>"
    print "<style type=\"text/css\" title=\"currentStyle\">@import \"css/table.css\";</style>"
    print "</head>"

    print "<body>"

    print "<h1>Movie Info Output</h1>"

    print "<div>"
    print "%d items matched in directory!<br />" % (len(movie_dict) + len(not_found_dict))
    print "%d movies which we found!<br />" % len(movie_dict)
    print "%d movies which we couldn't find!<br />" % len(not_found_dict)
    print "<br />"
    print "</div>"

    print "<table border=\"1\" id=\"movie_table\" class=\"display\">"

    print "<thead>"
    print "\t<tr> <th>Image</th> <th>Title</th> <th>IMDB Rating</th> <th>Year</th> <th>Rated</th> <th>Link</th> </tr>"
    print "</thead>"
    #Loop through the dictionary of found movies...

    print "<tbody>"
    #The second part of this sorts in order of highest IMDB rating
    for (current_movie,data) in sorted(movie_dict.iteritems(), reverse=True, key=lambda (k,v): (v[u'imdbRating'],k)):

        print "\t<tr>",
        print " <td><img src=\"%s\" class=\"cover\" /></td>" % data[u'Poster'],
        print " <td>%s</td>" % (data[u'Title']),
        print " <td>%s</td>" % data[u'imdbRating'],
        print " <td>%s</td>" % data[u'Released'][-4:],
        print " <td>%s</td>" % data[u'Rated'],
        print " <td><a href=\"http://imdb.com/title/%s\">Click Here</a></td>" % data[u'imdbID'],
        print "</tr>"

    print "</tbody>"

    print "</table>"

    print "</body>"
    print "</html>"


#go through everything in the current folder
for files in os.listdir("."):

        #Match our regex against everything in the folder
        matchObj = re.match( movie_match_regex , files)


        #Add all items which matched the pattern to our list to lookup later
        if matchObj:

            movie = matchObj.group()
            movie = removeTrailingNumber(movie)

            movies_list.append(movie)
            #print "Title: ", movie



#print "%d items matched in directory!" % len(movies_list)

#Loop through the potential movies in the list
count = 0   #keep a count of the number of items we have checked...
while (count < LIMIT and count < len(movies_list)):

    #print movies_list[count]

    #Replace spaces with a + (so it's a valid url)
    title = movies_list[count].replace(' ','+')
    #Get the year using the regex later if needed (it seems to be quite successful without it)
    year = ""

    #Generate the URL of the api lookup for each movie title
    url = 'http://www.imdbapi.com/?t=%s&y=%s' % (title, year)
    #print url


    #Try and get a json response from the URL...
    error = False
    try:
        data = urllib2.urlopen(url).read()
    except urllib2.HTTPError, e:
        print "HTTP error: %d" % e.code
        error = True
    except urllib2.URLError, e:
        print "Network error: %s" % e.reason.args[1]
        error = True

    #It looks like the lookup returned something...
    if not error:
        json_movie_data = json.loads(data)

        #Check if it found anything useful
        if json_movie_data[u'Response'] == "True":
            
            #print "A movie was found!"
            #print objs
            movie_dict[json_movie_data[u'Title']]     = json_movie_data
            #json_movie_data keys include: imdbRating, title, year, rated, released, director...

        else:
            #print "This movie was not found!"
            not_found_dict[movies_list[count]]     = json_movie_data
    
    else:
        print "Fatal Error, can not continue!"
        break;


    count += 1

#####################################################
#Output
#####################################################
if HTML_OUTPUT:
    generateHTMLOutput(movie_dict, not_found_dict)

#Do the simple output
else:
    print "---------------------------------------"
    print "Movie Info By Kim Bratzel (Simple Output)"
    print "---------------------------------------"
    print "%d items matched in directory!" % len(movies_list)
    print "%d movies which we found!" % len(movie_dict)
    print "%d movies which we couldn't find!" % len(not_found_dict)

    #Print movies which we found
    print "---------------------------------------"
    print "Movies which we found data for:\n"
    #The second part of this sorts in order of highest IMDB rating
    for (current_movie,data) in sorted(movie_dict.iteritems(), reverse=True, key=lambda (k,v): (v[u'imdbRating'],k)):
            print "-- %32s \t\t %s " % (current_movie, data[u'imdbRating'])

    print "---------------------------------------"
    print "Items which we found NO data for:\n"
    #Print movies which couldn't be found
    for (current_movie,data) in not_found_dict.iteritems():
            print "-- %32s " % current_movie
    print "---------------------------------------"
    print "Done."




