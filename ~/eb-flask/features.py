__author__ = 'Jason'

import os, re, csv, ast, csv
import math
import jinja2
jinja_environment = jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
import flask

def _show_frequent_features(mysql,g_sty):
    var, aggregator_output, minimum_value, maximum_value, lower, upper, value_range_verification_output, enrollment_value, value_spectrum_output, num_trials, phase_query, condition_query, query_used, phases, conditions, status_query, statuses, study_type_query, study_types, intervention_type_query, intervention_types, agency_type_query, agency_types, gender_query, gender, modal_boundary_output, enrollment_spectrum_output, num_of_trials_output, detail_enrollment_spectrum_output,value_spectrum_output_trial_ids, initial_value_spectrum, on_option_page, start_date_query, start_date, age_query, value_range_distribution_output,value_range_width_distribution_output, average_enrollment_spectrum_output, disease, intervention_model_query, allocation_query, intervention_models, allocations, time_perspective_query, time_perspectives, start_date_before, disease_query = '', "", '', '', '', '', '', '', "", [], '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', "", "", "", "", "", "", '', '', '', '', "", "", "", '', '','','','','','','',''

    topk = flask.request.form['topk']
    disease = flask.request.form['disease']

    # width_option = flask.request.form.get('width_option',False)
    # fixed_width = flask.request.form.get('fixed_width',None)
    condition_option = flask.request.form.get('conditions',None)
    # plot_type = flask.request.form.get('plot_type',None)
    start_month_option = flask.request.form.get('start_month',None)
    start_year_option = flask.request.form.get('start_year',None)
    start_month_before_option = flask.request.form.get('start_month_before',None)
    start_year_before_option = flask.request.form.get('start_year_before',None)
    minimum_age_option = flask.request.form.get('minimum_age',None)
    maximum_age_option = flask.request.form.get('maximum_age',None)
    gender = flask.request.form.get('gender',None)
    # aggregate_analysis_type = flask.request.form.get('aggregate_analysis_type',None)

    phase_option = flask.request.form.getlist('phase', None)
    status_option = flask.request.form.getlist('status', None)
    study_type_option = flask.request.form.getlist('study_types', None)
    intervention_type_option = flask.request.form.getlist('intervention_types', None)
    agency_type_option = flask.request.form.getlist('agency_types', None)
    intervention_model_option = flask.request.form.getlist('intervention_model', None)
    allocation_option = flask.request.form.getlist('allocation', None)
    time_perspective_option = flask.request.form.getlist('time_perspective', None)
    pattern_option = flask.request.form.getlist('pattern_option', None)

    conditions = condition_option

    # the list of trial IDs if the condition is not indexed in COMPACT
    trial_ids_with_conditions = []

    db = mysql.connect()
    cur = db.cursor()

    nest_status = " (V.nested = 'None' or V.nested = 'nesting') "

    disease_query = "V.task = '%s' " %(disease)
    # if (len(condition_option) != 0):
    #     list_of_diseases = []
    #     all_diseases_query = "select distinct task from cancer_cui"
    #     cur.execute(all_diseases_query)
    #     for row in cur.fetchall():
    #         list_of_diseases.append(row[0])
    #
    #     if condition_option in list_of_diseases:
    #         # generate the part of query containing the condition field
    #         #disease_query = " T.tid in (select tid from all_diseases_trials where disease='%s')" %condition_option
    #         disease_query = " (V.task='%s')" %condition_option
    #     else:
    #         # trial_ids_with_conditions only deals with disease name not in the disease_list table or multiple diseases in the condition field
    #         disease_query = " (T.conditions LIKE '%%')"
    #         trial_ids_with_conditions = get_disease_clinical_trials(condition_option)
    # else:
    #     disease_query = " (T.conditions LIKE '%%')"

    # check phase option and generate part of the query
    phase_query = ""
    if (len(phase_option) == 0):
        phase_query += " (T.phase LIKE '%%')"
    else:
        phase_query += " ("
        for phase in phase_option:
            phase_query += " T.phase LIKE '%s'" % (phase) +" OR"
            phases += phase + "/ "
        # this is not meaningful, just to terminate the part of the query
        phase_query += " T.phase LIKE '%terminated%')"

    # check status option and generate part of the query
    if (len(status_option) == 0):
        status_query += " (T.overall_status LIKE '%%')"
    else:
        status_query += " ("
        for status in status_option:
            if (status == "Open Studies"):
                status_query += " T.overall_status = 'Recruiting' OR T.overall_status = 'Not yet recruiting' OR"
            elif (status == "Closed Studies"):
                status_query += " T.overall_status = 'Active, not recruiting' OR T.overall_status = 'Active, not recruiting' OR T.overall_status = 'Completed' OR T.overall_status = 'Withdrawn' OR T.overall_status = 'Suspended' OR T.overall_status = 'Terminated' OR T.overall_status = 'Enrolling by invitation' OR"
            else:
                status_query += " T.overall_status = '%s'" % (status) + " OR"
            statuses += status + "/ "
        # this is not meaningful, just to terminate the part of the query
        status_query += " T.overall_status LIKE '%reterminated%')"

    # check study type option and generate part of the query
    if (len(study_type_option) == 0):
        study_type_query = " (T.study_type LIKE '%%')"
    else:
        study_type_query += " ("
        for study_type in study_type_option:
            study_type_query += " T.study_type = '%s'" %(study_type) +" OR"
            study_types += study_type + "/ "
        study_type_query += " T.study_type LIKE '%terminated%')"

    # check intervention type option and generate part of the query
    if (len(intervention_type_option) == 0):
        intervention_type_query = " (T.intervention_type LIKE '%%')"
    else:
        intervention_type_query += " ("
        for intervention_type in intervention_type_option:
            intervention_type_query += " T.intervention_type = '%s'" %(intervention_type) + " OR"
            intervention_types += intervention_type + "/ "
        intervention_type_query += " T.intervention_type LIKE '%terminated%')"

    # check agency type option and generate part of the query
    if (len(agency_type_option) == 0):
        agency_type_query = " (T.agency_type LIKE '%%')"
    else:
        agency_type_query += " ("
        for agency_type in agency_type_option:
            agency_type_query += " T.agency_type LIKE '%%%s%%'" %(agency_type) + " OR"
            agency_types += agency_type + "/ "
        agency_type_query += " T.agency_type LIKE '%terminated%')"

    # check agency type option and generate part of the query
    if (gender == '' or gender == 'all'):
        gender_query = " (T.gender LIKE '%%')"
    else:
        gender_query = " (T.gender = '%s'" %(gender) + ")"

    # check start_year_option start_month_option and generate start_date_query
    if (start_year_option == '' or start_month_option == '' or start_month_option == 'N/A'):
        start_date_query = " (T.start_date LIKE '%%')"
    else:
        start_date = str(start_month_option) + " " + str(start_year_option)
        start_date_query = " (STR_TO_DATE(T.start_date,'%%M %%Y') >= STR_TO_DATE('%s'" %(start_date) +",'%M %Y'))"

    if (start_year_before_option != '' and start_month_option != ''):
        start_date_before = str(start_month_before_option) + " " + str(start_year_before_option)
        start_date_query += " and (STR_TO_DATE(T.start_date,'%%M %%Y') <= STR_TO_DATE('%s'" %(start_date_before) +",'%M %Y'))"

    # check minimum_age, maximum_age and generate age_query

    minimum_age = 0
    maximum_age = 150

    if (minimum_age_option != ''):
        try:
            minimum_age = float(minimum_age_option)
        except TypeError:
            minimum_age = 0

    if (maximum_age_option != ''):
        try:
            maximum_age = float(maximum_age_option)
        except TypeError:
            maximum_age = 150

    #age_query = " (T.minimum_age_in_year >= %.9f" %float(minimum_age) +" and T.maximum_age_in_year <= %.9f)" %float(maximum_age)
    age_query = ("1=1")


    # check intervention model option and generate part of the query
    if (len(intervention_model_option) == 0):
        intervention_model_query = " (T.intervention_model LIKE '%%')"
    else:
        intervention_model_query += " ("
        for intervention_model in intervention_model_option:
            intervention_model_query += " T.intervention_model LIKE '%%%s%%'" %(intervention_model) + " OR"
            intervention_models += intervention_model + "/ "
        intervention_model_query += " T.intervention_model LIKE '%terminated%')"

    # check allocation option and generate part of the query
    if (len(allocation_option) == 0):
        allocation_query = " (T.allocation LIKE '%%')"
    else:
        allocation_query += " ("
        for allocation in allocation_option:
            allocation_query += " T.allocation LIKE '%%%s%%'" %(allocation) + " OR"
            allocations += allocation + "/ "
        allocation_query += " T.allocation LIKE '%terminated%')"

    # check time perspective option and generate part of the query
    if (len(time_perspective_option) == 0):
        #time_perspective_query = " (T.time_perspective LIKE '%%')"
        time_perspective_query = " (1=1)"
    else:
        time_perspective_query += " ("
        for time_perspective in time_perspective_option:
            time_perspective_query += " T.time_perspective LIKE '%%%s%%'" %(time_perspective) + " OR"
        time_perspective_query += " T.time_perspective LIKE '%terminated%')"

    # the filter of pattern
    pattern_query = ""
    if (len(pattern_option) == 0):
        pattern_query = " (1=1)"
    else:
        pattern_query += " ("
        for pt in pattern_option:
            pattern_query += " V.pattern = '%s'" % pt + " OR"
        pattern_query += " 1=0 )" # just add a false expression

    value_range_error = False

    # get the total enrollment of trials contaning the variable in the certain range
    enrollment_value = 0


    # start the aggregate analysis

    # get the total number of trials meeting the requirements
    trials_meeting_requirement = ()

    #sql = "SELECT distinct V.TID, V.month FROM cancer_cui V, meta T where %s" %(curr_condition) + " and T.tid = V.tid and "+ phase_query + " and "+ status_query + " and "+ study_type_query + " and "+ intervention_type_query + " and "+ agency_type_query + " and "+ gender_query + " and "+ start_date_query + " and "+ age_query + " and "+ intervention_model_query + " and "+ allocation_query + " and "+ time_perspective_query + " and "+ disease_query
    filter_builder = " T.tid = V.tid and "+ phase_query + " and "+ status_query + " and "+ study_type_query + " and "+ intervention_type_query + " and "+ \
                     agency_type_query + " and "+ gender_query + " and "+ start_date_query + " and "+ age_query + " and "+ intervention_model_query + " and "+ \
                     allocation_query + " and "+ time_perspective_query + " and "+ disease_query + " and " + nest_status + " and " + pattern_query
    #
    # sql = "SELECT V.month, count(*), count(distinct V.tid) FROM cancer_cui V, meta T where %s" % (filter_builder)
    # print sql

    num_trials_with_disease_sql = "select count(V.cui) from cancer_cui V, meta T where V.task = '%s' and %s " %(disease, filter_builder)
    print(num_trials_with_disease_sql)
    cur.execute(num_trials_with_disease_sql)
    num_trials_with_disease = ''
    for row in cur.fetchall():
        num_trials_with_disease = row[0]

    # fetch data for the "frequency table"
    if topk == 'all':
        topk = '100000000000' # big enough  number
    frequent_numeric_feature_sql = "select V.cui,V.sty,V.cui_str,count(*) as freq from cancer_cui V, meta T where task = '%s' and %s group by V.cui,V.sty order by freq desc limit %s " % (disease,filter_builder,topk)
    print frequent_numeric_feature_sql
    cur.execute(frequent_numeric_feature_sql)
    distribution_numeric_features = []
    for row in cur.fetchall():
        ###cui,sty,cui_str,freq
        distribution_numeric_features.append((row[2],row[1], row[0],row[3], g_sty[row[1]][3], g_sty[row[1]][1]))

    # fetch data for the "drop list menu", only the cui with duration
    duration_feature_sql = "select V.cui,V.sty,V.cui_str,count(*) as freq from cancer_cui V, meta T where month > 0 and task = '%s' and %s group by V.cui,V.sty order by freq desc limit %s " % (disease,filter_builder,topk)
    cur.execute(duration_feature_sql)
    duration_features = []
    for row in cur.fetchall():
        ###cui,sty,cui_str,freq
        duration_features.append((row[2],row[1], row[0],row[3]))




    if db.open:
        db.close()
    return flask.render_template('features.html', **locals())

