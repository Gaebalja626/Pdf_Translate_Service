# RunPod GPU 서버 사용 가이드

## 📌 RunPod란?

RunPod는 클라우드 GPU 서버를 쉽게 빌릴 수 있는 서비스입니다. 로컬에 GPU가 없어도 강력한 GPU 서버를 사용할 수 있습니다.

**가격 예시:**
- RTX 3090: ~$0.22/시간
- RTX 4090: ~$0.34/시간
- A100: ~$1.19/시간
- H100: ~$1.99/시간

**장점:**
- ✅ 초 단위 과금 (사용한 만큼만 지불)
- ✅ 데이터 전송 비용 없음
- ✅ 빠른 배포 (몇 초 만에 시작)
- ✅ Jupyter, SSH, 웹 터미널 지원

---

## 🚀 Step 1: RunPod 계정 생성

### 1.1 회원가입
1. **RunPod 웹사이트 접속**: https://www.runpod.io
2. **Sign Up** 클릭
3. Google 계정 또는 이메일로 가입
4. 이메일 인증 완료

### 1.2 잔액 충전
1. 대시보드에서 **Add Funds** 클릭
2. 카드 또는 Bitcoin으로 충전
3. **최소 $10 정도 충전 권장** (테스트용)

> [!TIP]
> 처음 사용하시면 $5-10 정도만 충전해서 테스트해보세요. RTX 4090 기준 1시간에 $0.34이므로 충분히 테스트 가능합니다.

---

## 🖥️ Step 2: GPU Pod 생성

### 2.1 Pod 생성 시작
1. RunPod 대시보드에서 **Pods** 메뉴 클릭
2. **+ Deploy** 또는 **GPU Cloud** 선택

### 2.2 GPU 선택
**추천 GPU (OCR + 번역용):**
- **RTX 4090** (24GB VRAM) - 가성비 좋음, $0.34/hr
- **RTX 3090** (24GB VRAM) - 저렴함, $0.22/hr
- **A100** (40GB/80GB) - 고성능, $1.19/hr

**필터 설정:**
- VRAM: 최소 16GB (24GB 권장)
- Storage: 50GB 이상
- Location: 가까운 지역 선택 (지연 시간 감소)

### 2.3 템플릿 선택
**옵션 1: PyTorch 템플릿 (권장)**
- 검색창에 "PyTorch" 입력
- **RunPod PyTorch** 또는 **RunPod Pytorch 2.x** 선택
- 이미 CUDA, Python, PyTorch가 설치되어 있음

**옵션 2: Ubuntu + CUDA 템플릿**
- 검색창에 "Ubuntu" 입력
- **RunPod Ubuntu** 선택
- 직접 패키지 설치 필요

### 2.4 설정 구성
**Pod 이름:** `ocr-translation-service`

**Container Disk (임시 저장소):**
- 20-30GB (Pod 종료 시 삭제됨)

**Volume Disk (영구 저장소):**
- 50-100GB (Pod 종료해도 유지됨)
- 프로젝트 파일과 모델 저장용

**Pricing Type:**
- **On-Demand** (권장): 안정적, 중단 없음
- **Spot**: 저렴하지만 중단될 수 있음

**Expose Ports:**
- HTTP Ports: `8000` 입력 (FastAPI 서버용)
- 이렇게 하면 외부에서 웹 접속 가능

### 2.5 배포
1. 설정 확인
2. **Deploy On-Demand** 클릭
3. 몇 초 후 Pod 시작됨

---

## 🔌 Step 3: Pod에 접속

Pod가 시작되면 여러 방법으로 접속 가능합니다:

### 3.1 Web Terminal (가장 쉬움)
1. Pod 카드에서 **Connect** 버튼 클릭
2. **Start Web Terminal** 선택
3. 브라우저에서 바로 터미널 사용 가능

### 3.2 JupyterLab
1. **Connect** → **Connect to JupyterLab**
2. 노트북에서 코드 실행 가능

### 3.3 SSH (고급)
1. RunPod 설정에서 SSH 공개키 등록
2. Pod 정보에서 SSH 명령어 복사
3. 로컬 터미널에서 접속

---

## 📦 Step 4: 프로젝트 배포

### 4.1 프로젝트 파일 업로드

**방법 1: GitHub 사용 (권장)**
```bash
# Web Terminal에서 실행
cd /workspace
git clone https://github.com/your-username/ocr-translation-service.git
cd ocr-translation-service
```

**방법 2: 직접 파일 업로드**
1. 로컬에서 프로젝트를 zip으로 압축
2. JupyterLab의 Upload 기능 사용
3. 터미널에서 압축 해제:
```bash
cd /workspace
unzip ocr-translation-service.zip
cd ocr-translation-service
```

### 4.2 의존성 설치

