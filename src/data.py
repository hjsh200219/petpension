from tqdm import tqdm
import pandas as pd
import requests as req
import json
import math
import datetime
from io import BytesIO, StringIO
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import os
from bs4 import BeautifulSoup as BS
from playwright.sync_api import sync_playwright
import streamlit as st
from typing import List, Dict, Any, Callable, Optional, Union, Tuple
import time
import random
from fake_useragent import UserAgent
from requests_html import HTMLSession
from math import ceil
from concurrent.futures import ThreadPoolExecutor
from src.payload import (
    payload_schedule,
    payload_booking_list,
    payload_visitor_reviews,
    payload_rating,
    payload_photos
)

class Common:
    def __init__(self):
        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random,
            'Referer': 'https://m.place.naver.com/',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
        }

class Naver:
    def __init__(self):
        self.url_schedule = "https://m.booking.naver.com/graphql?opName=schedule"
        self.url_booking_list = "https://m.booking.naver.com/graphql?opName=bizItems"
        self.url_pension_info = "https://m.place.naver.com/accommodation/"
        self.url_place_info = "https://pages.map.naver.com/save-widget/api/maps-search/place?id="
        self.url_booking = "https://map.naver.com/p/entry/place/"
        self.url_rating = "https://api.place.naver.com/graphql"
        self.url_rating_detail = "https://m.place.naver.com/place/"

        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random,
            'Referer': 'https://m.place.naver.com/',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        
    def get_schedule(self, businessId, bizItemId, startDateTime, endDateTime):
        # payload.py에서 페이로드 가져오기
        payload = payload_schedule(businessId, bizItemId, startDateTime, endDateTime)

        response = req.post(self.url_schedule, json=payload)
        data = response.json()["data"]["schedule"]["bizItemSchedule"]["daily"]['date']
        result = []
        for date_key, datum in data.items():
            result.append({
                'date': date_key,
                'isHoliday': datum['isHoliday'],
                'isBusinessDay': datum['isBusinessDay'],
                'hasBusinessDays': datum['hasBusinessDays'],
                'isSaleDay': datum['isSaleDay'],
                'stock': datum['stock'],
                'bookingCount': datum['bookingCount'],
                'occupiedBookingCount': datum['occupiedBookingCount'],
                'todayDealRate': datum['todayDealRate'],
                'minBookingCount': datum['minBookingCount'],
                'maxBookingCount': datum['maxBookingCount'],
                'startTime': datum['startTime'],
                'endTime': datum['endTime'],
                'prices': f"{datum['prices'][0]['price']:,}" if datum['prices'] and len(datum['prices']) > 0 else "0"
            })
        
        result = pd.DataFrame(result)
        return result
    
    def get_booking_list(self, businessId):
        # payload.py에서 페이로드 가져오기
        payload = payload_booking_list(businessId)

        response = req.post(self.url_booking_list, json=payload)
        data = response.json()["data"]["bizItems"]["bizItems"]
        result = []
        for bizItem in data:
            result.append({
                'bizItemId': bizItem['id'],
                'bizItemName': bizItem['name'],
                'businessId': businessId,
                'desc': bizItem['desc']
            })
        
        result = pd.DataFrame(result)
        return result
    
    def insert_pension_info(self, business_id, channel_id):
        name, address_old, address_new = self.get_pension_info(channel_id)
        result = self.get_booking_list(business_id)
        result['channelId'] = channel_id
        result['businessName'] = name
        result['addressOld'] = address_old
        result['addressNew'] = address_new
        result['businessId'] = business_id
        result['bookingUrl'] = f"{self.url_booking}{channel_id}"

        if not os.path.exists('./static/database/pension_info.csv'):
            result.to_csv('./static/database/pension_info.csv', index=False)
        else:
            result_old = pd.read_csv('./static/database/pension_info.csv')
            # 중복된 데이터가 생성되지 않도록 확인
            if not result['bizItemId'].isin(result_old['bizItemId']).any():
                result = pd.concat([result_old, result])
                result.to_csv('./static/database/pension_info.csv', index=False)

        result = pd.read_csv('./static/database/pension_info.csv')
        result.drop_duplicates(inplace=True)
        result.to_csv('./static/database/pension_info.csv', index=False)

    def get_pension_info(self, channel_id):
        url = f"{self.url_place_info}{channel_id}"
        response = req.get(url)
        data = response.json()['result']['place']['list'][0]
        name = data['name']
        address_old = data['address']
        address_new = data['roadAddress']
        return name, address_old, address_new

    def get_rating(self, channel_id):
        wait_time = random.uniform(0.1, 0.2)
        time.sleep(wait_time)
        
        # payload.py에서 페이로드 가져오기
        payload = payload_rating(channel_id)
        
        response = req.post(self.url_rating, json=payload, headers=self.headers)
        review_count = response.json()[0]['data']['getTotalReviewCount']['totalCount']
        rating_distribution = response.json()[0]['data']['getTotalReviewCount']['scoreDistribution']
        
        return {"review_count": review_count, "rating_distribution": rating_distribution}

    def _get_rating_playwright(self, channel_id):
        # 재시도 횟수 설정
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                with sync_playwright() as p:
                    # 브라우저 런치 옵션 설정
                    browser = p.chromium.launch(
                        headless=True,
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--disable-extensions',
                            '--no-sandbox',
                            '--disable-setuid-sandbox'
                        ]
                    )
                    
                    # 브라우저 컨텍스트 생성 및 더 실제 같은 설정
                    context = browser.new_context(
                        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        viewport={"width": 1920, "height": 1080},
                        has_touch=False,
                        java_script_enabled=True,
                        locale="ko-KR",
                        timezone_id="Asia/Seoul",
                        geolocation={"latitude": 37.5665, "longitude": 126.9780, "accuracy": 100},
                        color_scheme="light"
                    )
                    
                    # 쿠키 및 로컬 스토리지 설정 추가
                    context.add_cookies([
                        {"name": "NNB", "value": "".join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=12)), "domain": ".naver.com", "path": "/"}
                    ])
                    
                    # 페이지 생성 및 설정
                    page = context.new_page()
                    page.set_default_navigation_timeout(15000)  # 타임아웃을 15초로 줄임
                    page.set_default_timeout(15000)
                    
                    # 봇 감지 우회 스크립트 실행
                    page.evaluate("""
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => false,
                        });
                    """)
                    
                    # 무작위 지연 시간 추가 (1.25~2.5초, 첫 시도에서는 더 짧게)
                    delay = random.uniform(0.125, 0.25) if retry_count == 0 else random.uniform(0.125, 0.25)
                    print(f"요청 전 {delay:.1f}초 대기 중...")
                    time.sleep(delay)
                    
                    # 네이버 메인 페이지 먼저 방문
                    page.goto("https://www.naver.com")
                    time.sleep(random.uniform(0.125, 0.25))
                    
                    # 마우스 움직임 시뮬레이션
                    page.mouse.move(random.randint(100, 800), random.randint(100, 600))
                    time.sleep(random.uniform(0.0625, 0.125))
                    
                    # 페이지 스크롤
                    page.evaluate("window.scrollBy(0, 150)")
                    time.sleep(random.uniform(0.0625, 0.125))
                    
                    # 페이지 접속
                    print(f"리뷰 페이지로 이동 중...")
                    page.goto(f"{self.url_rating_detail}{channel_id}/review/visitor")
                    
                    # 페이지가 완전히 로드될 때까지 대기
                    page.wait_for_load_state('networkidle')

                    # '더보기' 버튼을 두 번 클릭하는 코드
                    for _ in range(2):
                        button = page.query_selector("a.dP0sq[role='button']")
                        if button:
                            button.click()
                            time.sleep(random.uniform(0.0625, 0.125))  # 클릭 후 대기
                    
                    # 페이지에 "과도한 접근 요청" 문구가 있는지 확인
                    content = page.content()
                    if "과도한 접근 요청으로 서비스 이용이 제한되었습니다" in content:
                        print(f"접근 제한 감지됨. 재시도 {retry_count + 1}/{max_retries}")
                        browser.close()
                        retry_count += 1
                        # 더 긴 대기 시간
                        wait_time = 15 + retry_count * 15  # 15초, 30초, 45초...
                        print(f"{wait_time}초 후에 재시도합니다...")
                        time.sleep(wait_time)
                        continue
                    
                    # 추가 지연 시간 및 활동 시뮬레이션
                    time.sleep(random.uniform(0.125, 0.375))
                    
                    # 페이지에서 스크롤
                    page.evaluate("window.scrollBy(0, 150)")
                    time.sleep(random.uniform(0.125, 0.25))
                    
                    # 페이지 내용 가져오기
                    html = page.content()
                    soup = BS(html, 'html.parser')
                    divs = soup.find_all('div', class_='place_section_content')
                    div = divs[0]
                    ul = div.find('ul')
                    lis = ul.find_all('li')
                    reviews_data = []
                    review_items = [
                        "인테리어가 멋져요", "동물을 배려한 환경이에요", "시설이 깔끔해요", "사진이 잘 나와요",
                        "야외공간이 멋져요", "뷰가 좋아요", "친절해요", "공간이 넓어요", "가격이 합리적이에요",
                        "매장이 청결해요", "화장실이 깨끗해요", "대화하기 좋아요", "반려동물과 가기 좋아요",
                        "조용히 쉬기 좋아요", "침구가 좋아요", "바비큐 해먹기 좋아요", "화장실이 잘 되어있어요",
                        "주차하기 편해요", "물놀이하기 좋아요", "냉난방이 잘돼요", "즐길 거리가 많아요",
                        "방음이 잘돼요", "컨셉이 독특해요", "취사시설이 잘 되어있어요"
                    ]
                    for item in review_items:
                        review_text = item
                        participant_count = 0  # 기본값 0으로 설정
                        for li in lis:
                            if li.find('span', class_='t3JSf').text.strip().replace('"', '') == review_text:
                                participant_count = ''.join(filter(str.isdigit, li.find('span', class_='CUoLy').text.strip()))
                                break
                        reviews_data.append({"channelId": channel_id, "review_item": review_text, "rating": participant_count})
                    reviews_data = pd.DataFrame(reviews_data)
                            
                    # 세션 정리
                    browser.close()
                    return reviews_data
                    
            except Exception as e:
                print(f"오류 발생: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 15 + retry_count * 15
                    print(f"{wait_time}초 후에 재시도합니다...")
                    time.sleep(wait_time)
                else:
                    return {"error": str(e), "status": "error"}
        
        return {"error": "최대 재시도 횟수 초과", "status": "failed"}
        
    def get_rating_data(self, df, method='default'):
        """
        리뷰 데이터를 수집하는 함수
        method: 'default', 'playwright', 'requests_html' 중 하나를 선택
        """
        rating_data = pd.DataFrame()
        errors = []  # 오류 기록용
        
        for index, row in tqdm(df.iterrows(), total=len(df)):
            # 크롤링 메서드 선택
            if method == 'playwright':
                result = self._get_rating_playwright(row['channelId'])
            elif method == 'requests_html':
                result = self._get_rating_requests_html(row['channelId'])
            else:  # default
                # 개발 환경인 경우 playwright, 그렇지 않으면 일반 method 사용
                result = self._get_rating_playwright(row['channelId']) if os.environ.get('STREAMLIT_DEVELOPMENT', 'false').lower() == 'true' else self._get_rating(row['channelId'])
            
            # 결과가 DataFrame인지 확인
            if isinstance(result, pd.DataFrame):
                result['businessName'] = row['businessName']
                result['channelId'] = row['channelId']
                rating_data = pd.concat([rating_data, result], ignore_index=True)
            else:
                # 에러 정보 저장
                error_info = {
                    'businessName': row['businessName'],
                    'channelId': row['channelId'],
                    'error': result.get('error', '알 수 없는 오류')
                }
                errors.append(error_info)
                print(f"경고: {row['businessName']}의 리뷰 데이터를 가져오는데 실패했습니다. {error_info['error']}")
        
        # 오류 정보 출력
        if errors:
            print(f"총 {len(errors)}개 펜션의 리뷰 데이터를 가져오는데 실패했습니다.")
        
        # 수집된 데이터가 있는 경우만 저장
        if not rating_data.empty:
            rating_data.to_csv('./static/database/rating_data.csv', index=False)
            return rating_data
        else:
            # 데이터가 없는 경우 빈 데이터프레임 반환
            print("경고: 수집된 리뷰 데이터가 없습니다!")
            return pd.DataFrame(columns=['channelId', 'review_item', 'rating', 'businessName']) 

    def _get_rating(self, channel_id):
        wait_time = random.uniform(0.1, 0.2)
        time.sleep(wait_time)
        url = f"{self.url_rating_detail}{channel_id}/review/visitor"
        res = req.get(url, headers=self.headers)
        res.encoding = 'utf-8'
        soup = BS(res.text, 'html.parser', from_encoding='utf-8')
        divs = soup.find_all('div', class_='place_section_content')
        div = divs[0]
        ul = div.find('ul')
        lis = ul.find_all('li')
        reviews_data = []
        review_items = [
            "인테리어가 멋져요", "동물을 배려한 환경이에요", "시설이 깔끔해요", "사진이 잘 나와요",
            "야외공간이 멋져요", "뷰가 좋아요", "친절해요", "공간이 넓어요", "가격이 합리적이에요",
            "매장이 청결해요", "화장실이 깨끗해요", "대화하기 좋아요", "반려동물과 가기 좋아요",
            "조용히 쉬기 좋아요", "침구가 좋아요", "바비큐 해먹기 좋아요", "화장실이 잘 되어있어요",
            "주차하기 편해요", "물놀이하기 좋아요", "냉난방이 잘돼요", "즐길 거리가 많아요",
            "방음이 잘돼요", "컨셉이 독특해요", "취사시설이 잘 되어있어요"
        ]
        for item in review_items:
            review_text = item
            participant_count = 0  # 기본값 0으로 설정
            for li in lis:
                if li.find('span', class_='t3JSf').text.strip().replace('"', '') == review_text:
                    participant_count = ''.join(filter(str.isdigit, li.find('span', class_='CUoLy').text.strip()))
                    break
            reviews_data.append({"channelId": channel_id, "review_item": review_text, "rating": participant_count})
        reviews_data = pd.DataFrame(reviews_data)
        return reviews_data

    def _get_rating_requests_html(self, channel_id):
        """
        requests-html을 사용하여 네이버 리뷰 데이터를 크롤링하는 함수
        """
        # 재시도 횟수 설정
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # HTMLSession 생성
                session = HTMLSession()
                
                # User-Agent 무작위 설정
                ua = UserAgent()
                headers = {
                    'User-Agent': ua.random,
                    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Referer': 'https://www.naver.com/',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
                
                # 쿠키 설정
                cookies = {
                    'NNB': ''.join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=12))
                }
                
                # 무작위 지연 시간 추가
                delay = random.uniform(0.5, 1.5) if retry_count == 0 else random.uniform(1, 3)
                print(f"요청 전 {delay:.1f}초 대기 중...")
                time.sleep(delay)
                
                # 네이버 메인 페이지 먼저 방문하여 쿠키 획득
                session.get("https://www.naver.com", headers=headers, cookies=cookies)
                time.sleep(random.uniform(0.5, 1))
                
                # 리뷰 페이지로 이동
                print(f"리뷰 페이지로 이동 중...")
                review_url = f"{self.url_rating_detail}{channel_id}/review/visitor"
                
                # 페이지 요청
                response = session.get(
                    review_url, 
                    headers=headers, 
                    cookies=cookies
                )
                
                # 자바스크립트 렌더링
                print("자바스크립트 렌더링 중...")
                response.html.render(sleep=2, timeout=20)
                
                # 페이지에 "과도한 접근 요청" 문구가 있는지 확인
                if "과도한 접근 요청으로 서비스 이용이 제한되었습니다" in response.html.html:
                    print(f"접근 제한 감지됨. 재시도 {retry_count + 1}/{max_retries}")
                    session.close()
                    retry_count += 1
                    # 더 긴 대기 시간
                    wait_time = 30 + retry_count * 30  # 30초, 60초, 90초...
                    print(f"{wait_time}초 후에 재시도합니다...")
                    time.sleep(wait_time)
                    continue
                
                # 페이지 내용 파싱
                soup = BS(response.html.html, 'html.parser')
                divs = soup.find_all('div', class_='place_section_content')
                
                if not divs:
                    print("리뷰 섹션을 찾을 수 없습니다. 다른 선택자를 시도합니다.")
                    # 다른 선택자로 시도해볼 수 있음
                    divs = soup.find_all('div', {'data-nclicks-area-code': 'rvw'})
                    
                    if not divs:
                        print("리뷰 데이터를 찾을 수 없습니다.")
                        # 페이지 저장하여 디버깅
                        with open(f"debug_review_page_{channel_id}.html", "w", encoding="utf-8") as f:
                            f.write(response.html.html)
                        print(f"디버깅용 페이지가 debug_review_page_{channel_id}.html에 저장되었습니다.")
                        session.close()
                        retry_count += 1
                        continue
                
                div = divs[0]
                ul = div.find('ul')
                
                if not ul:
                    print("리뷰 리스트를 찾을 수 없습니다.")
                    session.close()
                    retry_count += 1
                    continue
                    
                lis = ul.find_all('li')
                reviews_data = []
                
                # 리뷰 항목 리스트
                review_items = [
                    "인테리어가 멋져요", "동물을 배려한 환경이에요", "시설이 깔끔해요", "사진이 잘 나와요",
                    "야외공간이 멋져요", "뷰가 좋아요", "친절해요", "공간이 넓어요", "가격이 합리적이에요",
                    "매장이 청결해요", "화장실이 깨끗해요", "대화하기 좋아요", "반려동물과 가기 좋아요",
                    "조용히 쉬기 좋아요", "침구가 좋아요", "바비큐 해먹기 좋아요", "화장실이 잘 되어있어요",
                    "주차하기 편해요", "물놀이하기 좋아요", "냉난방이 잘돼요", "즐길 거리가 많아요",
                    "방음이 잘돼요", "컨셉이 독특해요", "취사시설이 잘 되어있어요"
                ]
                
                # 리뷰 데이터 추출
                for item in review_items:
                    review_text = item
                    participant_count = 0  # 기본값 0으로 설정
                    
                    for li in lis:
                        # 태그 이름 선택자에 맞게 조정
                        tag_span = li.find('span', class_='t3JSf')
                        if tag_span and tag_span.text.strip().replace('"', '') == review_text:
                            count_span = li.find('span', class_='CUoLy')
                            if count_span:
                                participant_count = ''.join(filter(str.isdigit, count_span.text.strip()))
                            break
                    
                    reviews_data.append({
                        "channelId": channel_id, 
                        "review_item": review_text, 
                        "rating": participant_count
                    })
                
                # 데이터프레임으로 변환
                reviews_data = pd.DataFrame(reviews_data)
                
                # 세션 정리
                session.close()
                return reviews_data
                
            except Exception as e:
                print(f"오류 발생: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 20 + retry_count * 20
                    print(f"{wait_time}초 후에 재시도합니다...")
                    time.sleep(wait_time)
                else:
                    return {"error": str(e), "status": "error"}
        
        return {"error": "최대 재시도 횟수 초과", "status": "failed"}
    
    def get_photo(self, channel_id):
        """
        네이버 플레이스에서 사진 정보를 가져오는 함수
        429 에러(Too Many Requests) 방지를 위한 재시도 로직 포함
        """
        # 재시도 설정
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 요청 간 지연 시간 증가 - 초기 지연 시간은 더 길게, 재시도마다 더 길어짐
                delay = random.uniform(1.5, 3.0) + (retry_count * 2)
                print(f"사진 데이터 요청 전 {delay:.1f}초 대기 중...")
                time.sleep(delay)
                
                # User-Agent 무작위 설정
                self.headers['User-Agent'] = self.ua.random
                
                # payload.py에서 페이로드 가져오기
                payload = payload_photos(channel_id)
                
                # 요청 보내기
                res = req.post(self.url_rating, json=payload, headers=self.headers)
                
                # 응답 코드 확인
                if res.status_code == 200:
                    # 성공적으로 데이터를 받았을 때
                    print(f"사진 데이터 수집 성공: 상태 코드 {res.status_code}")
                    return res.json()
                elif res.status_code == 429:
                    # 요청 제한에 걸렸을 때
                    retry_count += 1
                    wait_time = 30 + (retry_count * 30)  # 30초, 60초, 90초...
                    print(f"429 에러(Too Many Requests) 발생! {retry_count}/{max_retries} 회 재시도, {wait_time}초 후에 다시 시도합니다.")
                    time.sleep(wait_time)
                else:
                    # 다른 오류 발생
                    print(f"사진 데이터 수집 실패: 상태 코드 {res.status_code}")
                    retry_count += 1
                    if retry_count < max_retries:
                        wait_time = 10 + (retry_count * 10)
                        print(f"다른 오류 발생, {wait_time}초 후에 다시 시도합니다.")
                        time.sleep(wait_time)
                    else:
                        return {"error": f"상태 코드: {res.status_code}", "status": "error"}
            
            except Exception as e:
                print(f"예외 발생: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 15 + (retry_count * 15)
                    print(f"오류 발생, {wait_time}초 후에 다시 시도합니다.")
                    time.sleep(wait_time)
                else:
                    return {"error": str(e), "status": "error"}
        
        # 최대 재시도 횟수를 초과한 경우
        return {"error": "최대 재시도 횟수 초과", "status": "failed"}
    
class Public:
    def __init__(self):
        self.public_key = "k/yxtkMUkNQCQ9C6AyTGUtC7Zd58Wbff8Ndb7WKFZX8a1PBAUr8zSzaeBNHFGkFd5CxYWaEM+iQzaejQ5M+LXQ=="
        self.url_public_animal = "http://apis.data.go.kr/1543061/abandonmentPublicSrvc/abandonmentPublic"
        self.url_public_sido = "http://apis.data.go.kr/1543061/abandonmentPublicSrvc/sido"
        self.url_public_sigungu = "http://apis.data.go.kr/1543061/abandonmentPublicSrvc/sigungu"
        self.url_public_shelter = "http://apis.data.go.kr/1543061/abandonmentPublicSrvc/shelter"
        self.url_public_kind = "http://apis.data.go.kr/1543061/abandonmentPublicSrvc/kind"
        
    def totalCount(self, upkind=None):
        params = {
            'serviceKey': self.public_key,
            '_type': 'json',
            'pageNo': 1,
            'numOfRows': 1,
            'upkind': upkind
        }
        res = req.get(self.url_public_animal, params=params)
        data = res.json()
        totalCount = data['response']['body']['totalCount']
        return totalCount
    
    def find_pet(
            self, 
            bgnde=None, 
            endde=None, 
            upkind=None, 
            kind=None, 
            upr_cd=None, 
            org_cd=None, 
            care_reg_no=None, 
            state=None, 
            neuter_yn=None
        ):
        try:
            params = {
                'serviceKey': self.public_key,
                '_type': 'json',
                'pageNo': 1,
                'numOfRows': 1000,
                'bgnde': bgnde,
                'endde': endde,
                'upkind': upkind,
                'kind': kind,
                'upr_cd': upr_cd,
                'org_cd': org_cd,
                'care_reg_no': care_reg_no,
                'state': state,
                'neuter_yn': neuter_yn
            }
            
            # 초기 API 호출로 총 개수 가져오기
            res = req.get(self.url_public_animal, params=params)
            data = res.json()
            
            # 응답 확인
            if ('response' not in data or 
                'body' not in data['response'] or 
                'totalCount' not in data['response']['body']):
                print("API 응답 형식 오류 - 기본 정보를 가져올 수 없습니다.")
                return pd.DataFrame()
            
            totalCount = data['response']['body']['totalCount']
            
            if totalCount == 0:
                print("검색 조건에 맞는 동물 데이터가 없습니다.")
                return pd.DataFrame()
            
            result = []
            
            def fetch_pet_data(page):
                try:
                    # 페이지별 파라미터 설정
                    page_params = params.copy()
                    page_params['pageNo'] = page
                    
                    # API 호출
                    res = req.get(self.url_public_animal, params=page_params)
                    data = res.json()
                    
                    # 응답 검증
                    if ('response' not in data or 
                        'body' not in data['response'] or 
                        'items' not in data['response']['body']):
                        print(f"페이지 {page}에서 API 응답 형식 오류")
                        return []
                    
                    items = data['response']['body']['items']
                    
                    # items가 없거나 비어있는 경우
                    if not items or 'item' not in items:
                        print(f"페이지 {page}에 데이터가 없습니다.")
                        return []
                    
                    petlist = items['item']
                    
                    # 단일 항목인 경우 리스트로 변환
                    if isinstance(petlist, dict):
                        petlist = [petlist]
                    
                    return petlist
                    
                except Exception as e:
                    print(f"페이지 {page} 데이터 가져오기 실패: {str(e)}")
                    return []
            
            with ThreadPoolExecutor() as executor:
                pages = range(1, min(ceil(totalCount / 1000) + 1, 10))  # 너무 많은 페이지 방지
                pet_lists = list(executor.map(fetch_pet_data, pages))
            
            for petlist in pet_lists:
                for pet in petlist:
                    try:
                        pet_data = {
                            'desertionNo': pet.get('desertionNo', ''),
                            'filename': pet.get('filename', ''),
                            'happenDt': pet.get('happenDt', ''),
                            'happenPlace': pet.get('happenPlace', ''),
                            'kindCd': pet.get('kindCd', ''),
                            'colorCd': pet.get('colorCd', ''),
                            'age': pet.get('age', ''),
                            'weight': pet.get('weight', ''),
                            'noticeNo': pet.get('noticeNo', ''),
                            'noticeSdt': pet.get('noticeSdt', ''),
                            'noticeEdt': pet.get('noticeEdt', ''),
                            'popfile': pet.get('popfile', ''),
                            'processState': pet.get('processState', ''),
                            'sexCd': pet.get('sexCd', ''),
                            'neuterYn': pet.get('neuterYn', ''),
                            'specialMark': pet.get('specialMark', ''),
                            'careNm': pet.get('careNm', ''),
                            'careTel': pet.get('careTel', ''),
                            'careAddr': pet.get('careAddr', ''),
                            'orgNm': pet.get('orgNm', ''),
                            'chargeNm': pet.get('chargeNm', ''),
                            'officetel': pet.get('officetel', '')
                        }
                        result.append(pet_data)
                    except Exception as e:
                        print(f"동물 데이터 처리 오류: {str(e)}")
                        continue
            
            # 결과를 데이터프레임으로 변환
            df = pd.DataFrame(result)
            
            # 날짜 형식 변환 시도
            date_columns = ['happenDt', 'noticeSdt', 'noticeEdt']
            for col in date_columns:
                if col in df.columns:
                    try:
                        # 날짜 형식이 8자리 숫자인 경우 (YYYYMMDD)
                        df[col] = pd.to_datetime(df[col], format='%Y%m%d', errors='coerce')
                    except:
                        pass  # 변환 실패 시 원래 형식 유지
            
            # 데이터가 없는 경우 빈 데이터프레임 반환
            if df.empty:
                print("처리된 동물 데이터가 없습니다.")
            
            return df
            
        except Exception as e:
            print(f"동물 데이터 검색 중 오류 발생: {str(e)}")
            return pd.DataFrame()
    
    def find_sido(self):
        params = {
            'serviceKey': self.public_key,
            '_type': 'json',
            'pageNo': 1,
            'numOfRows': 1000
        }
        res = req.get(self.url_public_sido, params=params)
        data = res.json()
        sido_list = data['response']['body']['items']['item']
        result = []
        for sido in sido_list:
            orgCd = sido['orgCd']
            orgdownNm = sido['orgdownNm']
            result.append({'시도코드': orgCd, '시도명': orgdownNm})
        return pd.DataFrame(result)
    
    def find_sigungu(self, upr_cd):
        params = {
            'serviceKey': self.public_key,
            '_type': 'json',
            'pageNo': 1,
            'numOfRows': 1000,
            'upr_cd': upr_cd
        }
        res = req.get(self.url_public_sigungu, params=params)
        data = res.json()
        sigungu_list = data['response']['body']['items']['item']
        result = []
        for sigungu in sigungu_list:
            orgCd = sigungu['orgCd']
            orgdownNm = sigungu['orgdownNm']
            result.append({'시군구코드': orgCd, '시군구명': orgdownNm})
        return pd.DataFrame(result)
    
    def find_shelter(self, upr_cd=None, org_cd=None):
        params = {
            'serviceKey': self.public_key,
            '_type': 'json',
            'pageNo': 1,
            'numOfRows': 1000,
            'upr_cd': upr_cd,
            'org_cd': org_cd
        }
        
        try:
            res = req.get(self.url_public_shelter, params=params)
            data = res.json()
            
            # 응답 구조 검증
            if ('response' not in data or 
                'body' not in data['response'] or 
                'items' not in data['response']['body']):
                print(f"API 응답 형식 오류 또는 데이터 없음 - 시도코드: {upr_cd}, 시군구코드: {org_cd}")
                return pd.DataFrame(columns=['보호소코드', '보호소명'])
            
            shelter_items = data['response']['body']['items']
            
            # items가 비어있거나 item 키가 없는 경우
            if not shelter_items or 'item' not in shelter_items:
                return pd.DataFrame(columns=['보호소코드', '보호소명'])
            
            shelter_list = shelter_items['item']
            
            # item이 단일 딕셔너리인 경우 (항목이 1개일 때)
            if isinstance(shelter_list, dict):
                shelter_list = [shelter_list]
            
            # 유효한 보호소 목록이 아닌 경우
            if not isinstance(shelter_list, list):
                return pd.DataFrame(columns=['보호소코드', '보호소명'])
            
            result = []
            for shelter in shelter_list:
                try:
                    careRegNo = shelter['careRegNo']
                    careNm = shelter['careNm']
                    result.append({'보호소코드': careRegNo, '보호소명': careNm})
                except KeyError as e:
                    print(f"보호소 정보 키 오류: {e} - 시도코드: {upr_cd}, 시군구코드: {org_cd}")
                    # 특정 항목 오류는 건너뛰고 계속 진행
                    continue
            
            return pd.DataFrame(result)
            
        except Exception as e:
            print(f"보호소 조회 중 오류 발생: {str(e)} - 시도코드: {upr_cd}, 시군구코드: {org_cd}")
            return pd.DataFrame(columns=['보호소코드', '보호소명'])

    def find_kind(self, up_kind_cd = '417000'):
        """
         - 개 : 417000
         - 고양이 : 422400
         - 기타 : 429900
        """

        params = {
            'serviceKey': self.public_key,
            'up_kind_cd': up_kind_cd,
            '_type': 'json'
        }
        res = req.get(self.url_public_kind, params=params)
        data = res.json()
        kind_list = data['response']['body']['items']['item']
        result = []
        for kind in kind_list:
            kindCd = kind['kindCd']
            KNm = kind['knm']
            result.append({'품종코드': kindCd, '품종명': KNm})
        return pd.DataFrame(result)

    def update_shelter_info(self):
        result_sido = self.find_sido()
        result_sido.to_csv('./static/database/시도코드.csv', index=False)
        result_sigungu = pd.DataFrame()

        def process_sigungu(row):
            upr_cd = row['시도코드']
            upr_nm = row['시도명']
            result = self.find_sigungu(upr_cd)
            result['시도코드'] = upr_cd
            result['시도명'] = upr_nm
            return result

        with ThreadPoolExecutor() as executor:
            results = list(
                tqdm(
                    executor.map(process_sigungu, 
                                  [row for _, row in result_sido.iterrows()]), 
                    total=len(result_sido)
                )
            )

        result_sigungu = pd.concat(results, ignore_index=True)
        result_sigungu.to_csv('./static/database/시군구코드.csv', index=False)
        result_shelter = pd.DataFrame()

        def process_shelter(row):
            upr_cd = row['시도코드']
            upr_nm = row['시도명']
            org_cd = row['시군구코드']
            org_nm = row['시군구명']
            result = self.find_shelter(upr_cd, org_cd)
            result['시도코드'] = upr_cd
            result['시도명'] = upr_nm
            result['시군구코드'] = org_cd
            result['시군구명'] = org_nm
            return result

        with ThreadPoolExecutor() as executor:
            shelter_results = list(
                tqdm(
                    executor.map(process_shelter, 
                                  [row for _, row in result_sigungu.iterrows()]), 
                    total=len(result_sigungu)
                )
            )

        result_shelter = pd.concat(shelter_results, ignore_index=True)
        result_shelter.to_csv('./static/database/보호소코드.csv', index=False)

class AKC:
    def __init__(self):
        self.url = 'https://www.akc.org/dog-breeds/'

    def get_traits_info(self, breedurl):
        traits = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.url + breedurl)
        
            html = page.content()
            soup = BS(html, 'html.parser')
            overview_div = soup.find('div', class_='breed-page__hero__overview__icon-block-wrap')
            if overview_div is None:
                raise ValueError("Overview div not found")
            overview_ps = overview_div.find_all('p')
    
            
            traits_div = soup.find('div', id='breed-page__traits__all')
            traits_divcolumns = traits_div.find_all('div', class_='breed-trait-group__trait breed-trait-group__padded breed-trait-group__row-wrap')
            for traits_divcolumn in traits_divcolumns:
                trait_name = traits_divcolumn.find('h4').text
                trait_desc = traits_divcolumn.find('p').text
                
                if trait_name not in ['Coat Type', 'Coat Length']:
                    score_label_div = traits_divcolumn.find('div', class_='breed-trait-score__score-label')
                    score_label_spans = score_label_div.find_all('span')
                    score_low_label = score_label_spans[0].text
                    score_high_label = score_label_spans[1].text
                else:
                    score_low_label = ''
                    score_high_label = ''
            
                traits.append({'breed_name': breedurl, 'trait': trait_name, 'trait_desc': trait_desc, 'score_': score_low_label, 'score_high': score_high_label})

        return pd.DataFrame(traits)

    def get_breed_info(self, breedurl):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.url + breedurl)

            html = page.content()
            soup = BS(html, 'html.parser')
            overview_div = soup.find('div', class_='breed-page__hero__overview__icon-block-wrap')
            if overview_div is None:
                raise ValueError("Overview div not found")
                
            overview_columns = overview_div.find_all('div', class_='flex breed-page__hero__overview__icon-block')
            
            def extract_texts(column):
                return [p.text for p in column.find_all('p')]
            
            height = extract_texts(overview_columns[0])
            weight = extract_texts(overview_columns[1])
            life_expectancy = extract_texts(overview_columns[2])
            

            traits_div = soup.find('div', id='breed-page__traits__all')
            traits_divcolumns = traits_div.find_all('div', class_='breed-trait-group__trait breed-trait-group__padded breed-trait-group__row-wrap')

            def get_trait_score(index):
                return len(traits_divcolumns[index].find_all('div', class_='breed-trait-score__score-unit--filled'))

            trait_scores = {
                'Affectionate With Family': get_trait_score(0),
                'Good With Young Children': get_trait_score(1),
                'Good With Other Dogs': get_trait_score(2),
                'Shedding Level': get_trait_score(3),
                'Coat Grooming Frequency': get_trait_score(4),
                'Drooling Level': get_trait_score(5),
                'Openness To Strangers': get_trait_score(8),
                'Playfulness Level': get_trait_score(9),
                'Watchdog/Protective Nature': get_trait_score(10),
                'Adaptability Level': get_trait_score(11),
                'Trainability Level': get_trait_score(12),
                'Energy Level': get_trait_score(13),
                'Barking Level': get_trait_score(14),
                'Mental Stimulation Needs': get_trait_score(15),
            }

            coat_type = [div.find('span').text for div in traits_divcolumns[6].find_all('div', class_='breed-trait-score__choice--selected')]
            coat_length = [div.find('span').text for div in traits_divcolumns[7].find_all('div', class_='breed-trait-score__choice--selected')]

            traits_score = {
                'breed_name': breedurl,
                'height': height if height is not None else [],
                'weight': weight if weight is not None else [],
                'life_expectancy': life_expectancy if life_expectancy is not None else [],
                **trait_scores,
                'Coat Type': coat_type,
                'Coat Length': coat_length,
            }

        return pd.DataFrame([traits_score])
    
    def get_breed_info_all(self):
        akcURL = pd.read_csv('./static/database/akcUrl.csv')
        result = pd.DataFrame()
        
        # 저장된 인덱스 확인
        start_index = 0
        if os.path.exists('./static/database/last_index.txt'):
            with open('./static/database/last_index.txt', 'r') as f:
                start_index = int(f.read().strip())

        for index, row in tqdm(akcURL.iterrows(), total=len(akcURL)):
            if index < start_index:
                continue  # 저장된 인덱스 이전은 건너뜀
            
            breedurl = row['breedurl']
            result = pd.concat([result, self.get_breed_info(breedurl)], ignore_index=True)

            # 10개마다 저장
            if (index + 1) % 10 == 0:
                result.to_csv('./static/database/akcBreedInfo.csv', index=False, mode='a', header=not os.path.exists('./static/database/akcBreedInfo.csv'))
                with open('./static/database/last_index.txt', 'w') as f:
                    f.write(str(index + 1))  # 현재 인덱스 저장

        return result