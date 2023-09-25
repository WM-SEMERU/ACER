#! /bin/bash

set -e


project_name="argouml"
src_dir="/home/andrewchen/Downloads/argouml/argouml"
prev_res="evaluations/Calls_filter_OnlyProject_standarized.tsv"

# echo "Run this from root of this project" 
# mkdir -p evaluations/nr-$project_name
# mkdir -p evaluations/nr-$project_name-from-all
# mkdir -p evaluations/scha-$project_name-nofallback
# mkdir -p evaluations/scha-$project_name-nofallback-from-all


# python -m src.new_framework.examples.JavaNR.NR $src_dir --output_path=evaluations/nr-$project_name/pacer-results
# python -m src.new_framework.examples.JavaNR.NR $src_dir --output_path=evaluations/nr-$project_name-from-all/pacer-results --from-all
# python -m src.new_framework.examples.JavaSCHA.SCHA $src_dir --output_path=evaluations/scha-$project_name-nofallback/pacer-results --no-fallback
# python -m src.new_framework.examples.JavaSCHA.SCHA $src_dir --output_path=evaluations/scha-$project_name-nofallback-from-all/pacer-results --no-fallback --from-all


# python evaluations/merge.py --base_tsv=$prev_res --pacer_results_path=evaluations/nr-$project_name/pacer-results --output_path=evaluations/nr-$project_name/calls.tsv
# python evaluations/merge.py --base_tsv=$prev_res --pacer_results_path=evaluations/nr-$project_name-from-all/pacer-results --output_path=evaluations/nr-$project_name-from-all/calls.tsv
# python evaluations/merge.py --base_tsv=$prev_res --pacer_results_path=evaluations/scha-$project_name-nofallback/pacer-results --output_path=evaluations/scha-$project_name-nofallback/calls.tsv
# python evaluations/merge.py --base_tsv=$prev_res --pacer_results_path=evaluations/scha-$project_name-nofallback-from-all/pacer-results --output_path=evaluations/scha-$project_name-nofallback-from-all/calls.tsv

# python evaluations/merge.py --base_tsv=$prev_res --pacer_results_path=evaluations/nr-$project_name/pacer-results --output_path=evaluations/stash/calls.tsv -t PACER-NR -n 8

# echo "yo1"
# python evaluations/merge.py --base_tsv=evaluations/stash/calls_special.tsv --pacer_results_path=evaluations/nr-$project_name-from-all/pacer-results --output_path=evaluations/stash/calls.tsv -t PACER-NR-ALL -n 9
# echo "yo2"

# python evaluations/merge.py --base_tsv=evaluations/stash/calls_2.tsv --pacer_results_path=evaluations/scha-$project_name-nofallback/pacer-results --output_path=evaluations/stash/calls_3.tsv -t PACER-SCHA -n 10
# echo "yo3"


# python evaluations/merge.py --base_tsv=evaluations/stash/calls_3.tsv --pacer_results_path=evaluations/scha-$project_name-nofallback-from-all/pacer-results --output_path=evaluations/stash/calls_5.tsv -t PACER-SCHA-ALL -n 11



echo "Make tables"

# python evaluations/table.py --base_tsv=evaluations/nr-$project_name/calls.tsv --output_path=evaluations/nr-$project_name/table.csv
# python evaluations/table.py --base_tsv=evaluations/nr-$project_name-from-all/calls.tsv --output_path=evaluations/nr-$project_name-from-all/table.csv
# python evaluations/table.py --base_tsv=evaluations/scha-$project_name-nofallback/calls.tsv --output_path=evaluations/scha-$project_name-nofallback/table.csv
# python evaluations/table.py --base_tsv=evaluations/scha-$project_name-nofallback-from-all/calls.tsv --output_path=evaluations/scha-$project_name-nofallback-from-all/table.csv



python evaluations/table.py --base_tsv=evaluations/stash/calls_5.tsv --output_path=evaluations/stash/table.csv