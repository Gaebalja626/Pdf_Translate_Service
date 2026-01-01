# RunPod 빠른 시작 가이드

## 🚀 5분 안에 시작하기

### Step 1: RunPod 계정 및 Pod 생성

1. **RunPod 가입**: https://www.runpod.io
2. **잔액 충전**: $10 이상
3. **Pod 생성**:
   - GPU: RTX 4090 또는 RTX 3090
   - Template: **RunPod PyTorch**
   - Volume: 50GB
   - **Expose HTTP Ports**: `8000` 입력 ⚠️ 중요!
   - Deploy 클릭

---

## Step 2: 프로젝트 파일 업로드

### 방법 1: 직접 업로드 (추천)

1. **프로젝트 압축**:
   - 로컬에서 `ocr-translation-service` 폴더를 zip으로 압축
   - 파일명: `ocr-translation-service.zip`

2. **JupyterLab 접속**:
   - Pod에서 **Connect** → **Connect to JupyterLab** 클릭

3. **파일 업로드**:
   - JupyterLab 왼쪽 파일 브라우저에서 업로드 버튼 클릭
   - `ocr-translation-service.zip` 업로드

4. **압축 해제**:
   - JupyterLab에서 **Terminal** 열기
   - 다음 명령어 실행:
   ```bash
   cd /workspace
   unzip ocr-translation-service.zip
   cd ocr-translation-service
   ls -la  # 파일 확인
   ```

### 방법 2: GitHub 사용

```bash
cd /workspace
git clone https://github.com/YOUR_USERNAME/ocr-translation-service.git
cd ocr-translation-service
```

---

## Step 3: 자동 설치 스크립트 실행

Web Terminal 또는 JupyterLab Terminal에서:

```bash
cd /workspace/ocr-translation-service
chmod +x setup_runpod.sh
./setup_runpod.sh
```

이 스크립트가 자동으로:
- ✅ PaddlePaddle GPU 설치
- ✅ PaddleOCR 설치
- ✅ FastAPI 및 모든 의존성 설치
- ✅ GPU 확인

**예상 시간**: 5-10분

---

## Step 4: 서버 실행

```bash
cd /workspace/ocr-translation-service/backend
python main.py
```

서버가 시작되면:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Step 5: 웹 접속

1. **RunPod 대시보드**로 돌아가기
2. Pod 카드에서 **TCP Port Mappings** 찾기
3. **포트 8000** 옆의 URL 클릭 (예: `https://xxxxx-8000.proxy.runpod.net`)
4. 웹 페이지가 열리면 성공! 🎉

---

## 📝 수동 설치 (스크립트 실패 시)

```bash
# 1. PaddlePaddle GPU
pip install paddlepaddle-gpu==3.0.0b1 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/

# 2. PaddleOCR
pip install -U "paddleocr[doc-parser]"

# 3. 기타 의존성
pip install fastapi uvicorn python-multipart aiofiles pydantic
pip install transformers sentencepiece sacremoses torch
pip install reportlab Pillow pymupdf python-dotenv

# 4. 확인
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 🐛 문제 해결

### GPU 인식 안 됨
```bash
nvidia-smi  # GPU 확인
python -c "import torch; print(torch.cuda.is_available())"
```

### 포트 8000 접속 안 됨
- Pod 설정에서 HTTP Ports에 8000 추가했는지 확인
- 서버가 `0.0.0.0:8000`에서 실행 중인지 확인

### 메모리 부족
- `backend/config.py`에서 `TRANSLATION_BATCH_SIZE` 줄이기 (8 → 4)

---

## 💰 비용 절약 팁

1. **사용 후 즉시 중지**: Pod 카드에서 **Stop** 클릭
2. **장기간 미사용 시**: **Terminate** 클릭
3. **모델 캐싱**: Volume에 모델 저장하여 재사용
   ```bash
   export HF_HOME=/workspace/models
   export TRANSFORMERS_CACHE=/workspace/models
   ```

---

## ✅ 체크리스트

- [ ] RunPod 계정 생성 및 충전
- [ ] GPU Pod 생성 (포트 8000 노출!)
- [ ] 프로젝트 파일 업로드
- [ ] setup_runpod.sh 실행
- [ ] 서버 실행 (python main.py)
- [ ] 웹 브라우저에서 접속
- [ ] PDF 업로드 테스트
- [ ] 사용 후 Pod 중지

---

## 🎯 예상 소요 시간

- Pod 생성: 1분
- 파일 업로드: 2분
- 의존성 설치: 5-10분
- 서버 실행: 1분
- **총: 약 10-15분**

궁금한 점이 있으면 언제든지 물어보세요! 🚀
