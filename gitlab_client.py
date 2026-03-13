import re
from pathlib import Path
from urllib.parse import urlparse

import gitlab


def list_group_projects(gl: gitlab.Gitlab, group_path: str) -> list[dict]:
    try:
        group = gl.groups.get(group_path)
    except Exception:
        return []
    try:
        projects = group.projects.list(get_all=True)
    except Exception:
        return []
    result: list[dict] = []
    for p in projects:
        name = getattr(p, "name", "") or ""
        path_with_namespace = getattr(p, "path_with_namespace", "") or getattr(p, "path", "")
        result.append({"name": name, "path_with_namespace": path_with_namespace})
    result.sort(key=lambda x: (x["name"].upper(), x["path_with_namespace"]))
    return result


def get_project_path_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if "/-/boards" in path:
        path = path.split("/-/")[0]
    elif "/-" in path:
        path = path.split("/-")[0]
    return path


def list_project_members(gl: gitlab.Gitlab, project_identifier: str) -> list[dict]:
    project = gl.projects.get(project_identifier)
    members: list = []
    namespace = getattr(project, "namespace", None)
    namespace_id = getattr(project, "namespace_id", None)
    namespace_kind = None
    if namespace is not None and not isinstance(namespace, (int, str)):
        namespace_id = getattr(namespace, "id", None) or (namespace.get("id") if isinstance(namespace, dict) else namespace_id)
        namespace_kind = getattr(namespace, "kind", None) or (namespace.get("kind") if isinstance(namespace, dict) else None)
    if namespace_id is not None and namespace_kind != "user":
        try:
            group = gl.groups.get(namespace_id)
            try:
                members = group.members_all.list(get_all=True)
            except AttributeError:
                members = group.members.list(get_all=True)
        except Exception:
            pass
    if not members:
        try:
            members = project.members_all.list(get_all=True)
        except AttributeError:
            pass
    if not members:
        try:
            members = project.members.list(get_all=True)
        except Exception:
            try:
                members = list(project.members.all())
            except Exception:
                pass
    result: list[dict] = []
    seen_ids: set[int] = set()
    for m in members:
        attrs = getattr(m, "attributes", m)
        uid = getattr(attrs, "user_id", None) or getattr(attrs, "id", getattr(m, "id", 0))
        if uid in seen_ids:
            continue
        seen_ids.add(uid)
        username = getattr(attrs, "username", getattr(m, "username", ""))
        name = getattr(attrs, "name", getattr(m, "name", ""))
        result.append({"id": uid, "username": username or "", "name": name or ""})
    result.sort(key=lambda x: ((x["name"] or x["username"]).upper(), x["username"]))
    return result


def list_project_milestones(gl: gitlab.Gitlab, project_identifier: str) -> list[dict]:
    project = gl.projects.get(project_identifier)
    try:
        milestones = project.milestones.list(get_all=True)
    except Exception:
        return []
    result: list[dict] = []
    for ms in milestones:
        result.append({"id": ms.id, "title": getattr(ms, "title", ""), "state": getattr(ms, "state", "active")})
    return result


def upload_file(gl: gitlab.Gitlab, project_identifier: str, local_path: Path) -> str:
    project = gl.projects.get(project_identifier)
    result = project.upload(local_path.name, filepath=str(local_path.resolve()))
    return result.get("markdown", "")


def replace_local_images_in_description(
    gl: gitlab.Gitlab, project_identifier: str, description: str, base_dir: Path
) -> str:
    pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

    def repl(match: re.Match[str]) -> str:
        path_str = match.group(2).strip()
        if path_str.startswith("http://") or path_str.startswith("https://"):
            return match.group(0)
        resolved = (base_dir / path_str).resolve()
        if not resolved.is_file():
            return match.group(0)
        try:
            markdown = upload_file(gl, project_identifier, resolved)
            return markdown if markdown else match.group(0)
        except Exception:
            return match.group(0)

    return pattern.sub(repl, description)


def create_issue(
    base_url: str,
    private_token: str,
    project_identifier: str,
    title: str,
    description: str,
    labels: list[str] | None = None,
    milestone_id: int | None = None,
    assignee_id: int | None = None,
) -> str:
    gl = gitlab.Gitlab(base_url, private_token=private_token)
    project = gl.projects.get(project_identifier)
    payload: dict = {"title": title, "description": description}
    if labels:
        payload["labels"] = labels
    if milestone_id is not None:
        payload["milestone_id"] = milestone_id
    if assignee_id is not None:
        payload["assignee_id"] = assignee_id
    issue = project.issues.create(payload)
    return issue.web_url
