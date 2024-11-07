from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.colors import Color
import re
from typing import List
import aiohttp
import asyncio
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os


def create_pdf(content, output_filename, urls):
    def process_content(raw_content):

        content = re.sub(r'\r\n', '\n', raw_content)  # Normalize line endings
        content = re.sub(
            r'(-\s*Confidence Level\s*:)\s*(\d+\.?\d*)',
            r'\1 \2',
            content
        )
        content = re.sub(r'(?m)^(\d+\.)', r'\n\1', content)
        content = re.sub(
            r'(\*\*\[.*?\]\*\*)', 
            r'\n\1\n', 
            content
        )
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(
            r'(^[•-].*?)(\n{2,})',
            r'\1\n',
            content,
            flags=re.MULTILINE
        )
        
        content = content.strip()
        
        return content
    
    content = process_content(content)

    output_dir = 'output_reports'
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, output_filename)



    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Define styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        fontName='Helvetica-Bold',
        spaceAfter=30,
        spaceBefore=20,
        textColor=Color(0, 0, 0, 1),
        alignment=1,  # 1 is center alignment (0=left, 1=center, 2=right)
        leading=24    # Add some extra line height for better spacing
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        fontName='Helvetica-Bold',
        spaceAfter=12,
        spaceBefore=20,
        textColor=Color(0, 0, 0, 0.8)
    )
    
    bold_section_style = ParagraphStyle(
        'BoldSection',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        spaceAfter=12,
        spaceBefore=12,
        textColor=Color(0, 0, 0, 0.8),
        leftIndent=20
    )
    
    bullet_style = ParagraphStyle(
        'BulletPoint',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        spaceAfter=8,
        leftIndent=40,
        bulletIndent=20
    )
    
    sub_bullet_style = ParagraphStyle(
        'SubBulletPoint',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        spaceAfter=8,
        leftIndent=60,
        bulletIndent=40
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        spaceAfter=12,
        leading=16,
        leftIndent=20
    )

    # Build content
    story = []
    story.append(Paragraph("Website Audit Analysis Report", title_style))
    story.append(Spacer(1, 20))

    lines = content.split('\n')
    in_bullet_list = False

    for line in lines:
        line = line.strip()
        if not line:
            if in_bullet_list:
                story.append(Spacer(1, 10))
                in_bullet_list = False
            continue

        # Main sections (1., 2., etc.)
        if re.match(r'^\d+\.', line):
            story.append(Paragraph(line, section_style))
            continue

        # Bold subsections [Title]
        if line.startswith('**[') and line.endswith(']**'):
            section_title = line.replace('**[', '[').replace(']**', ']')
            story.append(Paragraph(section_title, bold_section_style))
            continue

        # Bullet points
        if line.startswith('•'):
            in_bullet_list = True
            bullet_text = line[1:].strip()
            story.append(Paragraph(f"• {bullet_text}", bullet_style))
            continue

        # Sub-bullet points
        if line.startswith('-'):
            bullet_text = line[1:].strip()
            story.append(Paragraph(f"- {bullet_text}", sub_bullet_style))
            continue

        # Normal text
        story.append(Paragraph(line, normal_style))

    # Add references if URLs provided
    if urls:
        story.append(Spacer(1, 20))
        story.append(Paragraph("3. References:", section_style))
        for url in urls:
            story.append(Paragraph(f"• {url}", bullet_style))

    doc.build(story)



def load_urls(urls:List[str]):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    successful_docs =  asyncio.run(lazy_load(user_agent, urls)) # type: ignore
    return successful_docs


def _splited_docs(docs:List[Document]):
        html2text = Html2TextTransformer(ignore_links=False, ignore_images=False)
        docs_transformed = html2text.transform_documents(docs)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        return text_splitter.split_documents(docs_transformed)

async def lazy_load(user_agent, urls):
    default_header_template = {
        'User-Agent': user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*"
        ";q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
}

    successful_docs = []
    for url in urls:
        try:
            loader = AsyncHtmlLoader([url], header_template=default_header_template, encoding="utf-8", raise_for_status=True)
            docs = loader.load()
            splited_docs = _splited_docs(docs)

            successful_docs.extend(splited_docs)
        except aiohttp.ClientConnectionError:
            pass

    return successful_docs # type: 




def save_graph_image(png_data, output_path):
    with open(output_path, 'wb') as f:
        f.write(png_data)
        
    print(f"Graph saved successfully to {output_path}")