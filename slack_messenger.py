from fastapi import HTTPException
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class SlackMessenger:
    def __init__(self, token: str, channel: str):
        self.slack_client = WebClient(token=token)
        self.channel = channel

    def send_message(self, message: str):
        try:
            response = self.slack_client.chat_postMessage(
                channel=self.channel,
                text=message
            )
            print(f"Message sent: {response['message']['text']}")
        except SlackApiError as e:
            print(f"Error sending Slack message: {e.response['error']}")
            raise HTTPException(status_code=500, detail=f"Slack API Error: {e.response['error']}")

