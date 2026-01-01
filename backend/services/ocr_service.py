import os
import json
import fitz
import numpy as np
from PIL import Image, ImageDraw
from paddleocr import PaddleOCR, FormulaRecognitionPipeline
from typing import List, Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import DPI, DEVICE_TEXT, DEVICE_FORMULA


class OCRService:
    """OCR service using PaddleOCR for text and formula recognition"""
    
    def __init__(self):
        """Initialize OCR models"""
        self.text_ocr = PaddleOCR(
            text_detection_model_name="PP-OCRv5_mobile_det",
            text_recognition_model_name="PP-OCRv5_mobile_rec",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            device=DEVICE_TEXT,
            text_recognition_batch_size=4
        )
        
        self.formula_pipeline = FormulaRecognitionPipeline(
            paddlex_config="FormulaRecognitionPipeline.yaml",
            device=DEVICE_FORMULA,
        )
    
    def process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Process PDF and extract structured content
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of page data with paragraphs containing text and formulas
        """
        # Convert PDF to images
        pages_data = []
        doc = fitz.open(pdf_path)
        
        scale = DPI / 72.0
        mat = fitz.Matrix(scale, scale)
        
        for page_idx in range(len(doc)):
            print(f"Processing page {page_idx + 1}/{len(doc)}")
            
            # Convert page to image
            pix = doc[page_idx].get_pixmap(matrix=mat)
            page_img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            np_page = np.array(page_img)
            
            # Process page
            page_content = self._process_page(page_img, np_page, page_idx + 1)
            pages_data.append(page_content)
        
        doc.close()
        return pages_data
    
    def _process_page(self, page_img: Image.Image, np_page: np.ndarray, page_num: int) -> Dict[str, Any]:
        """Process a single page"""
        # Layout detection and formula recognition
        out = self.formula_pipeline.predict(np_page)
        res = self._safe_result_to_dict(out[0])
        root = res.get("res", res)
        
        layout_boxes = root.get("layout_det_res", {}).get("boxes", [])
        formula_res_list = root.get("formula_res_list", [])
        
        # Mask formulas for text OCR
        masked = page_img.copy()
        d = ImageDraw.Draw(masked)
        for lb in layout_boxes:
            if lb.get("label") == "formula":
                x1, y1, x2, y2 = map(float, lb["coordinate"])
                d.rectangle([x1, y1, x2, y2], fill="white")
        
        # Text OCR
        text_out = self._safe_result_to_dict(self.text_ocr.predict(np.array(masked))[0])
        text_items = []
        for poly, txt in zip(
            text_out.get("dt_polys", []),
            text_out.get("rec_texts", [])
        ):
            if txt.strip():
                text_items.append({
                    "bbox": self._poly_to_xyxy(poly),
                    "text": txt.strip()
                })
        
        # Formula items
        formula_items = []
        for fr in formula_res_list:
            bbox = self._dt_polys_to_bbox(fr.get("dt_polys"))
            latex = fr.get("rec_formula", "").strip()
            if bbox and latex:
                formula_items.append({
                    "bbox": bbox,
                    "latex": latex
                })
        
        # Group into paragraphs by layout
        paragraphs = self._group_into_paragraphs(layout_boxes, text_items, formula_items)
        
        return {
            "page": page_num,
            "paragraphs": paragraphs,
            "layout_boxes": layout_boxes
        }
    
    def _group_into_paragraphs(self, layout_boxes: List, text_items: List, formula_items: List) -> List[Dict]:
        """Group text and formulas into paragraphs based on layout"""
        paragraphs = []
        
        for lb in layout_boxes:
            label = lb.get("label", "")
            if label not in ["text", "paragraph_title", "formula"]:
                continue
            
            lx1, ly1, lx2, ly2 = map(float, lb["coordinate"])
            elems = []
            
            # Find text elements in this layout box
            for t in text_items:
                cx, cy = self._center_of_box(t["bbox"])
                if self._point_in_box(cx, cy, (lx1, ly1, lx2, ly2)):
                    elems.append({"y": cy, "type": "text", "v": t["text"]})
            
            # Find formula elements in this layout box
            for f in formula_items:
                cx, cy = self._center_of_box(f["bbox"])
                if self._point_in_box(cx, cy, (lx1, ly1, lx2, ly2)):
                    elems.append({"y": cy, "type": "formula", "v": f["latex"]})
            
            if not elems:
                continue
            
            # Sort by vertical position
            elems.sort(key=lambda x: x["y"])
            
            # Build content
            content = []
            for e in elems:
                if e["type"] == "text":
                    content.append(e["v"])
                else:
                    content.append(f"$$\n{e['v']}\n$$")
            
            paragraphs.append({
                "type": label,
                "bbox": [lx1, ly1, lx2, ly2],
                "content": "\n\n".join(content),
                "num_elements": len(elems)
            })
        
        return paragraphs
    
    # Helper methods
    def _safe_result_to_dict(self, res):
        """Convert result to dictionary"""
        if isinstance(res, dict):
            return res
        for attr in ["json", "to_dict", "dict"]:
            if hasattr(res, attr):
                try:
                    v = getattr(res, attr)
                    return v() if callable(v) else v
                except:
                    pass
        return {}
    
    def _poly_to_xyxy(self, poly):
        """Convert polygon to bounding box"""
        xs = [float(p[0]) for p in poly]
        ys = [float(p[1]) for p in poly]
        return min(xs), min(ys), max(xs), max(ys)
    
    def _center_of_box(self, b):
        """Get center point of box"""
        x1, y1, x2, y2 = b
        return (x1 + x2) / 2, (y1 + y2) / 2
    
    def _point_in_box(self, px, py, box):
        """Check if point is in box"""
        x1, y1, x2, y2 = box
        return x1 <= px <= x2 and y1 <= py <= y2
    
    def _dt_polys_to_bbox(self, dt_polys):
        """Convert detection polygons to bbox"""
        if dt_polys is None:
            return None
        
        # bbox format
        if (
            isinstance(dt_polys, (list, tuple))
            and len(dt_polys) == 4
            and all(isinstance(v, (int, float, np.floating)) for v in dt_polys)
        ):
            return tuple(float(v) for v in dt_polys)
        
        # polygon format
        if (
            isinstance(dt_polys, (list, tuple))
            and len(dt_polys) >= 4
            and isinstance(dt_polys[0], (list, tuple))
        ):
            xs = [float(p[0]) for p in dt_polys]
            ys = [float(p[1]) for p in dt_polys]
            return min(xs), min(ys), max(xs), max(ys)
        
        return None
