import slack, certifi
import ssl as ssl_lib

token = '' #Copy from your 
ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
slack_client = slack.WebClient(token=token, ssl=ssl_context)


def lambda_handler(event, context):
    #Handle an incoming HTTP request from a Slack chat-bot.
    
    print(event)  # For checking the event in cloudwatch logs

    def usr_message(message, channel):
        response = slack_client.chat_postMessage(
            channel=channel,
            text=message
        )
        return response.status_code

    user_id = event['event']['user']
    channel = event['event']['channel']

    t_user_message = event['event']['blocks'][0]['elements'][0]['elements']
    user_message1 = ''

    for i in t_user_message:
        if 'text' in i:
            i['text'] = i['text'].replace(u'\xa0', u' ')
            user_message1 = user_message1 + i['text']
    user_message = user_message1.strip().lower()
    user_message = user_message.replace(u'“', u'"')
    user_message = user_message.replace(u'”', u'"')
    print(f'''User {user_id} Requesting app from channel {channel}''')
    print(user_message)

    if user_message == 'help':
        return_message = f'''Hello <@{user_id}>, I am your slack helper.'''
        slack_res = usr_message(return_message, channel)
    else:
        return_message = f'''Hello <@{user_id}>, I am an unfinished application with only `help` command. Please configure more accordingly!!!'''
        slack_res = usr_message(return_message, channel)
    return slack_res
