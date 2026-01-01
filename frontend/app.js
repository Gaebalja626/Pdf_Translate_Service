// API base URL
const API_BASE = window.location.origin;

// DOM elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const selectBtn = document.getElementById('selectBtn');
const changeFileBtn = document.getElementById('changeFileBtn');
const newFileBtn = document.getElementById('newFileBtn');
const retryBtn = document.getElementById('retryBtn');
const downloadBtn = document.getElementById('downloadBtn');

const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');

const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const progressPercent = document.getElementById('progressPercent');
const progressMessage = document.getElementById('progressMessage');

const resultSection = document.getElementById('resultSection');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');

// State
let currentFile = null;
let currentTaskId = null;
let pollInterval = null;

// Event listeners
selectBtn.addEventListener('click', () => fileInput.click());
changeFileBtn.addEventListener('click', () => fileInput.click());
newFileBtn.addEventListener('click', resetUpload);
retryBtn.addEventListener('click', resetUpload);
downloadBtn.addEventListener('click', downloadResult);

fileInput.addEventListener('change', handleFileSelect);

// Drag and drop
uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('drag-over');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

uploadZone.addEventListener('click', (e) => {
    if (e.target === uploadZone || e.target.closest('.upload-icon') || e.target.tagName === 'H3' || e.target.tagName === 'P') {
        fileInput.click();
    }
});

// Handle file selection
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    // Validate file type
    if (!file.name.endsWith('.pdf')) {
        showError('PDF 파일만 업로드 가능합니다.');
        return;
    }
    
    // Validate file size (50MB)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('파일 크기는 50MB를 초과할 수 없습니다.');
        return;
    }
    
    currentFile = file;
    
    // Show file info
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    uploadZone.style.display = 'none';
    fileInfo.style.display = 'flex';
    
    // Auto-start upload
    setTimeout(() => uploadFile(), 500);
}

// Upload file
async function uploadFile() {
    if (!currentFile) return;
    
    // Show progress section
    fileInfo.style.display = 'none';
    progressSection.style.display = 'block';
    
    updateProgress(0, '업로드 중...', '파일을 서버에 업로드하는 중입니다...');
    
    try {
        const formData = new FormData();
        formData.append('file', currentFile);
        
        const response = await fetch(`${API_BASE}/api/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '업로드 실패');
        }
        
        const data = await response.json();
        currentTaskId = data.task_id;
        
        // Start polling for status
        startPolling();
        
    } catch (error) {
        console.error('Upload error:', error);
        showError(error.message || '파일 업로드 중 오류가 발생했습니다.');
    }
}

// Poll for status
function startPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
    
    pollInterval = setInterval(checkStatus, 2000);
    checkStatus(); // Check immediately
}

async function checkStatus() {
    if (!currentTaskId) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/status/${currentTaskId}`);
        
        if (!response.ok) {
            throw new Error('상태 확인 실패');
        }
        
        const data = await response.json();
        
        // Update progress
        const progress = data.progress || 0;
        const status = data.status;
        const message = data.message || '';
        
        if (status === 'processing' || status === 'uploaded') {
            let statusText = '처리 중...';
            if (progress < 40) {
                statusText = 'OCR 처리 중...';
            } else if (progress < 70) {
                statusText = '번역 중...';
            } else {
                statusText = 'PDF 생성 중...';
            }
            
            updateProgress(progress, statusText, message);
        } else if (status === 'completed') {
            clearInterval(pollInterval);
            updateProgress(100, '완료!', '번역이 완료되었습니다.');
            setTimeout(() => showResult(), 500);
        } else if (status === 'failed') {
            clearInterval(pollInterval);
            showError(data.error || '처리 중 오류가 발생했습니다.');
        }
        
    } catch (error) {
        console.error('Status check error:', error);
        clearInterval(pollInterval);
        showError('상태 확인 중 오류가 발생했습니다.');
    }
}

// Update progress
function updateProgress(percent, text, message) {
    progressFill.style.width = `${percent}%`;
    progressPercent.textContent = `${Math.round(percent)}%`;
    progressText.textContent = text;
    progressMessage.textContent = message;
}

// Show result
function showResult() {
    progressSection.style.display = 'none';
    resultSection.style.display = 'block';
}

// Show error
function showError(message) {
    uploadZone.style.display = 'none';
    fileInfo.style.display = 'none';
    progressSection.style.display = 'none';
    resultSection.style.display = 'none';
    
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
}

// Download result
async function downloadResult() {
    if (!currentTaskId) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/download/${currentTaskId}`);
        
        if (!response.ok) {
            throw new Error('다운로드 실패');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `translated_${currentFile.name}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
    } catch (error) {
        console.error('Download error:', error);
        alert('다운로드 중 오류가 발생했습니다.');
    }
}

// Reset upload
function resetUpload() {
    currentFile = null;
    currentTaskId = null;
    
    if (pollInterval) {
        clearInterval(pollInterval);
    }
    
    fileInput.value = '';
    
    uploadZone.style.display = 'block';
    fileInfo.style.display = 'none';
    progressSection.style.display = 'none';
    resultSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    progressFill.style.width = '0%';
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
