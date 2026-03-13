import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import gitlab

from demand_parser import parse_demand, split_demands
from gitlab_client import (
    create_issue,
    get_project_path_from_url,
    list_group_projects,
    list_project_members,
    list_project_milestones,
    replace_local_images_in_description,
)

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
BOLD = "\033[1m"
DIM = "\033[2m"
BRIGHT = "\033[97m"
BRIGHT_GREEN = "\033[92m"
RESET = "\033[0m"


def _sep():
    print(f"{DIM}  {'-' * 50}{RESET}")


def _prompt(msg: str, hint: str = "") -> str:
    hint_str = f" {DIM}({hint}){RESET}" if hint else ""
    return input(f"  {MAGENTA}>>{RESET} {msg}{hint_str}: ").strip()

PROJECTS_FILE = "projects.json"
LABELS_FILE = "labels.json"
DEFAULT_DEMAND_FILE = "dmd.md"
LABEL_NEEDS_CORRECTION = "Precisa de Correção"
LABEL_DEFAULT_STATUS = "Não iniciado"
LABEL_CORRECAO = "Correção"
LABEL_MELHORIA = "Melhoria"
LABEL_PRIORIDADE_ALTA = "PRIORIDADE: ALTA"


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
        print(f"{RED}Erro: nenhum projeto em {projects_path}.{RESET}")
        sys.exit(1)
    print(f"\n{BOLD}{BLUE}[ 1 / 4 ] Projeto{RESET}")
    _sep()
    for i, name in enumerate(names, 1):
        print(f"  {CYAN}{i:2}.{RESET} {name}")
    _sep()
    raw = _prompt("Número do projeto", f"1 a {len(names)}")
    if not raw.isdigit():
        print(f"{RED}Erro: informe um número válido.{RESET}")
        sys.exit(1)
    idx = int(raw)
    if not 1 <= idx <= len(names):
        print(f"{RED}Erro: número inválido.{RESET}")
        sys.exit(1)
    project_name = names[idx - 1]
    print(f"  {GREEN}Projeto selecionado: {project_name}{RESET}\n")
    return project_name, config[project_name]


def interactive_select_project_from_api(projects: list[dict]) -> tuple[str, str]:
    if not projects:
        print(f"{RED}Erro: nenhum projeto encontrado no grupo.{RESET}")
        sys.exit(1)
    print(f"\n{BOLD}{BLUE}[ 1 / 4 ] Projeto (grupo GitLab){RESET}")
    _sep()
    for i, p in enumerate(projects, 1):
        name = p.get("name", "")
        path_ns = p.get("path_with_namespace", "")
        print(f"  {CYAN}{i:2}.{RESET} {name} {DIM}({path_ns}){RESET}")
    _sep()
    raw = _prompt("Número do projeto", f"1 a {len(projects)}")
    if not raw.isdigit():
        print(f"{RED}Erro: informe um número válido.{RESET}")
        sys.exit(1)
    idx = int(raw)
    if not 1 <= idx <= len(projects):
        print(f"{RED}Erro: número inválido.{RESET}")
        sys.exit(1)
    chosen = projects[idx - 1]
    project_name = chosen.get("name", "")
    project_path = chosen.get("path_with_namespace", "")
    print(f"  {GREEN}Projeto selecionado: {project_name}{RESET}\n")
    return project_name, project_path


def load_allowed_labels(path: str) -> list[str]:
    if not Path(path).exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return list(data) if isinstance(data, list) else []


def _has_priority_label(labels: list[str]) -> bool:
    return any(lb.startswith("PRIORIDADE:") for lb in labels)


def apply_label_defaults(selected: list[str], allowed_labels: list[str]) -> list[str]:
    out = list(selected)
    if LABEL_NEEDS_CORRECTION not in out and LABEL_DEFAULT_STATUS in allowed_labels and LABEL_DEFAULT_STATUS not in out:
        out.append(LABEL_DEFAULT_STATUS)
    if (LABEL_CORRECAO in allowed_labels or LABEL_MELHORIA in allowed_labels) and LABEL_MELHORIA not in out and LABEL_CORRECAO not in out and LABEL_CORRECAO in allowed_labels:
        out.append(LABEL_CORRECAO)
    if LABEL_PRIORIDADE_ALTA in allowed_labels and LABEL_PRIORIDADE_ALTA not in out and not _has_priority_label(out):
        out.append(LABEL_PRIORIDADE_ALTA)
    return out


