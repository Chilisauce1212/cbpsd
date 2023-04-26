import os
import fnmatch
import sys

def find_gitignore_files(path):
    gitignore_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file == '.gitignore':
                gitignore_files.append(os.path.join(root, file))
    return gitignore_files

def read_gitignore_rules(gitignore_file_path):
    with open(gitignore_file_path, 'r') as f:
        rules = f.readlines()
    return [rule.strip() for rule in rules]

def delete_files_and_dirs(path, rules):
    for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
            if file == '.gitignore':  # Skip .gitignore files
                continue
            file_path = os.path.join(root, file)
            for rule in rules:
                if rule.endswith('/'):
                    rule = os.path.join(rule, '*')
                if fnmatch.fnmatch(file_path, os.path.join(path, rule)):
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
        for directory in dirs:
            dir_path = os.path.join(root, directory)
            for rule in rules:
                # print()
                # print(f"dir_path:{dir_path}")
                # print(f"rule_path:{os.path.join(path, rule).rstrip('/')}")
                if fnmatch.fnmatch(dir_path, os.path.join(path, rule).rstrip('/')):
                    os.rmdir(dir_path)
                    print(f"Deleted directory: {dir_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: ./gitignore.py <path>")
        sys.exit(1)
    path = sys.argv[1]
    gitignore_files = find_gitignore_files(path)
    for gitignore_file in gitignore_files:
        # print(gitignore_files)
        rules = read_gitignore_rules(gitignore_file)
        gitignore_path = os.path.dirname(gitignore_file)
        delete_files_and_dirs(gitignore_path, rules)
