import schedule
import time
import json
import os
from slack_messenger import SlackMessenger
from dotenv import load_dotenv
from booking_checker import BookingChecker
from config_utils import load_config
from datetime import datetime
from config_utils import load_config
from json_utils import save_to_json_file

# .env 파일 로드
load_dotenv()

# SlackMessenger 인스턴스 생성
slack_messenger = SlackMessenger(
    token=os.getenv("BOT_USER_OAUTH_TOKEN"),
    channel=os.getenv("SLACK_TEST_CHANNEL")
)

def send_test_message():
    slack_messenger.send_message("테스트 입니다")

def check_and_save_availability():
    configs = load_config()
    availability_data = []

    # 이전 상태를 로드
    if os.path.exists('availability.json'):
        with open('availability.json', 'r', encoding='utf-8') as file:
            previous_data = json.load(file)
    else:
        previous_data = []

    previous_dict = {entry['title']: entry for entry in previous_data}

    for config in configs:
        checker = BookingChecker(config)
        available_times = checker.check_booking()

        # 현재 상태 저장
        current_entry = {
            "title": config.title,
            "date": config.date,
            "available_times": available_times if available_times else []
        }
        availability_data.append(current_entry)

        # 이전 상태와 비교
        if config.title in previous_dict:
            previous_entry = previous_dict[config.title]
            if previous_entry['available_times'] != current_entry['available_times']:
                # 변화가 있으면 Slack으로 메시지 전송
                message = f"변경된 예약 현황:\nTitle: {config.title}\nDate: {config.date}\nAvailable Times: {', '.join(current_entry['available_times'])}"
                slack_messenger.send_message(message)

    # 결과를 availability.json 파일에 저장
    with open('availability.json', 'w', encoding='utf-8') as file:
        json.dump(availability_data, file, ensure_ascii=False, indent=4)

    print("Availability data has been checked and updated.") 

def update_config_for_today():
    today = datetime.now().strftime("%Y-%m-%d")

    configs = load_config()

    for config in configs:
        if config.get("date") == today:
            config["commented"] = True
        
    save_to_json_file(configs, 'config.json')
    

def start_scheduler():
    """
    다양한 작업을 위한 스케줄러 시작.
    """
    # check_and_save_availability 함수를 3분마다 실행
    schedule.every(3).minutes.do(check_and_save_availability)

    # update_config_for_today 함수를 매일 00시 1분에 실행
    schedule.every().day.at("00:01").do(update_config_for_today)

    while True:
        schedule.run_pending()
        time.sleep(1)
