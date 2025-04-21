import xml.etree.ElementTree as ET
from typing import Dict
from parser.types import Volume

def get_text(element: ET.Element, path: str) -> str:
    """Safe text extraction helper"""
    found = element.find(path)
    return clean_text(found.text if found is not None else "")

def clean_part_number(text: str) -> str:
    """Clean part number text"""
    return text.replace("Pt.", "").strip()

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if text is None:
        return ""
    return " ".join(text.replace("\n", " ").replace("\t", " ").strip().split())

def parse_section(section: ET.Element) -> Dict:
    """Parse an individual section element with improved paragraph handling"""
    section_data = {
        "number": get_text(section, "SECTNO"),
        "subject": get_text(section, "SUBJECT"),
        "content": [],
        "citations": []
    }

    # Extract paragraphs and subparagraphs
    current_paragraph = None
    for elem in section:
        if elem.tag == "P":
            # Handle paragraph text and any child elements
            paragraph_text = ""
            for content in elem.itertext():
                paragraph_text += content
            paragraph_text = clean_text(paragraph_text)

            if paragraph_text:
                # Check if this is a new main paragraph (starts with (a), (b), etc.)
                if (paragraph_text.strip().startswith('(') and
                    len(paragraph_text) > 1 and
                    paragraph_text[1].isalpha() and
                    len(paragraph_text) > 3 and
                    paragraph_text[2] in (')', ' ')):

                    # If we have a current paragraph, add it before starting new one
                    if current_paragraph:
                        section_data["content"].append(current_paragraph)

                    # Extract the heading (e.g., "(a)")
                    heading_end = paragraph_text.find(')') + 1
                    heading = paragraph_text[:heading_end].strip()
                    remaining_text = paragraph_text[heading_end:].strip()

                    current_paragraph = {
                        "type": "paragraph",
                        "heading": heading,
                        "text": remaining_text,
                        "subparagraphs": []
                    }
                else:
                    # Check if this is a subparagraph (i), (ii), etc.
                    if (current_paragraph and
                        paragraph_text.strip().startswith('(') and
                        any(paragraph_text[1:].startswith(num)
                            for num in ['i)', 'ii)', 'iii)', 'iv)', 'v)', 'vi)', 'vii)', 'viii)', 'ix)', 'x)'])):

                        current_paragraph["subparagraphs"].append({
                            "type": "subparagraph",
                            "text": paragraph_text
                        })
                    else:
                        # Regular paragraph content
                        if current_paragraph:
                            current_paragraph["text"] += " " + paragraph_text
                        else:
                            section_data["content"].append({
                                "type": "paragraph",
                                "text": paragraph_text
                            })
        elif elem.tag == "IPAR":
            for sub_elem in elem:
                if sub_elem.tag == "P":
                    text = clean_text(sub_elem.text or "")
                    if text:
                        section_data["content"].append({
                            "type": "indented_paragraph",
                            "text": text
                        })

    # Add the last current paragraph if it exists
    if current_paragraph:
        section_data["content"].append(current_paragraph)

    # Extract citations
    for citation in section.findall(".//CITA"):
        citation_text = clean_text(citation.text or "")
        if citation_text:
            section_data["citations"].append(citation_text)

    return section_data

def parse_cfr_xml(xml_file: str) -> Volume:
    """
    Parse the CFR XML file and extract structured regulatory information.

    Args:
        xml_file: Path to the XML file

    Returns:
        Dictionary containing structured regulatory information
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Register namespaces if present (though CFR XML typically doesn't use them)
    namespaces = {'ns': 'http://www.w3.org/2001/XMLSchema-instance'} if 'xmlns' in root.attrib else {}

    # Initialize the result structure
    result = {
        "metadata": {},
        "titles": [],
        "chapters": [],
        "parts": [],
        "sections": []
    }

    # Extract metadata
    metadata = root.find(".//TITLEPG")
    if metadata is not None:
        result["metadata"] = {
            "title_number": get_text(metadata, "TITLENUM"),
            "subject": get_text(metadata, "SUBJECT"),
            "parts": get_text(metadata, "PARTS"),
            "revised": get_text(metadata, "REVISED"),
            "contains": get_text(metadata, "CONTAINS"),
            "date": get_text(metadata, "DATE"),
            "publication": get_text(metadata, "PUB/P")
        }

    # Extract chapters
    for chapter in root.findall(".//CHAPTI"):
        chapter_data = {
            "number": get_text(chapter, "PT"),
            "subject": get_text(chapter, "SUBJECT"),
            "page": get_text(chapter, "PG")
        }
        result["chapters"].append(chapter_data)

    # Extract parts and sections
    for part in root.findall(".//PART"):
        part_data = {
            "number": clean_part_number(get_text(part, "EAR")),
            "title": get_text(part, ".//HD[@SOURCE='HED']"),
            "authority": clean_text(get_text(part, ".//AUTH/P")),
            "source": clean_text(get_text(part, ".//SOURCE/P")),
            "subparts": [],
            "sections": []
        }

        # Extract subparts if they exist
        for subpart in part.findall(".//SUBPART"):
            subpart_data = {
                "title": get_text(subpart, ".//HD[@SOURCE='HED']"),
                "sections": []
            }

            # Extract sections within subparts
            for section in subpart.findall(".//SECTION"):
                section_data = parse_section(section)
                subpart_data["sections"].append(section_data)
                result["sections"].append(section_data)

            part_data["subparts"].append(subpart_data)

        # Extract sections not in subparts (using alternative approach)
        for section in part.findall(".//SECTION"):
            # Only include if not already captured in a subpart
            if not any(section in subpart for subpart in part.findall(".//SUBPART")):
                section_data = parse_section(section)
                part_data["sections"].append(section_data)
                result["sections"].append(section_data)

        result["parts"].append(part_data)

    return result
