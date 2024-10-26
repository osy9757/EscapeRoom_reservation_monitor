from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import re

# 1번 HTML 구조 파싱 함수
def parse_site1(driver, identifier, disabled_class):
    time_slots = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, f"//ul[@id='{identifier}']//li[not(contains(@class, '{disabled_class}'))]"))
    )
    # 각 요소의 텍스트를 추출하여 리스트로 반환
    return [slot.text for slot in time_slots]

# 2번 HTML 구조 파싱 함수
def parse_site2(driver, identifier, disabled_class):
    time_slots = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, f"//ul[@class='{identifier}']//li[a[span[contains(@class, '{disabled_class}')]]]"))
    )
    available_time_slots = [
        slot for slot in time_slots 
        if slot.find_elements(By.CLASS_NAME, 'possible')
    ]

    # 예약 가능한 시간대의 텍스트에서 '\n예약가능' 제거하고 텍스트 리스트로 반환
    return [slot.find_element(By.CLASS_NAME, 'time').text.split('\n')[0] for slot in available_time_slots]

# 3번 HTML 구조 파싱 함수
def parse_site3(driver, identifier, disabled_class):
    times = []
    buttons = driver.find_elements(By.CSS_SELECTOR, 'button')
    for button in buttons:
        if 'disabled' not in button.get_attribute('class'):
            time_match = re.search(r'\d{2}:\d{2}', button.text)
            if time_match:
                times.append(time_match.group())
    return times
