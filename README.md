ant
===

An implementation of
[Langton's Ant](https://en.wikipedia.org/wiki/Langton%27s_ant), and the
more general [turmites](https://en.wikipedia.org/wiki/Turmite).

## Examples
### Langton's Ant
```shell
uv run pyant run RL --step-limit 20000
```
![Ant RL on a square grid after 20k steps](./examples/ant-square-RL-20000.png)

### A 12 colour ant
```shell
uv run pyant run RLLRRLLLLRRR
```
![Ant RLLRRLLLLRRR on a square grid after 1 million steps](./examples/ant-square-RLLRRLLLLRRR-1000000.png)

### A 7 colour ant on a hex grid
```shell
uv run pyant run --grid hex R1R2NUR2R1L2 --step-limit 20000
```
![Ant R1R2NUR2R1L2 on a hex grid after 20k steps](./examples/ant-hex-R1R2NUR2R1L2-20000.png)

### A 14 colour ant on a triangle grid
```shell
uv run pyant run --grid triangle RLLLLLLLLLLLLL
```
![Ant RLLLLLLLLLLLLL on a triangle grid after 1 million steps](./examples/ant-triangle-RLLLLLLLLLLLLL-1000000.png)
