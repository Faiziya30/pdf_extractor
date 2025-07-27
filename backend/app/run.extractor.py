import os
import json
import logging
from pathlib import Path
from PDFOutlineExtractor import PDFOutlineExtractor  # Ensure this file exists

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")

    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)

    extractor = PDFOutlineExtractor()

    # Process all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning("No PDF files found in /app/input")
        return

    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing {pdf_file.name}")
            result = extractor.process_pdf(str(pdf_file))

            # Output file
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved to {output_file.name}")
        except Exception as e:
            logger.error(f"Failed to process {pdf_file.name}: {str(e)}")

if __name__ == "__main__":
    main()
