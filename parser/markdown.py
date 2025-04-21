from typing import Dict
from parser.utils import parse_cfr_xml

def write_section_markdown(file, section: Dict):
    """Helper to write a section in Markdown format with improved structure"""
    file.write(f"#### § {section['number']} {section['subject']}\n\n")

    for content in section["content"]:
        if content["type"] == "paragraph":
            if "heading" in content:
                # Main paragraph with heading (a), (b), etc.
                file.write(f"**{content['heading']}** {content['text']}\n\n")

                # Write subparagraphs if they exist
                for subpara in content.get("subparagraphs", []):
                    # Indent subparagraphs and make them italic
                    file.write(f"    *{subpara['text']}*\n\n")
            else:
                # Regular paragraph without heading
                file.write(f"{content['text']}\n\n")

        elif content["type"] == "indented_paragraph":
            # Indented paragraphs (from IPAR tags)
            file.write(f"    {content['text']}\n\n")

    # Write citations if they exist
    if section["citations"]:
        file.write("**Citations:**\n")
        for citation in section["citations"]:
            file.write(f"- {citation}\n")
        file.write("\n")

def save_to_markdown(data: Dict, output_file: str) -> None:
    """Save parsed data to Markdown format with improved formatting"""
    with open(output_file, "w", encoding="utf-8") as f:
        # Write metadata
        f.write(f"# Title {data['metadata']['title_number']}: {data['metadata']['subject']}\n\n")
        f.write(f"*Revised: {data['metadata']['revised']}*\n")
        f.write(f"*Date: {data['metadata']['date']}*\n")
        f.write(f"*Parts: {data['metadata']['parts']}*\n\n")

        # Write chapters
        if data["chapters"]:
            f.write("## Chapters\n")
            for chapter in data["chapters"]:
                f.write(f"- {chapter['number']}: {chapter['subject']} (Page {chapter['page']})\n")
            f.write("\n")

        # Write parts and sections
        for part in data["parts"]:
            f.write(f"## Part {part['number']}: {part['title']}\n\n")
            if part["authority"]:
                f.write(f"**Authority:** {part['authority']}\n\n")
            if part["source"]:
                f.write(f"**Source:** {part['source']}\n\n")

            # Write sections not in subparts
            for section in part["sections"]:
                write_section_markdown(f, section)

            # Write subparts and their sections
            for subpart in part["subparts"]:
                f.write(f"### Subpart: {subpart['title']}\n\n")
                for section in subpart["sections"]:
                    write_section_markdown(f, section)

def main():
    # input_file = "/content/drive/MyDrive/CIS 630 - Final Project/Source Data - CFR File/CFR-2024/title-12/CFR-2024-title12-vol1.xml"
    # md_output = "/content/drive/MyDrive/CIS 630 - Final Project/Pram XML Parser/CFR_parsed_output/title12-vol1_parsed_cfr.md"

    input_file = "title-12/CFR-2024-title12-vol1.xml"
    md_output = "cfr_parsed_output/title12-vol1_parsed_cfr.md"

    print(f"Parsing {input_file}...")
    parsed_data = parse_cfr_xml(input_file)

    print(f"Saving Markdown to {md_output}...")
    print(parsed_data)
    save_to_markdown(parsed_data, md_output)

    print("Done!")

if __name__ == "__main__":
    main()