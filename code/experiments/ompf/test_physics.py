"""Numerical checks of discrete laws and physical limiting cases, not mutant fits."""

from dataclasses import replace

import numpy as np
from physics import (
    AVOGADRO,
    KB,
    Config,
    E,
    deposit_charges,
    electrostatic,
    geometry,
    laplacian,
    mesh,
    neighbors,
    solve_spd,
    transport,
)


def test_charge_conservation_and_units():
    c = Config(spacing_nm=0.45, half_xy_nm=0.9, half_z_nm=0.9)
    points, shape = mesh(c)
    charges = np.array([1.0, -2.0, 0.3])
    xyz = np.array([[0.11, 0.02, 0.12], [-0.4, 0.25, -0.2], [0.2, 0.35, -0.3]])
    rho = deposit_charges(xyz, charges, points, shape, c.spacing_nm)
    assert np.isclose(rho.sum() * c.spacing_nm**3, -0.7)
    assert np.isclose(AVOGADRO / 1e24, 0.602214076)


def test_uniform_channel_ohms_law_and_conservation():
    shape = (5, 6, 11)
    n = np.prod(shape)
    left, right = neighbors(shape)
    c = Config(spacing_nm=0.2, concentration_M=0.1)
    g, stats = transport(
        np.zeros(n), np.ones(n, dtype=bool), shape, left, right, c, 1, 1.96e9
    )
    area = shape[0] * shape[1] * c.spacing_nm**2
    length = (shape[2] - 1) * c.spacing_nm
    expected = (
        E**2
        / (KB * c.temperature_K)
        * 1.96e9
        * (c.concentration_M * AVOGADRO / 1e24)
        * area
        / length
        * 1e9
    )
    assert np.isclose(g, expected, rtol=1e-8)
    assert stats["flux_plane_spread_relative"] < 1e-7
    g2, _ = transport(
        np.zeros(n),
        np.ones(n, dtype=bool),
        shape,
        left,
        right,
        replace(c, concentration_M=0.2),
        1,
        1.96e9,
    )
    assert np.isclose(g2, 2 * g)


def test_charge_sign_symmetry_and_boltzmann_limit():
    shape = (4, 4, 9)
    n = np.prod(shape)
    left, right = neighbors(shape)
    water = np.ones(n, dtype=bool)
    c = Config()
    potential = np.full(n, 0.8)
    zero, _ = transport(np.zeros(n), water, shape, left, right, c, 1, 1.0)
    plus, _ = transport(potential, water, shape, left, right, c, 1, 1.0)
    flipped, _ = transport(-potential, water, shape, left, right, c, -1, 1.0)
    assert np.isclose(plus, zero * np.exp(-0.8), rtol=1e-8)
    assert np.isclose(plus, flipped, rtol=1e-8)


def test_harmonic_dielectric_interface_series_resistance():
    left = np.arange(10)
    right = left + 1
    epsilon = np.r_[np.full(5, 2.0), np.full(6, 80.0)]
    weights = 2 * epsilon[left] * epsilon[right] / (epsilon[left] + epsilon[right])
    a = laplacian(11, left, right, weights)
    v = np.r_[np.zeros(10), 1.0]
    v[1:-1], _ = solve_spd(a[1:-1, 1:-1], -(a @ v)[1:-1], 1e-10)
    flux = weights * np.diff(v)
    assert np.allclose(flux, 1 / np.sum(1 / weights), rtol=1e-9)


def test_no_charge_zero_electrostatics_and_closed_membrane():
    c = Config(
        spacing_nm=0.45,
        half_xy_nm=0.9,
        half_z_nm=0.9,
        membrane_half_nm=0.5,
        aperture_radius_nm=0.0,
    )
    points, shape = mesh(c)
    left, right = neighbors(shape)
    data = {
        "xyz": np.array([[0.2, 0.2, 0.2]]),
        "charges": np.array([0.0]),
        "radii": np.array([0.1]),
        "heavy": np.array([True]),
    }
    eps, water = geometry(data, points, shape, c)
    assert not water.any()
    u, stats = electrostatic(
        data, points, shape, eps, np.ones(len(points), dtype=bool), left, right, c
    )
    assert np.all(u == 0)
    assert np.isclose(stats["debye_length_nm"], 0.304, rtol=0.01)


def test_manufactured_screened_poisson_convergence():
    # Analytic sin(pi*x/L) product with zero Dirichlet boundary.
    # Continuous -epsilon Laplacian(u) + screen*u is known exactly.
    errors = []
    for nodes in [9, 17, 33]:
        shape = (nodes, nodes, nodes)
        h = 2 / (nodes - 1)
        epsilon = 78.5
        kappa2 = 2.0
        axis = np.linspace(-1, 1, nodes)
        x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
        exact = (
            np.cos(np.pi * x / 2) * np.cos(np.pi * y / 2) * np.cos(np.pi * z / 2)
        ).ravel()
        left, right = neighbors(shape)
        a = laplacian(nodes**3, left, right, np.full(len(left), epsilon / h**2))
        from scipy import sparse

        a = a + sparse.eye(nodes**3) * epsilon * kappa2
        interior = np.zeros(shape, dtype=bool)
        interior[1:-1, 1:-1, 1:-1] = True
        inside = interior.ravel()
        rhs = epsilon * (3 * (np.pi / 2) ** 2 + kappa2) * exact
        result, _ = solve_spd(a[inside][:, inside].tocsr(), rhs[inside], 1e-10)
        errors.append(float(np.sqrt(np.mean((result - exact[inside]) ** 2))))
    assert errors[0] / errors[1] > 3.5
    assert errors[1] / errors[2] > 3.5


