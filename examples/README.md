# Examples


### Prerequisite
- We recommend `python >= 3.8.10`.
- Invoke `init_tree_sitter` (it's in the root folder): `python init_tree_sitter.py`. This should create the `build/` folder and the tree-sitter grammar file at `build/my-languages.so`. The `.so` can in fact contain multiple languages. Currently, the `init_tree_sitter` builds `Python`, `Java`, and `cpp` into the `.so`. If you wish to write generators of other languages, you will need to modify the script.


### Running

**Java/JavaNR**
(From the root folder): `python -m examples.Java.JavaNR.NR [your_java_directory] -o [your_output] --from-all=True`

The script must be run in `-m` module mode because we used relative importing. We have a simple `test.java` sitting in `JavaNR/` that you can use to test the Generator with. Note though, you must input the folder (so, `examples/Java/JavaNR`).

**Java/JavaSCHA**
(Similarily to `JavaNR`), `python -m examples.Java.JavaSCHA.SCHA [your_java_directory] -o [your_output] --from-all=True`

### Writing your own Generator
We recommend first reading the `JavaNR` example, and then the outline of the abstract classes (`Generator`, `Preprocessor`) in `src/acer.py`.