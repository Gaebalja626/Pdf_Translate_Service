# RunPod 즉시 시작 가이드

## ⚠️ 중요: 포트 8000 추가 필요

현재 Pod에 포트 8000이 노출되지 않았습니다. 다음 중 하나를 선택하세요:

### 옵션 1: Pod 편집 (권장)
1. RunPod 대시보드에서 Pod 찾기
2. **Edit** 버튼 클릭
3. **Expose HTTP Ports** 섹션에 `8000` 추가
4. **Save** 클릭
5. Pod 재시작

### 옵션 2: 포트 8888 사용 (임시)
Jupyter Lab 포트를 사용하여 테스트:
- `backend/main.py`에서 포트를 8888로 변경
- 또는 실행 시: `uvicorn main:app --host 0.0.0.0 --port 8888`

---

## 🚀 빠른 시작 (Web Terminal 사용)

### 1. Web Terminal 활성화
RunPod 대시보드에서:
1. **Enable web terminal** 클릭
2. Web Terminal 열기

### 2. 프로젝트 다운로드 및 설치

```bash
# 작업 디렉토리로 이동
cd /workspace

# 프로젝트 클론 (GitHub 업로드 후)
# git clone https://github.com/YOUR_USERNAME/ocr-translation-service.git

# 임시: 직접 파일 업로드 사용
# JupyterLab에서 프로젝트 zip 파일 업로드 후:
unzip ocr-translation-service.zip
cd ocr-translation-service

# 자동 설치 스크립트 실행
chmod +x setup_runpod.sh
./setup_runpod.sh
```

### 3. 서버 실행

**포트 8000 추가한 경우:**
```bash
cd backend
python main.py
```

**포트 8888 사용하는 경우 (임시):**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8888
```

### 4. 접속

**포트 8000 사용:**
- RunPod 대시보드에서 포트 8000 URL 찾기
- 예: `https://xxxxx-8000.proxy.runpod.net`

**포트 8888 사용:**
- Jupyter Lab URL 사용
- 예: `https://wz51w18ljho2dl-8888.proxy.runpod.io`

---

## 📦 GitHub 업로드 방법

### 수동 업로드 (GitHub 웹사이트)

1. **GitHub 접속**: https://github.com
2. **New Repository** 클릭
3. 설정:
   - Name: `ocr-translation-service`
   - Public
   - **README 체크 해제**
4. **Create repository**

5. **로컬에서 푸시**:
```powershell
cd C:\Users\gaeba\.gemini\antigravity\scratch\ocr-translation-service
git remote add origin https://github.com/YOUR_USERNAME/ocr-translation-service.git
git branch -M main
git push -u origin main
```

---

## 🎯 현재 상황 요약

✅ **완료된 것:**
- RunPod Pod 생성됨
- SSH 접속 가능
- Jupyter Lab 사용 가능 (포트 8888)

⚠️ **필요한 작업:**
1. 포트 8000 추가 (Pod 편집) 또는 포트 8888 사용
2. 프로젝트 파일 업로드 (JupyterLab 또는 GitHub)
3. 의존성 설치 (`setup_runpod.sh`)
4. 서버 실행

---

## 💡 추천 방법

**가장 빠른 방법:**
1. JupyterLab 접속 (이미 가능)
2. 프로젝트 zip 파일 업로드
3. Terminal에서 설치 스크립트 실행
4. 포트 8888로 서버 실행
5. Jupyter Lab URL로 접속

이렇게 하면 Pod 설정 변경 없이 바로 테스트 가능합니다!
