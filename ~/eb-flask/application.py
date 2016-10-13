import os, re, csv, ast, csv
import math
import jinja2
jinja_environment = jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
import flask
from flask.ext.mysql import MySQL

from features import _show_frequent_features
from builder import _build_query
from raw_data import _raw_data
from download import _download
from analysis import _analysis

mysql = MySQL()
application = flask.Flask(__name__)

# Put the credential in the config file
application.config['MYSQL_DATABASE_USER'] = 'root'
application.config['MYSQL_DATABASE_PASSWORD'] = 'HeRa@CCI@FSU'
application.config['MYSQL_DATABASE_DB'] = 'cancer'
application.config['MYSQL_DATABASE_HOST'] = 'somelab12.cci.fsu.edu'
application.config['MYSQL_DATABASE_PORT'] = 3306

mysql.init_app(application)

#Set application.debug=true to enable tracebacks on Beanstalk log output.
#Make sure to remove this line before deploying to production.
application.debug=True


# init semantic group list
g_sty = {}
stys = open("SemGroups.txt").read().splitlines()
for sty in stys:
    sty_token = sty.split("|")
    if len(sty_token) >= 4:
        g_sty[sty_token[2]] = sty_token

# get all disease type
db = mysql.connect()
cur = db.cursor()
disease_sql = "select distinct task from cancer_cui"
cur.execute(disease_sql)
diseases_list = ()
for row in cur.fetchall():
    diseases_list += (row[0],)
if db.open:
    db.close()

@application.route('/', methods=['POST','GET'])
def vatec_main():
    global diseases_list
    if diseases_list is None:
        return "Failed in retrieving the list of disease."
    else:
        return flask.render_template('index.html', diseases_list=diseases_list)

@application.route('/raw_data', methods=['POST','GET'])
def raw_data():
    global diseases_list
    return _raw_data(mysql,diseases_list,g_sty)

@application.route('/features',methods=['POST','GET'])
def show_frequent_features():
    return _show_frequent_features(mysql,g_sty)

@application.route('/builder',methods=['POST','GET'])
def build_query():
    return _build_query(mysql)

@application.route('/analysis',methods=['POST','GET'])
def analysis():
    _analysis(mysql)

@application.route('/download', methods=['POST','GET'])
def download():
    return _download(mysql)

# start point of the application
if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)
