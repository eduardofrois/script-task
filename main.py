import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from demand_parser import parse_demand
from gitlab_client import create_issue, get_project_path_from_url


PROJECTS_FILE = "projects.json"
LABELS_FILE = "labels.json"
DEFAULT_DEMAND_FILE = "dmd.txt"
LABEL_NEEDS_CORRECTION = "Precisa de Correção"
LABEL_DEFAULT_STATUS = "Não iniciado"


def load_projects_config(path: str) -> dict[str, str]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    result: dict[str, str] = {}
    for name, value in raw.items():
        if value.startswith("http://") or value.startswith("https://"):
            result[name.upper()] = get_project_path_from_url(value)
        else:
            result[name.upper()] = value
    return result


def resolve_project_path(projects_path: str, project_name: str) -> str:
    config = load_projects_config(projects_path)
    key = project_name.strip().upper()
    if key not in config:
        raise ValueError(
            f"Projeto '{project_name}' não está em {PROJECTS_FILE}. "
            f"Projetos disponíveis: {', '.join(config.keys())}"
        )
    return config[key]


def interactive_select_project(projects_path: str) -> tuple[str, str]:
    config = load_projects_config(projects_path)
    names = list(config.keys())
    if not names:
        print(f"Erro: nenhum projeto em {projects_path}.")
        sys.exit(1)
    print("Projetos disponíveis:")
    for i, name in enumerate(names, 1):
        print(f"  {i}. {name}")
    raw = input("Escolha o projeto (número): ").strip()
    if not raw.isdigit():
        print("Erro: informe um número válido.")
        sys.exit(1)
    idx = int(raw)
    if not 1 <= idx <= len(names):
        print("Erro: número inválido.")
        sys.exit(1)
    project_name = names[idx - 1]
    return project_name, config[project_name]


def load_allowed_labels(path: str) -> list[str]:
    if not Path(path).exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return list(data) if isinstance(data, list) else []


def interactive_select_labels(allowed_labels: list[str]) -> list[str]:
    if not allowed_labels:
        return []
    print("Labels disponíveis:")
    for i, lb in enumerate(allowed_labels, 1):
        print(f"  {i}. {lb}")
    raw = input("Escolha a(s) label(s) (números separados por vírgula, ou Enter para nenhuma): ").strip()
    if not raw:
        return []
    selected: list[str] = []
    for part in raw.split(","):
        part = part.strip()
        if not part.isdigit():
            continue
        idx = int(part)
        if 1 <= idx <= len(allowed_labels) and allowed_labels[idx - 1] not in selected:
            selected.append(allowed_labels[idx - 1])
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cria issue no GitLab. Refine o dmd.txt no Cursor antes; selecione projeto e labels no terminal."
    )
    parser.add_argument("--demand-file", "-f", default=DEFAULT_DEMAND_FILE, help=f"Arquivo da demanda (padrão: {DEFAULT_DEMAND_FILE})")
    parser.add_argument("--projects-config", default=PROJECTS_FILE, help=f"Caminho do {PROJECTS_FILE}")
    parser.add_argument("--labels-config", default=LABELS_FILE, help=f"Caminho do {LABELS_FILE}")
    args = parser.parse_args()

    demand_path = Path(args.demand_file)
    if not demand_path.exists():
        print(f"Erro: arquivo de demanda não encontrado: {demand_path}")
        sys.exit(1)

    load_dotenv()
    gitlab_url = os.getenv("GITLAB_URL")
    gitlab_token = os.getenv("GITLAB_PRIVATE_TOKEN")
    if not gitlab_url or not gitlab_token:
        print("Erro: GITLAB_URL e GITLAB_PRIVATE_TOKEN devem estar definidos no .env")
        sys.exit(1)

    projects_path = args.projects_config
    if not Path(projects_path).exists():
        print(f"Erro: arquivo {projects_path} não encontrado.")
        sys.exit(1)

    project_name, project_path = interactive_select_project(projects_path)

    with open(demand_path, encoding="utf-8") as f:
        demand_content = f.read().strip()
    if not demand_content:
        print(f"Erro: arquivo {demand_path} está vazio.")
        sys.exit(1)

    print(f"Lendo demanda de {demand_path}...")
    parsed = parse_demand(demand_content)

    labels_path = args.labels_config
    allowed_labels = load_allowed_labels(labels_path)
    selected_labels = interactive_select_labels(allowed_labels)
    if LABEL_NEEDS_CORRECTION not in selected_labels and LABEL_DEFAULT_STATUS in allowed_labels:
        if LABEL_DEFAULT_STATUS not in selected_labels:
            selected_labels.append(LABEL_DEFAULT_STATUS)

    try:
        issue_url = create_issue(
            base_url=gitlab_url.rstrip("/"),
            private_token=gitlab_token,
            project_identifier=project_path,
            title=parsed["title"],
            description=parsed["description"],
            labels=selected_labels if selected_labels else None,
        )
        print(f"Issue criada: {issue_url}")
    except Exception as e:
        print(f"Erro ao criar issue no GitLab: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
