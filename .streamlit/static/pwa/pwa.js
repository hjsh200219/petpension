// PWA 기능 초기화
document.addEventListener('DOMContentLoaded', function() {
    initPWA();
});

function initPWA() {
    // 서비스 워커 등록
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/static/pwa/sw.js')
                .then(function(registration) {
                    console.log('서비스 워커 등록 성공:', registration.scope);
                })
                .catch(function(error) {
                    console.log('서비스 워커 등록 실패:', error);
                });
        });
    }

    // 설치 프롬프트 처리
    let deferredPrompt;
    const installButton = document.getElementById('install-pwa');
    
    window.addEventListener('beforeinstallprompt', (e) => {
        // 브라우저 기본 설치 프롬프트 방지
        e.preventDefault();
        // 이벤트 저장
        deferredPrompt = e;
        // 설치 버튼 표시
        if (installButton) {
            installButton.style.display = 'block';
        }
    });

    // 설치 버튼 이벤트 리스너
    if (installButton) {
        installButton.addEventListener('click', async () => {
            if (deferredPrompt) {
                // 설치 프롬프트 표시
                deferredPrompt.prompt();
                // 사용자의 응답 대기
                const { outcome } = await deferredPrompt.userChoice;
                console.log(`사용자 응답: ${outcome}`);
                // 이벤트 초기화
                deferredPrompt = null;
                // 설치 버튼 숨기기
                installButton.style.display = 'none';
            }
        });
    }

    // 이미 설치된 경우 버튼 숨기기
    window.addEventListener('appinstalled', (e) => {
        if (installButton) {
            installButton.style.display = 'none';
        }
        console.log('앱이 설치되었습니다.');
    });
} 