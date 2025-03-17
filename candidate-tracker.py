# Import libraries
import hashlib
import hmac
import pandas as pd
import os
import requests
import base64
import json
import math
import re
import datetime

path = { INSERT PATH TO YAML }
f = open(path + '\\tokens.yml',"r+")
access = json.loads(f.read())
email_addr = access['EML']
password = access['EMLPASS']
api_key = access['BEAMERY_KEY']
api_secret = bytes(access['BEAMERY_SECRET'],encoding='utf-8')
f.close()

priority_dict = {
    '42937d0648362caae00c54316adbf083':'P0',
    'ec6ef230f1828039ee794566b9c58adc':'P1',
    '1d665b9b1467944c128a5575119d1cfd':'P2',
    '7bc3ca68769437ce986455407dab2a1f':'P3',
    '13207e3d5722030f6c97d69b4904d39d':'P4'
}

request_body = '{}'
dig = hmac.new(api_secret, msg=request_body.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
jload = {'Signature': dig}

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(re.compile('<td>'),'   ',raw_html)
  cleantext = re.sub(re.compile('</tr>'),'\n',cleantext)
  cleantext = re.sub(cleanr, '', cleantext)
  return cleantext

#Import all contact IDs
counter,index,end = 0,1,2
while index < end:
    URL = "https://api.beamery.com/v1/contacts?token=" + api_key + "&page=" + str(index) + \
          "&per_page=100&createdAt-op=lte"
    response = requests.get(URL,headers=jload)
#     test_response = requests.get(URL,headers=jload)
#     break
    if index == 1:
        total_len = json.loads(response.content)['totalCount']
        end = math.ceil(json.loads(response.content)['totalCount']/100) + 1
        candidate_df = pd.DataFrame({'first_name':['']*total_len,\
                                     'last_name':['']*total_len,\
                                     'location':['']*total_len,\
                                     'id':['']*total_len,\
                                     'email':['']*total_len,\
                                     'link':['']*total_len,\
                                     'company_id':['']*total_len,\
                                     'company':['']*total_len,\
                                     'role':['']*total_len,\
                                     'vacancies':['']*total_len,\
                                     'status':['']*total_len,\
                                     'assigned_to':['']*total_len,\
                                     'updated_at':['']*total_len,\
                                     'last_activity':['']*total_len,\
                                     'last_contacted':['']*total_len,\
                                     'last_heard_from':['']*total_len,\
                                     'ranking':['']*total_len,\
                                     'next_steps':['']*total_len,\
                                     'relationship_origin':['']*total_len})
        
    for ix,entry in enumerate(json.loads(response.content)['data']):
        if counter == json.loads(response.content)['totalCount']:
            break

        candidate_df.set_value(counter,'first_name',entry['firstName'])
        candidate_df.set_value(counter,'last_name',entry['lastName'])
        try:
            candidate_df.set_value(counter,'location',entry['location'])
        except:
            candidate_df.set_value(counter,'location','')
        candidate_df.set_value(counter,'id',entry['id'])
        candidate_df.set_value(counter,'company_id',str(entry['companyId']))
        try:
            candidate_df.set_value(counter,'vacancies',entry['vacancies'])
        except:
            candidate_df.set_value(counter,'vacancies','')
        if 'primaryExperience' in entry.keys():
            try:
                candidate_df.set_value(counter,'company',entry['primaryExperience']['organisationName'])
            except:
                candidate_df.set_value(counter,'company','')
            try:
                candidate_df.set_value(counter,'role',entry['primaryExperience']['role'])
            except:
                candidate_df.set_value(counter,'role','')
        else:
            candidate_df.set_value(counter,'company','')
            candidate_df.set_value(counter,'role','')
        try:
            candidate_df.set_value(counter,'status',entry['status']['value'])
        except:
            candidate_df.set_value(counter,'status','')
        if len(entry['emails']['keys']) > 0:
            candidate_df.set_value(counter,'email',\
                entry['emails']['values'][entry['emails']['keys'][0]]['value'])
        else:
            candidate_df.set_value(counter,'email','')
        if len(entry['links']['keys']) > 0:
            candidate_df.set_value(counter,'link',\
                entry['links']['values'][entry['links']['keys'][0]])
        else:
            candidate_df.set_value(counter,'link','')
        
        candidate_df.set_value(counter,'ranking','')
        if 'customFields' in entry:
            custom_tracker = 0
            for item in entry['customFields']:
                if 'Ranking' in item['displayName']:
                    candidate_df.set_value(counter,'ranking',item['value'])
                    custom_tracker += 1
                if 'Next Steps' in item['displayName']:
                    candidate_df.set_value(counter,'next_steps',item['value'])
                    custom_tracker += 1
                if 'Relationship Origin' in item['displayName']:
                    candidate_df.set_value(counter,'relationship_origin',item['value'])
                if custom_tracker == 2:
                    break
    
        candidate_df.set_value(counter,'last_activity',datetime.datetime.strptime(entry['lastActivity'],\
        '%Y-%m-%dT%H:%M:%S.%fZ')) if 'lastActivity' in entry.keys() else \
        candidate_df.set_value(counter,'last_activity','')
                               
        candidate_df.set_value(counter,'last_contacted',datetime.datetime.strptime(entry['lastContact'],\
        '%Y-%m-%dT%H:%M:%S.%fZ')) if 'lastContact' in entry.keys() else \
        candidate_df.set_value(counter,'last_contacted','')
                               
        candidate_df.set_value(counter,'last_heard_from',datetime.datetime.strptime(entry['lastHeardFrom'],\
        '%Y-%m-%dT%H:%M:%S.%fZ')) if 'lastHeardFrom' in entry.keys() else \
        candidate_df.set_value(counter,'last_heard_from','')
        
        candidate_df.set_value(counter,'assigned_to',entry['assignedTo'])
        candidate_df.set_value(counter,'updated_at',datetime.datetime.strptime(entry['updatedAt'],\
            '%Y-%m-%dT%H:%M:%S.%fZ'))
        counter += 1
    index += 1

#Import all vacancy IDs
counter,index,end = 0,1,2
while index < end:
#     URL = "https://api.beamery.com/v1/vacancies?token=" + api_key + "&page=" + str(index) + \
#           "&per_page=100&status=open"
    URL = "https://api.beamery.com/v1/vacancies?token=" + api_key + "&page=" + str(index) + \
          "&per_page=100"
    response = requests.get(URL,headers=jload)
#     test_response = requests.get(URL,headers=jload)
#     break
    if index == 1:
        total_len = json.loads(response.content)['totalCount']
        end = math.ceil(json.loads(response.content)['totalCount']/100) + 1
        vacancies_df = pd.DataFrame({'title':['']*total_len,\
                                     'id':['']*total_len,\
                                     'priority':['']*total_len,\
                                     'priority_value':['']*total_len,\
                                     'num_contacts':['']*total_len,\
                                     'updated_at':['']*total_len,\
                                     'updated_by':['']*total_len,\
                                     'status':['']*total_len,\
                                     'owner':['']*total_len,\
                                     'opened_at':['']*total_len
                                     })
    for entry in json.loads(response.content)['data']:
        if counter == total_len:
            break
        vacancies_df.set_value(counter,'title',entry['title'])
        vacancies_df.set_value(counter,'id',entry['id'])
        vacancies_df.set_value(counter,'priority',entry['priority'])
        vacancies_df.set_value(counter,'num_contacts',entry['contactCount'])
        vacancies_df.set_value(counter,'updated_at',entry['createdAt'])
        vacancies_df.set_value(counter,'updated_by',entry['owner'])
        vacancies_df.set_value(counter,'status',entry['status'])
        vacancies_df.set_value(counter,'opened_at',entry['openAt'][0:10])
        toggle = 0
        if 'globalTags' in entry.keys():
            for tag in entry['globalTags']:
                if tag['id'] in priority_dict:
                    toggle = 1
                    break
        if toggle == 1:
            vacancies_df.set_value(counter,'priority_value',priority_dict[tag['id']])
        else:
            vacancies_df.set_value(counter,'priority_value','')
        counter += 1
    index += 1

stages_json = json.loads(response.content)['data'][0]['stages']['entities']['stages'].values()
stages_df = pd.DataFrame({'name':['']*len(stages_json),\
                          'id':['']*len(stages_json),\
                          'order':['']*len(stages_json)})
for index,stage in enumerate(stages_json):
    stages_df.set_value(index,'id',stage['id'])
    stages_df.set_value(index,'name',stage['name'])
    stages_df.set_value(index,'order',stage['order'])

#get all vacancies a candidate is linked to
test_list = []
for index,row in candidate_df.iterrows():
    local = ''
    for item in row['vacancies']:
        if 'value' in item:
            local += item['value'] + ','
    test_list.append(local[:-1])
candidate_df['vacancy_names'] = test_list

test_list = []
for index,row in candidate_df.iterrows():
    if 'value' in str(row['link']):
        test_list.append(row['link']['value'])
    else:
        test_list.append('')
candidate_df['active_link'] = test_list
candidate_df['full_name'] = candidate_df['first_name'] + ' ' + candidate_df['last_name']

yesterday = datetime.date.today() - datetime.timedelta(1)
yesterday = datetime.datetime(yesterday.year,yesterday.month,yesterday.day,20,0,0)

name_list = []
role_list = []
company_list = []
vacancy_list = []
updated_list = []
link_list = []
status_list = []
next_steps_list = []

for ix,rw in vacancies_df.loc[(vacancies_df['priority'] == 'High') & \
                              (vacancies_df['status'] == 'open')].iterrows():
    for index,row in candidate_df.loc[candidate_df['vacancy_names'].str.contains(\
        rw['title'])].iterrows():
        for vacancy in row['vacancies']:
            if rw['title'] in vacancy['value']:
                break
        if 'priority' in vacancy:
            if (vacancy['priority'] == 'high') or ((row['status'] == 'Interview') or \
                                                   (row['status'] == 'Exercise')):
                name_list.append(row['first_name'] + ' ' + row['last_name'])
                role_list.append(row['role'])
                company_list.append(row['company'])
                vacancy_list.append(rw['title'])
                updated_list.append(row['updated_at'])
                if 'value' in row['link']:
                    link_list.append(row['link']['value'])
                else:
                    link_list.append('')
                status_list.append(row['status'])
                next_steps_list.append(row['next_steps'])
        else:
            if ((row['status'] == 'Interview') or (row['status'] == 'Exercise')):
                name_list.append(row['first_name'] + ' ' + row['last_name'])
                role_list.append(row['role'])
                company_list.append(row['company'])
                vacancy_list.append(rw['title'])
                updated_list.append(row['updated_at'])
                if 'value' in row['link']:
                    link_list.append(row['link']['value'])
                else:
                    link_list.append('')
                status_list.append(row['status'])
                next_steps_list.append(row['next_steps'])
        

priorities = pd.DataFrame({'Name':name_list,'Role':role_list,'Company':company_list,\
                           'Vacancy':vacancy_list,'Updated At':updated_list,\
                           'Link':link_list,'Status':status_list,'Next Steps':next_steps_list})

vacancies_df = vacancies_df.sort_values('priority_value')

priorities['Update Date'] = priorities['Updated At'].astype(str)
priorities['Update Date'] = priorities['Update Date'].str.slice(0,10)

vacancies_df['update_date'] = vacancies_df['updated_at'].str.slice(0,10)

#temporary update date fix
test_list = []
for ix,rw in vacancies_df.iterrows():
    if len(candidate_df.loc[candidate_df['vacancy_names'].str.contains(\
        rw['title'])]) > 0:
        test_list.append(str(candidate_df.loc[candidate_df['vacancy_names'].str.contains(\
            rw['title'])].sort_values('updated_at',ascending=False).iloc[0]['updated_at'])[0:10])
    else:
        test_list.append(rw['update_date'])
vacancies_df['updated_date_backup'] = test_list

#set up vacancy_stages
vacancy_stages = pd.DataFrame({'Role':vacancies_df.loc[vacancies_df['priority'] == 'High']['title']})
for stage in stages_df['name']:
#     if stage == 'Accepted':
#         break
    vacancy_stages[stage] = ''

#CURRENT STATE TEST
for vacancy in vacancies_df.loc[vacancies_df['priority'] == 'High']['title']:
    
    for stage in stages_df['name']:
#         if stage == 'Accepted':
#             break
        if (stage != 'Intro Meeting Scheduled') and (stage != 'Intro Meeting Conducted') and \
        (stage != 'Interview') and (stage != 'Exercise') and (stage != 'Offer') and \
        (stage != 'Accepted'):
#         if (stage == 'Prospect') or (stage == 'Initial Outreach') or (stage == 'Engaged') or \
#         (stage == 'Intro Call Scheduled') or (stage == 'Intro Call Conducted') or \
#         (stage == 'Awaiting Response'):
            vacancy_stages.loc[vacancy_stages['Role'] == vacancy,stage] = \
                (len(candidate_df.loc[(candidate_df['vacancy_names'].str.contains(vacancy)) & \
                (candidate_df['status'] == stage)]))
        else:
#             vacancy_stages.loc[vacancy_stages['Role'] == vacancy,stage] = \
            target_set = candidate_df.loc[(candidate_df['vacancy_names'].str.contains(vacancy))].copy()
    
            status_list = []
            for index,row in target_set.iterrows():
                for local_vacancy in row['vacancies']:
                    if local_vacancy['value'] == vacancy:
                        status_list.append(local_vacancy['stage']['value'])
            target_set['status'] = status_list
            target_set = target_set.loc[target_set['status'] == stage]

            if len(target_set) == 0:
                vacancy_stages.loc[vacancy_stages['Role'] == vacancy,stage] = 0
            else:
                test_list = []
                for index,row in target_set.iterrows():
                    test_list.append(row['first_name'] + ' ' + row['last_name'])
                vacancy_stages.loc[vacancy_stages['Role'] == vacancy,stage] = \
                    ',\n'.join(test_list)
vacancy_stages = vacancy_stages.reset_index(drop=True)

vacancy_stages_full = vacancy_stages.copy()
vacancy_stages = vacancy_stages[['Role','Prospect','Initial Outreach','Awaiting Response',\
    'Engaged','Intro Call Scheduled','Intro Call Conducted','Intro Meeting Scheduled',\
    'Intro Meeting Conducted','Interview','Exercise','Offer','Accepted']]
vacancy_stages_full['Rejected'] = vacancy_stages_full['Rejected by Candidate'] + \
    vacancy_stages_full['Rejected by Company'] + vacancy_stages_full['Industry Contact'] + \
    vacancy_stages_full['Inactive'] + vacancy_stages_full['Unresponsive']
vacancy_stages_full['Rejected'] = vacancy_stages_full['Rejected'].astype(int)
vacancy_stages_full = vacancy_stages_full[['Role','Prospect','Rejected','Initial Outreach','Awaiting Response',\
    'Engaged','Intro Call Scheduled','Intro Call Conducted','Intro Meeting Scheduled',\
    'Intro Meeting Conducted','Interview','Exercise','Offer','Accepted']]

contacted = candidate_df.loc[(candidate_df['vacancy_names'].str.contains('subsidiary CMO')) & \
                             (candidate_df['updated_at'] > yesterday) & \
                             (candidate_df['last_contacted'] != '')]
heard_from = candidate_df.loc[(candidate_df['vacancy_names'].str.contains('subsidiary CMO')) & \
                              (candidate_df['updated_at'] > yesterday) & \
                              (candidate_df['last_heard_from'] != '')]
corresponded = candidate_df.loc[(candidate_df['vacancy_names'].str.contains('subsidiary CMO')) & \
                                (candidate_df['updated_at'] > yesterday) & \
                                (candidate_df['last_contacted'] != '') & \
                                (candidate_df['last_heard_from'] != '')]
                                
p_report = '''<font size="+2"><b>Executive Search Daily Activity Report - %s</b></font size>

<b>%d</b> candidates were updated since 6 am yesterday.
Of these, 
<b>%d</b> candidates were contacted.
<b>%d</b> candidates were heard from.
We had two-way correspondence with <b>%d</b> candidates.''' % \
       (datetime.datetime.today().strftime('%B %d, %Y'),\
       len(candidate_df.loc[(candidate_df['vacancy_names'].str.contains('subsidiary CMO')) & \
                            (candidate_df['updated_at'] > yesterday)]),\
       len(contacted.loc[(candidate_df['vacancy_names'].str.contains('subsidiary CMO')) & \
                         (contacted['updated_at'] > yesterday) & \
                         (contacted['last_contacted'] > yesterday)]),\
       len(heard_from.loc[(candidate_df['vacancy_names'].str.contains('subsidiary CMO')) & \
                          (heard_from['updated_at'] > yesterday) & \
                          (heard_from['last_heard_from'] > yesterday)]),\
       len(corresponded.loc[(candidate_df['vacancy_names'].str.contains('subsidiary CMO')) & \
                            (corresponded['last_contacted'] > yesterday) & \
                            (corresponded['last_heard_from'] > yesterday)]))

contacted = candidate_df.loc[(candidate_df['updated_at'] > yesterday) & \
                             (candidate_df['last_contacted'] != '')]
heard_from = candidate_df.loc[(candidate_df['updated_at'] > yesterday) & \
                              (candidate_df['last_heard_from'] != '')]
corresponded = candidate_df.loc[(candidate_df['updated_at'] > yesterday) & \
                                (candidate_df['last_contacted'] != '') & \
                                (candidate_df['last_heard_from'] != '')]
                                
report = '''<font size="+2"><b>Executive Search Daily Activity Report - %s</b></font size>

<b>%d</b> candidates were updated since 6 am yesterday.
Of these, 
<b>%d</b> candidates were contacted.
<b>%d</b> candidates were heard from.
We had two-way correspondence with <b>%d</b> candidates.''' % \
       (datetime.datetime.today().strftime('%B %d, %Y'),\
       len(candidate_df.loc[candidate_df['updated_at'] > yesterday]),\
       len(contacted.loc[(contacted['updated_at'] > yesterday) & \
                         (contacted['last_contacted'] > yesterday)]),\
       len(heard_from.loc[(heard_from['updated_at'] > yesterday) & \
                          (heard_from['last_heard_from'] > yesterday)]),\
       len(corresponded.loc[(corresponded['last_contacted'] > yesterday) & \
                            (corresponded['last_heard_from'] > yesterday)]))


candidate_df['activity_status'] = 'no activity'
candidate_df.loc[candidate_df['id'].isin(contacted.loc[contacted['last_contacted'] > yesterday]['id']),\
                 'activity_status'] = 'contacted'
candidate_df.loc[candidate_df['id'].isin(heard_from.loc[heard_from['last_heard_from'] > yesterday\
                ]['id']),'activity_status'] = 'heard from'
candidate_df.loc[candidate_df['id'].isin(corresponded.loc[(corresponded['last_contacted'] > yesterday) & \
                 (corresponded['last_heard_from'] > yesterday)]['id']),'activity_status'] = 'corresponded'

test_list = []
for index,row in candidate_df.iterrows():
    if row['location'] != '':
        if len(row['location']['address'].split(',')) > 2:
            test_list.append(','.join(row['location']['address'].split(',')[0:2]))
        elif len(row['location']['address'].split(',')) > 1:
            if 'United States' in row['location']['address'].split(',')[1]:
                test_list.append(row['location']['address'].split(',')[0])
            else:
                test_list.append(','.join(row['location']['address'].split(',')))
        else:
            test_list.append(row['location']['address'])
    else:
        test_list.append('')
candidate_df['location_string'] = test_list

target_df = candidate_df.loc[candidate_df['updated_at'] > yesterday][['full_name','role','company',\
    'location_string','active_link','status','vacancy_names','activity_status']]

target_df = target_df.reset_index(drop=True)

target_df = target_df.rename(columns={'full_name':'name','location_string':'location',\
                                      'vacancy_names':'considering for','activity_status':'activity'})
#CEO REQUEST TOGGLE
# target_df = target_df.loc[target_df['considering for'] == 'subsidiary CMO']

report += '\n\n'
report += '<table><tr bgcolor="#2e1a47"><fontcolor ="white">'
for column in target_df.columns.values:
    if column != 'active_link':
        report += '<th>' + column + '</th>'
report += '</fontcolor>'
for index,row in target_df.iterrows():
    if index % 2 == 1:
        report += '<tr bgcolor="#f6efff">'
    else:
        report += '<tr>'
    report += '<td>'
    if row['active_link'] != '':
        report += '''<a href="''' + row['active_link'] + '''">''' + row['name'] + '</a>'
    else:
        report += row['name']
    report += '</td><td>' + row['role'] + '</td><td>' + row['company'] + '</td><td>' + \
        row['location'] + '</td><td>' + row['status'] + '</td><td>' + row['considering for'] + '</td>'
    if row['activity'] == 'contacted':
        report += '<td bgcolor="#f4c741">' + row['activity'] + '</td>'
    elif row['activity'] == 'heard from':
        report += '<td bgcolor="#d86338">' + row['activity'] + '</td>'
    elif row['activity'] == 'corresponded':
        report += '<td bgcolor="#42f4c5">' + row['activity'] + '</td>'
    else:
        report += '<td bgcolor="#3895d8">' + 'note updated' + '</td>'
    report += '</tr>'
report += '</table>'
report += '\n\n'

p_target_df = candidate_df.loc[(candidate_df['updated_at'] > yesterday)][['full_name','role','company',\
    'location_string','active_link','status','vacancy_names','activity_status']]

p_target_df = p_target_df.reset_index(drop=True)

p_target_df = p_target_df.rename(columns={'full_name':'name','location_string':'location',\
                                      'vacancy_names':'considering for','activity_status':'activity'})
#CEO REQUEST TOGGLE
p_target_df = p_target_df.loc[target_df['considering for'] == 'subsidiary CMO']

p_report += '\n\n'
p_report += '<table><tr bgcolor="#2e1a47"><fontcolor ="white">'
for column in p_target_df.columns.values:
    if column != 'active_link':
        p_report += '<th>' + column + '</th>'
p_report += '</fontcolor>'
for index,row in p_target_df.iterrows():
    if index % 2 == 1:
        p_report += '<tr bgcolor="#f6efff">'
    else:
        p_report += '<tr>'
    p_report += '<td>'
    if row['active_link'] != '':
        p_report += '''<a href="''' + row['active_link'] + '''">''' + row['name'] + '</a>'
    else:
        p_report += row['name']
    p_report += '</td><td>' + row['role'] + '</td><td>' + row['company'] + '</td><td>' + \
        row['location'] + '</td><td>' + row['status'] + '</td><td>' + row['considering for'] + '</td>'
    if row['activity'] == 'contacted':
        p_report += '<td bgcolor="#f4c741">' + row['activity'] + '</td>'
    elif row['activity'] == 'heard from':
        p_report += '<td bgcolor="#d86338">' + row['activity'] + '</td>'
    elif row['activity'] == 'corresponded':
        p_report += '<td bgcolor="#42f4c5">' + row['activity'] + '</td>'
    else:
        p_report += '<td bgcolor="#3895d8">' + 'note updated' + '</td>'
    p_report += '</tr>'
p_report += '</table>'
p_report += '\n\n'

subsidiary_stages = vacancy_stages.loc[vacancy_stages['Role'] == 'subsidiary CMO']
p_report += '<table><tr bgcolor="#2e1a47"><fontcolor ="white">'
for column in subsidiary_stages.columns.values:
    p_report += '<th>' + column + '</th>'
p_report += '</fontcolor>'
for index,row in subsidiary_stages.iterrows():
    if index % 2 == 1:
        p_report += '<tr bgcolor="#f6efff">'
    else:
        p_report += '<tr>'
    for column in subsidiary_stages.columns.values:
        if row[column] == 0:
            p_report += '<font color="#B6B6B4"><td>' + str(row[column]) + \
                      '</td></font color>'
        else:
            if column == 'Role':
                level = vacancies_df.loc[vacancies_df['title'] == \
                        row[column]]['priority_value'].iloc[0][1]
                p_report += '<td><b>'
                if level == '0':
                    p_report += '<span style="background-color:#e63b3b;color:#ffffff">'
                elif level == '1':
                    p_report += '<span style="background-color:#fa9327;color=#ffffff">'
                elif level == '2':
                    p_report += '<span style="background-color:#f2cd00;color=#000000">'
                elif level == '3':
                    p_report += '<span style="background-color:#3878b8;color=#ffffff">'
                else:
                    p_report += '<span style="background-color:#059c64;color=#ffffff">'
                p_report += level + '</span> ' + str(row[column]) + '</b></td>'
            else:
#                 if (column != 'Prospect') & (column != 'Initial Outreach') & (column != 'Engaged') & \
#                     (column != 'Intro Call Scheduled') & (column != 'Intro Call Conducted') & \
#                     (column != 'Awaiting Response'):
#                     report += '<td><b>' + str(row[column]) + '</b></td>'
#                 else:
#                     report += '<td><b>' + str(row[column]) + '</b></td>'
                p_report += '<td><b>' + str(row[column]) + '</b></td>'
    p_report += '</tr>'
p_report += '</table>'

report += '\n<font size="+1"><b>Priority Search Pipeline</b></font size>'
report += '<table><tr bgcolor="#2e1a47"><fontcolor ="white">'
for column in vacancy_stages.columns.values:
    report += '<th>' + column + '</th>'
report += '</fontcolor>'
for index,row in vacancy_stages.iterrows():
    if index % 2 == 1:
        report += '<tr bgcolor="#f6efff">'
    else:
        report += '<tr>'
    for column in vacancy_stages.columns.values:
        if row[column] == 0:
            report += '<font color="#B6B6B4"><td>' + str(row[column]) + \
                      '</td></font color>'
        else:
            if column == 'Role':
                level = vacancies_df.loc[vacancies_df['title'] == \
                        row[column]]['priority_value'].iloc[0][1]
                report += '<td><b>'
                if level == '0':
                    report += '<span style="background-color:#e63b3b;color:#ffffff">'
                elif level == '1':
                    report += '<span style="background-color:#fa9327;color=#ffffff">'
                elif level == '2':
                    report += '<span style="background-color:#f2cd00;color=#000000">'
                elif level == '3':
                    report += '<span style="background-color:#3878b8;color=#ffffff">'
                else:
                    report += '<span style="background-color:#059c64;color=#ffffff">'
                report += level + '</span> ' + str(row[column]) + '</b></td>'
            else:
#                 if (column != 'Prospect') & (column != 'Initial Outreach') & (column != 'Engaged') & \
#                     (column != 'Intro Call Scheduled') & (column != 'Intro Call Conducted') & \
#                     (column != 'Awaiting Response'):
#                     report += '<td><b>' + str(row[column]) + '</b></td>'
#                 else:
#                     report += '<td><b>' + str(row[column]) + '</b></td>'
                report += '<td><b>' + str(row[column]) + '</b></td>'
    report += '</tr>'
report += '</table>'

report += '''\n\n<font size="+1"><b>Priority Search Status & Top Candidates</b></font size>

We are currently recruiting for <b>%d</b> active roles.
<b>%d</b> are <span style="background-color:#e63b3b;color:#ffffff"><b> Priority 0</b></span> \
 <i>  (Substantial parent-level risk if role not filled within 3 months)</i>
<b>%d</b> are <span style="background-color:#fa9327;color=#ffffff"><b> Priority 1</b></span> \
 <i>  (Substantial subsidiary-level risk if role not filled within 3 months)</i>
<b>%d</b> are <span style="background-color:#f2cd00;color=#000000"><b> Priority 2</b></span> \
 <i>  (Substantial subsidiary-level risk if role not filled within 6 months)</i>
<b>%d</b> are <span style="background-color:#3878b8;color=#ffffff"><b> Priority 3</b></span> \
 <i>  (Urgent to fill within 6 months)</i>
<b>%d</b> are <span style="background-color:#059c64;color=#ffffff"><b> Priority 4</b></span> \
 <i>  (Important to fill within 6 months)</i>''' % \
       (len(vacancies_df.loc[vacancies_df['status'] == 'open']),\
       len(vacancies_df.loc[vacancies_df['priority_value'] == 'P0']),\
       len(vacancies_df.loc[vacancies_df['priority_value'] == 'P1']),\
       len(vacancies_df.loc[vacancies_df['priority_value'] == 'P2']),\
       len(vacancies_df.loc[vacancies_df['priority_value'] == 'P3']),\
       len(vacancies_df.loc[vacancies_df['priority_value'] == 'P4']))

report += '''
<table>
'''

# for index,row in vacancies_df.loc[vacancies_df['priority'] == 'High'].iterrows():
for index,row in vacancies_df.loc[vacancies_df['status'] == 'open'].iterrows():
    report += '<tr bgcolor="#e6f7ff"><td colspan="3" valign="middle"><b>' + row['title'] + '</b></td><td><b>'
    if (datetime.datetime.today()-datetime.datetime.strptime(row['updated_date_backup'],\
    '%Y-%m-%d')).days > 3:
        report += '<font color="red">' + row['updated_date_backup'] + '</font color>'
    else:
        report += row['updated_date_backup']
    report += '</b></td><td colspan="2" valign="middle"><b>' + str(row['num_contacts']) + \
    ' Candidates</b></td></tr>'
    for ix,rw in priorities.loc[priorities['Vacancy'] == row['title']].iterrows():
        report += '<tr><td>' 
        if rw['Link'] != '':
            report += '''<a href="''' + rw['Link'] + '''">''' + rw['Name'] + '</a>'
        else:
            report += rw['Name']
        
        report += '</td><td>' + rw['Role'] + '</td><td>' + rw['Company'] + \
                  '</td><td>' + rw['Status'] + '</td><td>' + rw['Update Date'] + \
                  '</td><td>' + rw['Next Steps'] + '</td></tr>'

report += '</tr></table>'

p_report += '''
<table>
'''

for index,row in vacancies_df.loc[(vacancies_df['priority'] == 'High') & \
                                  (vacancies_df['title']).str.contains('subsidiary CMO')].iterrows():
    p_report += '<tr bgcolor="#e6f7ff"><td colspan="3" valign="middle"><b>' + row['title'] + '</b></td><td><b>'
    if (datetime.datetime.today()-datetime.datetime.strptime(row['updated_date_backup'],\
    '%Y-%m-%d')).days > 3:
        p_report += '<font color="red">' + row['updated_date_backup'] + '</font color>'
    else:
        p_report += row['updated_date_backup']
    p_report += '</b></td><td><b>' + str(row['num_contacts']) + ' Candidates</b></td></tr>'
    for ix,rw in priorities.loc[priorities['Vacancy'] == row['title']].iterrows():
        p_report += '<tr><td>' 
        if rw['Link'] != '':
            p_report += '''<a href="''' + rw['Link'] + '''">''' + rw['Name'] + '</a>'
        else:
            p_report += rw['Name']
        
        p_report += '</td><td>' + rw['Role'] + '</td><td>' + rw['Company'] + \
                  '</td><td>' + rw['Status'] + '</td><td>' + rw['Update Date'] + '</td></tr>'

p_report += '</tr></table>'

hired_df = candidate_df.loc[candidate_df['status'] == 'Accepted'].copy()
test_list = []
city_list = []
for index,row in hired_df.iterrows():
    for item in row['vacancies']:
        if item['stage']['value'] == 'Accepted':
            test_list.append(item['value'])
    if len(row['location']['address'].split(',')) == 3:
        city_list.append(','.join(row['location']['address'].split(',')[0:2]))
    else:
        if len(row['location']['address'].split(',')) > 1:
            if row['location']['address'].split(',')[1].strip() == 'United States of America':
                city_list.append(row['location']['address'].split(',')[0])
            else:
                city_list.append(row['location']['address'])
        else:
            city_list.append(row['location']['address'])
hired_df['hired_for'] = test_list
hired_df['city'] = city_list

closed_positions = vacancies_df.loc[vacancies_df['status'] == 'closed'].copy()
test_list = []
city_list = []
rorg_list = []
for index,row in closed_positions.iterrows():
    test_list.append(','.join(list(hired_df.loc[hired_df['hired_for'] == row['title']]['full_name'])))
    city_list.append(','.join(list(hired_df.loc[hired_df['hired_for'] == row['title']]['city'])))
    rorg_list.append(','.join(list(hired_df.loc[hired_df['hired_for'] == row['title']]['relationship_origin'])))
closed_positions['Candidate'] = test_list
closed_positions['Location'] = city_list
closed_positions['Relationship Origin'] = rorg_list

closed_positions['priority_value'] = closed_positions['priority_value'].str.replace('P','')
closed_positions = closed_positions[['priority_value','title','num_contacts','Candidate','Location',\
                                     'Relationship Origin']]
closed_positions = closed_positions.rename(columns={'priority_value':'Px','title':'Role',\
                                                    'num_contacts':'# Candidates'})
closed_positions = closed_positions.reset_index(drop=True).sort_values('Px')

def generate_excel_table(workbook,worksheet_name,df):
    workbook.add_worksheet(worksheet_name)
    worksheet = workbook.get_worksheet_by_name(worksheet_name)
    fmt = workbook.add_format({'bold':True})
    worksheet.write(0,0,worksheet_name,fmt)

    for ix,column in enumerate(df.columns.values):
        fmt = workbook.add_format({'bg_color':'#2e1a47','font_color':'white','bold':True})
        worksheet.write(1,ix,column,fmt)
    counter = 2
    for index,row in df.iterrows():
        for col_ix,col in enumerate(df.columns.values):
            fdict = {'border':1,'text_wrap':True}
            if index % 2 == 1:
                fdict['bg_color'] = '#f6efff'
            fmt = workbook.add_format(fdict)
            worksheet.write(counter,col_ix,row[col],fmt)
        counter += 1
    return(worksheet)

def priority_formatter(worksheet,df,priority_name):
    for index,row in df.iterrows():
        level = row[priority_name]
        if level == '0':
            fmt = workbook.add_format({'bg_color':'#e63b3b','font_color':'#ffffff','border':1})
        elif level == '1':
            fmt = workbook.add_format({'bg_color':'#fa9327','font_color':'#ffffff','border':1})
        elif level == '2':
            fmt = workbook.add_format({'bg_color':'#f2cd00','font_color':'#000000','border':1})
        elif level == '3':
            fmt = workbook.add_format({'bg_color':'#3878b8','font_color':'#ffffff','border':1})
        else:
            fmt = workbook.add_format({'bg_color':'#059c64','font_color':'#ffffff','border':1})
        worksheet.write(index+2,0,level,fmt)
    return(worksheet)

vacancy_table = vacancies_df.loc[(vacancies_df['status'] == 'open') & \
                                 (vacancies_df['priority_value'] != '')].sort_values('priority_value')
vacancy_table['Company'] = vacancy_table['title'].str.split(' ').str.get(0)
vacancy_table.loc[~vacancy_table['Company'].str.contains('parent',case=False),'Company'] = 'parent'
vacancy_table['priority_value'] = vacancy_table['priority_value'].str.replace('P','')
vacancy_table['Executive Role'] = vacancy_table['title']
vacancy_table['Executive Role'] = vacancy_table['Executive Role'].replace(vacancy_table['Company'],\
                                  '',regex=True).str.strip()
vacancy_table['Business DRI'] = ''
vacancy_table['People DRI'] = ''
vacancy_table['Search Health'] = ''
vacancy_table['Comments'] = ''
vacancy_table = vacancy_table[['priority_value','Company','Executive Role','Business DRI','People DRI',\
                               'opened_at','Search Health','Comments']]
vacancy_table = vacancy_table.rename(columns={'priority_value':'Priority','opened_at':"Search Initiation"})
vacancy_table = vacancy_table.reset_index(drop=True)

writer = pd.ExcelWriter('C:\\Users\\james.birch\\Documents\\Executive Daily Tracker.xlsx')
# pd.io.formats.excel.header_style = None
workbook = writer.book
workbook.add_worksheet('Pipeline')
worksheet = workbook.get_worksheet_by_name('Pipeline')
fmt = workbook.add_format({'bg_color':'#2e1a47','font_color':'white','bold':True})
worksheet.write(1,0,'Px',fmt)
for ix,column in enumerate(vacancy_stages_full.columns.values):
        worksheet.write(1,ix+1,column,fmt)
for ix,rw in vacancy_stages_full.iterrows():
    level = vacancies_df.loc[vacancies_df['title'] == rw['Role']]['priority_value'].iloc[0][1]
    if level == '0':
        fmt = workbook.add_format({'bg_color':'#e63b3b','font_color':'#ffffff','border':1})
    elif level == '1':
        fmt = workbook.add_format({'bg_color':'#fa9327','font_color':'#ffffff','border':1})
    elif level == '2':
        fmt = workbook.add_format({'bg_color':'#f2cd00','font_color':'#000000','border':1})
    elif level == '3':
        fmt = workbook.add_format({'bg_color':'#3878b8','font_color':'#ffffff','border':1})
    else:
        fmt = workbook.add_format({'bg_color':'#059c64','font_color':'#ffffff','border':1})
    worksheet.write(ix+2,0,level,fmt)
    
    for col,value in enumerate(rw):
        fdict = {'border':1,'text_wrap':True}
        if ix % 2 == 1:
            fdict['bg_color'] = '#f6efff'
        if value != 0:
            fdict['bold'] = True
        else:
            fdict['font_color'] = '#B6B6B4'
        fmt = workbook.add_format(fdict)
        worksheet.write(ix+2,col+1,value,fmt)

fmt = workbook.add_format({'align':'center','valign':'vcenter','bold':True,'font_color':'white',\
                           'bg_color':'#A6A6A6'})
worksheet.merge_range('C1:D1',"CHURN",fmt)
fmt = workbook.add_format({'align':'center','valign':'vcenter','bold':True,'font_color':'white',\
                           'bg_color':'#F79646'})
worksheet.merge_range('E1:G1',"OUTREACH",fmt)
fmt = workbook.add_format({'align':'center','valign':'vcenter','bold':True,'font_color':'white',\
                           'bg_color':'#9BBB59'})
worksheet.merge_range('H1:K1',"INTRODUCTION",fmt)
fmt = workbook.add_format({'align':'center','valign':'vcenter','bold':True,'font_color':'white',\
                           'bg_color':'#31869B'})
worksheet.merge_range('L1:M1',"EVALUATION",fmt)
fmt = workbook.add_format({'align':'center','valign':'vcenter','bold':True,'font_color':'white',\
                           'bg_color':'#403151'})
worksheet.merge_range('N1:O1',"OFFER",fmt)
fmt = workbook.add_format({'bg_color':'#538DD5','font_color':'white','bold':True})
worksheet.write(1,2,'Prospect',fmt)
fmt = workbook.add_format({'bg_color':'#C0504D','font_color':'white','bold':True})
worksheet.write(1,3,'Rejection',fmt)
        
worksheet.set_column(0,0,2)
worksheet.set_column(1,1,23)
worksheet.set_column(2,2,8)
worksheet.set_column(3,3,12.8)
worksheet.set_column(4,4,14.14)
worksheet.set_column(5,5,16.53)
worksheet.set_column(6,6,16.87)
worksheet.set_column(7,7,20.53)
worksheet.set_column(8,8,20.87)
worksheet.set_column(9,9,23.29)
worksheet.set_column(10,10,23.86)
worksheet.set_column(11,11,15.73)
worksheet.set_column(12,12,15.73)

workbook.add_worksheet('Leaderboard')
worksheet = workbook.get_worksheet_by_name('Leaderboard')

fmt = workbook.add_format({'bold':True,'border':1})
worksheet.write(0,0,'Priority Search Status & Top Candidates',fmt)
counter = 1
for index,row in vacancies_df.loc[(vacancies_df['priority'] == 'High') & \
                                  (vacancies_df['status'] == 'open')].iterrows():
    fmt = workbook.add_format({'bg_color':'#e6f7ff','bold':True,'align':'left','border':1})
    worksheet.merge_range(counter,0,counter,3,row['title'],fmt)
    fmt = workbook.add_format({'bg_color':'#e6f7ff','bold':True,'align':'right','border':1})
    worksheet.write(counter,5,str(row['num_contacts']) + ' Candidates',fmt)
#     worksheet.merge_range(counter,4,counter,5,str(row['num_contacts']) + ' Candidates',fmt)
    if (datetime.datetime.today()-datetime.datetime.strptime(row['updated_date_backup'],\
    '%Y-%m-%d')).days > 3:
        fmt = workbook.add_format({'bg_color':'#e6f7ff','bold':True,'font_color':'red','border':1})
    else:
        fmt = workbook.add_format({'bg_color':'#e6f7ff','bold':True,'border':1})
    worksheet.write(counter,4,row['updated_date_backup'],fmt)
    counter += 1
    for ix,rw in priorities.loc[priorities['Vacancy'] == row['title']].iterrows(): 
        fmt = workbook.add_format({'border':1,'text_wrap':True})
        if rw['Link'] != '':
            worksheet.write_url(counter,0,rw['Link'],fmt,string=rw['Name'])
        else:
            worksheet.write(counter,0,rw['Name'],fmt)
        worksheet.write(counter,1,rw['Role'],fmt)
        worksheet.write(counter,2,rw['Company'],fmt)
        worksheet.write(counter,3,rw['Status'],fmt)
        worksheet.write(counter,4,rw['Update Date'],fmt)
        worksheet.write(counter,5,rw['Next Steps'],fmt)
        counter += 1

worksheet.set_column(0,0,32.67)
worksheet.set_column(1,1,75.53)
worksheet.set_column(2,2,23.2)
worksheet.set_column(3,3,20)
worksheet.set_column(4,4,11.6)
worksheet.set_column(5,5,40)

# ***************************************************************************************

links = target_df['active_link'].copy()
target_df = target_df.drop('active_link',1)

workbook.add_worksheet('Activity Report')
worksheet = workbook.get_worksheet_by_name('Activity Report')
fmt = workbook.add_format({'bold':True})

worksheet.write(0,0,'Daily Activity Report',fmt)
for ix,column in enumerate(target_df.columns.values):
    fmt = workbook.add_format({'bg_color':'#2e1a47','font_color':'white','bold':True})
    worksheet.write(1,ix,column,fmt)
counter = 2
for index,row in target_df.iterrows():
    for col_ix,col in enumerate(target_df.columns.values):
        fdict = {'border':1,'text_wrap':True}
        if index % 2 == 1:
            fdict['bg_color'] = '#f6efff'
        if col == 'activity':
            if row['activity'] == 'contacted':
                fdict['bg_color'] = '#f4c741'
            elif row['activity'] == 'heard from':
                fdict['bg_color'] = '#d86338'
            elif row['activity'] == 'corresponded':
                fdict['bg_color'] = '#42f4c5'
            else:
                fdict['bg_color'] = '#3895d8'
                fmt = workbook.add_format(fdict)
                worksheet.write(counter,col_ix,'note updated',fmt)
                continue
        fmt = workbook.add_format(fdict)
        if col == 'name':
            if links[index] != '':
                fdict['font_color'] = '#0000EE'
                fdict['underline'] = True
                fmt = workbook.add_format(fdict)
                worksheet.write_url(counter,col_ix,links[index],fmt,row[col])
            else:
                worksheet.write(counter,col_ix,row[col],fmt)
        else:
            worksheet.write(counter,col_ix,row[col],fmt)
    counter += 1

worksheet.set_column(0,0,22.14)
worksheet.set_column(1,1,80.29)
worksheet.set_column(2,2,54.43)
worksheet.set_column(3,3,23.14)
worksheet.set_column(4,4,22.86)
worksheet.set_column(5,5,26.71)
worksheet.set_column(6,6,12.71)

target_df['active_link'] = links

# ***************************************************************************************

workbook.add_worksheet('Closed Positions')
worksheet = workbook.get_worksheet_by_name('Closed Positions')
fmt = workbook.add_format({'bold':True})
worksheet.write(0,0,'Closed Positions',fmt)

for ix,column in enumerate(closed_positions.columns.values):
    fmt = workbook.add_format({'bg_color':'#2e1a47','font_color':'white','bold':True})
    worksheet.write(1,ix,column,fmt)
counter = 2
for index,row in closed_positions.iterrows():
    for col_ix,col in enumerate(closed_positions.columns.values):
        fdict = {'border':1,'text_wrap':True}
        if index % 2 == 1:
            fdict['bg_color'] = '#f6efff'
        fmt = workbook.add_format(fdict)
        worksheet.write(counter,col_ix,row[col],fmt)
    counter += 1
worksheet = priority_formatter(worksheet,closed_positions,'Px')
    
worksheet.set_column(0,0,2)
worksheet.set_column(1,1,22.67)
worksheet.set_column(2,2,10.53)
worksheet.set_column(3,3,18)
worksheet.set_column(4,4,13.53)
worksheet.set_column(5,5,15.73)

# ***************************************************************************************

worksheet = generate_excel_table(workbook,'Vacancies',vacancy_table)
worksheet = priority_formatter(worksheet,vacancy_table,'Priority')
    
worksheet.set_column(0,0,8.47)
worksheet.set_column(1,1,10.13)
worksheet.set_column(2,2,22.07)
worksheet.set_column(3,3,10.47)
worksheet.set_column(4,4,9)
worksheet.set_column(5,5,13.47)
worksheet.set_column(6,6,11.33)
worksheet.set_column(7,7,53.93)
writer.save()

candidate_df['full_name'] = candidate_df['first_name'] + ' ' + candidate_df['last_name']
df_out = candidate_df[['full_name','role','company','location','vacancy_names','vacancies']].copy()
test_list = []
for index,row in df_out.iterrows():
    if 'address' in row['location']:
        test_list.append(row['location']['address'])
    else:
        test_list.append('')
df_out['location'] = test_list
df_out.to_excel("C:\\Users\\james.birch\\Documents\\Beamery Candidate Dump.xlsx",index=False)

#CMO SEARCH TABLE
cmo_search_df = candidate_df.loc[(candidate_df['vacancy_names'].str.contains('subsidiary CMO'))][['ranking','full_name',\
    'location','role','company','assigned_to','email','last_activity','vacancies','id','status']]

cmo_search_df.loc[cmo_search_df['ranking'] == '','ranking'] = 'U'
cmo_search_df = cmo_search_df.sort_values('ranking',ascending=True)

assignment_dict = {
    '74e5221679ad8e13fa34':'James Birch',
    '96d75e13602a6f3897bc':'Brian Kim',
    '9f01e7986d94b829e92d':'None',
    '63e7ed8a0f9066d03722':'Alan Roemer'
}

test_list = []
locations = []
assignments = []
for index,row in cmo_search_df.iterrows():
    for vacancy in row['vacancies']:
        if 'subsidiary CMO' in vacancy['value']:
            test_list.append(vacancy['stage']['value'])
            break
    if len(row['location']['address'].split(',')) == 3:
        locations.append(','.join(row['location']['address'].split(',')[0:1]))
    elif len(row['location']['address'].split(',')) == 2:
        locations.append(row['location']['address'].split(',')[0])
    else:
        locations.append(row['location']['address'])
    
    try:
        assignments.append(assignment_dict[row['assigned_to']])
    except:
        assignments.append('Other')

cmo_search_df['vacancy_stage'] = test_list
cmo_search_df['location'] = locations
cmo_search_df['assigned_to'] = assignments

cmo_search_df = cmo_search_df.drop('vacancies',1)
cmo_search_df = cmo_search_df.reset_index(drop = True)
cmo_search_df['last_activity'] = cmo_search_df['last_activity'].astype(str).str.slice(0,10)
cmo_search_df['next_steps'] = ''
cmo_search_df['CDA'] = ''

cmo_search_df = cmo_search_df[['ranking','full_name','last_activity','vacancy_stage','next_steps','CDA',\
    'location','role','company','assigned_to','email','status','id']]

writer = pd.ExcelWriter('C:\\Users\\james.birch\\Documents\\CMO Daily Tracker.xlsx')
# pd.io.formats.excel.header_style = None
workbook = writer.book
workbook.add_worksheet('Pipeline')
worksheet = workbook.get_worksheet_by_name('Pipeline')
fmt = workbook.add_format({'bg_color':'#2e1a47','font_color':'white','bold':True})
for ix,column in enumerate(cmo_search_df.columns.values):
        worksheet.write(0,ix,column,fmt)
for ix,rw in cmo_search_df.iterrows():
    for col,value in enumerate(rw):
        fdict = {'border':1}
        if ix % 2 == 1:
            fdict['bg_color'] = '#f6efff'
        fmt = workbook.add_format(fdict)
        if type(value) == list:
            print(value)
        worksheet.write(ix+1,col,value,fmt)
        
worksheet.set_column(0,0,6.2)
worksheet.set_column(1,1,20)
worksheet.set_column(2,2,9.8)
worksheet.set_column(3,3,19.6)
worksheet.set_column(4,4,17)
worksheet.set_column(5,5,3.53)
worksheet.set_column(6,6,12.07)
worksheet.set_column(7,7,69.8)
worksheet.set_column(8,8,46.67)
worksheet.set_column(9,9,10.27)
worksheet.set_column(10,10,28.87)
worksheet.set_column(11,11,17.8)
worksheet.set_column(12,12,34.8)
        
writer.save()

import smtplib
# import email
import email.mime.application
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# me == my email address
# you == recipient's email address
me = email_addr
recipients = [ {INSERT RECIPIENTS HERE} ]

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "Executive Search Daily Update - " + datetime.datetime.today().strftime('%B %d, %Y')
msg['From'] = me
msg['To'] = ", ".join(recipients)

# Create the body of the message (a plain-text and an HTML version).
text = cleanhtml(report)
html = """\
<html>
<head>
<style>
table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
}

td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
}

tr:nth-child(even) {
    background-color: #dddddd;
}
</style>
</head>
<body>
<p>""" + report.replace('\n','<br>') + """</p>
</body>
</html>
"""

# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(part1)
msg.attach(part2)

# PDF attachment
filename='C:\\Users\\james.birch\\Documents\\Executive Daily Tracker.xlsx'
fileMsg = email.mime.base.MIMEBase('application','vnd.ms-excel')
fileMsg.set_payload(open(filename,'rb').read())
email.encoders.encode_base64(fileMsg)
fileMsg.add_header('Content-Disposition','attachment;filename=Executive Daily Tracker.xlsx')
msg.attach(fileMsg)

# Send the message via local SMTP server.
s = smtplib.SMTP('smtp.office365.com',587)
s.connect('smtp.office365.com',587)
s.ehlo()
s.starttls()
s.ehlo()
s.login(email_addr,password)
# sendmail function takes 3 arguments: sender's address, recipient's address
# and message to send - here it is sent as one string.
for person in recipients:
    s.sendmail(me, person, msg.as_string())    
# s.sendmail(me, you, msg.as_string())
s.quit()

# **********************************************************************************************

# me == my email address
# you == recipient's email address
me = email_addr
recipients = [ {INSERT RECIPIENTS HERE} ]

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "subsidiary CMO Search Daily Update - " + datetime.datetime.today().strftime('%B %d, %Y')
msg['From'] = me
msg['To'] = ", ".join(recipients)

# Create the body of the message (a plain-text and an HTML version).
text = cleanhtml(report)
html = """\
<html>
<head>
<style>
table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
}

td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
}

tr:nth-child(even) {
    background-color: #dddddd;
}
</style>
</head>
<body>
<p>""" + p_report.replace('\n','<br>') + """</p>
</body>
</html>
"""

# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(part1)
msg.attach(part2)

# Send the message via local SMTP server.
s = smtplib.SMTP('smtp.office365.com',587)
s.connect('smtp.office365.com',587)
s.ehlo()
s.starttls()
s.ehlo()
s.login(email_addr,password)
# sendmail function takes 3 arguments: sender's address, recipient's address
# and message to send - here it is sent as one string.
for person in recipients:
    s.sendmail(me, person, msg.as_string())    
# s.sendmail(me, you, msg.as_string())
s.quit()
