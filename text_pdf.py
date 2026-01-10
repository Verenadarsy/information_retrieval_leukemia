import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import os
import re

# URL Wikipedia Indonesia
url = "https://id.wikipedia.org/wiki/Leukemia"

def extract_important_sections(soup):
    """Ekstrak bagian-bagian penting dari artikel"""
    
    important_data = {
        "title": "",
        "definisi": [],
        "istilah": [],
        "gejala": [],
        "pengobatan": [],
        "referensi": [],
        "info_box": {}
    }
    
    # Judul
    title = soup.find("h1")
    if title:
        important_data["title"] = title.text.strip()
    
    # Ambil kotak info (infobox) jika ada
    infobox = soup.find("table", {"class": "infobox"})
    if infobox:
        info_items = {}
        rows = infobox.find_all("tr")
        for row in rows:
            th = row.find("th")
            td = row.find("td")
            if th and td:
                key = th.text.strip().replace('\n', ' ')
                value = td.text.strip().replace('\n', ' ')
                info_items[key] = value
        important_data["info_box"] = info_items
    
    # Cari section berdasarkan heading
    content_div = soup.find("div", {"id": "mw-content-text"})
    if not content_div:
        return important_data
    
    # Cari semua heading dan kontennya
    current_section = ""
    elements = content_div.find_all(['h2', 'h3', 'h4', 'p', 'ul'])
    
    for element in elements:
        if element.name in ['h2', 'h3', 'h4']:
            current_section = element.text.strip().lower()
            
            # Cek apakah heading mengandung kata kunci penting
            keywords = {
                'definisi': ['pengertian', 'definisi', 'apa itu', 'penjelasan'],
                'gejala': ['gejala', 'tanda', 'manifestasi', 'simtom'],
                'pengobatan': ['pengobatan', 'perawatan', 'terapi', 'penanganan', 'obat'],
                'istilah': ['istilah', 'terminologi', 'kosa kata', 'glosarium']
            }
            
            for key, key_list in keywords.items():
                if any(keyword in current_section for keyword in key_list):
                    current_section = key
                    break
        
        elif element.name == 'p':
            text = element.text.strip()
            if len(text) > 30:
                # Klasifikasikan ke section yang sesuai
                if 'definisi' in current_section or 'pengertian' in current_section:
                    important_data["definisi"].append(text)
                elif 'gejala' in current_section:
                    important_data["gejala"].append(text)
                elif 'pengobatan' in current_section:
                    important_data["pengobatan"].append(text)
                elif text and len(text) > 100:  # Paragraf umum panjang
                    important_data["definisi"].append(text)
        
        elif element.name == 'ul':
            # Ambil list items untuk gejala atau pengobatan
            items = element.find_all('li')
            item_texts = [li.text.strip() for li in items if len(li.text.strip()) > 10]
            
            if 'gejala' in current_section:
                important_data["gejala"].extend(item_texts)
            elif 'pengobatan' in current_section:
                important_data["pengobatan"].extend(item_texts)
            elif 'istilah' in current_section:
                important_data["istilah"].extend(item_texts)
    
    # Ambil referensi
    ref_section = soup.find("div", {"id": "catlinks"}) or soup.find("div", {"class": "reflist"})
    if ref_section:
        links = ref_section.find_all("a")
        for link in links:
            href = link.get('href', '')
            if href and 'http' in href:
                important_data["referensi"].append({
                    'text': link.text.strip(),
                    'url': href if href.startswith('http') else 'https://id.wikipedia.org' + href
                })
    
    return important_data

