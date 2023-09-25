def compare_files(file1_path: str, file2_path: str):
    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
        lines_file1 = set(file1.readlines())
        lines_file2 = set(file2.readlines())

        common_lines = lines_file1.intersection(lines_file2)
        unique_file1 = list(lines_file1.difference(lines_file2))
        unique_file2 = list(lines_file2.difference(lines_file1))

        total_lines_file1 = len(lines_file1)
        total_lines_file2 = len(lines_file2)

        print("Comparison Table:")
        print("|---------------------------------------------------|")
        print("| Metric                                            | Fraction | Percentage |")
        print("|---------------------------------------------------|")
        print(f"| Lines in {file1_path} also in {file2_path} | {len(common_lines)}/{total_lines_file1}   | {len(common_lines)/total_lines_file1 * 100:.2f}%      |")
        print(f"| Lines in {file1_path} not in {file2_path} | {len(unique_file1)}/{total_lines_file1}   | {len(unique_file1)/total_lines_file1 * 100:.2f}%      |")
        print(f"| Lines in {file2_path} also in {file1_path} | {len(common_lines)}/{total_lines_file2}   | {len(common_lines)/total_lines_file2 * 100:.2f}%      |")
        print(f"| Lines in {file2_path} not in {file1_path} | {len(unique_file2)}/{total_lines_file2}   | {len(unique_file2)/total_lines_file2 * 100:.2f}%      |")
        print("|---------------------------------------------------|")

        print(f"\nFirst 10 lines in {file1_path} not in {file2_path}:")
        for line in unique_file1[:10]:
            print(line.strip())

        print(f"\nFirst 10 lines in {file2_path} not in {file1_path}:")
        for line in unique_file2[:10]:
            print(line.strip())
            
if __name__ == "__main__":
	file1_path = 'converted-wala'
	file2_path = 'evaluations/scha-jdk8-fromall-level3/pacer-results'
	compare_files(file1_path, file2_path)
