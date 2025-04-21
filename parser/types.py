from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel

class MetaData(BaseModel):
    title_number: str
    subject: str
    parts: str
    revised: str
    contains: str
    date: str
    publication: str

class Chapter(BaseModel):
    number: str
    subject: str
    page: int

class Content(BaseModel):
    type: str
    text: str
    heading: Optional[str] = None
    subparagraphs: List[Content] = []

class Section(BaseModel):
    number: str
    subject: str
    content: List[Content]
    citations: List[str] = []

class Subpart(BaseModel):
    title: str
    sections: List[Section] = []

class Part(BaseModel):
    number: str
    title: str
    authority: str
    source: str
    subparts: List[Subpart] = []
    sections: List[Section] = []

class Volume(BaseModel):
    metadata: MetaData
    titles: List[str]
    chapters: List[Chapter]
    parts: List[Part]
    sections: List[Section] = []
