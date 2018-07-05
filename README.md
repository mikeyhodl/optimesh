# optimesh

[![CircleCI](https://img.shields.io/circleci/project/github/nschloe/optimesh/master.svg)](https://circleci.com/gh/nschloe/optimesh)
[![codecov](https://img.shields.io/codecov/c/github/nschloe/optimesh.svg)](https://codecov.io/gh/nschloe/optimesh)
[![Codacy grade](https://img.shields.io/codacy/grade/97175bbf62854fcfbfc1f5812ce840f7.svg)](https://app.codacy.com/app/nschloe/optimesh/dashboard)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![smooth](https://img.shields.io/badge/smooth-operator-8209ba.svg)](https://youtu.be/4TYv2PhG89A)
[![PyPi Version](https://img.shields.io/pypi/v/optimesh.svg)](https://pypi.org/project/optimesh)
[![GitHub stars](https://img.shields.io/github/stars/nschloe/optimesh.svg?logo=github&label=Stars)](https://github.com/nschloe/optimesh)

Several mesh smoothing/optimization methods with one simple interface. For now only
works for flat triangular meshes. Supports all mesh formats that
[meshio](https://github.com/nschloe/meshio) read and write.

Example call:
```
optimesh in.e out.vtk --method lloyd -n 50
```
Output:
```
Before:

           █                          min angle:      29.811                 █▃    min quality: 0.485    energy: 1.43225e-02
          ▆█ ▇ ▃                      avg angle:      60.000                 ██    avg quality: 0.919
          ██ █▃█                      max angle:     118.316                 ██    max quality: 0.999
         ▁██▆█▉█▆▅                    std dev angle:  14.039                 ██
       ▁▁█████▉███ ▃                                                       ▂ ██
       ███████▉███▇█                                                       █▇██
       ███████▉█████▆ ▇                                                   ▆████
      ▅███████▉████████▃▃                                                ██████
     ▆████████▉██████████▅▂                                           ▂ ▆██████
  ▁▃▅█████████▉████████████▆▅▃▅▅▁▁                              ▁▁▃▆▃▂█████████

Final (50 steps):

           █                   min angle:      25.830             █    min quality: 0.693    energy: 1.35054e-02
          ▅▉▇                  avg angle:      60.000             █    avg quality: 0.962
          █▉█▅                 max angle:      97.417             █    max quality: 1.000
         ██▉██                 std dev angle:   9.493             █
        ▅██▉██                                                    █
        ███▉██                                                    █
       ████▉██▇▄                                                 ▇█
      ▂████▉████▇▁                                               ██
    ▂▃█████▉██████▁ ▂                                          ▁▂██
  ▁▂███████▉███████▇█▅▁▃▃▂▁                              ▁▂▁▂▃▇████

```
The left hand-side graph shows the distribution of angles (the grid line is at the
optimal 60 degrees). The right hand-side graph shows the distribution of simplex
quality, where quality is twice the ratio of circumcircle and incircle radius.

All command-line options are viewed with
```
optimesh -h
```

#### Laplacian smoothing
![laplace](https://nschloe.github.io/optimesh/laplace.png)

Ordinary [Laplacian mesh smoothing](https://en.wikipedia.org/wiki/Laplacian_smoothing).
Fast, preserves the mesh density.
```
optimesh circle.vtk out.vtk --method laplace
```

#### ODT smoothing
![odt](https://nschloe.github.io/optimesh/odt.png)

Optimal Delaunay Triangulation (ODT) treated as a minimzation problem.
Unconditonally assumes uniform mesh density (for now) so it does _not_ preserve the mesh
density.
```
optimesh circle.vtk out.vtk --method odt
```

#### CVT/pseudo-Lloyd smoothing
![lloyd](https://nschloe.github.io/optimesh/lloyd.png)

Centroidal Voronoi tessellation smoothing, realized by [Lloyd's
algorithm](https://en.wikipedia.org/wiki/Lloyd%27s_algorithm) adapted for triangular
meshes. The central assumption here is that the topological neighhbors of any point are
also the geometrically closest points. That is fulfilled "most of the time", but the
algorithm can break down if it is not.

Unconditonally assumes uniform mesh density (for now) so it does _not_ preserve the mesh
density.
```
optimesh circle.vtk out.vtk --method lloyd
```

#### Chen-Holst smoothing

Mesh optimization after [Chen and Holst](#relevant-publications). Both methods honor the
`-u`/`--uniform-density` command line option. If not given, the mesh density is
preserved.

* ODT-like smoothing

  ![ch-odt](https://nschloe.github.io/optimesh/ch-odt.png)
  ```
  optimesh circle.vtk out.vtk --method chen-odt --uniform-density
  ```

* CPT (Centroidal Patch Triangulation, CVT-like smoothing)

  ![ch-cpt](https://nschloe.github.io/optimesh/ch-cpt.png)
  ```
  optimesh circle.vtk out.vtk --method chen-cpt --uniform-density
  ```

### Installation

optimesh is [available from the Python Package
Index](https://pypi.org/project/optimesh/), so simply do
```
pip install -U optimesh
```
to install or upgrade. Use `sudo -H` to install as root or the `--user` option
of `pip` to install in `$HOME`.

### Relevant publications

 * [Long Chen, Michael Holst, _Efficient mesh optimization schemes based on Optimal Delaunay Triangulations_,
   Comput. Methods Appl. Mech. Engrg. 200 (2011) 967–984.](https://doi.org/10.1016/j.cma.2010.11.007)


### Testing

To run the optimesh unit tests, check out this repository and type
```
pytest
```

### Distribution
To create a new release

1. bump the `__version__` number,

2. publish to PyPi and tag on GitHub:
    ```
    $ make publish
    ```

### License

optimesh is published under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).
