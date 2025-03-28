import json
import re
from pathlib import Path
from typing import Dict, List, Optional
'''
This script is used to deal with the problem that the best parameter json file and the running log are difficult to correspond.
You only need to change the path of the last line to your directory, and the script will automatically find the lowest directory, 
automatically read the unique json file and the.log file inside, and update the best parameter fold information to the json file.
'''
def parse_parameters(line: str) -> Optional[Dict]:
    """Parsing of parameters"""
    param_pattern = {
        "batch": r"batch: (.+?)\s",
        "lr": r"lr: (.+?)\s",
        "patience": r"patience: (.+?)\s",
        "dropout1": r"dropout1: (.+?)\s",
        "dropout2": r"dropout2: (.+?)\s",
        "earlystopping": r"earlystopping: (.+?)\s",
        "tsv_file": r"tsv_file: (\S+\.tsv)"
    }
    
    params = {}
    for key, pattern in param_pattern.items():
        match = re.search(pattern, line)
        if not match:
            return None
        params[key] = match.group(1).strip()
    return params

def find_closest_statistics(log_lines: List[str], param_line_num: int) -> List[str]:
    """Statistical value extraction"""
    for i in range(param_line_num, len(log_lines)):
        if "Statistic values for all folds" in log_lines[i]:
            values_str = log_lines[i].split("[")[1].split("]")[0]
            return [v.strip() for v in values_str.split(",")]
    return []

def match_string_parameters(config_params: Dict, log_params: Dict) -> bool:
    """String matching"""
    keys_to_match = ["batch", "lr", "patience", 
                    "dropout1", "dropout2", "earlystopping"]
    return all(
        config_params.get(k, "") == log_params.get(k, "")
        for k in keys_to_match
    )

def process_directory(dir_path: Path):
    try:
        json_file = next(dir_path.glob("*.json"))
        log_file = next(dir_path.glob("*.log"))
    except StopIteration:
        return

    with open(json_file, 'r+') as f:
        config = json.load(f)
        log_lines = open(log_file, 'r').readlines()
        
        param_white_list = {}
        for tsv_name, entries in config.items():
            param_white_list[tsv_name] = {
                "batch": str(entries[1]["batch_size"]),
                "lr": str(entries[1]["lr"]),
                "patience": str(entries[1]["patience"]),
                "dropout1": str(entries[1]["dropout1"]),
                "dropout2": str(entries[1]["dropout2"]),
                "earlystopping": str(entries[1]["earlystopping"])
            }
        
        matched_stats = {}
        for line_num, line in enumerate(log_lines):
            params = parse_parameters(line)
            if not params:
                continue
            
            tsv_name = params["tsv_file"]
            if tsv_name not in param_white_list:
                continue
            
            if match_string_parameters(param_white_list[tsv_name], params):
                stats = find_closest_statistics(log_lines, line_num)
                if stats:
                    matched_stats[tsv_name] = stats
        
        for tsv_name, stats in matched_stats.items():
            try:
                config[tsv_name][0] = [float(v) for v in stats]
            except ValueError:
                config[tsv_name][0] = []
        
        f.seek(0)
        json.dump(config, f, indent=4)
        f.truncate()

def main(root_dir: Path):
    for dir_path in root_dir.rglob('*'):
        if dir_path.is_dir():
            process_directory(dir_path)

if __name__ == "__main__":
    main(Path(r"Your/path/"))
