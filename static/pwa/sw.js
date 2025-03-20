const CACHE_NAME = 'petpension-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/pwa/manifest.json'
];

// 서비스 워커 설치 및 리소스 캐싱
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('캐시를 열었습니다.');
        return cache.addAll(urlsToCache);
      })
  );
});

// 네트워크 요청 가로채기 및 캐시된 응답 반환
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // 캐시에서 찾은 경우 해당 응답 반환
        if (response) {
          return response;
        }
        
        // 캐시에서 찾지 못한 경우 네트워크에서 가져오기
        return fetch(event.request)
          .then(response => {
            // 유효한 응답이 아니거나 오류 응답인 경우 그대로 반환
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            
            // 응답을 복제하여 캐시에 저장
            let responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });
            
            return response;
          })
          .catch(error => {
            console.log('네트워크 요청 실패:', error);
            // 오프라인 페이지나 오류 페이지 표시
          });
      })
  );
});

// 이전 캐시 삭제
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
}); 