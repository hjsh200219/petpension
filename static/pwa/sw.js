const CACHE_NAME = 'petpension-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/pwa/manifest.json',
  '/static/pwa/offline.html',
  '/static/pwa/pwa.js'
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
            
            // HTML 페이지 요청인 경우 오프라인 페이지 반환
            if (event.request.mode === 'navigate') {
              return caches.match('/static/pwa/offline.html');
            }
            
            // 이미지 요청인 경우 기본 이미지 반환 (선택적)
            if (event.request.destination === 'image') {
              return caches.match('/static/pwa/icons/icon-192x192.png');
            }
            
            // 기타 리소스는 실패 처리
            return new Response('오프라인 상태입니다.', {
              status: 503,
              statusText: 'Service Unavailable',
              headers: new Headers({
                'Content-Type': 'text/plain'
              })
            });
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

// 온라인/오프라인 상태 변경 처리
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'ONLINE_STATUS_CHANGE') {
    // 클라이언트에 상태 변경 메시지 전달
    self.clients.matchAll().then(clients => {
      clients.forEach(client => {
        client.postMessage({
          type: 'ONLINE_STATUS_UPDATE',
          online: event.data.online
        });
      });
    });
  }
}); 