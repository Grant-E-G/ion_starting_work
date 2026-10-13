# Reduced membrane-function objectives and gradients

October 13, 2026. Proposed modeling scaffold, not a validated protein-function predictor. Literature context: [physics-model assessment](../notes/physics_based_membrane_function.md).

## One-dimensional steady permeation

Let z range from 0 to L. Let rho(z) be the linear ion density, D(z)>0 a diffusion coefficient, and W(z;theta) a potential of mean force including the applied electrical energy and any consistent geometric entropy convention. Under a dilute, overdamped, single-coordinate approximation,

\[
J=-D(z)\left[\partial_z\rho+\beta\rho\partial_z W\right],\qquad \beta=(k_BT)^{-1}.
\]

For fixed boundary densities, integrating the stationary equation gives

\[
J(\theta)=\frac{\rho(0)e^{\beta W(0;\theta)}-\rho(L)e^{\beta W(L;\theta)}}{\int_0^L e^{\beta W(z;\theta)}D(z;\theta)^{-1}\,dz},\qquad I=qJ.
\]

J has units of particles/time because rho is particles/length. Boundary densities must be mapped consistently from bath concentrations and pore cross-section. Variable area can be folded into an entropic potential with corresponding boundary conventions; it must not be silently omitted.

This provides differentiable dependence on discretized W and positive D. A constant shift of W cancels and cannot be treated as a design improvement. Lowering a single barrier is not automatically sufficient: binding wells, entry density and friction matter. Stable exponential quadrature and positive-parameter representations are required numerically.

This model does not capture correlated multi-ion knock-on, an unreliable reaction coordinate, or changing protein states. Accurate gradients through this formula do not prove accurate permeation predictions or supply the upstream sequence-to-W/D map.

## Implicit electrodiffusion sensitivities

For a discretized steady PDE with residual R(u,theta)=0, let the objective be O(u,theta). If the boundary-constrained Jacobian R_u is invertible,

\[
\frac{du}{d\theta}=-R_u^{-1}R_\theta.
\]

An adjoint lambda solving R_u^T lambda=O_u^T yields

\[
\frac{dO}{d\theta}=O_\theta-\lambda^T R_\theta.
\]

This is our mathematical route for differentiating a suitable PNP/reduced transport solve, not evidence that a particular published channel solver exposes these derivatives or predicts mutants. Discontinuous remeshing, hard molecular boundaries, nonunique solutions and missing correlations require separate treatment.

## Equilibrium observable gradients

For a fixed-topology canonical distribution proportional to exp[-beta U_theta(x)] and observable A_theta(x),

\[
\partial_\theta\langle A\rangle=\langle\partial_\theta A\rangle-\beta\operatorname{Cov}(A,\partial_\theta U).
\]

The identity motivates equilibrium reweighting and free-energy derivatives without differentiating a whole trajectory. Reference samples must cover the perturbed ensemble. It does not by itself give a derivative of a transport coefficient or transition rate. For mutation alchemy, shared/dual topology and proper dummy-atom/end-state treatment are necessary.

## State populations and kinetics

With two equilibrium states and DeltaG=G_open-G_closed,

\[
P_{open}=\frac{1}{1+e^{\beta\Delta G}},\qquad \partial_\theta P_{open}=-\beta P_{open}(1-P_{open})\partial_\theta\Delta G.
\]

This equilibrium formula must not be applied unmodified to a driven photocycle. For state probabilities p and a continuous-time generator Q(theta,stimulus),

\[
\dot p=Q^T p,\qquad I(t)=N\sum_s p_s(t)i_s(V,\theta).
\]

ODE sensitivities differentiate the stimulus-to-current model. Protein sequence does not automatically specify Q. Barrier energies alone do not determine absolute rates without prefactors and a defensible reaction-coordinate/dynamical model. State-dependent detailed balance must be applied only where thermodynamically appropriate, accounting for driving.

## Design objective and validation

Use a phenotype-specific objective, for example expected desired-ion flux subject to unintended leakage/selectivity and protein-viability constraints. Distinguish simulation calibration parameters from allowed protein design variables. Candidate gain must exceed uncertainty due to sampling and physical-model assumptions; penalizing uncertainty is a decision rule, not a substitute for validation.

Gradients over physical parameters can guide where to perturb. Discrete mutation proposals still require actual end-state structures, correct topology/chemistry, new sampling and independent functional evaluation. Compare that proposal mechanism with enumeration or a simple heuristic at the same evaluation budget.
