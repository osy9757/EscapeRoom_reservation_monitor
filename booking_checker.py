from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from fastapi import HTTPException
from models import SiteConfig
import time
from parsing_func import *

class BookingChecker:
    def __init__(self, config: SiteConfig):
        self.config = config
        self.driver = self._initialize_driver()

    def _initialize_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        return webdriver.Chrome(options=chrome_options)

    def _navigate_to_url(self):
        try:
            self.driver.get(self.config.url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"URL {self.config.url} 로드 실패: {e}")

    def _perform_click_center(self):
        if self.config.click_center:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.TAG_NAME, "body"))
                ).click()
                time.sleep(3)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"중앙 클릭 실패: {e}")

    def click_element_by_text(self, text, tag_name=None, element_id=None, element_name=None, element_class=None):
        """
        주어진 텍스트와 선택적인 태그 이름, id, name 속성을 기반으로 Selenium에서 해당 요소를 클릭하는 함수.
        
        :param text: 해당 태그 안에 있는 텍스트
        :param tag_name: HTML 태그 이름 (예: 'a', 'li', 'td' 등, 선택적)
        :param element_id: 요소의 id 속성 (선택적)
        :param element_name: 요소의 name 속성 (선택적)
        :param element_class: 요소의 class 속성 (선택적 빈칸가능)
        """
        try:
            # 기본 XPath는 텍스트를 기준으로 생성
            if tag_name:
                xpath = f"//{tag_name}[contains(text(), '{text}')]"
            else:
                xpath = f"//*[contains(text(), '{text}')]"

            # id 속성이 주어졌을 때 이를 추가
            if element_id:
                xpath = f"//{tag_name if tag_name else '*'}[@id='{element_id}' and contains(text(), '{text}')]"

            # name 속성이 주어졌을 때 이를 추가
            elif element_name:
                xpath = f"//{tag_name if tag_name else '*'}[@name='{element_name}' and contains(text(), '{text}')]"

            # class 속성이 주어졌을 때 이를 추가
            if element_class is not None:
                if element_class == "":
                    xpath = f"//{tag_name if tag_name else '*'}[@class='' and contains(text(), '{text}')]"
                else:
                    xpath = f"{xpath}[contains(@class, '{element_class}')]"


            # 요소 찾기
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.click()
        
        except NoSuchElementException:
            print(f"'{text}' 텍스트를 가진 요소를 찾을 수 없습니다.")
        except Exception as e:
            print(f"요소 클릭 중 오류 발생: {e}")

    def _check_time_slots(self, parse_num, identifier=None, disabled_class=None):
        """
        파싱 함수를 선택하고 indentifier와 disabled_class로 예약가능 시간 확인 함수

        :param parse_num: 파싱 함수 선택 
        :param identifier: 사이트 별 class, id, name 등 검색할 때 사용할 식별자 (선택적)
        :param disabled_class: 예약 가능여부 판별 식별자 (선택적)
        """
        # 파싱 함수 매핑
        parse_functions = {
            1: parse_site1,
            2: parse_site2,
            3: parse_site3,
        }

        try:
            parse_function = parse_functions.get(parse_num)
            if not parse_function:
                raise ValueError("지원하지 않은 파서 번호")
            time_slots = parse_function(self.driver, identifier, disabled_class)
            return time_slots
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"시간 슬롯 확인 오류: {e}")
        
    def _switch_to_iframe(self, iframe_name=None, iframe_id=None, iframe_index=None):
        """
        주어진 iframe으로 전환하고, iframe_name이 'default'일 경우 원래 페이지로 복귀.
        
        :param iframe_name: iframe의 name 속성 또는 'default'로 원래 페이지로 복귀
        :param iframe_id: iframe의 id 속성
        :param iframe_index: iframe의 index
        """
        try:
            # 원래 페이지로 돌아가기 (iframe_name이 'default'일 경우)
            if iframe_name == "default":
                self.driver.switch_to.default_content()
                print("원래 페이지로 돌아왔습니다.")
                return

            # iframe으로 전환 (name, id, index 중 하나를 기준으로 전환)
            if iframe_name:
                self.driver.switch_to.frame(iframe_name)
            elif iframe_id:
                iframe_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, iframe_id))
                )
                self.driver.switch_to.frame(iframe_element)
            elif iframe_index is not None:
                self.driver.switch_to.frame(iframe_index)
            else:
                raise ValueError("iframe 전환에 필요한 name, id 또는 index 중 하나가 필요합니다.")

            print("iframe으로 전환 성공")

        except NoSuchElementException:
            print("iframe을 찾을 수 없습니다.")
        except Exception as e:
            print(f"iframe 전환 중 오류 발생: {e}")

    def check_booking(self):
        try:
            self._navigate_to_url()
            self._perform_click_center()

            for action in self.config.actions:
                if action.type == 'click':
                    self.click_element_by_text(
                        tag_name=action.tag_name,
                        text=action.text,
                        element_id=action.element_id,
                        element_name=action.element_name,
                        element_class=action.element_class
                    )
                elif action.type == 'switch_iframe':
                    self._switch_to_iframe(
                        iframe_name=action.iframe_name,
                        iframe_id=action.iframe_id,
                        iframe_index=action.iframe_index
                    )
                elif action.type == 'check_time':
                    if action.parse_num is None:
                        raise ValueError("parse_num 변수값이 필요합니다.")
                    return self._check_time_slots(
                        parse_num=action.parse_num,
                        identifier=action.identifier,
                        disabled_class=action.disabled_class
                    )

        except HTTPException as e:
            raise e
        finally:
            self.driver.quit()
