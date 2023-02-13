# Equilibrium calculation code

## Procedure of calculation

1. Assume $`j_{t}(R, z)`$.
1. Calculate the total magnetic flux $`\psi (R, z)`$ of the coil current and plasma current.
1. Determines the last closed flux surface (LCFS).
1. Represent $`j_{t}`$ at the corresponding point by a linear combination of the coefficients of $`dP/d \psi`$ and $`dI^ {2}/d \psi `$, which is $`j_{t1} (i, j)`$.
1. Find coefficients using the least squares method. The coefficients that minimizes the following values

```math
error = \frac{1}{2}\sum_{(i, j)}(j_{t1}(i, j)-j_{t0}(i, j))^{2}
```

, where $`j_{t0} (i, j)`$ is initial $`j_{t}`$ assumed firstly.

```mermaid
graph TD;
  A(Assume Jt)-->F(Calculate total flux);
  F-->D(Determin LCFS);
  D-->J(Represent jt by the coefficients);
  J-->E(Find coefficients to minimize error);
  E-->C{small error?};
  C-->|Yes|G(End)
  C-->|No|N(Calculate new jt with coefficients);  
  N-->F;
```

The plasma current density is given by the following equation.

```math
j_{\psi} = 2 \pi R \frac{dP(\psi)}{d\psi}+\frac{\mu_{0}}{4 \pi R} \frac{dI^{2}(\psi)}{d\psi}
```

$`P(\psi)`$：Plasma pressure

$`I(\psi)`$：Poloidal current, **including toroidal coil current**.

## Functions in the magnetic surface

Let $`x`$ be the variable of the polynomial, and $`x = (\psi- \psi_{M}) / (\psi_{B}- \psi_{M})`$.

$`x =0,\quad when\quad\psi = \psi_{M}`$: magnetic axis

$`x =1,\quad when\quad\psi = \psi_{B} `$: boundary

$` 0 \leqq x \leqq 1`$

The $`dP/d\psi`$ and $`dI^{2}/d\psi`$ are approximated by functions of $`x`$ as shown in the equations below.

```math
\frac{dP}{d \psi}(x)=\sum_{n=0}^{n_p}a_{n}x^{n}- x^{n_{p}+1} \sum_{n=0}^{n_{p}}a_{n}
```

```math
\frac{dI^{2}}{d \psi}(x)=\sum_{n=0}^{n_I}b_{n}x^{n}- x^{n_{I}+1} \sum_{n=0}^{n_{I}}b_{n}
```

Specifically, write down when $`n=2`$.

$`a_{0}+a_{1} x+a_{2}x^{2} -x^{3}(a_{0}+a_{1}+a{2})`$

$`=(1-x^{3})a_{0}+(x-x^{3})a_{1}+(x^{2}-x^{3})a_{2}`$

Thus, the coefficient for $`a_{n}`$ is given by $`x^{n}-x^{p}`$.  
The values ​​of these functions at the magnetic axis and the boundary are as follows.

```math
\frac{dP}{d \psi}(x)= 
\left \{ \begin{array}{ll}
a_{0}&x=0 \;(axis)\\
0&x=1 \; (boudary)
\end{array} \right.
```

```math
\frac{dI^{2}}{d \psi}(x)= 
\left \{ \begin{array}{ll}
b_{0}&x=0 \;(axis)\\
0&x=1 \; (boudary)
\end{array} \right.
```

This is a differentiated formula and actually needs to be integrated to calculate pressure and the like.

Integrating each term and setting it to zero at x = 1, each term becomes the following equation.

```math
\frac{x^{n+t}-1}{n+1} - \frac{x^{p+1}-1}{p+1}
```

Note that a coefficient is applied when integrating by $`\psi`$.

```math
P(\psi)=\int d \psi \frac{dP}{d \psi}(x)=(\psi_{B}- \psi_{M}) \int dx \: (\sum_{n=0}^{n_p}\alpha_{n}x^{n}- x^{n_{p}+1} \sum_{n=0}^{n_{p}}\alpha_{n})
```

```math
\because d \psi = (\psi_{B}- \psi_{M}) \: dx
```

## The least squares method

$j_{0i}$ : Initial current profile  
$j_{1i}$ : New current profile with coefficiencies

```math
j_{1i} = \sum_{j}f_{ij}a_{j}
```

$a_{j}$ : coefficiencies of polynominal function $dp/d\psi$,  $dI^{2}/d\psi$
, which should be determined with the least square method.  
$f_{ij}$ :  values calculated from normalized flux.

```math
E = \frac{1}{2}\sum_{i}(j_{1i}-j_{0i})^{2}
```

```math
E = \frac{1}{2}\sum_{i}(\sum_{j}f_{ij}a_{j}-j_{0i})^{2}
```

Find $a_{j}$ to minimize $E$ with the least mean square method.

```math
\begin{align}
\frac{\partial E}{\partial a_{k}}
&=\sum_{i}(\sum_{j}f_{ij}a_{j}-b_{i})f_{ik}\\
&=\sum_{i,j}f_{ik}f_{ij}a_{j}-\sum_{i}f_{ik}j_{0i}\\
&=0
\end{align}
```

If you rewrite it in the form of a matrix, the $\boldsymbol{a}$ satisfies the following equation.

```math
F^{T}F\boldsymbol{a}=F^{T}\boldsymbol{j}_{0}
```

## Evaluation of error

There are several ways to evaluate errors.

1. Calculate the average of the original current densities.
1. Find the maximum difference between the new current density and the original current density.
1. When the ratio is less than a given value, the convergence occurs and the equilibrium calculation stops.

Expressed in Python, it becomes the following formula.

```python
error = np.max(np.abs(j0-j))/np.average(np.abs(j))
```

j0: New current density profile  
j: Original current density profile

## Handling of poloidal current

Poloidal currents include those derived from plasma and those derived from toroidal coils.  
The poloidal current in the equilibrium code also includ those derived from toroidal coils.  
Here, we represent the integral of $`dI^{2}/d\psi`$ as $`K(x)`$, and  K is adjusted so that $`K(x)=0`$ at $`x=1`$ (boundary). Thus,  

```math
I^{2}(x)=K(x)+I_{0}^{2}
```

$`I_{0}`$ : Derived from toroidal coil current  

$`I^{2}(x)`$ should be positive in the interval where x is from 0 (axis) to 1 (boundary).

```math
I(x) = 
\left \{ \begin{array}{ll}
+\sqrt{K(x)+I_{0}^{2}} &(I_{0}>0)\\
-\sqrt{K(x)+I_{0}^{2}} &(I_{0}<0)
\end{array} \right.
```

## Reference

- L.L. Lao, H.S. John, R.D. Stambaugh, A.G. Kellman, W. Pfeiffer, Reconstruction of current profile parameters and plasma shapes in tokamaks, Nucl. Fusion. 25 (1985) 1611. <https://doi.org/10.1088/0029-5515/25/11/007>.

- <https://www.jstage.jst.go.jp/article/ieejfms/124/5/124_5_393/_pdf>

- <https://www.jstage.jst.go.jp/article/jspf/79/2/79_2_123/_pdf>

- <http://www.jspf.or.jp/Journal/PDF_JSPF/jspf2003_02/jspf2003_02-121.pdf>
