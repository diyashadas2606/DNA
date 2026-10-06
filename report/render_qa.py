from pathlib import Path
from pypdf import PdfReader
import pypdfium2 as pdfium
root=Path('report');pdf=pdfium.PdfDocument(str(root/'DNA_HCV_Report.pdf'));qa=root/'qa';qa.mkdir(exist_ok=True)
for i,page in enumerate(pdf): page.render(scale=1.5).to_pil().save(qa/f'page-{i+1}.png')
reader=PdfReader(root/'DNA_HCV_Report.pdf')
print('Pages:',len(reader.pages))
for i,page in enumerate(reader.pages): print(i+1, page.extract_text().splitlines()[0],len(page.extract_text()))
