from pyzbar import pyzbar
from PIL import Image
import io
from pathlib import Path
import contextlib
import os

AAMVA_FIELDS = {
    "DCS": {"name": "Last Name", "category": "personal"},
    "DAC": {"name": "First Name", "category": "personal"},
    "DAD": {"name": "Middle Name", "category": "personal"},
    "DBB": {"name": "Date of Birth", "category": "personal"},
    "DBC": {"name": "Sex", "category": "personal"},
    "DAY": {"name": "Eye Color", "category": "physical"},
    "DAU": {"name": "Height", "category": "physical"},
    "DAW": {"name": "Weight", "category": "physical"},
    "DAG": {"name": "Street Address", "category": "address"},
    "DAI": {"name": "City", "category": "address"},
    "DAJ": {"name": "State", "category": "address"},
    "DAK": {"name": "Postal Code", "category": "address"},
    "DAQ": {"name": "ID Number", "category": "document"},
    "DBA": {"name": "Expiration Date", "category": "document"},
    "DBD": {"name": "Issue Date", "category": "document"},
    "DCG": {"name": "Country", "category": "document"},
    "DCA": {"name": "Vehicle Class", "category": "document"},
    "DCB": {"name": "Restriction Codes", "category": "document"},
    "DCD": {"name": "Endorsement Codes", "category": "document"},
    "DCL": {"name": "Race/Ethnicity", "category": "physical"},
    "DCM": {"name": "Vehicle Classification", "category": "document"},
    "DDB": {"name": "Card Revision Date", "category": "document"},
}