def interactive_select_labels(allowed_labels: list[str]) -> list[str]:
    if not allowed_labels:
        return []
    for i, lb in enumerate(allowed_labels, 1):
        print(f"  {CYAN}{i:2}.{RESET} {lb}")
    _sep()
    raw = _prompt("Números das labels", "ex: 1,3,5 ou Enter para padrão")
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


def interactive_select_milestone(milestones: list[dict]) -> int | None:
    if not milestones:
        print(f"{YELLOW}Nenhum milestone encontrado no projeto.{RESET}\n")
        return None
    print(f"\n{BOLD}{BLUE}[ 2 / 4 ] Milestone{RESET}")
    _sep()
    for i, ms in enumerate(milestones, 1):
        title = ms.get("title", "")
        state = ms.get("state", "")
        print(f"  {CYAN}{i:2}.{RESET} {title} {DIM}({state}){RESET}")
    _sep()
    raw = _prompt("Número do milestone", f"1 a {len(milestones)} ou Enter para nenhum")
    if not raw:
        print(f"  {DIM}Nenhum milestone atribuído.{RESET}\n")
        return None
    if not raw.isdigit():
        print(f"{YELLOW}Entrada inválida; nenhum milestone será atribuído.{RESET}\n")
        return None
    idx = int(raw)
    if not 1 <= idx <= len(milestones):
        print(f"{YELLOW}Número inválido; nenhum milestone será atribuído.{RESET}\n")
        return None
    chosen = milestones[idx - 1].get("title", "")
    print(f"  {GREEN}Milestone: {chosen}{RESET}\n")
    return milestones[idx - 1]["id"]


