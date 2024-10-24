from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

app = FastAPI()

class Action(BaseModel):
    type: str
    text: Optional[str] = None
    ul_data_view: Optional[str] = None
    disabled_class: Optional[str] = None
    ul_id: Optional[str] = None

class SiteConfig(BaseModel):
    url: str
    click_center: bool
    actions: List[Action]

class BookingChecker:
    def __init__(self, config: SiteConfig):
        self.config = config
        self.driver = webdriver.Chrome()
        self.slack_client = WebClient(token=os.getenv("BOT_USER_OAUTH_TOKEN"))
        self.slack_channel = os.getenv("SLACK_CHANNEL")

    def click_element_by_text(self, text, ul_data_view=None, disabled_class=None):
        xpath = f"//*[contains(text(), '{text}')]"
        if ul_data_view:
            xpath = f"//ul[@data-view='{ul_data_view}']//li[not(contains(@class, '{disabled_class}')) and contains(text(), '{text}')]"
        
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.click()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error clicking text '{text}': {e}")

    def check_booking(self):
        url = self.config.url
        click_center = self.config.click_center
        actions = self.config.actions

        try:
            self.driver.get(url)

            if click_center:
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.TAG_NAME, "body"))
                ).click()
                time.sleep(3)

            for action in actions:
                if action.type == 'click':
                    self.click_element_by_text(action.text, action.ul_data_view, action.disabled_class)
                elif action.type == 'check_time':
                    time_slots = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, f"//ul[@id='{action.ul_id}']//li[not(contains(@class, '{action.disabled_class}'))]"))
                    )
                    return [slot.text for slot in time_slots]

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing site {url}: {e}")
        finally:
            self.driver.quit()

    def send_slack_message(self, message):
        try:
            response = self.slack_client.chat_postMessage(
                channel=self.slack_channel,
                text=message
            )
        except SlackApiError as e:
            raise HTTPException(status_code=500, detail=f"Slack API Error: {e.response['error']}")

@app.post("/check-booking/")
async def check_booking(config: SiteConfig):
    checker = BookingChecker(config)
    available_times = checker.check_booking()
    if available_times:
        message = f"Available booking times for {config.url}: {', '.join(available_times)}"
        checker.send_slack_message(message)
    return {"available_times": available_times}
