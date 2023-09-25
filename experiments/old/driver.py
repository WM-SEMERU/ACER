import logging
import os, argparse, git
from pandas import DataFrame
from src.utils.general import walkDirectoryForFileNames
from src.my_enums.shared import ProgrammingLanguage
from old.Generator import Generator
from pprint import pprint
from dataclasses import dataclass

@dataclass
class Args: 
    input_path: str 
    language: str 
    output_dir: str
    log_level: str


argparser = argparse.ArgumentParser(description='interpret type of parsing')
argparser.add_argument('input_path', help="Could be the path to a file, a directory, or link to a git repository.")
argparser.add_argument('--language', required=True, help="Specify the language of the file(s) under inspection. E.g., java | python.")
argparser.add_argument('-o', '--output_dir', required=True, help="Output directory.")
argparser.add_argument('--log_level', default='warning', help='Provide logging level. Example --loglevel debug, default=warning' )

def main(args: Args): 
    logging.basicConfig(level=args.log_level.upper())
    method_dict: dict
    edge_dict: dict

    assert args.language in ProgrammingLanguage
    generator = Generator(ProgrammingLanguage.from_str(args.language))

    # BEGIN: Generate callgraph
    if os.path.isdir(args.input_path): # Directory mode
        print(f"Operating on directory {args.input_path}")
        method_dict, edge_dict = generator.generate(
            walkDirectoryForFileNames(args.input_path))
        print("Method Dict: \n")
        pprint(method_dict)
        print("Edge Dict: \n")
        pprint(edge_dict)

    elif os.path.isfile(args.input_path): # Single File moe
        print(f"Operating on the single file {args.input_path}")
        method_dict, edge_dict = generator.generate(
            [args.input_path])
        print("Method Dict: \n") 
        pprint(method_dict)
        print("Edge Dict: \n")
        pprint(edge_dict)

    else: # Assume Repository mode, where args.input_path is the link to the repo
        repo_name = args.input_path.split('/')[-1].replace('.git','')
        repo_path = os.path.join(os.path.dirname(__file__), repo_name)
        if not os.path.exists(repo_path):
            try:
                git.Repo.clone_from(args.input_path, repo_path) # type: ignore — Repo is in fact under git.
            except Exception:
                exit_with_message(f"Given repository link {args.input_path} does not exist")
        with open(".gitignore", "a") as f:
            f.write(repo_path)
        method_dict, edge_dict = generator.generate(
            walkDirectoryForFileNames(repo_path))
    # END: Generate callgraph
    
    # BEGIN: Output callgraph
    if not os.path.isdir(args.output_dir): 
        os.mkdir(args.output_dir)
    
    DataFrame({'method': map(str, method_dict.keys())}).to_csv(f'{args.output_dir + os.sep}method.csv')
    temp = [(k, callee) for k, callees in edge_dict.items() for callee in callees]
    DataFrame({"caller": [str(k) for k, _ in temp], "callee": [str(v) for _, v in temp]}).to_csv(f"{args.output_dir + os.sep}edge.csv")
    # END: Output callgraph
		
def exit_with_message(message):
    print(f"{message} Exiting...")
    exit(1)

if __name__ == "__main__":
    args = argparser.parse_args()
    main(Args(**vars(args)))