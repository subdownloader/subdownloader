#Some examples:
   ## Test if a Movie object is a tv (mini) series:
 #> if movie['kind'] in ('tv series', 'tv mini series'):
 #>     print '%s is a series' % movie['title']
   ## Test if a Movie object is an episode of a tv (mini) series:
 #> if movie['kind'] == 'episode':
 #>     print '%s is an episode of a series' % movie['title']

#For the series, you can access the list of episodes:
 #> from imdb import IMDb
 #> i = IMDb()
 #> er = i.get_movie('0108757') # E.R.
 #> i.update(er, 'episodes')
 #> print er['episodes']

#er['episodes'] is a dictionary of dictionary in the form
#{#season_number: {#episode_number: Movie object}}

#You can handle the content of er['episodes'] using the sortedSeasons()
#and sortedEpisodes() functions that you can find in the imdb.helpers
#module.  E.g.:
 #> from imdb.helpers import *
   ## For every season of the er Movie object...
 #> for season in sortedSeasons(er):
       ## For every episode in a season...
       #for episode in sortedEpisodes(er, season=season):
           #print 'Episode title: %s' % episode['title']

#For an episode, you can access information about the relative series:
   ## The season and espide number
 #> print movie['season'], movie['episode']
   ## A Movie object which represents the series of the given episode.
 #> theSeries = episode['episode of']
 #> print theSeries['title']

#You can find the complete documentation about tv series in the
#README.series file, in the IMDbPY package.


    
from imdb import IMDb
i = IMDb()
m = i.get_movie('0389564')  # The 4400.
m['kind']    # kind is 'tv series'.
#i.update(m, 'episodes')   # retrieves episodes information.
print m['cover url']