from langchain.tools import Tool
from .analytics_tool import analyze_metrics
from .seo_tool import seo_analysis
from .social_tool import social_media_optimizer
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import re
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_metrics_from_image(image_file):
    """
    Extract engagement metrics from social media screenshot.
    Enhanced to handle dark backgrounds (white text on black).
    """
    from PIL import Image, ImageOps, ImageEnhance, ImageFilter
    import pytesseract, re

    try:
        img = Image.open(image_file)

        # 1️⃣ Convert to grayscale
        img = img.convert("L")

        # 2️⃣ Invert colors if background is dark
        # (detect by checking average pixel brightness)
        if img.getextrema()[1] < 128:  # if overall dark
            img = ImageOps.invert(img)

        # 3️⃣ Enhance contrast & sharpen
        img = ImageEnhance.Contrast(img).enhance(2.5)
        img = img.filter(ImageFilter.SHARPEN)

        # 4️⃣ OCR to extract text
        text = pytesseract.image_to_string(img, config="--psm 6").lower()
        print("🔍 OCR Extracted Text:\n", text)

        metrics = {}

        # Helper to parse numbers like 23,158 or 2.3K
        def parse_number(segment):
            match = re.search(r"([\d,.]+)\s*(k|m)?", segment)
            if not match:
                return 0
            num = float(match.group(1).replace(",", ""))
            unit = match.group(2)
            if unit == "k":
                num *= 1_000
            elif unit == "m":
                num *= 1_000_000
            return int(num)

        # 5️⃣ Extract metrics by keyword
        for line in text.splitlines():
            if "like" in line:
                metrics["likes"] = parse_number(line)
            elif "save" in line:
                metrics["saves"] = parse_number(line)
            elif "comment" in line:
                metrics["comments"] = parse_number(line)
            elif "share" in line:
                metrics["shares"] = parse_number(line)
            elif "view" in line:
                metrics["views"] = parse_number(line)

        # Fill missing ones
        for key in ["likes", "saves", "comments", "shares", "views"]:
            metrics.setdefault(key, 0)

        return metrics

    except Exception as e:
        print("❌ OCR Error:", e)
        return {"likes": 0, "saves": 0, "comments": 0, "shares": 0, "views": 0}


def content_growth_advanced(post_url=None, screenshot=None, metrics=None, caption=""):
    """
    Offline content growth analysis using OCR + text-based reasoning.
    """
    final_metrics = metrics or {}

    # 1️⃣ Extract metrics from screenshot if provided
    if screenshot:
        print("📸 Extracting metrics from screenshot...")
        img_metrics = extract_metrics_from_image(screenshot)
        final_metrics.update(img_metrics)

    # 2️⃣ Combine with any manual metrics
    if not final_metrics:
        final_metrics = {"likes": 0, "comments": 0, "shares": 0, "views": 0}

    # 3️⃣ Analyze with existing tools
    result = analyze_metrics(final_metrics) or {}
    advice = result.get("advice", "")

    seo_result = seo_analysis(caption) if caption else ""
    social_result = social_media_optimizer(caption) if caption else ""

    return {
        "metrics": final_metrics,
        "advice": advice or "No advice generated.",
        "seo": seo_result or "No SEO analysis available.",
        "social": social_result or "No social suggestions available."
    }


# ✅ Wrap as LangChain Tool
content_growth_tool = Tool(
    name="ContentGrowthPro",
    func=content_growth_advanced,
    description="Offline content growth analysis using screenshots + caption."
)

print("✅ Content Growth Tool Ready!")
