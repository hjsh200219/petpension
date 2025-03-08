"""
네이버 API 요청을 위한 페이로드 템플릿을 관리하는 모듈
"""

def payload_schedule(business_id, biz_item_id, start_date_time, end_date_time):
    """
    일정 조회를 위한 API 페이로드
    """
    return {
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
                "businessId": business_id,
                "bizItemId": biz_item_id,
                "businessTypeId": 5,
                "startDateTime": start_date_time,
                "endDateTime": end_date_time
            }
        }
    }

def payload_booking_list(business_id):
    """
    숙박 상품 목록 조회를 위한 API 페이로드
    """
    return {
        "operationName": "bizItems",
        "query": """
            query bizItems($bizItemsParams: BizItemsParams) {
                bizItems(input: $bizItemsParams) {
                    bizItems {
                        optionsUnified
                        id
                        category
                        name
                        desc
                        tags
                        images {
                            url
                            desc
                            __typename
                        }
                        price {
                            isFixedPrice
                            fixedPrice
                            useRealTime
                            __typename
                        }
                        avgRating
                        ratingCount
                        bookingSettings {
                            isImprovePriceUse
                            price
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
            }
        """,
        "variables": {
            "bizItemsParams": {
                "businessId": business_id,
                "businessTypeId": 5,
                "useNaverMemberCoupon": False
            }
        }
    }

def payload_visitor_reviews(business_id, page=1, display=100):
    """
    방문자 리뷰 조회를 위한 API 페이로드
    """
    return {
        "query": """
        query getVisitorReviews($input: VisitorReviewsInput) {
          visitorReviews(input: $input) {
            items {
              id
              rating
              body
              thumbnailUrl
              tags
            }
            totalCount
          }
        }
        """,
        "variables": {
            "input": {
                "businessId": business_id,
                "businessType": "restaurant",
                "page": page,
                "display": display,
                "includeContent": True,
                "getAuthorInfo": False
            }
        }
    }

def payload_rating(channel_id):
    """
    평점 조회를 위한 API 페이로드
    """
    return [
        {
            "operationName": "getTotalReviewCount",
            "query": "query getTotalReviewCount($input: GetTotalReviewCountInput) {\n  getTotalReviewCount(input: $input) {\n    totalCount\n    photosCount\n    scoreDistribution {\n      count\n      score\n      __typename\n    }\n    __typename\n  }\n}",
            "variables": {
                "input": {
                    "businessId": channel_id,
                    "businessType": "accommodation",
                    "item": "total"
                }
            }
        },
        {
            "operationName": "getReviews",
            "query": "query getReviews($input: GetReviewsInput) {\n  getReviews(input: $input) {\n    reviewsByItem {\n      items {\n        id\n        name\n        score\n        avatarUrl\n        isFollowing\n        createdAt\n        isUserRate\n        body\n        authorLocation\n        authorDate\n        authorVehicle\n        isVerification\n        visitCount\n        tags\n        userPhotos {\n          id\n          url\n          thumbnailUrl\n          isAlive\n          videoId\n          videoPlaytime\n          thumbnailImageSize {\n            width\n            height\n            __typename\n          }\n          imageSize {\n            width\n            height\n            __typename\n          }\n          __typename\n        }\n        reply {\n          itemReply {\n            body\n            updatedAt\n            managerNickname\n            __typename\n          }\n          businessReply {\n            body\n            updatedAt\n            managerNickname\n            __typename\n          }\n          __typename\n        }\n        originCode\n        items {\n          name\n          url\n          bookingParameters {\n            checkIn\n            checkOut\n            entry\n            guest\n            roomId\n            roomName\n            __typename\n          }\n          options {\n            name\n            __typename\n          }\n          paymentInfo {\n            pgPayment\n            naverPoint\n            naverpayPoint\n            totalPayment\n            __typename\n          }\n          __typename\n        }\n        contract {\n          sid\n          name\n          options {\n            name\n            __typename\n          }\n          paymentInfo {\n            pgPayment\n            naverPoint\n            naverpayPoint\n            totalPayment\n            __typename\n          }\n          __typename\n        }\n        originBusinessName\n        marketerAuthorId\n        compensationInfo {\n          compensated\n          compensationChannel\n          __typename\n        }\n        easeYn\n        reviewEventContent\n        reviewCriterias {\n          code\n          name\n          score\n          __typename\n        }\n        __typename\n      }\n      starDistribution {\n        rating\n        count\n        ratio\n        __typename\n      }\n      filterItemCount {\n        name\n        count\n        __typename\n      }\n      hideProductSelectBox\n      totalCount\n      totalPages\n      hasMore\n      __typename\n    }\n    __typename\n  }\n}",
            "variables": {
                "input": {
                    "businessId": channel_id,
                    "businessType": "accommodation",
                    "display": 3,
                    "item": "total",
                    "page": 1
                }
            }
        }
    ]

def payload_photos(channel_id, page=1, display=10):
    """
    사진 조회를 위한 API 페이로드
    """
    return [
        {
            "operationName": "getPlacePhotos",
            "query": "query getPlacePhotos($input: PlacePhotosInput) {\n  placePhotos(input: $input) {\n    total\n    items {\n      id\n      type\n      photoType\n      photoCount\n      url\n      aspectRatio\n      seoUrl\n      seoText\n      htmlClassName\n      author {\n        id\n        nickname\n        objectId\n        url\n        type\n        profile {\n          url\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
            "variables": {
                "input": {
                    "businessId": channel_id,
                    "businessType": "accommodation",
                    "photoType": "photo",
                    "page": page,
                    "display": display,
                    "isPhotoViewer": False,
                    "includeAllPhotos": False,
                    "includeHdPhoto": False,
                    "includeMarketItem": False
                }
            }
        },
        {
            "operationName": "getPhotoTabFilters",
            "query": "query getPhotoTabFilters($input: PhotoTabFiltersInput) {\n  photoTabFilters(input: $input) {\n    tabFilters {\n      item\n      imgUrl\n      __typename\n    }\n    __typename\n  }\n}",
            "variables": {
                "input": {
                    "businessId": channel_id,
                    "businessType": "accommodation"
                }
            }
        }
    ] 