```bash
# PaddlePaddle GPU 설치 (CUDA 11.8)
pip install paddlepaddle-gpu==3.0.0b1 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/

# PaddleOCR 설치
pip install -U "paddleocr[doc-parser]"

# 기타 의존성
pip install fastapi uvicorn python-multipart aiofiles pydantic
pip install transformers sentencepiece sacremoses torch
pip install reportlab Pillow pymupdf python-dotenv
```

> [!IMPORTANT]
> CUDA 버전 확인: `nvidia-smi` 명령어로 CUDA 버전 확인 후 맞는 PaddlePaddle 버전 설치

### 4.3 서버 실행

```bash
cd backend
python main.py
```

서버가 시작되면:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🌐 Step 5: 웹 접속

### 5.1 Public URL 확인
1. RunPod 대시보드에서 Pod 카드 확인
2. **TCP Port Mappings** 섹션에서 포트 8000 찾기
3. URL이 표시됨 (예: `https://xxxxx-8000.proxy.runpod.net`)

### 5.2 웹 브라우저에서 접속
1. 위 URL을 브라우저에 입력
2. OCR Translation Service 웹 페이지가 열림
3. PDF 업로드 및 번역 테스트!

---

## 💰 Step 6: 비용 관리

### 6.1 Pod 중지
**사용하지 않을 때는 반드시 중지하세요!**

1. Pod 카드에서 **Stop** 버튼 클릭
2. 중지 시 컴퓨팅 비용은 청구 안 됨
3. Volume Disk 비용만 청구 ($0.07/GB/월)

### 6.2 Pod 종료
**완전히 삭제:**
1. Pod 카드에서 **Terminate** 클릭
2. 모든 데이터 삭제됨 (Volume 포함)
3. 비용 청구 완전 중지

> [!WARNING]
> **중요:** Pod를 사용하지 않을 때는 반드시 Stop 또는 Terminate 하세요. 그렇지 않으면 계속 과금됩니다!

---

## 🛠️ 추가 팁

### 파일 다운로드
```bash
# 터미널에서 로컬로 파일 다운로드
# JupyterLab 사용 시 파일 우클릭 → Download
```

### 모델 캐싱
```bash
# 모델을 Volume에 저장하여 재사용
export HF_HOME=/workspace/models
export TRANSFORMERS_CACHE=/workspace/models
```

### 로그 확인
```bash
# 서버 로그 실시간 확인
tail -f /var/log/app.log
```

### GPU 사용률 모니터링
```bash
# 실시간 GPU 사용률 확인
watch -n 1 nvidia-smi
```

---

## 📋 체크리스트

### 시작 전
- [ ] RunPod 계정 생성
- [ ] 잔액 충전 ($10 이상)
- [ ] 프로젝트 GitHub에 업로드 (선택)

### Pod 설정
- [ ] GPU 선택 (RTX 4090 권장)
- [ ] PyTorch 템플릿 선택
- [ ] Volume Disk 50GB 이상 설정
- [ ] Port 8000 노출 설정
- [ ] Pod 배포

### 배포
- [ ] Web Terminal 접속
- [ ] 프로젝트 파일 업로드/클론
- [ ] PaddlePaddle GPU 설치
- [ ] PaddleOCR 설치
- [ ] 기타 의존성 설치
- [ ] 서버 실행

### 테스트
- [ ] Public URL 접속
- [ ] PDF 업로드 테스트
- [ ] 번역 결과 확인
- [ ] GPU 사용률 확인

### 종료
- [ ] Pod 중지 또는 종료
- [ ] 비용 확인

---

## ❓ 문제 해결

### GPU가 인식되지 않음
```bash
nvidia-smi  # GPU 확인
python -c "import torch; print(torch.cuda.is_available())"  # PyTorch CUDA 확인
```

### PaddlePaddle 설치 오류
- CUDA 버전 확인 후 맞는 버전 설치
- CUDA 11.8: `paddlepaddle-gpu==3.0.0b1`
- CUDA 12.6: `paddlepaddle-gpu==3.2.1`

### 포트 접속 안 됨
- Pod 설정에서 포트 8000이 노출되었는지 확인
- 방화벽 설정 확인
- 서버가 `0.0.0.0:8000`에서 실행 중인지 확인

### 메모리 부족
- 더 큰 GPU 선택 (24GB VRAM 이상)
- 배치 크기 줄이기 (`config.py`에서 조정)

---

## 💡 예상 비용

**RTX 4090 기준 ($0.34/시간):**
- 1시간 테스트: $0.34
- 하루 8시간 사용: $2.72
- 일주일 (주 5일, 하루 8시간): $13.60

**Volume Storage (50GB):**
- 월 $3.50 ($0.07/GB/월)

**총 예상 비용 (1주일 테스트):**
- 컴퓨팅: ~$14
- 스토리지: ~$1
- **합계: ~$15**

---

## 🎯 다음 단계

1. RunPod 계정 생성 및 충전
2. GPU Pod 배포
3. 프로젝트 업로드 및 설치
4. 서버 실행 및 테스트
5. 필요 시 코드 수정 및 재배포

궁금한 점이 있으면 언제든지 물어보세요! 🚀
