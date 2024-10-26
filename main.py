from fastapi import FastAPI, Request
from slack_bolt import App as SlackApp
from slack_bolt.adapter.fastapi import SlackRequestHandler
from slack_messenger import SlackMessenger
from booking_checker import BookingChecker
from models import SiteConfig
import json
import os
from dotenv import load_dotenv
from config_utils import load_config
from json_utils import append_to_json_file
from scheduler_tasks import start_scheduler, send_test_message, check_and_save_availability
import threading

# .env 파일 로드
load_dotenv()

app = FastAPI()

# Slack Bolt 앱 초기화
slack_app = SlackApp(token=os.getenv("BOT_USER_OAUTH_TOKEN"), signing_secret=os.getenv("SLACK_SIGNING_SECRET"))
slack_handler = SlackRequestHandler(slack_app)

# 스케줄러를 별도의 스레드에서 시작
scheduler_thread = threading.Thread(target=start_scheduler)
scheduler_thread.start()

@slack_app.command("/checkbooking")
def check_booking_command(ack, body, client):
    ack("Booking check started. We will notify you once the results are ready.")
    configs = load_config()

    slack_messenger = SlackMessenger(
        token=os.getenv("BOT_USER_OAUTH_TOKEN"),
        channel=os.getenv("SLACK_ESCAPEROOM_CHANNEL")
    )

    messages = []
    for config in configs:
        checker = BookingChecker(config)
        available_times = checker.check_booking()
    
        if available_times:
            messages.append(f"{config.title} ({config.date}): {', '.join(available_times)}")
        else:
            messages.append(f"{config.title} ({config.date}): 예약 가능한 시간대가 없습니다.")

    # 모든 지점의 예약 가능 시간을 한 번에 전송
    full_message = "\n".join(messages)
    slack_messenger.send_message(full_message)

@slack_app.command("/addlist")
def add_list_command(ack, body, client):
    text = body.get('text', '').strip()
    user_id = body["user_id"]

    # 인자를 json에 저장합니다.
    if text:
        data = {"user_id" : user_id, "entry" : text}
        append_to_json_file(data, 'addlist.json')
    
        ack(f"'{text}'가 신청 리스트에 저장되었습니다.")
    else:
        ack(f"알람에 추가 할 방탈출명과 날짜를 입력해주세요.")

# Slack 명령어 처리
@slack_app.command("/hello")
def hello_command(ack, body):
    user_id = body["user_id"]
    ack(f"Hi, <@{user_id}>!")

# FastAPI와 Slack Bolt 통합
@app.post("/slack/events")
async def slack_events(req: Request):
    return await slack_handler.handle(req)
