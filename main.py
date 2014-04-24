#!/usr/bin/env python

import jinja2
import os
import webapp2
import datetime
#import problems


from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

def get_problems():
    text_file = open("problems.txt", "r")
    #text_file.encode('utf-16','ignore')
    arr = text_file.read().split("!*QUES*!")
    arr = [strip_non_ascii(i) for i in arr]
    #arr = []
    return arr

problem_arr = get_problems()

class Leaderboard(db.Expando):
    """Models the name and score database"""
    name = db.StringProperty()
    score = db.IntegerProperty(default=0)
    solved = db.StringProperty(default="")
    #solved_arr = db.StringListProperty(default=[])

class Recent_activity(db.Expando):
    """Models each submission entry with name, time , problem and result """
    name = db.StringProperty()
    problem = db.IntegerProperty()
    result = db.StringProperty()
    date = datetime.datetime

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            name = user.nickname()
            l_url = users.create_logout_url('/')
            template = jinja_environment.get_template('templates/index.html')
            self.response.out.write(template.render(l_url=l_url,name=name))
        else:
            self.redirect(users.create_login_url(self.request.uri))

class problem(webapp2.RequestHandler):

    def get_user(self):
        user = users.get_current_user()
        query = db.GqlQuery("SELECT * FROM Leaderboard ORDER BY score DESC")
        exist = False
        for i in query:
            if user.nickname() == i.name:
                exist = True
                return exist,i
        
        if exist == False:
            # create new entity and return its params
            i = Leaderboard()
            i.name =  user.nickname()
            i.score = 0
            i.put()
            return exist,i

    def add_to_recent(self,n,result):
        user = users.get_current_user()
        j= Recent_activity()
        j.name = user.nickname()
        j.date = datetime.datetime.now()
        j.problem=n
        j.result=result
        j.put() 

        return j.name + str(j.problem) + j.result + str(j.date)

    def get(self):
        exist,i = self.get_user()
        n = int(self.request.get('n'))
        if n > 5:
            n=-1
        question = problem_arr[n].split('!*ANS*!')[0]
        template = jinja_environment.get_template('templates/problem.html')
        self.response.out.write(template.render(question=question,n=n,name=i.name,score=i.score))
        #self.redirect('/?n='+str(n))

    
    def post(self):
        tmp=[]
        params=[]
        exist = False

        n = int(self.request.get('n'))
        answer = problem_arr[n].split('!*ANS*!')[1]
        
        user_input = self.request.get('answer')
    
        query = db.GqlQuery("SELECT * FROM Leaderboard")

        if len(user_input) != 0 and int(user_input) == int(answer):          
            exist,i = self.get_user()
            if exist:
                tmp = i.solved.split(":")
                #tmp = i.solved_arr
                if str(n) not in tmp and n not in tmp: 
                    tmp.append(n)
                i.score = len(tmp)*10
                i.solved = ":".join(str(x) for x in tmp)
                #i.solved_arr = tmp
                #for j in tmp: i.solved_arr.append(str(j))
                i.put()        
            else:
                tmp.append(n)
                i.score = len(tmp)*10
                i.solved = ":".join(str(x) for x in tmp)
                #i.solved_arr = tmp
                #for j in tmp: i.solved_arr.append(str(j))
                i.put()
            
            self.add_to_recent(n,"Correct")

            n=n+1

            template = jinja_environment.get_template('templates/success.html')
            self.response.out.write(template.render(n=n))

        else :
            self.add_to_recent(n,"Wrong")
            template = jinja_environment.get_template('templates/error.html')
            self.response.out.write(template.render(n=n))

        #self.redirect('/?n='+str(n))

class Recent_activity_page(webapp2.RequestHandler): 
    def get(self):
        arr=[]
        j=0
        q = db.GqlQuery("SELECT * FROM Recent_activity ORDER BY date DESC")
        template = jinja_environment.get_template('templates/recent.html')
        self.response.out.write(template.render(q=q))


class Leaderboard_page(webapp2.RequestHandler): 
    def get(self):
        arr=[]
        j=0
        q = db.GqlQuery("SELECT * FROM Leaderboard ORDER BY score DESC")
        template = jinja_environment.get_template('templates/leaderboard.html')
        self.response.out.write(template.render(q=q))

class Problem_list_page(webapp2.RequestHandler): 
    def get(self):
        q=[]
        for i in problem_arr:
            q.append(i.split('!*ANS*!')[0])

        template = jinja_environment.get_template('templates/problem_list.html')
        self.response.out.write(template.render(q=q))

class More_page(webapp2.RequestHandler): 
    def get(self):
        template = jinja_environment.get_template('templates/more.html')
        self.response.out.write(template.render())        

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/problem',problem),
    ('/recent',Recent_activity_page),
    ('/leaderboard',Leaderboard_page),
    ('/list',Problem_list_page),
    ('/more',More_page)
], debug=True)



'''
## TODO  ##

Already solved the problem alert

Show problems already done

View date in nice format

UI :extend templates with jinja [DONE] and add bootstrap css [DONE]

collect pictures to be shown in error and correct pages

push to github AFTER EDITING .GITIGNORE

add a footer and add source code link and facebook page link
'''