def create_formatted_pdf(data, url, output_folder="dataset/wiki"):
    """Buat PDF dengan format yang rapih"""
    
    os.makedirs(output_folder, exist_ok=True)
    
    # Buat nama file
    safe_title = re.sub(r'[^\w\s-]', '', data["title"]).strip().replace(' ', '_')
    filename = f"wiki_{safe_title}_formatted.pdf"
    filepath = os.path.join(output_folder, filename)
    
    # Setup styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#2C3E50')
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor('#2980B9')
    )
    
    content_style = ParagraphStyle(
        'Content',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=content_style,
        leftIndent=20,
        firstLineIndent=-10,
        bulletIndent=10
    )
    
    ref_style = ParagraphStyle(
        'Reference',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        textColor=colors.HexColor('#7F8C8D'),
        leftIndent=10
    )
    
    # Buat dokumen
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    story = []
    
    # HEADER
    story.append(Paragraph(data["title"], title_style))
    
    # Metadata section
    meta_table_data = [
        ["Sumber Artikel", f"<link href='{url}'>{url}</link>"],
        ["Tanggal Akses", datetime.now().strftime("%d %B %Y %H:%M")],
        ["Format", "Dokumen Informasi Medis - Ringkasan"]
    ]
    
    meta_table = Table(meta_table_data, colWidths=[2*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDC3C7')),
    ]))
    
    story.append(meta_table)
    story.append(Spacer(1, 20))
    
    # INFORMASI SINGKAT (dari infobox)
    if data["info_box"]:
        story.append(Paragraph("INFORMASI SINGKAT", section_style))
        
        info_items = list(data["info_box"].items())[:8]  # Ambil 8 item pertama
        for key, value in info_items:
            story.append(Paragraph(f"<b>{key}:</b> {value}", content_style))
        
        story.append(Spacer(1, 15))
    
    # DEFINISI / PENJELASAN
    if data["definisi"]:
        story.append(Paragraph("DEFINISI DAN PENJELASAN", section_style))
        for para in data["definisi"][:3]:  # Ambil 3 paragraf pertama
            story.append(Paragraph(para, content_style))
            story.append(Spacer(1, 8))
    
    # GEJALA
    if data["gejala"]:
        story.append(Paragraph("GEJALA DAN TANDA-TANDA", section_style))
        
        # Jika berupa list
        if len(data["gejala"]) > 0 and any('•' in g or '-' in g for g in data["gejala"][:3]):
            for symptom in data["gejala"][:15]:  # Batasi 15 gejala
                story.append(Paragraph(f"• {symptom}", bullet_style))
        else:
            for symptom in data["gejala"][:5]:  # Ambil 5 paragraf tentang gejala
                story.append(Paragraph(symptom, content_style))
                story.append(Spacer(1, 4))
    
    # PENGOBATAN
    if data["pengobatan"]:
        story.append(Paragraph("PENGOBATAN DAN PERAWATAN", section_style))
        
        # Jika berupa list
        if len(data["pengobatan"]) > 0 and any('•' in t or '-' in t for t in data["pengobatan"][:3]):
            for treatment in data["pengobatan"][:10]:  # Batasi 10 item
                story.append(Paragraph(f"• {treatment}", bullet_style))
        else:
            for treatment in data["pengobatan"][:3]:  # Ambil 3 paragraf
                story.append(Paragraph(treatment, content_style))
                story.append(Spacer(1, 4))
    
    # ISTILAH PENTING
    if data["istilah"]:
        story.append(Paragraph("ISTILAH PENTING", section_style))
        for term in data["istilah"][:10]:  # Ambil 10 istilah
            story.append(Paragraph(f"• {term}", bullet_style))
    
    story.append(Spacer(1, 25))
    
    # REFERENSI DAN SUMBER
    story.append(Paragraph("REFERENSI DAN SUMBER INFORMASI", section_style))
    
    # Sumber utama
    story.append(Paragraph(f"<b>Sumber Utama:</b>", content_style))
    story.append(Paragraph(f"Wikipedia Bahasa Indonesia - {data['title']}", content_style))
    story.append(Paragraph(f"URL: <link href='{url}'>{url}</link>", ref_style))
    story.append(Spacer(1, 10))
    
    # Referensi tambahan
    if data["referensi"]:
        story.append(Paragraph("<b>Referensi Tambahan:</b>", content_style))
        for idx, ref in enumerate(data["referensi"][:5], 1):  # Ambil 5 referensi
            story.append(Paragraph(f"{idx}. {ref['text']}", ref_style))
            story.append(Paragraph(f"   <link href='{ref['url']}'>{ref['url']}</link>", ref_style))
            story.append(Spacer(1, 4))
    
    story.append(Spacer(1, 20))
    
    # FOOTER / DISCLAIMER
    disclaimer = """
    <b>DISCLAIMER:</b> Dokumen ini merupakan ringkasan informasi dari sumber publik (Wikipedia) 
    untuk tujuan pendidikan dan referensi. Informasi ini tidak menggantikan saran medis profesional. 
    Konsultasikan dengan dokter atau tenaga kesehatan untuk diagnosis dan pengobatan yang tepat.
    """
    story.append(Paragraph(disclaimer, ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        textColor=colors.HexColor('#E74C3C'),
        alignment=TA_CENTER,
        borderPadding=10,
        borderColor=colors.HexColor('#FADBD8'),
        borderWidth=1
    )))
    
    # Build PDF
    try:
        doc.build(story)
        print(f"✅ PDF berhasil dibuat dengan format rapih!")
        print(f"📁 Lokasi: {filepath}")
        print(f"📊 Konten yang diekstrak:")
        print(f"   - Definisi: {len(data['definisi'])} paragraf")
        print(f"   - Gejala: {len(data['gejala'])} item")
        print(f"   - Pengobatan: {len(data['pengobatan'])} item")
        print(f"   - Referensi: {len(data['referensi'])} sumber")
        
    except Exception as e:
        print(f"❌ Error membuat PDF: {e}")

def wiki_to_structured_pdf(url, output_folder="dataset/wiki"):
    """Main function untuk scrape dan buat PDF terstruktur"""
    
    print(f"🔍 Memulai scraping dari: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        # Fetch halaman
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        print("✅ Berhasil mengakses halaman")
        
        # Parse HTML
        soup = BeautifulSoup(res.text, "html.parser")
        print("✅ HTML berhasil di-parse")
        
        # Ekstrak informasi penting
        print("⏳ Mengekstrak informasi penting...")
        important_data = extract_important_sections(soup)
        
        if not important_data["title"]:
            important_data["title"] = url.split('/')[-1].replace('_', ' ')
        
        # Buat PDF dengan format rapih
        print("📝 Membuat PDF terstruktur...")
        create_formatted_pdf(important_data, url, output_folder)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error koneksi: {e}")
    except Exception as e:
        print(f"❌ Error tidak terduga: {e}")

if __name__ == "__main__":
    # Contoh dengan beberapa artikel kesehatan
    articles = [
        "https://id.wikipedia.org/wiki/Leukemia",
        "https://id.wikipedia.org/wiki/Leukemia_mieloblastik_akut",
        "https://id.wikipedia.org/wiki/Leukemia_limfoblastik_akut",
        "https://id.wikipedia.org/wiki/Leukemia_mielositik_kronis",
        "https://id.wikipedia.org/wiki/Leukemia_limfositik_kronis",
        "https://id.wikipedia.org/wiki/Kanker_darah",
        "https://id.wikipedia.org/wiki/Sumsum_tulang",
        "https://id.wikipedia.org/wiki/Sel_punca",
        "https://id.wikipedia.org/wiki/Transplantasi_sumsum_tulang",
        "https://id.wikipedia.org/wiki/Kemoterapi"
    ]
    
    for article_url in articles:
        print("\n" + "="*60)
        wiki_to_structured_pdf(article_url)
        print("="*60)