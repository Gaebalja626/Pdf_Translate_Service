import re
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from typing import List, Union
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import TRANSLATION_MODEL, TRANSLATION_DEVICE, TRANSLATION_BATCH_SIZE


class TranslationService:
    """Translation service using NLLB for English to Korean translation"""
    
    def __init__(self):
        """Initialize NLLB model"""
        print(f"Loading translation model: {TRANSLATION_MODEL}")
        self.tokenizer = AutoTokenizer.from_pretrained(TRANSLATION_MODEL)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(TRANSLATION_MODEL)
        
        # Move to GPU if available
        if torch.cuda.is_available() and TRANSLATION_DEVICE == "cuda":
            self.model = self.model.to(TRANSLATION_DEVICE)
            print(f"Translation model loaded on {TRANSLATION_DEVICE}")
        else:
            print("Translation model loaded on CPU")
        
        self.model.eval()
    
    def translate_content(self, content: str) -> str:
        """
        Translate content while preserving LaTeX formulas
        
        Args:
            content: Text content with potential LaTeX formulas ($$...$$)
            
        Returns:
            Translated content with formulas preserved
        """
        # Split content by formula blocks
        parts = re.split(r'(\$\$.*?\$\$)', content, flags=re.DOTALL)
        
        translated_parts = []
        for part in parts:
            # Check if this is a formula block
            if part.startswith('$$') and part.endswith('$$'):
                # Preserve formula as-is
                translated_parts.append(part)
            elif part.strip():
                # Translate text
                translated = self._translate_text(part)
                translated_parts.append(translated)
            else:
                # Preserve whitespace
                translated_parts.append(part)
        
        return ''.join(translated_parts)
    
    def _translate_text(self, text: str) -> str:
        """Translate plain text (no formulas)"""
        if not text.strip():
            return text
        
        # Split into sentences for better translation
        sentences = self._split_sentences(text)
        
        if not sentences:
            return text
        
        # Translate in batches
        translated_sentences = []
        for i in range(0, len(sentences), TRANSLATION_BATCH_SIZE):
            batch = sentences[i:i + TRANSLATION_BATCH_SIZE]
            translated_batch = self._translate_batch(batch)
            translated_sentences.extend(translated_batch)
        
        return ' '.join(translated_sentences)
    
    def _translate_batch(self, texts: List[str]) -> List[str]:
        """Translate a batch of texts"""
        if not texts:
            return []
        
        # Tokenize with source language
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        # Move to device
        if torch.cuda.is_available() and TRANSLATION_DEVICE == "cuda":
            inputs = {k: v.to(TRANSLATION_DEVICE) for k, v in inputs.items()}
        
        # Generate translation with target language code for Korean
        with torch.no_grad():
            translated = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.lang_code_to_id.get("kor_Hang", self.tokenizer.lang_code_to_id["kor_Hang"]),
                max_length=512
            )
        
        # Decode
        translated_texts = self.tokenizer.batch_decode(translated, skip_special_tokens=True)
        
        return translated_texts
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (can be improved with nltk)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def translate_paragraphs(self, paragraphs: List[dict]) -> List[dict]:
        """
        Translate paragraphs from OCR output
        
        Args:
            paragraphs: List of paragraph dictionaries with 'content' field
            
        Returns:
            List of paragraphs with translated content
        """
        translated_paragraphs = []
        
        for para in paragraphs:
            translated_para = para.copy()
            original_content = para.get("content", "")
            
            if original_content.strip():
                print(f"Translating paragraph ({len(original_content)} chars)...")
                translated_content = self.translate_content(original_content)
                translated_para["content"] = translated_content
                translated_para["original_content"] = original_content
            
            translated_paragraphs.append(translated_para)
        
        return translated_paragraphs
