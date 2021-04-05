import slack, certifi, json
import ssl as ssl_lib
import boto3, os
import datetime as datetime
import requests
import json

token = 'Slack-Token'
ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
slack_client = slack.WebClient(token=token, ssl=ssl_context)
headers = {'content-type': 'application/json'}
#my_slack_channel = "#my-workspace"

def lambda_handler(event, context):
    #print(event)
    if event['httpMethod'] == 'POST':
        msg_to_send = json.loads(event['body'])
        #print(msg_to_send)
    else:
        msg_to_send = {"msg": "`Test Msg`", "channel": "#my-workspace"}

    expected_keys_list = msg_to_send.keys()

    if 'ticket_id' in expected_keys_list:
        ticket_id = msg_to_send['ticket_id']

    if 'ticket_sub' in expected_keys_list:
        ticket_sub = msg_to_send['ticket_sub']

    if 'portal_name' in expected_keys_list:
        portal_name = msg_to_send['portal_name']

    if 'ticket_type' in expected_keys_list:
        ticket_type = msg_to_send['ticket_type']

    if 'ticket_url' in expected_keys_list:
        ticket_url = msg_to_send['ticket_url']

    if 'channel' in expected_keys_list:
        channel = msg_to_send['channel']

    aws_accnt = {
        'NOC-Freedy': ['apikey', 'apiurl'], 
        'NOC-Desk': ['apikey', 'apiurl'], 
        'NOC-Staging': ['apikey', 'apiurl']
    }

    cross_account_role = {
        'acct-id': 'acct-role'
    }

    def get_perma_link(chn, thread):
        perma_url = "https://slack.com/api/chat.getPermalink"
        params = {"token": token, "channel": chn, "message_ts": thread}
        res = requests.get(url=perma_url, params=params)
        if res.status_code == 200:
            output = res.text
            output_js = json.loads(output)
            perma_link = output_js['permalink']
            return perma_link
        else:
            perma_link = "Unable to get perma link"
            return perma_link

    def add_note_ticket(code, permalink):
        if code == 200:
            ticketid = ticket_id.split('-')[1]
            api_url = aws_accnt[portal_name][1]
            api_key = aws_accnt[portal_name][0]
            apiurl = f'{api_url}/{ticketid}/notes'
            print("apiurl", apiurl)
            data = {
                "body": f'''Kindly check the below slack permalink for status of this\n{permalink}'''
            }
            data = json.dumps(data)
            content = requests.post(apiurl, data=data, auth=(api_key, 'xx'), headers=headers)
            return content.status_code

    def new_usr_message(message, channel, color):
        def_slack_json_template = {
            "attachments": [
                {
                    "color": color,
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": message
                            }
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Redis Labs",
                                        "emoji": True
                                    },
                                    "value": "redis_labs",
                                    "url": "redislabds url"
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "SOP",
                                        "emoji": True
                                    },
                                    "value": "SOP",
                                    "url": "sop"
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Owner Details",
                                        "emoji": True
                                    },
                                    "value": "Owner Details",
                                    "url": "details"
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Infra Oncall",
                                        "emoji": True
                                    },
                                    "value": "Infra Oncall",
                                    "url": "oncall"
                                }
                            ]
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": "*Posted by NOC Automator* "
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        l_url = "https://slack.com/api/chat.postMessage"
        params = {"token": token, "channel": channel,
                  "attachments": json.dumps(def_slack_json_template['attachments'])}
        res = requests.post(url=l_url, params=params)
        code = res.status_code
        res = res.text
        res = json.loads(res)
        thread = res['ts']
        chn = res['channel']
        permalink = get_perma_link(chn, thread)
        print(permalink)
        # return code, thread, permalink
        result = add_note_ticket(code, permalink)
        print("Output of posting permalink in slack is ", result)

    def usr_message(message, channel):
        response = slack_client.chat_postMessage(
            channel=channel,
            text=message
        )
        code = response.status_code
        print(response)
        thread = response['ts']
        chn = response['channel']
        permalink = get_perma_link(chn, thread)
        print(permalink)
        #return code, thread, permalink
        result = add_note_ticket(code, permalink)
        print("Output of posting permalink in slack is ", result)

    def graph_upload(filename, name, initial_cmt, channel):
        file_name = filename
        name = name
        initial_cmt = initial_cmt
        upload_graph = slack_client.files_upload(
                channels=channel,
                file=file_name,
                filename=name,
                initial_comment=initial_cmt,
            )
        code = upload_graph.status_code
        print(upload_graph)
        key = upload_graph['file']['shares']['private'].keys()
        for k in key:
            chn = k #channel id
        chn = chn
        value = upload_graph['file']['shares']['private'].values()
        for v in value:
            ts_i = v
        thread = ts_i[0]['ts']
        permalink = get_perma_link(chn, thread)
        print(permalink)
        #return code, thread, permalink
        result = add_note_ticket(code, permalink)
        print("Output of posting permalink in slack is ", result)

    def view_ticket(id, api_url, api_key):
        url_to_connect = f'{api_url}/{id}'
        # print(url_to_connect)
        try:
            content = requests.get(url_to_connect, auth=(api_key, 'xx'), headers=headers)
            # print(content.text)
            tick_code = content.status_code

            if tick_code == 200:
                # print("in true part")
                final = json.loads(content.text)
                # print(type(final))
                return final
            else:
                # print("in false part")
                tick_view = "Failed"
                return tick_view
        except:
            tick_view = "Failed"
            return tick_view

    def ticket_find(ticket_id, ticket_sub, aws_acct, ticket_type, ticket_url, channel):
        #hit api with ticket id to get ticket description
        api_key = aws_accnt[aws_acct][0]
        api_url = aws_accnt[aws_acct][1]
        n_ticket = ticket_id.split('-')[1]
        ticket_description_text = view_ticket(n_ticket, api_url, api_key)
        #print(ticket_description_text)
        #print(type(ticket_description_text))
        ticket_description_text = ticket_description_text['ticket']['description_text']
        #print(type(ticket_description_text))
        if ticket_type == "CW_ALARM" and ticket_description_text != "Failed":
            #print("in 2 true")
            #Ticket is an cloudwatch alarm ticket
            ticket_description_text = ticket_description_text.replace('\r','')
            ticket_description_text = ticket_description_text.replace('\\','')
            ticket_desc_list = ticket_description_text.split('\n')
            while ('' in ticket_desc_list):
                ticket_desc_list.remove('')
            alarm_arn = [s for s in ticket_desc_list if "Alarm Arn" in s]
            alarm_arn_final = str(alarm_arn[0])[2:].split('Alarm Arn:')[1].strip()
            alarm_aws_acct = [s for s in ticket_desc_list if "AWS Account" in s]
            alr_aws_acct = str(alarm_aws_acct[0]).split(':')[1].strip()
            alarm_reg = str(alarm_arn).split(':')[4]
            #print(alarm_reg, str(alarm_aws_acct[0]).split(':')[1].strip())
            #alarm_url = ticket_desc_list[2]
            alarm_url = [s for s in ticket_desc_list if "https://" in s]
            alarm_url = alarm_url[0]
            alarm_name = [s for s in ticket_desc_list if "Name" in s]
            alarm_name = str(alarm_name[0]).split(':')[1].strip()
            #alarm_name = alarm_arn_final.split(':')[-1]
            #cloudclient = boto3.client('cloudwatch', alarm_reg)
            product_arn = cross_account_role[alr_aws_acct]
            try:
                sts_client = boto3.client('sts')
                rolearn_value = product_arn
                response = sts_client.assume_role(RoleArn=rolearn_value, RoleSessionName="my_session")
                cloudclient = boto3.client('cloudwatch', alarm_reg,
                                      aws_access_key_id=response['Credentials']['AccessKeyId'],
                                      aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                                      aws_session_token=response['Credentials']['SessionToken'])
            except:
                print("Exception: Unable to use cross account role for ", rolearn_value)
                exit(0)


            details = cloudclient.describe_alarms(
                AlarmNames=[
                    alarm_name,
                ],
            )
            print(details)  # to refer in cloudwatch logs
            output = details

            if len(output['MetricAlarms']) != 0:
                #Alarm details fetched properly
                filter_output = output['MetricAlarms']
            else:
                exp_out = f'''Unable to get alarm details for `Alarm_Name:`:{alarm_name}`Ticket_URL:`{ticket_url}`Ticket_SUB:`{ticket_sub}'''
                print("Exception: ", exp_out)
                exit(0)
            # print(filter_output)
            if 'Namespace' in filter_output[0]:
                ALR_Namespace = filter_output[0]['Namespace']
            else:
                ALR_Namespace = filter_output[0]['Metrics'][0]['MetricStat']['Metric']['Namespace']
            # print(ALR_Namespace)
            if ALR_Namespace == 'AWS/ELB' or ALR_Namespace == 'AWS/SQS' or ALR_Namespace == 'AWS/EBS' or ALR_Namespace == 'AWS/ApplicationELB' or ALR_Namespace == 'AWS/RDS' \
                    or ALR_Namespace == 'AWS/NetworkELB' or ALR_Namespace == 'AWS/Lambda' or ALR_Namespace == 'AWS/EFS' or ALR_Namespace == 'LogMetrics' \
                    or ALR_Namespace == 'AWS/EC2' or ALR_Namespace == 'AWS/OpsWorks' or ALR_Namespace == 'AWS/ECS' or ALR_Namespace == 'AWS/DynamoDB' or ALR_Namespace == 'AWS/ElastiCache' \
                    or ALR_Namespace == 'central-iris-prod' or ALR_Namespace == 'euc-central' or ALR_Namespace == 'mumbai-central' or ALR_Namespace == 'sydney-central':
                ALR_Alarmname_raw = filter_output[0]['AlarmName']
                string1 = ALR_Alarmname_raw.replace("'", "\\'")
                ALR_Alarmname = string1.replace('"', '\\"')
                len_d = len(filter_output[0]['Dimensions'])
                if len(filter_output[0]['Dimensions']) != 0:
                    ALR_Queuename = filter_output[0]['Dimensions'][0]['Name']
                    ALR_Queuevalue = filter_output[0]['Dimensions'][0]['Value']
                    ALR_Dimesions_length = len(filter_output[0]['Dimensions'])
                    if ALR_Dimesions_length > 1:
                        ALR_Queuename_1 = filter_output[0]['Dimensions'][1]['Name']
                        ALR_Queuevalue_1 = filter_output[0]['Dimensions'][1]['Value']
                        Graph_Json = 13
                    else:
                        Graph_Json = 11
                    ALR_Statistic = filter_output[0]['Statistic']
                    ALR_DatapointsToAlarm = filter_output[0]['EvaluationPeriods']
                    ALR_Period = filter_output[0]['Period']
                    ALR_ComparisonOperator = filter_output[0]['ComparisonOperator']
                    ALR_StateValue = filter_output[0]['StateValue']
                    ALR_Threshold = filter_output[0]['Threshold']
                    ALR_MetricName = filter_output[0]['MetricName']
                    ALR_Alarm_state_reason = filter_output[0]['StateReason']
                    file_tmp_smp = datetime.datetime.now()
                    final_output = f'''
*Namespace:* {ALR_Namespace}
*MetricName:* {ALR_MetricName}
*State of alarm:* `{ALR_StateValue}`
*Reason:* `{ALR_Alarm_state_reason}`
*Threshold Breach* for {ALR_MetricName}, Value should be {ALR_ComparisonOperator} {ALR_Threshold} for {ALR_DatapointsToAlarm} Datapoint within {ALR_DatapointsToAlarm} * {ALR_Period} seconds 
'''
                else:
                    print("Bot-alarms type")
                    file_tmp_smp = datetime.datetime.now()
                    m_dp = filter_output[0]['DatapointsToAlarm']
                    m_n = filter_output[0]['AlarmName']
                    m_de = filter_output[0]['EvaluationPeriods']
                    m_ns = filter_output[0]['Metrics'][0]['MetricStat']['Metric']['Namespace']
                    m_na = filter_output[0]['Metrics'][0]['MetricStat']['Metric']['MetricName']
                    ALR_MetricName = filter_output[0]['Metrics'][0]['MetricStat']['Metric']['MetricName']
                    m_id = filter_output[0]['Metrics'][0]['Id']
                    m_state = filter_output[0]['StateValue']
                    m_state_r = filter_output[0]['StateReason']
                    m_st = filter_output[0]['Metrics'][0]['MetricStat']['Stat']
                    m_period = filter_output[0]['Metrics'][0]['MetricStat']['Period']
                    if filter_output[0]['Metrics'][0]['ReturnData'] == True:
                        m_vs = "true"
                    else:
                        m_vs = False
                    m1_id = filter_output[0]['Metrics'][1]['Id']
                    m1_ex = filter_output[0]['Metrics'][1]['Expression']
                    m1_lb = filter_output[0]['Metrics'][1]['Label']
                    if filter_output[0]['Metrics'][1]['ReturnData'] == True:
                        m1_vs = "true"
                    else:
                        m1_vs = False
                    b_region = filter_output[0]['AlarmArn'].split(':')[3]
                    if len(filter_output[0]['Metrics'][0]['MetricStat']['Metric']['Dimensions']) > 0:
                        m_dn = filter_output[0]['Metrics'][0]['MetricStat']['Metric']['Dimensions'][0]['Name']
                        m_dv = filter_output[0]['Metrics'][0]['MetricStat']['Metric']['Dimensions'][0]['Value']
                        b_json = f'''
                                                                "metrics": [
                                                                    [ "{m_ns}", "{m_na}", "{m_dn}", "{m_dv}", {{ "id": "{m_id}", "stat": "{m_st}", "visible": {m_vs} }} ],
                                                                    [ {{  "id": "{m1_id}", "expression": "{m1_ex}", "label": "{m1_lb}", "visible": {m1_vs}, "region": "{b_region}"  }} ]
                                                                ]'''
                    else:
                        b_json = f'''
                                                                "metrics": [
                                                                      [ "{m_ns}", "{m_na}", {{ "id": "{m_id}", "stat": "{m_st}", "visible": {m_vs} }} ],
                                                                      [ {{  "id": "{m1_id}", "expression": "{m1_ex}", "label": "{m1_lb}", "visible": {m1_vs}, "region": "{b_region}"  }} ]
                                                                ]
                                                            '''

                    Graph_Json = 14
                    final_output = f'''
*Namespace:* {m_ns}
*MetricName:* {m_na}
*State of alarm:* `{m_state}`
*Reason:* `{m_state_r}`
'''
                if Graph_Json == 14:
                    print("Inside 14 graph json")
                    abc = f'''{{
                                                "region": "{b_region}",
                                                {b_json},
                                                "view": "timeSeries",
                                                "stacked": false,
                                                "period": {m_period},
                                                "title": "{m_n}",
                                                "width": 900, 
                                                "height": 250, 
                                                "start": "-PT3H",
                                                "end": "P0D",
                                                "timezone": "+0530" 
                                                }}
                                    '''
                elif Graph_Json == 11:
                    print("Lambda inside graph_json 11")
                    abc = '''
                                                                {{"metrics": [["{}", "{}", "{}", 
                                                                                                    "{}", {{"stat": "{}"}}]], 
                                                                    "view": "timeSeries", 
                                                                    "period": {}, 
                                                                    "annotations": {{
                                                                        "horizontal": [
                                                                            {{
                                                                                "label": "For TH Breach: {}*{} Seconds in {} Datapoints, Metric should be {}", 
                                                                                "value": {}
                                                                            }}
                                                                        ]
                                                                    }},
                                                                    "title": "{}",
                                                                    "width": 900, 
                                                                    "height": 250, 
                                                                    "start": "-PT3H",
                                                                    "end": "P0D" ,
                                                                    "timezone": "+0530"
                                                                }}
                                                                '''.format(ALR_Namespace, ALR_MetricName, ALR_Queuename,
                                                                           ALR_Queuevalue,
                                                                           ALR_Statistic,
                                                                           ALR_Period,
                                                                           ALR_DatapointsToAlarm, ALR_Period,
                                                                           ALR_DatapointsToAlarm,
                                                                           ALR_ComparisonOperator,
                                                                           ALR_Threshold, ALR_Alarmname)
                else:
                    # print("Lambda inside graph_json 13 and below are queue1 and value1")
                    # print(ALR_Queuename_1, ALR_Queuevalue_1)
                    print("Inside 13")
                    abc = '''
                                                                {{"metrics": [["{}", "{}", "{}", "{}", "{}","{}", {{"stat": "{}"}}]], 
                                                                    "view": "timeSeries", 
                                                                    "period": {}, 
                                                                    "annotations": {{
                                                                        "horizontal": [
                                                                            {{
                                                                                "label": "For TH Breach: {}*{} Seconds in {} Datapoints, Metric should be {}", 
                                                                                "value": {}
                                                                            }}
                                                                        ]
                                                                    }},
                                                                    "title": "{}",
                                                                    "width": 900, 
                                                                    "height": 250, 
                                                                    "start": "-PT3H",
                                                                    "end": "P0D",
                                                                    "timezone": "+0530" 
                                                                }}
                                                                '''.format(ALR_Namespace, ALR_MetricName, ALR_Queuename,
                                                                           ALR_Queuevalue,
                                                                           ALR_Queuename_1,
                                                                           ALR_Queuevalue_1, ALR_Statistic, ALR_Period,
                                                                           ALR_DatapointsToAlarm, ALR_Period,
                                                                           ALR_DatapointsToAlarm,
                                                                           ALR_ComparisonOperator,
                                                                           ALR_Threshold, ALR_Alarmname)
                # print(abc)
                try:
                    response1 = cloudclient.get_metric_widget_image(MetricWidget=abc)
                    filename = f'''/tmp/{ALR_MetricName}_{file_tmp_smp}.png'''
                    with open(filename, 'wb') as f:
                        f.write(response1["MetricWidgetImage"])
                        f.close()
                    command = f'''ls -lrt /tmp/*png'''
                    print(os.popen(command).read())
                    name = f'''{ALR_MetricName}_{file_tmp_smp}.png'''
                    initial_cmt = f'''*Ticket_URL: * {ticket_url}\n *Subject: * {ticket_sub}\n *Alarm_URL: * {alarm_url}\
{final_output} '''
                    graph_upload(filename, name, initial_cmt, channel)
                    command = f'''rm -f "{filename}"'''
                    os.popen(command).read()
                    #return inout
                except:
                    print("In except block 1")
                    message = f'''*Ticket_URL: * {ticket_url}\n *Subject: * {ticket_sub}\n *Alarm_URL: * {alarm_url}{final_output} and there was aaa problem with metric widget image'''
                    usr_message(message, channel)
                    #return ou
            else:
                ALR_Alarmname_raw = filter_output[0]['AlarmName']
                string1 = ALR_Alarmname_raw.replace("'", "\\'")
                ALR_Alarmname = string1.replace('"', '\\"')
                if 'Statistic' in filter_output[0]:
                    ALR_Statistic = filter_output[0]['Statistic']
                else:
                    ALR_Statistic = filter_output[0]['ExtendedStatistic']
                ALR_DatapointsToAlarm = filter_output[0]['EvaluationPeriods']
                ALR_Period = filter_output[0]['Period']
                ALR_ComparisonOperator = filter_output[0]['ComparisonOperator']
                ALR_StateValue = filter_output[0]['StateValue']
                ALR_Threshold = filter_output[0]['Threshold']
                ALR_MetricName = filter_output[0]['MetricName']
                ALR_Alarm_state_reason = filter_output[0]['StateReason']
                file_tmp_smp = datetime.datetime.now()
                final_output = f'''
*Namespace:* {ALR_Namespace}
*MetricName:* {ALR_MetricName}
*State of alarm:* `{ALR_StateValue}`
*Reason:* `{ALR_Alarm_state_reason}`
*Threshold Breach* for {ALR_MetricName}, Value should be  {ALR_ComparisonOperator} {ALR_Threshold} for {ALR_DatapointsToAlarm} Datapoint within {ALR_DatapointsToAlarm} * {ALR_Period} seconds
'''
                abc = '''
                                 {{"metrics": [["{}", "{}", {{"stat": "{}"}}]], 
                                     "view": "timeSeries", 
                                     "period": {}, 
                                     "annotations": {{
                                         "horizontal": [
                                             {{
                                                 "label": "For TH Breach: {}*{} Seconds in {} Datapoints, Metric should be {}", 
                                                 "value": {}
                                             }}
                                         ]
                                    }},
                                     "title": "{}",
                                     "stacked": true,
                                     "width": 900, 
                                     "height": 450, 
                                     "start": "-PT3H",
                                     "end": "P0D",
                                     "timezone": "+0530" 
                                 }}
                                 '''.format(ALR_Namespace, ALR_MetricName, ALR_Statistic, ALR_Period,
                                            ALR_DatapointsToAlarm, ALR_Period, ALR_DatapointsToAlarm,
                                            ALR_ComparisonOperator,
                                            ALR_Threshold, ALR_Alarmname)
                try:
                    response1 = cloudclient.get_metric_widget_image(MetricWidget=abc)
                    filename = f'''/tmp/{ALR_MetricName}_{file_tmp_smp}.png'''
                    with open(filename, 'wb') as f:
                        f.write(response1["MetricWidgetImage"])
                        f.close()
                    command = f'''ls -lrt /tmp/*png'''
                    # print(os.popen(command).read())
                    name = f'''{ALR_MetricName}_{file_tmp_smp}.png'''
                    initial_cmt = f'''*Ticket_URL: * {ticket_url}\n *Subject: * {ticket_sub}\n *Alarm_URL: * {alarm_url}{final_output}'''
                    graph_upload(filename, name, initial_cmt, channel)
                    command = f'''rm -f "{filename}"'''
                    os.popen(command).read()
                    #return inout
                except:
                    print("In except block 2")
                    message = f'''*Ticket_URL: * {ticket_url}\n *Subject: * {ticket_sub}\n *Alarm_URL: * {alarm_url}{final_output} and there was a problem with metric widget image'''
                    usr_message(message, channel)
                    #return ou
            #final_msg = f'''*Ticket_URL: * {ticket_url}\n *Subject: * {ticket_sub}\n *Alarm_URL: * {alarm_url}\n *Alarm_ARN: * {alarm_arn_final}'''
            #usr_message(final_msg, my_slack_channel)
        elif ticket_type == "REDIS" and ticket_description_text != "Failed":
            ticket_description_text = ticket_description_text.replace('\r', '')
            ticket_description_text = ticket_description_text.replace('\\', '')
            ticket_desc_list = ticket_description_text.split('\n')
            while ('' in ticket_desc_list):
                ticket_desc_list.remove('')

            try:
                redis_size = [s for s in ticket_desc_list if "indicated below" in s]
                redis_size = str(redis_size)[2:-2]
            except:
                redis_size = ''

            def extract_content(key):
                try:
                    key = [s for s in ticket_desc_list if key in s]
                    key = str(key[0]).strip()
                except:
                    key = ''
                return key

            account = extract_content("Account: ")
            Subs = extract_content("Subscription: ")
            db_id = extract_content("Database Id: ")
            db_enp = extract_content("Database Endpoint: ")
            db_name = extract_content("Database Name: ")
            res_name = extract_content("Resource Name: ")

            redis_content = f'''*Ticket_URL:* {ticket_url}\n*Subject*: {ticket_sub}\n\n'''
            if 'alert off' in ticket_sub:
                colour = '#228B22'
            else:
                colour = '#ff0000'
            if len(redis_size) > 0:
                redis_content = redis_content + f'''{redis_size}\n'''
            if len(res_name) > 0:
                redis_content = redis_content + f'''{res_name}\n'''
            if len(account) > 0:
                redis_content = redis_content + f'''{account}\n'''
            if len(Subs) > 0:
                redis_content = redis_content + f'''{Subs}\n'''
            if len(db_id) > 0:
                redis_content = redis_content + f'''{db_id}\n'''
            if len(db_enp) > 0:
                redis_content = redis_content + f'''{db_enp}\n'''
            if len(db_name) > 0:
                redis_content = redis_content + f'''{db_name}\n'''
            new_usr_message(redis_content, channel, colour)
        else:
            #print("in 2 false")
            msg_to_send = {
                "msg": f'''NOC Automator failed to fetch details for this ticket. Kindly check manually,\n*Ticket_URL: * \
{ticket_url}\n *Subject: * {ticket_sub}''', "channel": {channel}}
            usr_message(msg_to_send['msg'], msg_to_send['channel'])

    if "ticket_id" in locals() and "ticket_sub" in locals() and "ticket_url" in locals()\
            and "portal_name" in locals() and "ticket_type" in locals() and "channel" in locals():
        #proceed with logic
        #print("in 1 true")
        ticket_find(ticket_id, ticket_sub, portal_name, ticket_type, ticket_url, channel)
        #print("final ", fin_out)
    else:
        #print("in 1 false")
        usr_message(msg_to_send['msg'], msg_to_send['channel'])

