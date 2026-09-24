from dataclasses import dataclass


@dataclass
class NkSection:
    id: str
    name: str


NK_SECTIONS = [
    NkSection(id="allgemein", name="Allgemein"),
    NkSection(id="wohnen", name="Wohnen"),
    NkSection(id="gewerbe", name="Gewerbe"),
    NkSection(id="lager", name="Lager/Sonstiges"),
]


def get_section_by_id(section_id: str):
    for section in NK_SECTIONS:
        if section.id == section_id:
            return section
    return None
