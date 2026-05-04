import os
from github import Github
from dotenv import load_dotenv

load_dotenv()


class GitHubClient:
    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")
        repo_name = os.getenv("GITHUB_REPO")
        if not token or not repo_name:
            raise ValueError("GITHUB_TOKEN and GITHUB_REPO must be set in .env")
        self.gh = Github(token)
        self.repo = self.gh.get_repo(repo_name)

    def get_open_issues(self, label=None):
        """Fetch open issues, optionally filtered by label."""
        issues = self.repo.get_issues(state="open", labels=[label] if label else [])
        return [
            {
                "number": i.number,
                "title": i.title,
                "body": i.body or "",
                "labels": [l.name for l in i.labels],
            }
            for i in issues
        ]

    def get_file_content(self, filepath):
        """Read a file's content from the repo."""
        try:
            content = self.repo.get_contents(filepath)
            return content.decoded_content.decode("utf-8")
        except Exception as e:
            return f"Error reading file: {e}"

    def get_repo_structure(self, path=""):
        """List files/dirs in a path."""
        try:
            contents = self.repo.get_contents(path)
            return [c.path for c in contents]
        except Exception as e:
            return [f"Error: {e}"]

    def create_pull_request(self, branch_name, title, body, base="main"):
        """Open a pull request from branch_name → base."""
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=branch_name,
                base=base,
            )
            return {"url": pr.html_url, "number": pr.number}
        except Exception as e:
            return {"error": str(e)}