import re
from typing import TypedDict

_IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\([^)]+\)")
_IMAGE_PLACEMENT_HEADERS = ("## Resumo", "## História de Usuário")


class ParsedDemand(TypedDict):
    title: str
    description: str
    project_name: str
    labels: list[str]


def split_demands(text: str) -> list[str]:
    raw = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not raw:
        return []
    blocks: list[str] = []
    current: list[str] = []
    for line in raw.split("\n"):
        if line.strip() == "----":
            if current:
                blocks.append("\n".join(current).strip())
                current = []
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current).strip())
    return blocks


def parse_demand(text: str) -> ParsedDemand:
    raw = text.strip()
    if not raw:
        return ParsedDemand(title="Demanda", description="", project_name="", labels=[])
    lines = raw.split("\n")
    title = lines[0].lstrip("#").strip() if lines else "Demanda"
    rest = "\n".join(lines[1:]).lstrip()
    description = rest if rest else raw
    project_name = _extract_project_from_text(description)
    labels = _extract_labels_from_text(description)
    return ParsedDemand(
        title=title,
        description=description,
        project_name=project_name,
        labels=labels,
    )


def _extract_labels_from_text(text: str) -> list[str]:
    lines = text.split("\n")
    labels: list[str] = []
    for i, line in enumerate(lines):
        if line.strip() == "## Labels":
            j = i + 1
            while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith("##"):
                for part in lines[j].split(","):
                    label = part.strip()
                    if label and label not in labels:
                        labels.append(label)
                j += 1
            break
    return labels


def place_images_after_context_section(description: str) -> str:
    images = _IMAGE_PATTERN.findall(description)
    if not images:
        return description
    desc_no_images = _IMAGE_PATTERN.sub("", description)
    desc_no_images = re.sub(r"\n{3,}", "\n\n", desc_no_images).strip()
    for header in _IMAGE_PLACEMENT_HEADERS:
        idx = desc_no_images.find(header)
        if idx == -1:
            continue
        insert_start = idx + len(header)
        next_section = desc_no_images.find("\n## ", insert_start)
        if next_section == -1:
            insert_pos = len(desc_no_images)
        else:
            insert_pos = next_section
        block = "\n\n" + "\n\n".join(images) + "\n\n"
        return desc_no_images[:insert_pos] + block + desc_no_images[insert_pos:]
    return description


def _extract_project_from_text(text: str) -> str:
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "## Projeto" in line and "Módulo" in line:
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and " - " in lines[j]:
                return lines[j].strip().split(" - ")[0].strip()
    return ""