class BarcodeDecoder:
    """Decode 1D and 2D barcodes using pyzbar"""
    
    @staticmethod
    def _preprocess_image(cv_image):
        """Apply advanced preprocessing for better barcode detection"""
        import cv2
        import numpy as np  # noqa: F401 - imported for OpenCV operations
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to reduce noise while preserving edges
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Apply histogram equalization
        gray = cv2.equalizeHist(gray)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Apply morphological operations to enhance barcode patterns
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        
        return gray
    
    @staticmethod
    def decode_barcode(image_path):
        """Decode barcode from image file with multi-scale detection"""
        try:
            # Lazy import cv2 and numpy here so that the rest of the app can run
            # even if OpenCV/NumPy binaries are not correctly installed. If the
            # import fails, report a clear error instead of crashing the server.
            try:
                import cv2  # type: ignore
                import numpy as np  # type: ignore  # noqa: F401
            except Exception as import_err:
                return {"error": f"OpenCV/NumPy import error: {import_err}"}

            image = Image.open(image_path)
            # Convert RGBA to RGB if needed
            if image.mode in ('RGBA', 'LA', 'P'):
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = rgb_image
            
            # Convert PIL to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            @contextlib.contextmanager
            def suppress_c_stderr():
                try:
                    devnull_fd = os.open(os.devnull, os.O_RDWR)
                    orig_stderr_fd = os.dup(2)
                    os.dup2(devnull_fd, 2)
                    try:
                        yield
                    finally:
                        os.dup2(orig_stderr_fd, 2)
                        os.close(orig_stderr_fd)
                        os.close(devnull_fd)
                except Exception:
                    yield
            
            decoded_objects = []
            
            # Try original image
            with suppress_c_stderr():
                decoded_objects.extend(pyzbar.decode(cv_image))
            
            if not decoded_objects:
                # Try preprocessed image
                gray = BarcodeDecoder._preprocess_image(cv_image)
                with suppress_c_stderr():
                    decoded_objects.extend(pyzbar.decode(gray))
            
            if not decoded_objects:
                # Try upscaled image
                upscaled = cv2.resize(cv_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                gray = BarcodeDecoder._preprocess_image(upscaled)
                with suppress_c_stderr():
                    decoded_objects.extend(pyzbar.decode(gray))
            
            if not decoded_objects:
                # Try rotated images
                for angle in [90, 180, 270]:
                    h, w = cv_image.shape[:2]
                    center = (w // 2, h // 2)
                    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                    rotated = cv2.warpAffine(cv_image, matrix, (w, h))
                    gray = BarcodeDecoder._preprocess_image(rotated)
                    with suppress_c_stderr():
                        decoded_objects.extend(pyzbar.decode(gray))
                    if decoded_objects:
                        break
            
            if not decoded_objects:
                return {"error": "No barcode detected in image"}
            
            results = []
            for obj in decoded_objects:
                results.append({
                    "type": obj.type,
                    "data": obj.data.decode('utf-8'),
                    "quality": "detected"
                })
            
            return {"success": True, "barcodes": results}
        
        except Exception as e:
            return {"error": f"Barcode decode error: {str(e)}"}

class PDF417Decoder:
    """Decode PDF417 codes with AAMVA format parsing"""
    
    @staticmethod
    def format_date_readable(date_str):
        """Convert MMDDYYYY to Month Day, Year format (e.g., October 17, 2002)"""
        if not date_str or len(date_str) < 8:
            return date_str
        try:
            month_num = int(date_str[0:2])
            day = int(date_str[2:4])
            year = date_str[4:8]
            
            months = ["", "January", "February", "March", "April", "May", "June",
                     "July", "August", "September", "October", "November", "December"]
            
            month_name = months[month_num] if 1 <= month_num <= 12 else date_str[0:2]
            return f"{month_name} {day}, {year}"
        except:
            return date_str
    
    @staticmethod
    def format_sex(sex_code):
        """Convert sex code to Male/Female"""
        if not sex_code:
            return sex_code
        try:
            code = sex_code.strip()
            if code == "1":
                return "Male"
            elif code == "2":
                return "Female"
            else:
                return code
        except:
            return sex_code
    
    @staticmethod
    def format_date(date_str):
        """Convert MMDDYYYY to YYYY-MM-DD"""
        if not date_str or len(date_str) < 8:
            return date_str
        try:
            month = date_str[0:2]
            day = date_str[2:4]
            year = date_str[4:8]
            return f"{year}-{month}-{day}"
        except:
            return date_str
    
    @staticmethod
    def format_height(height_str):
        """Convert height format (e.g., '067 in' to '5\'7\"')"""
        if not height_str:
            return height_str
        try:
            # Remove 'in' and spaces
            height_str = height_str.replace('in', '').strip()
            # Convert to integer
            inches = int(height_str)
            feet = inches // 12
            remaining_inches = inches % 12
            return f"{feet}'{remaining_inches}\""
        except:
            return height_str
    
    @staticmethod
    def extract_user_data(parsed_data):
        """Extract and format user data in the required XML structure"""
        try:
            raw_fields = parsed_data.get("raw_fields", {})
            
            user_data = {
                "last": raw_fields.get("DCS", ""),
                "first": raw_fields.get("DAC", ""),
                "dob": PDF417Decoder.format_date_readable(raw_fields.get("DBB", "")),
                "eyes": raw_fields.get("DAY", ""),
                "sex": PDF417Decoder.format_sex(raw_fields.get("DBC", "")),
                "height": PDF417Decoder.format_height(raw_fields.get("DAU", "")),
                "weight": raw_fields.get("DAW", ""),
                "street": raw_fields.get("DAG", ""),
                "city": raw_fields.get("DAI", ""),
                "state": raw_fields.get("DAJ", ""),
                "postal": raw_fields.get("DAK", ""),
                "country": raw_fields.get("DCG", ""),
                "id": raw_fields.get("DAQ", ""),
                "issued": PDF417Decoder.format_date_readable(raw_fields.get("DBD", "")),
                "expires": PDF417Decoder.format_date_readable(raw_fields.get("DBA", "")),
            }
            
            return user_data
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def parse_aamva_data(raw_data):
        """Parse AAMVA format data from PDF417"""
        try:
            fields = {}
            i = 0
            
            while i < len(raw_data):
                if i + 2 < len(raw_data):
                    code = raw_data[i:i+3]
                    if code in AAMVA_FIELDS:
                        i += 3
                        # Find the next valid AAMVA code
                        value_start = i
                        while i < len(raw_data) - 2:
                            potential_code = raw_data[i:i+3]
                            if potential_code in AAMVA_FIELDS:
                                break
                            i += 1
                        
                        # Get value up to next valid code
                        value = raw_data[value_start:i].strip()
                        
                        # This handles cases where invalid codes are concatenated
                        if value:
                            # Split by common delimiters to get just the main value
                            value = value.split()[0]  # Take only first word/token
                        
                        fields[code] = value
                    else:
                        i += 1
                else:
                    i += 1
            
            user_data = PDF417Decoder.extract_user_data({"raw_fields": fields})
            
            # Structure the parsed data
            structured_data = {
                "personal": {},
                "physical": {},
                "address": {},
                "document": {},
                "raw_fields": fields,
                "user": user_data  # Add formatted user data
            }
            
            for code, value in fields.items():
                if code == "DDD":
                    continue
                if code in AAMVA_FIELDS:
                    field_info = AAMVA_FIELDS[code]
                    category = field_info["category"]
                    name = field_info["name"]
                    structured_data[category][name] = value
            
            return structured_data
        except Exception as e:
            return {"error": f"AAMVA parsing error: {str(e)}"}
    
    @staticmethod
    def decode_pdf417(image_path):
        """Decode PDF417 from image file"""
        try:
            # Lazy import pdf417decoder and its cv2 dependency so that the
            # server can start even if those binaries are not correctly
            # installed. If imports fail, report a clear error.
            try:
                from pdf417decoder.Decoder import PDF417Decoder as PDF417DecoderLib  # type: ignore
                import cv2  # type: ignore  # noqa: F401
            except Exception as import_err:
                return {"error": f"PDF417/OpenCV import error: {import_err}"}

            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            try:
                decoder = PDF417DecoderLib(image)
                cnt = decoder.decode()
                
                if cnt <= 0:
                    return {"error": "No PDF417 code detected in image"}
                
                results = []
                for i in range(cnt):
                    try:
                        # Try to get barcode data as string
                        text = decoder.barcode_data_index_to_string(i)
                    except Exception:
                        # Fallback: try to access barcodes_data directly
                        try:
                            raw = decoder.barcodes_data[i]
                            text = raw.decode('utf-8', errors='replace')
                        except Exception:
                            text = ""
                    
                    if text.startswith("@") or "DL" in text:
                        parsed_data = PDF417Decoder.parse_aamva_data(text)
                        results.append({
                            "data": text,
                            "type": "PDF417",
                            "format": "AAMVA",
                            "parsed": parsed_data
                        })
                    else:
                        results.append({
                            "data": text,
                            "type": "PDF417",
                            "format": "raw"
                        })
                
                return {"success": True, "pdf417_data": results}
            
            except Exception as e:
                return {"error": f"PDF417 decode error: {str(e)}"}
        
        except Exception as e:
            return {"error": f"PDF417 processing error: {str(e)}"}

class ImageProcessor:
    """Process card and checkbook images"""
    
    @staticmethod
    def process_image(image_path, image_type="card"):
        """Process and validate image"""
        try:
            image = Image.open(image_path)
            
            # Get image info
            info = {
                "type": image_type,
                "format": image.format,
                "size": image.size,
                "mode": image.mode,
                "path": str(image_path)
            }
            
            return {"success": True, "image_info": info}
        
        except Exception as e:
            return {"error": str(e)}
