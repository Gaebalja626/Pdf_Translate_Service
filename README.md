# OCR Translation Service

AI-powered PDF translation service: English → Korean with OCR and layout preservation.

## 🌟 Features

- **High-precision OCR**: PaddleOCR v5 for text and formula recognition
- **Natural Translation**: MarianMT model for English → Korean translation
- **Layout Preservation**: Maintains original document structure and formulas
- **Modern Web UI**: Drag-and-drop upload with real-time progress tracking

## 🚀 Quick Start (RunPod)

### 1. Create RunPod Account
- Sign up at https://www.runpod.io
- Add $10+ credits

### 2. Deploy GPU Pod
- GPU: RTX 4090 or RTX 3090
- Template: **RunPod PyTorch**
- Volume: 50GB
- **Expose HTTP Ports**: `8000` ⚠️ Important!

### 3. Clone and Setup
```bash
cd /workspace
git clone https://github.com/YOUR_USERNAME/ocr-translation-service.git
cd ocr-translation-service
chmod +x setup_runpod.sh
./setup_runpod.sh
```

### 4. Run Server
```bash
cd backend
python main.py
```

### 5. Access Web Interface
- Find your Pod's public URL in RunPod dashboard
- Look for port 8000 mapping (e.g., `https://xxxxx-8000.proxy.runpod.net`)
- Open in browser and upload PDF!

## 📁 Project Structure

```
ocr-translation-service/
├── backend/
│   ├── main.py                    # FastAPI server
│   ├── config.py                  # Configuration
│   └── services/
│       ├── ocr_service.py         # PaddleOCR integration
│       ├── translation_service.py # MarianMT translation
│       └── pdf_generator.py       # PDF generation
├── frontend/
│   ├── index.html                 # Web UI
│   ├── style.css                  # Styling
│   └── app.js                     # Frontend logic
├── setup_runpod.sh                # Automated setup script
└── requirements.txt               # Python dependencies
```

## 🛠️ Technology Stack

- **Backend**: FastAPI, PaddleOCR, MarianMT
- **Frontend**: HTML/CSS/JavaScript (Glassmorphism design)
- **OCR**: PaddlePaddle v5 + Formula Recognition
- **Translation**: Helsinki-NLP/opus-mt-en-ko
- **PDF**: PyMuPDF, ReportLab

## 💰 Cost Estimate (RunPod)

- **RTX 4090**: $0.34/hour
- **1 week testing** (5 days × 8 hours): ~$15

## 📖 Documentation

- [`RUNPOD_GUIDE.md`](RUNPOD_GUIDE.md) - Detailed RunPod setup guide
- [`QUICKSTART_RUNPOD.md`](QUICKSTART_RUNPOD.md) - Quick start guide

## 🐛 Troubleshooting

### GPU not detected
```bash
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

### Port 8000 not accessible
- Ensure HTTP Ports includes `8000` in Pod settings
- Check server is running on `0.0.0.0:8000`

### Out of memory
- Edit `backend/config.py`: reduce `TRANSLATION_BATCH_SIZE` from 8 to 4

## 📄 License

MIT License

## 🙏 Credits

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [MarianMT](https://huggingface.co/Helsinki-NLP)
- [FastAPI](https://fastapi.tiangolo.com/)
