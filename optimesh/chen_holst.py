# -*- coding: utf-8 -*-
#
"""
From

Long Chen, Michael Holst,
Efficient mesh optimization schemes based on Optimal Delaunay
Triangulations,
Comput. Methods Appl. Mech. Engrg. 200 (2011) 967–984,
<https://doi.org/10.1016/j.cma.2010.11.007>.
"""
import numpy
import fastfunc
from meshplex import MeshTri

from .helpers import print_stats, energy


def odt(*args, **kwargs):
    """Optimal Delaunay Triangulation.

    Idea:
    Move interior mesh points into the weighted averages of the circumcenters
    of their adjacent cells. If a triangle cell switches orientation in the
    process, don't move quite so far.
    """

    def get_reference_points(mesh):
        cc = mesh.get_cell_circumcenters()
        bc = mesh.get_cell_barycenters()
        # Find all cells with a boundary edge
        boundary_cell_ids = mesh._edges_cells[1][:, 0]
        cc[boundary_cell_ids] = bc[boundary_cell_ids]
        return cc

    return _run(get_reference_points, *args, **kwargs)


def cpt(*args, **kwargs):
    """Centroidal Patch Triangulation. Mimics the definition of Centroidal
    Voronoi Tessellations for which the generator and centroid of each Voronoi
    region coincide.

    Idea:
    Move interior mesh points into the weighted averages of the centroids
    (barycenters) of their adjacent cells. If a triangle cell switches
    orientation in the process, don't move quite so far.
    """
    return _run(lambda mesh: mesh.get_centroids(), *args, **kwargs)


def _run(
    get_reference_points_,
    X,
    cells,
    tol,
    max_num_steps,
    verbosity=1,
    step_filename_format=None,
    uniform_density=False,
):
    if X.shape[1] == 3:
        # create flat mesh
        assert numpy.all(abs(X[:, 2]) < 1.0e-15)
        X = X[:, :2]

    mesh = MeshTri(X, cells, flat_cell_correction=None)
    mesh.flip_until_delaunay()

    if step_filename_format:
        mesh.save(
            step_filename_format.format(0), show_centroids=False, show_coedges=False
        )

    if verbosity > 0:
        print("Before:")
        extra_cols = [
            "energy: {:.5e}".format(energy(mesh, uniform_density=uniform_density))
        ]
        print_stats(mesh, extra_cols=extra_cols)

    mesh.mark_boundary()

    k = 0
    while True:
        k += 1

        rp = get_reference_points_(mesh)
        if uniform_density:
            scaled_rp = (rp.T * mesh.cell_volumes).T

            weighted_rp_average = numpy.zeros(mesh.node_coords.shape)
            for i in mesh.cells["nodes"].T:
                fastfunc.add.at(weighted_rp_average, i, scaled_rp)

            omega = numpy.zeros(len(mesh.node_coords))
            for i in mesh.cells["nodes"].T:
                fastfunc.add.at(omega, i, mesh.cell_volumes)

            new_points = (weighted_rp_average.T / omega).T
        else:
            # Estimate the density as 1/|tau|. This leads to some simplifcations: The
            # new point is simply the average of of the reference points
            # (barycenters/cirumcenters) in the star.
            rp_average = numpy.zeros(mesh.node_coords.shape)
            for i in mesh.cells["nodes"].T:
                fastfunc.add.at(rp_average, i, rp)

            omega = numpy.zeros(len(mesh.node_coords))
            for i in mesh.cells["nodes"].T:
                fastfunc.add.at(omega, i, numpy.ones(i.shape, dtype=float))

            new_points = (rp_average.T / omega).T

        original_orient = mesh.get_signed_tri_areas() > 0.0
        original_coords = mesh.node_coords.copy()

        # Step unless the orientation of any cell changes.
        alpha = 1.0
        while True:
            xnew = (1 - alpha) * original_coords + alpha * new_points
            # Preserve boundary nodes
            xnew[mesh.is_boundary_node] = original_coords[mesh.is_boundary_node]
            mesh.update_node_coordinates(xnew)
            new_orient = mesh.get_signed_tri_areas() > 0.0
            if numpy.all(original_orient == new_orient):
                break
            alpha /= 2

        mesh.flip_until_delaunay()

        if step_filename_format:
            mesh.save(
                step_filename_format.format(k), show_centroids=False, show_coedges=False
            )

        # Abort the loop if the update is small
        diff = mesh.node_coords - original_coords
        if numpy.all(numpy.einsum("ij,ij->i", diff, diff) < tol ** 2):
            break

        if k >= max_num_steps:
            break

        if verbosity > 1:
            print("\nstep {}:".format(k))
            print_stats(mesh)

    if verbosity > 0:
        print("\nFinal ({} steps):".format(k))
        extra_cols = [
            "energy: {:.5e}".format(energy(mesh, uniform_density=uniform_density))
        ]
        print_stats(mesh, extra_cols=extra_cols)
        print()

    return mesh.node_coords, mesh.cells["nodes"]
