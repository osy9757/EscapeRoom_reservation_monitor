# 방탈출 예약 모니터 (EscapeRoom_reservation_monitor)

이 프로젝트는 방탈출 예약 가능 시간을 모니터링하고, 예약 가능 시간의 변화를 Slack을 통해 알림으로 전송하는 시스템입니다. FastAPI와 Slack API를 사용하여 예약 상태를 주기적으로 확인하고, 변경 사항을 사용자에게 알립니다.

## 주요 기능

- **예약 가능 시간 확인**: 지정된 웹사이트에서 예약 가능한 시간을 주기적으로 확인합니다.
- **Slack 알림**: 예약 가능 시간에 변화가 있을 경우, Slack 채널로 알림을 전송합니다.
- **스케줄링**: 예약 확인 작업을 주기적으로 실행하고, 매일 특정 시간에 설정 파일을 업데이트합니다.

## 설치 방법

1. **프로젝트 클론**
   ```bash
   git clone (url)
   cd EscapeRoom_reservation_monitor
   ```

2. **가상 환경 생성 및 활성화**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows의 경우 `venv\Scripts\activate`
   ```

3. **필요한 패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **환경 변수 설정**
   - `.env` 파일을 생성하고 다음과 같은 형식으로 Slack API 토큰과 채널 정보를 입력합니다:
     ```
     BOT_USER_OAUTH_TOKEN=your-slack-bot-token
     SLACK_SIGNING_SECRET=your-slack-signing-secret
     SLACK_TEST_CHANNEL=your-test-channel
     SLACK_ESCAPEROOM_CHANNEL=your-escape-room-channel
     ```
## 파일 설명

- `main.py`: FastAPI 서버와 Slack 명령어를 처리하는 메인 파일입니다.
- `scheduler_tasks.py`: 예약 확인 및 설정 파일 업데이트 작업을 스케줄링합니다.
- `booking_checker.py`: 웹사이트에서 예약 가능 시간을 확인하는 로직을 포함합니다.
- `slack_messenger.py`: Slack 메시지를 전송하는 기능을 제공합니다.
- `config_utils.py`: 설정 파일을 로드하고 저장하는 유틸리티 함수들을 포함합니다.
- `json_utils.py`: JSON 파일에 데이터를 추가하거나 덮어쓰는 기능을 제공합니다.
- `parsing_func.py`: 웹사이트의 HTML 구조에 따라 예약 가능 시간을 파싱하는 함수들을 포함합니다.
- `models.py`: Pydantic 모델을 정의하여 설정 파일의 구조를 명확히 합니다.

## JSON 파일 설명 

- `config.json`: 예약 모니터링을 위한 설정 파일입니다. 각 항목은 모니터링할 사이트의 정보를 포함합니다.
- `availability.json`: 현재 예약 가능 상태를 저장하는 파일입니다.
- `listup.json`: 예약 모니터링을 위한 추가적인 설정을 포함할 수 있는 파일입니다.
- `addlist.json`: Slack 명령어를 통해 추가된 예약 요청을 저장하는 파일입니다.


## 사용법

1. **FastAPI 서버 실행**
   ```bash
   uvicorn main:app --reload
   ```

2. **Slack 명령어 사용**
   - `/checkbooking`: 예약 가능 시간을 확인하고 결과를 Slack에 전송합니다.
   - `/addlist`: 방탈출명과 날짜를 신청 리스트에 추가합니다.
   - `/hello`: 간단한 인사말을 전송합니다.

3. **스케줄러 실행**
   - 스케줄러는 `scheduler_tasks.py`에서 정의된 작업을 주기적으로 실행합니다. 예약 가능 시간을 3분마다 확인하고, 매일 00시 1분에 설정 파일을 업데이트합니다.

4. **서버 실행**
   - Slack api와 연결하여 사용하기 위해선 배포 혹은 포트포워딩등을 진행해야 합니다. 테스트시에는 ngrok과 fly.io로 진행했습니다.