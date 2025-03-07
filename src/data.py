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
        self.url_review_list = "https://m.place.naver.com/restaurant/"


        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random,
            'Referer': 'https://m.place.naver.com/',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
        }

    def get_schedule(self, businessId, bizItemId, startDateTime, endDateTime):
        payload = {
            "operationName": "schedule",
            "query": """
                query schedule($scheduleParams: ScheduleParams) {
                    schedule(input: $scheduleParams) {
                        bizItemSchedule {
                            daily {
                                date
                                summary {
                                    dateKey
                                    minBookingCount
                                    maxBookingCount
                                    bookingCount
                                    stock
                                    isBusinessDay
                                    hasBusinessDays
                                    isSaleDay
                                    startTime
                                    endTime
                                    todayDealRate
                                    prices {
                                        groupName
                                        isDefault
                                        price
                                        priceId
                                        name
                                        normalPrice
                                        desc
                                        order
                                        saleStartDateTime
                                        saleEndDateTime
                                        __typename
                                    }
                                    __typename
                                }
                                __typename
                            }
                            __typename
                        }
                        __typename
                    }
                }
            """,
            "variables": {
                "scheduleParams": {
                    "businessId": businessId,
                    "bizItemId": bizItemId,
                    "businessTypeId": 5,
                    "startDateTime": startDateTime,
                    "endDateTime": endDateTime
                }
            }
        }

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
                'prices': datum['prices'][0]['price'] if datum['prices'] and len(datum['prices']) > 0 else 0
            })
        
        result = pd.DataFrame(result)
        return result
    
    def get_booking_list(self, businessId):
        payload = {
            "operationName": "bizItems",
            "query": """
                query bizItems(
                    $input: BizItemsParams, 
                    $withTypeValues: Boolean = false, 
                    $withReviewStat: Boolean = false, 
                    $withBookedCount: Boolean = false
                ) {
                    bizItems(input: $input) {
                        ...BizItemFragment
                        __typename
                    }
                }

                fragment BizItemFragment on BizItem {
                    id
                    agencyKey
                    businessId
                    bizItemId
                    bizItemType
                    name
                    desc
                    phone
                    stock
                    price
                    addressJson
                    startDate
                    endDate
                    refundDate
                    availableStartDate
                    bookingConfirmCode
                    bookingTimeUnitCode
                    isPeriodFixed
                    isOnsitePayment
                    isClosedBooking
                    isClosedBookingUser
                    isImp
                    minBookingCount
                    maxBookingCount
                    minBookingTime
                    maxBookingTime
                    extraFeeSettingJson
                    bookableSettingJson
                    bookingCountSettingJson
                    paymentSettingJson
                    bizItemSubType
                    priceByDates
                    websiteUrl
                    discountCardCode
                    customFormJson
                    optionCategoryMappings
                    bizItemCategoryId
                    additionalPropertyJson {
                        ageRatingSetting
                        openingHoursSetting
                        runningTime
                        parkingInfoSetting
                        ticketingTypeSetting
                        accommodationAdditionalProperty
                        arrangementCountSetting {
                            isUsingHeadCount
                            minHeadCount
                            maxHeadCount
                            __typename
                        }
                        bizItemCategorySpecificSetting {
                            instructorName
                            gatheringPlaceAddress
                            bizItemCategoryInfoMapping
                            bizItemCategoryInfo {
                                type
                                option
                                categoryInfoId
                                __typename
                            }
                            __typename
                        }
                        __typename
                    }
                    bookingCountType
                    isRequiringBookingOption
                    bookingUseGuideJson {
                        type
                        content
                        __typename
                    }
                    todayDealRate
                    extraDescJson
                    bookingPrecautionJson
                    isSeatUsed
                    isNPayUsed
                    isDeducted
                    isImpStock
                    isGreenTicket
                    orderSettingJson
                    isRobotDeliveryAvailable
                    bizItemAmenityJson {
                        amenityCode
                        amenityCategory
                        __typename
                    }
                    resources {
                        resourceUrl
                        __typename
                    }
                    bizItemResources {
                        resourceUrl
                        bizItemResourceSeq
                        bizItemId
                        order
                        resourceTypeCode
                        regDateTime
                        __typename
                    }
                    totalBookedCount @include(if: $withBookedCount)
                    currentDateTime @include(if: $withBookedCount)
                    reviewStatDetails @include(if: $withReviewStat) {
                        totalCount
                        avgRating
                        __typename
                    }
                    ...BizItemTypeValues @include(if: $withTypeValues)
                    ...MinMaxPrice
                    __typename
                }

                fragment BizItemTypeValues on BizItem {
                    typeValues {
                        bizItemId
                        code
                        codeValue
                        __typename
                    }
                    __typename
                }

                fragment MinMaxPrice on BizItem {
                    minMaxPrice {
                        minPrice
                        minNormalPrice
                        maxPrice
                        maxNormalPrice
                        isSinglePrice
                        discountRate {
                            min
                            max
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
            """,
            "variables": {
                "withTypeValues": False,
                "withReviewStat": False,
                "withBookedCount": False,
                "input": {
                    "businessId": businessId,
                    "lang": "ko",
                    "projections": "RESOURCE"
                },
                "withClosedBizItem": False
            }
        }

        response = req.post(self.url_booking_list, json=payload)
        data = response.json()["data"]["bizItems"]
        result = []
        for item in data:
            result.append({
                'bizItemId': item['bizItemId'],
                'bizItemName': item['name'],
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

        if not os.path.exists('./static/pension_info.csv'):
            result.to_csv('./static/pension_info.csv', index=False)
        else:
            result_old = pd.read_csv('./static/pension_info.csv')
            # 중복된 데이터가 생성되지 않도록 확인
            if not result['bizItemId'].isin(result_old['bizItemId']).any():
                result = pd.concat([result_old, result])
                result.to_csv('./static/pension_info.csv', index=False)

        result = pd.read_csv('./static/pension_info.csv')
        result.drop_duplicates(inplace=True)
        result.to_csv('./static/pension_info.csv', index=False)

    def get_pension_info(self, channel_id):
        url = f"{self.url_place_info}{channel_id}"
        response = req.get(url)
        data = response.json()['result']['place']['list'][0]
        name = data['name']
        address_old = data['address']
        address_new = data['roadAddress']
        return name, address_old, address_new

    def get_rating(self, channel_id):
        payload = [
            {
                "operationName": "getMyPlaceProfile",
                "variables": {},
                "query": "query getMyPlaceProfile {\n  user {\n    partnerHashedIdNo\n    myplace {\n      profile {\n        imageUrl\n        borderImageUrl\n        myplaceId\n        myplaceNickname\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}"
            },
            {
                "operationName": "getAnnouncements",
                "variables": {
                    "businessId": "1306861767",
                    "businessType": "place",
                    "deviceType": "pc"
                },
                "query": "query getAnnouncements($businessId: String!, $businessType: String!, $deviceType: String!) {\n  announcements: announcementsViaCP0(\n    businessId: $businessId\n    businessType: $businessType\n    deviceType: $deviceType\n  ) {\n    ...AnnouncementFields\n    __typename\n  }\n}\n\nfragment AnnouncementFields on Feed {\n  feedId\n  category\n  categoryI18n\n  title\n  relativeCreated\n  period\n  thumbnail {\n    url\n    count\n    isVideo\n    __typename\n  }\n  __typename\n}"
            },
            {
                "operationName": "getPromotions",
                "variables": {
                    "channelId": "1306861767",
                    "input": {"channelId": "1306861767"},
                    "isBooking": False
                },
                "query": "query getPromotions($channelId: String, $input: PromotionInput, $isBooking: Boolean!) {\n  naverTalk @skip(if: $isBooking) {\n    alarm(channelId: $channelId) {\n      friendYn\n      validation\n      __typename\n    }\n    __typename\n  }\n  promotionCoupons(input: $input) {\n    total\n    naverId\n    coupons {\n      promotionSeq\n      placeSeq\n      couponSeq\n      userCouponSeq\n      promotionTitle\n      conditionType\n      couponUseType\n      title\n      description\n      type\n      expiredDateDescription\n      status\n      image {\n        url\n        width\n        height\n        desc\n        __typename\n      }\n      downloadableCountInfo\n      expiredPeriodInfo\n      usedConditionInfos\n      couponButtonText\n      daysBeforeCouponStartDate\n      usableLandingUrl {\n        useSiteUrl\n        useBookingUrl\n        useOrderUrl\n        __typename\n      }\n      couponUsableDetail {\n        isImpPlace\n        isImpBooking\n        isImpOrder\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}"
            },
            {
                "operationName": "getBookmarks",
                "variables": {
                    "businessIdList": ["1306861767"]
                },
                "query": "query getBookmarks($businessIdList: [String]!) {\n  bookmarks(businessIdList: $businessIdList) {\n    id\n    sid\n    memo\n    __typename\n  }\n}"
            },
            {
                "operationName": "folder",
                "variables": {
                    "businessIdList": ["1306861767"]
                },
                "query": "query folder($businessIdList: [String]!) {\n  bookmarkFolders(businessIdList: $businessIdList) {\n    id\n    bookmarkId\n    placeId\n    folderMappings {\n      id\n      shareId\n      creationTime\n      name\n      markerColor\n      isDefaultFolder\n      __typename\n    }\n    __typename\n  }\n}"
            },
            {
                "operationName": "getVisitorReviews",
                "variables": {
                    "input": {
                        "businessId": "1306861767",
                        "bookingBusinessId": "896898",
                        "businessType": "place",
                        "size": 3,
                        "page": 1
                    }
                },
                "query": "query getVisitorReviews($input: VisitorReviewsInput) {\n  visitorReviews(input: $input) {\n    ...VisitorReviews\n    __typename\n  }\n}\n\nfragment VisitorReviews on VisitorReviewsResult {\n  items {\n    id\n    reviewId\n    rating\n    author {\n      id\n      nickname\n      from\n      imageUrl\n      borderImageUrl\n      objectId\n      url\n      review {\n        totalCount\n        imageCount\n        avgRating\n        __typename\n      }\n      theme {\n        totalCount\n        __typename\n      }\n      apolloCacheId\n      isFollowing\n      followerCount\n      followRequested\n      __typename\n    }\n    body\n    thumbnail\n    media {\n      type\n      thumbnail\n      thumbnailRatio\n      class\n      videoId\n      videoUrl\n      trailerUrl\n      __typename\n    }\n    tags\n    status\n    visitCount\n    viewCount\n    visited\n    visitedDate\n    created\n    reply {\n      editUrl\n      body\n      editedBy\n      created\n      date\n      status\n      replyTitle\n      isReported\n      isSuspended\n      __typename\n    }\n    themes {\n      theme\n      pattern\n      category\n      offsetStart\n      offsetEnd\n      similarity\n      miningValue\n      __typename\n    }\n    originType\n    item {\n      name\n      code\n      options\n      __typename\n    }\n    language\n    translatedText\n    bookingItemName\n    bookingItemOptions\n    businessName\n    showBookingItemName\n    showBookingItemOptions\n    votedKeywords {\n      code\n      iconUrl\n      iconCode\n      name\n      __typename\n    }\n    userIdno\n    isFollowing\n    followerCount\n    followRequested\n    loginIdno\n    apolloCacheId\n    receiptInfoUrl\n    showPaymentInfo\n    reactionStat {\n      id\n      typeCount {\n        name\n        count\n        __typename\n      }\n      totalCount\n      __typename\n    }\n    hasViewerReacted {\n      id\n      reacted\n      __typename\n    }\n    nickname\n    __typename\n  }\n  starDistribution {\n    score\n    count\n    __typename\n  }\n  hideProductSelectBox\n  total\n  score\n  showRecommendationSort\n  itemReviewStats {\n    itemId\n    count\n    score\n    __typename\n  }\n  __typename\n}"
            },
            {
                "operationName": "getVisitorReviewStats",
                "variables": {
                    "businessType": "place",
                    "id": "1306861767",
                    "itemId": "0"
                },
                "query": "query getVisitorReviewStats($id: String, $itemId: String, $businessType: String = \"place\") {\n  visitorReviewStats(\n    input: {businessId: $id, itemId: $itemId, businessType: $businessType}\n  ) {\n    id\n    name\n    apolloCacheId\n    review {\n      avgRating\n      totalCount\n      scores {\n        count\n        score\n        __typename\n      }\n      starDistribution {\n        count\n        score\n        __typename\n      }\n      imageReviewCount\n      authorCount\n      maxSingleReviewScoreCount\n      maxScoreWithMaxCount\n      __typename\n    }\n    analysis {\n      themes {\n        code\n        label\n        count\n        __typename\n      }\n      menus {\n        code\n        label\n        count\n        __typename\n      }\n      votedKeyword {\n        totalCount\n        reviewCount\n        userCount\n        details {\n          category\n          code\n          iconUrl\n          iconCode\n          displayName\n          count\n          previousRank\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    visitorReviewsTotal\n    ratingReviewsTotal\n    __typename\n  }\n}"
            },
            {
                "operationName": "getVisitorReviewStats",
                "variables": {
                    "businessType": "place",
                    "id": "1306861767"
                },
                "query": "query getVisitorReviewStats($id: String, $itemId: String, $businessType: String = \"place\") {\n  visitorReviewStats(\n    input: {businessId: $id, itemId: $itemId, businessType: $businessType}\n  ) {\n    id\n    name\n    apolloCacheId\n    review {\n      avgRating\n      totalCount\n      scores {\n        count\n        score\n        __typename\n      }\n      starDistribution {\n        count\n        score\n        __typename\n      }\n      imageReviewCount\n      authorCount\n      maxSingleReviewScoreCount\n      maxScoreWithMaxCount\n      __typename\n    }\n    analysis {\n      themes {\n        code\n        label\n        count\n        __typename\n      }\n      menus {\n        code\n        label\n        count\n        __typename\n      }\n      votedKeyword {\n        totalCount\n        reviewCount\n        userCount\n        details {\n          category\n          code\n          iconUrl\n          iconCode\n          displayName\n          count\n          previousRank\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    visitorReviewsTotal\n    ratingReviewsTotal\n    __typename\n  }\n}"
            }
        ]

        response = req.post(self.url_rating, json=payload)
        return response

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
        
    def get_rating_data(self, df):
        rating_data = pd.DataFrame()
        errors = []  # 오류 기록용
        
        for index, row in tqdm(df.iterrows(), total=len(df)):
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
            rating_data.to_csv('./static/rating_data.csv', index=False)
            return rating_data
        else:
            # 데이터가 없는 경우 빈 데이터프레임 반환
            print("경고: 수집된 리뷰 데이터가 없습니다!")
            return pd.DataFrame(columns=['channelId', 'review_item', 'rating', 'businessName']) 
        

    def _get_rating(self, channel_id):
        wait_time = random.uniform(0.1, 0.2)
        time.sleep(wait_time)
        url = f"{self.url_review_list}{channel_id}/review/visitor"
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