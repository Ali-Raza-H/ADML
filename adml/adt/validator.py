import os
from dataclasses import dataclass
from adml.adt.core import DesignDocument
from adml.utils.colours import is_readable

@dataclass
class ValidationResult:
    errors: list[str]
    warnings: list[str]

def validate(doc: DesignDocument) -> ValidationResult:
    errors = []
    warnings = []
    
    if doc.width <= 0 or doc.height <= 0:
        errors.append("Canvas dimensions must be positive and non-zero")
        
    slide_ids = set()
    for slide in doc.slides:
        if not slide.id:
            errors.append("A slide has an empty ID")
        if slide.id in slide_ids:
            errors.append(f"Duplicate slide ID: {slide.id}")
        slide_ids.add(slide.id)
        
        if not slide.elements:
            warnings.append(f"Slide '{slide.id}' has no elements")
            
        for el in slide.elements:
            if hasattr(el, 'src') and getattr(el, 'src'):
                if not os.path.exists(el.src):
                    warnings.append(f"Image source '{el.src}' not found on disk")
                    
            if hasattr(el, 'font'):
                if el.font.size < 6.0 or el.font.size > 400.0:
                    errors.append(f"Font size {el.font.size}pt is outside valid range (6-400)")
                    
                # Check contrast
                if hasattr(slide, 'background') and slide.background.colour and el.font.colour:
                    large = el.font.size >= 18.0 or (el.font.size >= 14.0 and el.font.weight == 'bold')
                    if not is_readable(el.font.colour, slide.background.colour, large_text=large):
                        warnings.append(f"Low contrast text '{getattr(el, 'content', '')}' on slide '{slide.id}'")
                        
    return ValidationResult(errors, warnings)
