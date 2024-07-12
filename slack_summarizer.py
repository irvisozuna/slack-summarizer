import os
import openai
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.rtm_v2 import RTMClient

# Configurar API keys
slack_token = os.getenv('SLACK_BOT_TOKEN')
openai.api_key = os.getenv('OPENAI_API_KEY')

# Crear cliente de Slack
client = WebClient(token=slack_token)

def get_thread_messages(channel_id, thread_ts):
    try:
        response = client.conversations_replies(channel=channel_id, ts=thread_ts)
        messages = [msg['text'] for msg in response['messages']]
        return messages
    except SlackApiError as e:
        print(f"Error fetching thread: {e.response['error']}")
        return []

def summarize_text(text):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Summarize the following text:\n\n{text}",
        max_tokens=150
    )
    return response.choices[0].text.strip()

def handle_message(event_data):
    message = event_data['event']
    if '#resume' in message.get('text', ''):
        channel_id = message['channel']
        thread_ts = message['thread_ts'] if 'thread_ts' in message else message['ts']
        messages = get_thread_messages(channel_id, thread_ts)
        full_text = "\n".join(messages)
        summary = summarize_text(full_text)
        client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text=f"#resume\nSummary: {summary}")

if __name__ == "__main__":
    rtm_client = RTMClient(token=slack_token)
    rtm_client.on(event="message", callback=handle_message)
    print("Bot is running...")
    rtm_client.start()
