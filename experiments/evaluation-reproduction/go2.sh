#! /bin/bash

set -e

project_name="jdk8"
src_dir="/usr/lib/jvm/java-8-openjdk-amd64/src_temp/"

# mkdir -p evaluations/nr-$project_name
# mkdir -p evaluations/nr-$project_name-from-all
# mkdir -p evaluations/scha-$project_name-nofallback
mkdir -p evaluations/scha-$project_name-nofallback-from-all

# echo "NR"
# python -m src.new_framework.examples.JavaNR.NR $src_dir --output_path=evaluations/nr-$project_name/pacer-results
echo "NR-all"
python -m src.new_framework.examples.JavaNR.NR $src_dir --output_path=evaluations/nr-$project_name-from-all/pacer-results --from-all
# echo "SCHA"
# python -m src.new_framework.examples.JavaSCHA.SCHA $src_dir --output_path=evaluations/scha-$project_name-nofallback/pacer-results --no-fallback
echo "SCHA-all"
python -m src.new_framework.examples.JavaSCHA.SCHA $src_dir --output_path=evaluations/scha-$project_name-nofallback-from-all/pacer-results --no-fallback --from-all
