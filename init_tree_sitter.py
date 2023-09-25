from tree_sitter import Language
import os
import git
from pathlib import Path

def main():
    path = os.path.dirname(__file__)
    folder_path = os.path.join(path, "vendor")
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    repository_path = os.path.join(folder_path, "tree-sitter-python")
    if not os.path.exists(repository_path):
        git.Repo.clone_from("https://github.com/tree-sitter/tree-sitter-python", repository_path)
    repository_path = os.path.join(folder_path,"tree-sitter-java")
    if not os.path.exists(repository_path):
        git.Repo.clone_from("https://github.com/tree-sitter/tree-sitter-java", repository_path)
    repository_path = os.path.join(folder_path,"tree-sitter-cpp")
    if not os.path.exists(repository_path):
        git.Repo.clone_from("https://github.com/tree-sitter/tree-sitter-cpp", repository_path)

    Language.build_library(
    os.path.join(path, 'build/my-languages.so'),
    [
        os.path.join(path, 'vendor/tree-sitter-python'),
        os.path.join(path, 'vendor/tree-sitter-java'),
        os.path.join(path, 'vendor/tree-sitter-cpp')
    ]
    )

if __name__ == '__main__':
    main()
