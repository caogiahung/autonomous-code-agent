import os
import anthropic
from dotenv import load_dotenv
from agent.tools import run_code_sandbox, security_scan, summarize_issue
from agent.github_client import GitHubClient

load_dotenv()

MODEL = "claude-sonnet-4-20250514"
MAX_ITERATIONS = 4


class CodeAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.github = GitHubClient()

    def _call_claude(self, messages: list, system: str) -> str:
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=system,
            messages=messages,
        )
        return response.content[0].text

    def analyze_and_fix(self, issue: dict) -> dict:
        print(f"\n🔍 Analyzing issue #{issue['number']}: {issue['title']}")

        repo_files = self.github.get_repo_structure()
        repo_overview = "\n".join(repo_files[:30])

        system_prompt = (
            "You are an autonomous coding agent. Your job is to read a GitHub issue, "
            "understand the problem, and produce a minimal, clean Python code fix. "
            "Always think step by step. Never hardcode secrets. Write secure, readable code."
        )

        conversation = [
            {
                "role": "user",
                "content": (
                    f"Here is a GitHub issue to fix:\n\n{summarize_issue(issue)}\n\n"
                    f"Repository file structure (top-level):\n{repo_overview}\n\n"
                    "Which file(s) are most relevant to this issue? "
                    "Reply with the file paths only, one per line."
                ),
            }
        ]

        relevant_files_response = self._call_claude(conversation, system_prompt)
        print(f"📁 Relevant files identified:\n{relevant_files_response}")

        file_paths = [
            line.strip()
            for line in relevant_files_response.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

        file_contents = {}
        for path in file_paths[:3]:
            content = self.github.get_file_content(path)
            file_contents[path] = content

        files_text = "\n\n".join(
            f"### {path}\n```python\n{content}\n```"
            for path, content in file_contents.items()
        )

        conversation.append({"role": "assistant", "content": relevant_files_response})
        conversation.append(
            {
                "role": "user",
                "content": (
                    f"Here are the file contents:\n\n{files_text}\n\n"
                    "Now write the fix. Output ONLY the corrected Python code block for "
                    "the most relevant file. No explanations, just code."
                ),
            }
        )

        fix_code = ""
        for iteration in range(MAX_ITERATIONS):
            print(f"\n🔄 Iteration {iteration + 1}/{MAX_ITERATIONS}")
            fix_response = self._call_claude(conversation, system_prompt)

            if "```python" in fix_response:
                fix_code = fix_response.split("```python")[1].split("```")[0].strip()
            elif "```" in fix_response:
                fix_code = fix_response.split("```")[1].split("```")[0].strip()
            else:
                fix_code = fix_response.strip()

            warnings = security_scan(fix_code)
            if warnings:
                print(f"⚠️  Security warnings: {warnings}")
                conversation.append({"role": "assistant", "content": fix_response})
                conversation.append(
                    {
                        "role": "user",
                        "content": (
                            f"Security issues found: {warnings}. "
                            "Please fix them and return only the corrected code."
                        ),
                    }
                )
                continue

            result = run_code_sandbox(fix_code)
            print(f"🧪 Sandbox result: exit_code={result['exit_code']}")

            if result["success"]:
                print("✅ Fix validated successfully.")
                break
            else:
                print(f"❌ Validation failed: {result['stderr']}")
                conversation.append({"role": "assistant", "content": fix_response})
                conversation.append(
                    {
                        "role": "user",
                        "content": (
                            f"Running the code produced this error:\n{result['stderr']}\n"
                            "Please fix the error and return only the corrected code."
                        ),
                    }
                )

        return {
            "issue_number": issue["number"],
            "issue_title": issue["title"],
            "fix_code": fix_code,
            "target_files": file_paths,
            "security_clean": len(security_scan(fix_code)) == 0,
        }

    def run(self):
        print("🚀 Autonomous Code Agent starting...\n")
        issues = self.github.get_open_issues(label="bug")

        if not issues:
            print("No open bug issues found.")
            return

        for issue in issues[:2]:
            result = self.analyze_and_fix(issue)
            print(f"\n📋 Result for issue #{result['issue_number']}:")
            print(f"   Security clean: {result['security_clean']}")
            print(f"   Target files: {result['target_files']}")
            print(f"   Fix preview:\n{result['fix_code'][:300]}...")
            print("\n" + "─" * 60)