def interactive_select_assignee(members: list[dict], show_header: bool = True) -> int | None:
    if not members:
        print(f"{YELLOW}Nenhum membro encontrado no projeto.{RESET}\n")
        return None
    if show_header:
        print(f"\n{BOLD}{BLUE}[ 3 / 4 ] Responsável{RESET}")
    _sep()
    for i, mem in enumerate(members, 1):
        name = mem.get("name", "") or mem.get("username", "")
        username = mem.get("username", "")
        print(f"  {CYAN}{i:2}.{RESET} {name} {DIM}(@{username}){RESET}")
    _sep()
    raw = _prompt("Número do responsável", f"1 a {len(members)} ou Enter para nenhum")
    if not raw:
        print(f"  {DIM}Nenhum responsável atribuído.{RESET}\n")
        return None
    if not raw.isdigit():
        print(f"{YELLOW}Entrada inválida; nenhum responsável será atribuído.{RESET}\n")
        return None
    idx = int(raw)
    if not 1 <= idx <= len(members):
        print(f"{YELLOW}Número inválido; nenhum responsável será atribuído.{RESET}\n")
        return None
    chosen = members[idx - 1].get("name", "") or members[idx - 1].get("username", "")
    print(f"  {GREEN}Responsável: {chosen}{RESET}\n")
    return members[idx - 1]["id"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cria issue no GitLab. Refine o dmd.md no Cursor antes; selecione projeto e labels no terminal."
    )
    parser.add_argument("--demand-file", "-f", default=DEFAULT_DEMAND_FILE, help=f"Arquivo da demanda (padrão: {DEFAULT_DEMAND_FILE})")
    parser.add_argument("--projects-config", default=PROJECTS_FILE, help=f"Caminho do {PROJECTS_FILE}")
    parser.add_argument("--labels-config", default=LABELS_FILE, help=f"Caminho do {LABELS_FILE}")
    args = parser.parse_args()

    demand_path = Path(args.demand_file)
    if not demand_path.exists():
        print(f"{RED}Erro: arquivo de demanda não encontrado: {demand_path}{RESET}")
        sys.exit(1)

    load_dotenv()
    gitlab_url = os.getenv("GITLAB_URL")
    gitlab_token = os.getenv("GITLAB_PRIVATE_TOKEN")
    if not gitlab_url or not gitlab_token:
        print(f"{RED}Erro: GITLAB_URL e GITLAB_PRIVATE_TOKEN devem estar definidos no .env{RESET}")
        sys.exit(1)

    gl = gitlab.Gitlab(gitlab_url.rstrip("/"), private_token=gitlab_token)
    group_path = (os.getenv("GITLAB_GROUP_PATH") or "").strip()
    if group_path:
        projects = list_group_projects(gl, group_path)
        if not projects:
            print(f"{RED}Erro: nenhum projeto encontrado no grupo '{group_path}' ou grupo inválido.{RESET}")
            sys.exit(1)
        project_name, project_path = interactive_select_project_from_api(projects)
    else:
        projects_path = args.projects_config
        if not Path(projects_path).exists():
            print(f"{RED}Erro: arquivo {projects_path} não encontrado. Defina GITLAB_GROUP_PATH no .env para listar projetos do grupo via API.{RESET}")
            sys.exit(1)
        project_name, project_path = interactive_select_project(projects_path)
    milestones: list[dict] = []
    members: list[dict] = []
    try:
        milestones = list_project_milestones(gl, project_path)
    except Exception:
        print(f"{YELLOW}Não foi possível carregar milestones do projeto.{RESET}")
    try:
        members = list_project_members(gl, project_path)
    except Exception:
        print(f"{YELLOW}Não foi possível carregar membros do projeto.{RESET}")

    milestone_id: int | None = interactive_select_milestone(milestones)

    with open(demand_path, encoding="utf-8") as f:
        demand_content = f.read().strip()
    if not demand_content:
        print(f"{RED}Erro: arquivo {demand_path} está vazio.{RESET}")
        sys.exit(1)

    blocks = split_demands(demand_content)
    if not blocks:
        print(f"{RED}Erro: nenhuma demanda encontrada em {demand_path}.{RESET}")
        sys.exit(1)

    assignee_ids_per_demand: list[int | None] = []
    if len(blocks) == 1:
        assignee_ids_per_demand = [interactive_select_assignee(members)]
    else:
        for i, block in enumerate(blocks):
            parsed = parse_demand(block)
            title = parsed["title"]
            short = title[:50] + "..." if len(title) > 50 else title
            print(f"\n{BOLD}{BLUE}[ 3 / 4 ] Responsável - Demanda {i + 1}/{len(blocks)}{RESET}")
            print(f"  {DIM}{short}{RESET}")
            assignee_ids_per_demand.append(interactive_select_assignee(members, show_header=False))
            if i < len(blocks) - 1:
                _sep()

    print(f"\n{BOLD}{BLUE}[ 4 / 4 ] Labels e demandas{RESET}")
    print(f"  {DIM}Arquivo: {demand_path} ({len(blocks)} demanda(s)){RESET}")
    _sep()

    labels_path = args.labels_config
    allowed_labels = load_allowed_labels(labels_path)
    labels_per_demand: list[list[str]] = []

    if len(blocks) == 1:
        print(f"  {CYAN}Labels para a demanda:{RESET}")
        selected_labels = interactive_select_labels(allowed_labels)
        labels_per_demand = [apply_label_defaults(selected_labels, allowed_labels)]
    else:
        for i, block in enumerate(blocks):
            parsed = parse_demand(block)
            title = parsed["title"]
            short = title[:50] + "..." if len(title) > 50 else title
            print(f"  {BOLD}Demanda {i + 1}/{len(blocks)}:{RESET} {DIM}{short}{RESET}")
            selected = interactive_select_labels(allowed_labels)
            labels_per_demand.append(apply_label_defaults(selected, allowed_labels))
            if i < len(blocks) - 1:
                _sep()

    issue_urls: list[str] = []
    try:
        for i, block in enumerate(blocks):
            parsed = parse_demand(block)
            description = parsed["description"].replace("[Nome do Projeto]", project_name)
            description = replace_local_images_in_description(gl, project_path, description, demand_path.parent)
            labels = labels_per_demand[i] if labels_per_demand else None
            assignee_id = assignee_ids_per_demand[i] if i < len(assignee_ids_per_demand) else None
            issue_url = create_issue(
                base_url=gitlab_url.rstrip("/"),
                private_token=gitlab_token,
                project_identifier=project_path,
                title=parsed["title"],
                description=description,
                labels=labels if labels else None,
                milestone_id=milestone_id,
                assignee_id=assignee_id,
            )
            issue_urls.append(issue_url)
        print(f"\n{BOLD}{GREEN}Issues criadas com sucesso{RESET}")
        _sep()
        for i, url in enumerate(issue_urls, 1):
            print(f"  {CYAN}Issue {i}:{RESET} {BRIGHT_GREEN}{url}{RESET}")
        _sep()
        print()
    except Exception as e:
        print(f"{RED}Erro ao criar issue no GitLab: {e}{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
