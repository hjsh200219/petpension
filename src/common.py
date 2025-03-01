from tqdm import tqdm
import pandas as pd
import requests as req
import json, math, datetime
import concurrent.futures
from io import BytesIO, StringIO
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import os

class Common:
    def __init__(self):
        pass


class Naver:
    def __init__(self):
        self.url_schedule = "https://m.booking.naver.com/graphql?opName=schedule"
        self.url_booking_list = "https://m.booking.naver.com/graphql?opName=bizItems"


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
        print(response.status_code)
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
                'address_old': item['addressJson']['jibun'],
                'address_new': item['addressJson']['roadAddr'],
            })

        result = pd.DataFrame(result)
        return result
    
    def insert_pension_info(self, business_name, business_id):
        result = self.get_booking_list(business_id)
        result['businessName'] = business_name
        result['businessId'] = business_id

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


