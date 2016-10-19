__author__ = 'Jason'
import os, re, csv, ast, csv
import math
import jinja2
jinja_environment = jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
import flask

def _raw_data(mysql,diseases_list,g_sty):
    if diseases_list is None:
        return "Failed in retrieving the list of disease."

    input_tid = flask.request.form.get('input_tid',None)
    title_output = "<tr><td><b>"
    data_output = ""

    if input_tid is not None:
        db = mysql.connect()
        cur = db.cursor()

        raw_data_list = True
        num_umls_term = 0
        cols_title_str = "Disease,type,pattern,duration,month,negation,sty,cui,org_str,cui_str,sentence"
        cols_title = cols_title_str.split(",")
        for col in cols_title:
            title_output += "%s</b></td><td><b>" % (col)
        title_output += "</b></td></tr>"
        sql_var = [input_tid]
        sql_data = "select task,type,pattern,duration,month,neg,sty,cui,org_str,cui_str,sentence from cancer_cui where tid = %s and (nested = 'None' or nested='nesting') "
        cur.execute(sql_data, sql_var)
        for row in cur.fetchall():
            num_umls_term += 1
            data_output += "<tr><td>"
            for idx,f in enumerate(row):
                if idx == cols_title.index("sty"): f = g_sty[f][3]
                data_output += "%s</td><td>" % (str(f))
            data_output += "</td></tr>"

        cols = "tid,brief_title,official_title,location,agency,overall_status,start_date,gender,minimum_age,maximum_age,enrollment,conditions,phase,study_pop," \
               "intervention_type,intervention_name,authority,source,study_type,agency_type,enrollment_type,minimum_age_in_year,maximum_age_in_year," \
               "intervention_model,allocation,masking,primary_purpose,endpoint_classification,observational_model,time_perspective".split(",")
        sql = "select * from meta where tid=%s limit 1 "
        cur.execute(sql, sql_var)
        tidInfo = {}
        for row in cur.fetchall():
            tidInfo["brief_title"]=row[cols.index("brief_title")]
            tidInfo["overall_status"]=row[cols.index("overall_status")]
            tidInfo["study_type"]=row[cols.index("study_type")]
            tidInfo["phase"]=row[cols.index("phase")]
            tidInfo["intervention_type"]=row[cols.index("intervention_type")]
            tidInfo["intervention_name"]=row[cols.index("intervention_name")]
            tidInfo["phase"]=row[cols.index("phase")]

        if db.open:
            db.close()
    return flask.render_template('raw_data.html', **locals())

