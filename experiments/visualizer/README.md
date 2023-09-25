## Callgraph Visualizer

**First**, run the `index.html` file to start the tool. Since it's just a single `html` file, you can just open the file up in chrome. If this module were to have additional source files, use a simple static page run tool like [http-server](https://github.com/http-party/http-server).


**Then**, upload your edge `csv` to visualize it. Your upload must conform to the following — 

- Have two columns: `caller` and `callee`,
- `caller` and `callee` are stringified representations of methods

For an example of a valid `csv` file to visualize, see [test_edges.csv](./test_edges.csv). The example generators in [TODO] also outputs edges in this format.




![demo](./demo.mp4)