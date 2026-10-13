# OmpF physical slice: equations and scope

The computational observable is zero-voltage slope conductance in symmetric
monovalent salt. Finite-voltage closure-step measurements are a separate challenge.
Coordinates are nanometres; fixed charges are in units of elementary charge.

Let u = e phi/(k_B T), n_b = 0.602214076 c_M nm^-3 and
l_B,vac = e^2/(4 pi epsilon_0 k_B T), converted to nm.
The dimensionless Poisson–Boltzmann equation is

    -div(epsilon_r grad u) + 8 pi l_B,vac n_b water_mask sinh(u)
        = 4 pi l_B,vac rho_fixed.

Linearized PB replaces sinh(u) with u. This is a diagnostic approximation,
not the principal model, because the actual aqueous potentials exceed 1 kT.
Protein epsilon_r=4, membrane=2, water=78.5; temperature=298.15 K is an
assumption where the paper provides room temperature or no value.
Atomic charges are deposited by charge-conserving cloud-in-cell interpolation.
Face permittivities use harmonic averaging. Electrostatic boundary u=0 on every
box face approximates reservoirs and a distant reference potential.

Accessible ion space excludes heavy-atom van der Waals spheres expanded by
0.10 nm and the membrane slab outside explicitly placed pore apertures.
Only water components connecting both reservoirs conduct. This construction
uses a sharp voxel mask: sub-grid geometry and membrane placement are assumptions.
It does not represent lipid headgroups, LPS, hydration shells or explicit water.

For each monovalent species z=+1 or -1, equilibrium density is

    n_z = n_b exp(-z u).

In linear response the electrochemical-potential perturbation solves

    div(D_z n_z grad v_z) = 0,

with v=0,1 at the two z reservoir faces and no flux through other boundaries.
This gives the equilibrium linear-response Nernst–Planck conductance without
running a finite-voltage trajectory. The electrical conductance is

    G_z = (e^2 / (k_B T)) D_z n_b h F_z,

where F_z is the discrete summed flux of exp(-z u) grad v and h is grid spacing.
The code converts Siemens to nS explicitly. D_K=1.96e9, D_Na=1.33e9 and
D_Cl=2.03e9 nm^2/s are assumed infinite-dilution 298 K values; salt activity
and concentration-dependent diffusion are absent. A single optional common
multiplier is calibrated to WT at 1 M KCl and transferred to every mutant/condition.
Condition-normalized mutant/WT ratios are also reported; these cancel that
multiplier but are not a successful test of absolute cross-condition transfer.

Species mobilities remain constant between mutants. Ion-specific binding,
gating, protein dynamics and calcium binding are missing. Steric crowding and
dielectric reaction/self-energy are optional diagnostic extensions below. Nonlinear PB treats mobile ions as a dilute
mean-field distribution; it does not make these omissions disappear.

The geometry-only baseline sets u=0 in exactly the same transport mesh.
A charge-only Donnan cylinder uses the six constriction residues, WT charge
+2e, volume 2 nm^3, and u_D=asinh(Q/(2 n_b volume)). Its conductance scales
as D_plus exp(-u_D)+D_minus exp(u_D); all parameters are fixed before comparison.
This local charge baseline omits entrance charges and therefore does not
reproduce WT cation selectivity. The null baseline predicts the WT value.

The monomer approximation omits neighboring subunits and multiplies conductance
by three when required by the experimental reporting unit. The full trimer
check reconstructs all biological symmetry copies and solves their shared field.
Experimental mutant coordinates are reserved diagnostics, not design inputs.

Fixed-mask electrostatic and transport solves have implicit derivatives with
respect to continuous charge/coefficient inputs. This implementation does not
compute those derivatives. Voxel occupancy and discrete sequence mutation are
not differentiable; no differentiable protein-design platform is claimed.

Two diagnostic extensions test specific omissions without fitting mutant labels.
The entrance-charge Donnan baseline additionally includes the published -3e
space-charge convention, giving WT charge -1e at the same fixed 2 nm^3 volume.
It is reported alongside the local-only charge baseline, not used to select a
favorable comparison.

A lattice-gas crowding sensitivity follows
[Borukhov, Andelman and Orland (1997)](https://doi.org/10.1103/PhysRevLett.79.435).
For equal ion volume v, nu=2 n_b v and denominator d=1+nu(cosh(u)-1), replace
sinh(u) by sinh(u)/d and use n_z=n_b exp(-z u)/d. The exact Newton derivative
is ((1-nu)cosh(u)+nu)/d^2. The combined ion density is bounded by 1/v.
Diagnostic volumes 0.03 and 0.10 nm^3 bracket plausible crowding scales; they
are assumptions, not fitted ion volumes or experimentally established OmpF
parameters. The geometry probe radius stays fixed to isolate the constitutive
change. Bulk occupancy nu must remain below one. This does not include
correlations, dielectric self-energy or ion-specific hydration/binding, and
cannot be promoted to a validated design model because a sensitivity looks
better on already known labels.

The dielectric-image diagnostic computes a monovalent reaction self-energy
w(r)=0.5[ u_heterogeneous(r)-u_uniform-water(r) ] for a unit point source at r.
The two unscreened Poisson problems use identical outer zero boundaries. Lower
permittivity inclusions must give nonnegative w. Sampled energies are nearest-
interpolated and smoothed over 0.65 voxels in a prescribed channel/entrance region.
Outside that region w=0. Both spatial truncation and smoothing are approximations.

With this diagnostic the equilibrium ion densities are n_z=n_b exp(-w-z u),
so PB screening becomes exp(-w)sinh(u), and transport mobility includes exp(-w).
Protein charge and ion self-energy are distinct contributions. No extra diffusion
or mutant-specific parameter is fitted. This is an exploratory correction, not
an implementation of all ionic correlations. The implemented image model is
unscreened. A final unfitted sensitivity combines image and lattice-gas terms
consistently: t=exp(-w), d=1-nu+nu t cosh(u), densities
n_z=n_b t exp(-z u)/d, screening=t sinh(u)/d, and exact derivative
t[(1-nu)cosh(u)+nu t]/d^2. The zero-volume and zero-image limits recover the
individual models; the combined total density remains bounded by 1/v.
These combined runs use the same two assumed volumes and the saved full-trimer
image maps. They do not improve the gain-cohort error over the image-only model.

The [primary 2003 self-energy study](https://pmc.ncbi.nlm.nih.gov/articles/PMC1302945/)
warns that adding this term does not make continuum theories universally reliable.
Our planar-interface check approaches the analytic image result as the box grows,
but finite boundaries remain measurable. A CUDA float64 batched-CG backend is
checked against the same CPU Green operators; a faster solve changes no physics.


## An exact limitation of the present salt representation

Let A and B be nonnegative cation and anion geometric/field transport factors.
Because the present model uses the same equilibrium field for Na and K,
G_Na/G_K=(D_Na A+D_Cl B)/(D_K A+D_Cl B). Thus
D_Na/D_K <= G_Na/G_K <= 1, here 0.678571 <= ratio <= 1.
The bound holds for every geometry, grid, and implemented crowding/image variant.
The primary WT 1M measured ratio is 2.39/4.20=0.569048, outside this interval.
Grid refinement and a better folding model cannot change this bound while these
chemical assumptions remain fixed. This establishes a cross-salt representation
failure, not a proof that within-salt mutant/WT predictions are impossible.
A separate two-WT diagnostic fits an effective sodium diffusion and common
mobility scale; this is explicitly two calibration parameters, not a new
independently validated physical explanation.
