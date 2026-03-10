from urllib.parse import urlparse

import gitlab


def get_project_path_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if "/-/boards" in path:
        path = path.split("/-/")[0]
    elif "/-" in path:
        path = path.split("/-")[0]
    return path


def create_issue(
    base_url: str,
    private_token: str,
    project_identifier: str,
    title: str,
    description: str,
    labels: list[str] | None = None,
) -> str:
    gl = gitlab.Gitlab(base_url, private_token=private_token)
    project = gl.projects.get(project_identifier)
    payload: dict = {"title": title, "description": description}
    if labels:
        payload["labels"] = labels
    issue = project.issues.create(payload)
    return issue.web_url