def test_positive_charge_yields_positive_potential_and_nonlinear_screening():
    c = Config(spacing_nm=0.15, half_xy_nm=0.6, half_z_nm=0.6)
    points, shape = mesh(c)
    left, right = neighbors(shape)
    data = {
        "xyz": np.array([[0.0, 0.0, 0.0]]),
        "charges": np.array([1.0]),
        "radii": np.array([0.15]),
        "heavy": np.array([True]),
    }
    eps = np.full(len(points), c.epsilon_water)
    water = np.ones(len(points), dtype=bool)
    linear, _ = electrostatic(data, points, shape, eps, water, left, right, c)
    nonlinear, stats = electrostatic(
        data,
        points,
        shape,
        eps,
        water,
        left,
        right,
        replace(c, electrostatics="nonlinear_pb"),
    )
    assert linear.max() > 0
    assert nonlinear.max() < linear.max()
    assert nonlinear.min() >= -1e-12
    assert stats["relative_residual"] < 1e-7


def test_steric_screening_derivative_and_density_bound():
    from physics import ion_density_factor, screening_response

    u = np.linspace(-8, 8, 100)
    nu = 0.12
    _f, derivative = screening_response(u, nu)
    delta = 1e-5
    finite = (
        screening_response(u + delta, nu)[0] - screening_response(u - delta, nu)[0]
    ) / (2 * delta)
    assert np.allclose(derivative, finite, rtol=1e-7, atol=1e-7)
    assert np.all(derivative > 0)
    c = Config(ion_volume_nm3=0.1)
    occupation = (
        (ion_density_factor(u, 1, c) + ion_density_factor(u, -1, c))
        * (c.concentration_M * AVOGADRO / 1e24)
        * c.ion_volume_nm3
    )
    assert np.all(occupation < 1)
    zero, _ = screening_response(u, 0.0)
    assert np.allclose(zero, np.sinh(u))


def test_gauss_law_with_screening():
    c = Config(
        spacing_nm=0.15,
        half_xy_nm=0.6,
        half_z_nm=0.6,
        electrostatics="nonlinear_pb",
        ion_volume_nm3=0.03,
    )
    points, shape = mesh(c)
    left, right = neighbors(shape)
    data = {"xyz": np.array([[0.05, 0.02, -0.03]]), "charges": np.array([0.7])}
    _u, stats = electrostatic(
        data,
        points,
        shape,
        np.full(len(points), 78.5),
        np.ones(len(points), dtype=bool),
        left,
        right,
        c,
    )
    assert stats["mobile_charge_e"] < 0
    assert stats["gauss_law_relative_error"] < 1e-7


def test_closed_transport_is_zero():
    shape = (3, 3, 5)
    left, right = neighbors(shape)
    g, stats = transport(
        np.zeros(np.prod(shape)),
        np.zeros(np.prod(shape), dtype=bool),
        shape,
        left,
        right,
        Config(),
        1,
        1.0,
    )
    assert g == 0.0
    assert stats["water_nodes"] == 0


def test_constant_image_energy_suppresses_transport():
    shape = (4, 4, 9)
    left, right = neighbors(shape)
    n = np.prod(shape)
    water = np.ones(n, dtype=bool)
    zero = np.zeros(n)
    g, _ = transport(zero, water, shape, left, right, Config(), 1, 1.0)
    corrected, _ = transport(
        zero, water, shape, left, right, Config(), 1, 1.0, self_energy=np.ones(n) * 0.7
    )
    assert np.isclose(corrected, g * np.exp(-0.7), rtol=1e-8)


def test_uniform_dielectric_has_no_image_energy():
    from reaction import sample_reaction

    c = Config(spacing_nm=0.15, half_xy_nm=0.6, half_z_nm=0.6)
    points, shape = mesh(c)
    index = np.array([len(points) // 2])
    energy, _ = sample_reaction(np.full(len(points), c.epsilon_water), shape, c, index)
    assert abs(energy[0]) < 1e-7


def test_combined_image_steric_derivative_and_packing():
    from physics import ion_density_factor, screening_response

    u = np.linspace(-9, 9, 120)
    w = np.linspace(0, 3, 120)
    nu = 0.12
    delta = 1e-5
    _f, derivative = screening_response(u, nu, w)
    finite = (
        screening_response(u + delta, nu, w)[0]
        - screening_response(u - delta, nu, w)[0]
    ) / (2 * delta)
    assert np.allclose(derivative, finite, rtol=1e-7, atol=1e-7)
    config = Config(ion_volume_nm3=0.1)
    density = config.concentration_M * AVOGADRO / 1e24
    total = density * (
        ion_density_factor(u, 1, config, w) + ion_density_factor(u, -1, config, w)
    )
    assert np.all(total * config.ion_volume_nm3 < 1)
    ordinary = ion_density_factor(u, 1, Config())
    image = ion_density_factor(u, 1, Config(), w)
    assert np.allclose(image, ordinary * np.exp(-w))
