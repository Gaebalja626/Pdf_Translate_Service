#!/bin/bash
# RunPod 배포 스크립트
# 이 스크립트를 RunPod Web Terminal에서 실행하세요

set -e  # 에러 발생 시 중단

echo "=========================================="
echo "OCR Translation Service - RunPod 배포"
echo "=========================================="

# 1. 작업 디렉토리로 이동
cd /workspace
echo "✓ 작업 디렉토리: /workspace"

# 2. 프로젝트 디렉토리 생성
mkdir -p ocr-translation-service
cd ocr-translation-service
echo "✓ 프로젝트 디렉토리 생성"

# 3. CUDA 버전 확인
echo ""
echo "=========================================="
echo "GPU 정보 확인"
echo "=========================================="
nvidia-smi
echo ""

# 4. Python 버전 확인
echo "Python 버전: $(python --version)"
echo ""

# 5. PaddlePaddle GPU 설치
echo "=========================================="
echo "PaddlePaddle GPU 설치 중..."
echo "=========================================="
pip install paddlepaddle-gpu==3.0.0b1 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/ --no-cache-dir

# 6. PaddleOCR 설치
echo ""
echo "=========================================="
echo "PaddleOCR 설치 중..."
echo "=========================================="
pip install -U "paddleocr[doc-parser]" --no-cache-dir

# 7. 기타 의존성 설치
echo ""
echo "=========================================="
echo "기타 의존성 설치 중..."
echo "=========================================="
pip install fastapi uvicorn[standard] python-multipart aiofiles pydantic --no-cache-dir
pip install transformers sentencepiece sacremoses torch torchvision torchaudio --no-cache-dir
pip install reportlab Pillow pymupdf python-dotenv --no-cache-dir

# 8. 설치 확인
echo ""
echo "=========================================="
echo "설치 확인"
echo "=========================================="
python -c "import paddle; print('PaddlePaddle 버전:', paddle.__version__)"
python -c "import torch; print('PyTorch 버전:', torch.__version__)"
python -c "import torch; print('CUDA 사용 가능:', torch.cuda.is_available())"

echo ""
echo "=========================================="
echo "설치 완료!"
echo "=========================================="
echo ""
echo "다음 단계:"
echo "1. 프로젝트 파일을 /workspace/ocr-translation-service에 업로드하세요"
echo "2. cd /workspace/ocr-translation-service/backend"
echo "3. python main.py"
echo ""
