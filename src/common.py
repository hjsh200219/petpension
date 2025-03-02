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


class Common:
    def __init__(self):
        pass


class UI:
    @staticmethod
    def load_css(css_file):
        """CSS 파일을 로드하는 함수"""
        with open(css_file) as f:
            st.markdown(
                f'<style>{f.read()}</style>', 
                unsafe_allow_html=True
            )

    @staticmethod
    def display_banner():
        """페이지 상단에 배너를 표시하는 함수"""
        st.markdown(
            """
             <div class="banner">
                    <iframe 
                        src="https://ads-partners.coupang.com/widgets.html?id=842740&template=carousel&trackingCode=AF6451134&subId=&width=680&height=140&tsource=" 
                        frameborder="0" 
                        scrolling="no" 
                        referrerpolicy="unsafe-url" 
                        browsingtopics>
                    </iframe>
                </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def display_footer():
        """페이지 하단에 푸터를 표시하는 함수"""
        current_year = datetime.now().year
        st.markdown(
            f"""
            <div class="footer">
                <p>© {current_year} SH Consulting. All rights reserved.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def add_input_focus_js(selector="input[type='password']", delay=800):
        """
        특정 입력 필드에 자동 포커스를 추가하는 JavaScript 코드
        
        Parameters:
        -----------
        selector : str
            포커스할 HTML 요소의 CSS 선택자
        delay : int
            페이지 로드 후 포커스를 적용할 지연 시간(밀리초)
        """
        js_code = f"""
        <script>
        // 페이지 로드 후 {delay}ms 후에 포커스 시도
        setTimeout(function() {{
            const inputs = parent.document.querySelectorAll('{selector}');
            if (inputs.length > 0) {{
                inputs[0].focus();
            }}
        }}, {delay});
        </script>
        """
        st.components.v1.html(js_code, height=0)

    @staticmethod
    def create_password_input(on_change_callback: Callable, 
                            error_message: str = "비밀번호가 틀렸습니다. 다시 시도해주세요.",
                            has_error: bool = False,
                            placeholder: str = "비밀번호를 입력하세요",
                            key: str = "password_input"):
        """
        비밀번호 입력 양식을 생성합니다.
        
        Parameters:
        -----------
        on_change_callback : Callable
            비밀번호 입력 시 호출될 콜백 함수
        error_message : str
            오류 발생 시 표시할 메시지
        has_error : bool
            오류 상태 여부
        placeholder : str
            입력 필드에 표시할 안내 텍스트
        key : str
            입력 필드의 고유 키 (기본값: "password_input")
        """
        # 자동 포커스 스크립트 추가
        UI.add_input_focus_js()
        
        # 오류 메시지 표시
        if has_error:
            st.error(error_message)
        
        # 비밀번호 입력 UI
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input(
                placeholder, 
                type="password", 
                key=key, 
                label_visibility="collapsed", 
                on_change=on_change_callback
            )
        with col2:
            st.button(
                "확인", 
                key=f"{key}_button", 
                use_container_width=False,
                on_click=on_change_callback
            )
        
        return password

    @staticmethod
    def create_filter_ui(data: pd.DataFrame, 
                        filter_values: Dict[str, str], 
                        on_change_callbacks: Dict[str, Callable],
                        column_names: Dict[str, str]) -> None:
        """
        필터링 UI를 생성합니다.
        
        Parameters:
        -----------
        data : pd.DataFrame
            필터링할 데이터
        filter_values : Dict[str, str]
            현재 필터 값 (key: 필터 이름, value: 선택된 값)
        on_change_callbacks : Dict[str, Callable]
            각 필터의 값이 변경될 때 호출할 콜백 함수
        column_names : Dict[str, str]
            컬럼 매핑 정보 (key: 내부 컬럼명, value: 표시 컬럼명)
        """
        # 컬럼 생성
        filter_cols = st.columns(len(filter_values))
        
        # 필터 값 목록 추출
        for i, (filter_key, current_value) in enumerate(filter_values.items()):
            if filter_key not in column_names:
                continue
                
            display_name = column_names[filter_key]
            column_name = column_names[filter_key]
            
            # 필터 옵션 생성
            options = ["전체"]
            if filter_key in data.columns:
                options.extend(list(data[filter_key].unique()))
            
            # 현재 선택 인덱스
            selected_index = 0
            if current_value in options:
                selected_index = options.index(current_value)
                
            # 셀렉트박스 생성
            with filter_cols[i]:
                st.selectbox(
                    f"{display_name} 선택",
                    options=options,
                    key=f"{filter_key}_filter_widget",
                    index=selected_index,
                    on_change=on_change_callbacks.get(filter_key, None)
                )

    @staticmethod
    def show_dataframe_with_info(df: pd.DataFrame, 
                                hide_index: bool = True, 
                                use_container_width: bool = True) -> None:
        """
        데이터프레임을 표시하고 결과 개수도 함께 보여줍니다.
        
        Parameters:
        -----------
        df : pd.DataFrame
            표시할 데이터프레임
        hide_index : bool
            인덱스 숨김 여부
        use_container_width : bool
            컨테이너 너비 사용 여부
        """
        # 데이터프레임 표시
        st.dataframe(
            df, 
            use_container_width=use_container_width,
            hide_index=hide_index
        )
        
        # 결과 개수 표시
        st.info(f"총 {len(df)}개의 결과가 있습니다.")

    @staticmethod
    def show_date_range_selector(default_start_date=None, 
                                default_end_date=None, 
                                search_button_label="검색") -> Tuple:
        """
        날짜 범위 선택기를 표시합니다.
        
        Parameters:
        -----------
        default_start_date : datetime.date, optional
            기본 시작 날짜
        default_end_date : datetime.date, optional
            기본 종료 날짜
        search_button_label : str
            검색 버튼 라벨
            
        Returns:
        --------
        Tuple[datetime.date, datetime.date, bool]
            선택된 시작 날짜, 종료 날짜, 검색 버튼 클릭 여부
        """
        if default_start_date is None:
            default_start_date = datetime.now().date()
            
        if default_end_date is None:
            default_end_date = (datetime.now() + timedelta(days=30)).date()
        
        # 날짜 선택 레이아웃
        col1, col2, col3 = st.columns((1, 1, 3))
        
        with col1:
            start_date = st.date_input(
                "시작 날짜", 
                default_start_date, 
                label_visibility="collapsed"
            )
            
        with col2:
            end_date = st.date_input(
                "종료 날짜", 
                default_end_date, 
                label_visibility="collapsed"
            )
            
        with col3:
            search_button = st.button(
                search_button_label, 
                use_container_width=False
            )
        
        return start_date, end_date, search_button


class Naver:
    def __init__(self):
        self.url_schedule = "https://m.booking.naver.com/graphql?opName=schedule"
        self.url_booking_list = "https://m.booking.naver.com/graphql?opName=bizItems"
        self.url_pension_info = "https://m.place.naver.com/accommodation/"
        self.url_place_info = "https://pages.map.naver.com/save-widget/api/maps-search/place?id="
        self.url_booking = "https://map.naver.com/p/entry/place/"
        self.url_rating = "https://api.place.naver.com/graphql"
        self.url_rating_detail = "https://m.place.naver.com/place/"

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
                'prices': datum['prices'][0]['price'] 
                          if datum['prices'] and len(datum['prices']) > 0 
                          else 0
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

    def _get_rating(self, channel_id):
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
                    page.set_default_navigation_timeout(60000)  # 60초로 타임아웃 증가
                    page.set_default_timeout(60000)
                    
                    # 봇 감지 우회 스크립트 실행
                    page.evaluate("""
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => false,
                        });
                    """)
                    
                    # 무작위 지연 시간 추가 (10~20초, 첫 시도에서는 더 짧게)
                    delay = random.uniform(5, 10) if retry_count == 0 else random.uniform(10, 20)
                    print(f"요청 전 {delay:.1f}초 대기 중...")
                    time.sleep(delay)
                    
                    # 네이버 메인 페이지 먼저 방문
                    page.goto("https://www.naver.com")
                    time.sleep(random.uniform(3, 5))
                    
                    # 마우스 움직임 시뮬레이션
                    page.mouse.move(random.randint(100, 800), random.randint(100, 600))
                    time.sleep(random.uniform(0.5, 2))
                    
                    # 페이지 스크롤
                    page.evaluate("window.scrollBy(0, 300)")
                    time.sleep(random.uniform(0.5, 2))
                    
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
                            time.sleep(random.uniform(1, 2))  # 클릭 후 대기
                    
                    # 페이지에 "과도한 접근 요청" 문구가 있는지 확인
                    content = page.content()
                    if "과도한 접근 요청으로 서비스 이용이 제한되었습니다" in content:
                        print(f"접근 제한 감지됨. 재시도 {retry_count + 1}/{max_retries}")
                        browser.close()
                        retry_count += 1
                        # 더 긴 대기 시간
                        wait_time = 30 + retry_count * 30  # 30초, 60초, 90초...
                        print(f"{wait_time}초 후에 재시도합니다...")
                        time.sleep(wait_time)
                        continue
                    
                    # 추가 지연 시간 및 활동 시뮬레이션
                    time.sleep(random.uniform(1, 3))
                    
                    # 페이지에서 스크롤
                    page.evaluate("window.scrollBy(0, 300)")
                    time.sleep(random.uniform(1, 2))
                    
                    # 페이지 내용 가져오기
                    html = page.content()
                    soup = BS(html, 'html.parser')
                    divs = soup.find_all('div', class_='place_section_content')
                    div = divs[0]
                    ul = div.find('ul')
                    lis = ul.find_all('li')
                    reviews_data = []
                    for li in lis:
                        review_text = li.find('span', class_='t3JSf').text.strip().replace('"', '')
                        participant_count = ''.join(filter(str.isdigit, li.find('span', class_='CUoLy').text.strip()))
                        reviews_data.append({"channelId": channel_id, "review_item": review_text, "raing": participant_count})
                    reviews_data = pd.DataFrame(reviews_data)
                            
                    # 세션 정리
                    browser.close()
                    return reviews_data
                    
            except Exception as e:
                print(f"오류 발생: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 30 + retry_count * 30
                    print(f"{wait_time}초 후에 재시도합니다...")
                    time.sleep(wait_time)
                else:
                    return {"error": str(e), "status": "error"}
        
        return {"error": "최대 재시도 횟수 초과", "status": "failed"}
        
    def get_rating_data(self):
        pension_info = pd.read_csv('./static/pension_info.csv')[['businessName', 'channelId']].drop_duplicates()
        rating_data = pd.DataFrame()
        for index, row in tqdm(pension_info.iterrows(), total=len(pension_info)):
            result = self._get_rating(row['channelId'])
            result['businessName'] = row['businessName']
            result['channelId'] = row['channelId']
            rating_data = pd.concat([rating_data, result], ignore_index=True)
        rating_data.to_csv('./static/rating_data.csv', index=False)
        return rating_data