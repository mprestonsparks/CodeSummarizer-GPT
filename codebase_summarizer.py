import os
from pathlib import Path
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
from dotenv import load_dotenv

load_dotenv()
CODEBASE_PATH = os.getenv("CODEBASE_PATH")

if not os.path.exists('summaries'):
    os.makedirs('summaries')

class CodebaseSummarizer:
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        self.summary = []
        self.ignore_patterns = []
        self.read_gitignore()
        self.read_ignore()
        self.ignore_spec = PathSpec.from_lines(GitWildMatchPattern, self.ignore_patterns)

    def read_gitignore(self):
        gitignore_path = self.directory / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                self.ignore_patterns.extend(f.read().splitlines())

    def read_ignore(self):
        ignore_path = Path(__file__).resolve().parent / ".ignore"
        print(f"Reading from .ignore file at: {ignore_path}")  # <-- This is the print statement
        if ignore_path.exists():
            with open(ignore_path, "r") as f:
                self.ignore_patterns.extend(f.read().splitlines())



    def read_codebase(self):
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                full_file_path = os.path.join(root, file)
                if self.ignore_spec.match_file(full_file_path):
                    continue
                relative_path = os.path.relpath(full_file_path, start=os.path.dirname(self.directory))
                self.summary.append(relative_path)

    def create_tree(self):
        tree = {}
        for file_path in self.summary:
            parts = file_path.split(os.sep)
            node = tree
            for part in parts:
                node = node.setdefault(part, {})
        return tree

    def print_tree(self, tree, prefix="", index=""):
        lines = []
        for i, key in enumerate(sorted(tree.keys()), start=1):
            new_index = f"{index}.{i}" if index else str(i)
            is_dir = isinstance(tree[key], dict)
            lines.append(f"{prefix}{'|_ ' if prefix else '- '}{key}{os.sep if is_dir else ''} ({new_index})")
            if is_dir:
                lines.extend(self.print_tree(tree[key], prefix=prefix+"  ", index=new_index))
        return lines

    def write_summary(self):
        tree = self.create_tree()
        lines = self.print_tree(tree)
        with open('summaries/codebase-summary.txt', "w") as f:
            f.write("This is a directory tree of the codebase, each item has a unique numbering scheme:\n")
            f.write("- Directories are indicated by a trailing slash and have format (x) or (x.y)\n")
            f.write("- Files are located inside directories and have format (x.y.z)\n")
            f.write("\n")
            for line in lines:
                f.write(f"{line}\n")

def main():
    summarizer = CodebaseSummarizer(CODEBASE_PATH)
    summarizer.read_codebase()
    summarizer.write_summary()

if __name__ == "__main__":
    main()
