# 📱 안드로이드 앱으로 만들기

이 streamlit 앱을 안드로이드 앱(`.apk` / Google Play)으로 배포하는 방법.

## 1단계 ⭐ — 가장 쉬움: "홈 화면에 추가" (PWA)

설치 없이 5초 만에 앱처럼 사용:

### Android (Chrome)
1. Chrome에서 `https://wilkommen-schatziya.streamlit.app` 접속
2. 우상단 메뉴 `⋮` → **"홈 화면에 추가"** 또는 **"앱 설치"**
3. 홈에 한국어 아이콘 생김. 풀스크린으로 실행됨

### iPhone (Safari)
1. Safari에서 접속
2. 하단 공유 버튼 → **"홈 화면에 추가"**
3. 같은 결과

> manifest + theme-color는 `app.py`에서 자동으로 inject 되므로 그냥 위 단계만 따라가면 됩니다.

## 2단계 ⭐⭐ — 진짜 `.apk` 만들기 (PWABuilder, 무료)

[PWABuilder.com](https://www.pwabuilder.com)이 PWA URL → `.apk` 자동 빌드.

1. https://www.pwabuilder.com 접속
2. URL 입력: `https://wilkommen-schatziya.streamlit.app`
3. **"Start"** → manifest/service worker 분석 보고서
4. **"Package for stores"** → **Android** 탭
5. **"Generate Package"** → ZIP 다운로드
6. ZIP 안의 `.apk` 또는 `.aab` 파일이 진짜 안드로이드 패키지

### 사이드로드 (Google Play 거치지 않고 바로 설치)
- `.apk`를 본인 폰에 복사 → 파일 열기 → "알 수 없는 앱 설치 허용" → 설치

### Google Play 게시 (전 세계 배포)
- [Google Play Console](https://play.google.com/console) 개발자 등록 **(1회 $25)**
- 위 ZIP 안의 `.aab` 파일 업로드
- 스크린샷·설명·정책 페이지 작성
- 심사 1–7일 → Play에 노출

## 3단계 ⭐⭐⭐ — 완전 네이티브 (Bubblewrap CLI)

Google이 권장하는 PWA → TWA (Trusted Web Activity) 변환:

```bash
# Node.js 필요
npm install -g @bubblewrap/cli
bubblewrap init --manifest=https://wilkommen-schatziya.streamlit.app/app/static/manifest.json
bubblewrap build
```

`app-release-signed.apk` 생성됨. PWABuilder와 결과는 비슷.

## ⚠️ 주의 & 한계

- **인터넷 필요**: streamlit cloud 위에서 실행되므로 오프라인 동작 안 됨
- **첫 로딩 느림**: streamlit cloud free tier는 idle 후 sleep → 첫 접속 시 30초 wake-up
- **iOS 앱스토어**: TWA는 Android 전용. iOS 앱은 별도 작업(SwiftUI WebView wrapper 등)
- **돈 절약**: 본인+남친만 쓸 거면 1단계(PWA)로 충분. Play 게시는 $25 + 심사 노력

## 추천 경로

| 목표 | 방법 |
|---|---|
| 본인/지인용 폰에 앱처럼 띄움 | **1단계** (홈 화면 추가) |
| `.apk` 파일 만들어 친구한테 보냄 | **2단계** PWABuilder → .apk 사이드로드 |
| Play Store 정식 배포 | **2단계** PWABuilder → .aab → Play Console |

---

생성된 PWA 파일:
- `static/manifest.json` — 앱 메타데이터
- `static/icon.svg` — 보라/핑크 그라데이션 위 "한" 아이콘
- `.streamlit/config.toml` — `enableStaticServing = true` (static/ 서빙)
- `app.py` — `<head>`에 manifest link 자동 inject
