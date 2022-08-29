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


----- Wrong description from here -----

Poloidal currents include those derived from plasma and those derived from toroidal coils. The process of expressing the poloidal current as a polynomial of x means that I in the equilibrium calculation code does not include those derived from the toroidal coil.  
Namely, 
$`I(x)=0`$ at x=1 (boundary).  
If plasma current is positive, poloidal current is also positive, and vice versa. Thus,

```math
I(x) = 
\left \{ \begin{array}{ll}
+\sqrt{I^{2}(x)} &(I_{p}>0)\\
-\sqrt{I^{2}(x)} &(I_{p}<0)
\end{array} \right.
```

Total poloidal currents is denoted as below.

```math
I_{total} = I(x) + I_{0}
```

$`I_{0}`$ : Derived from toroidal coil current  

```math
\frac{d I_{total}^{2}}{d \psi} = \frac{dI^{2}}{d \psi}(x)+2I_{0}\frac{dI(x)}{d \psi}
```

The second term of right hand side can be transformed as below.

```math
\frac{dI(x)}{d \psi}
= \pm \frac{1}{2} \frac{dI^{2}/d \psi}{\sqrt{I^{2}(x)}}
=\frac{1}{2} \frac{1}{I(x)} \frac{d I^{2}}{d \psi}
```

Thus,  

```math
\frac{d I_{total}^{2}}{d \psi} = \frac{dI^{2}}{d \psi}(x)
+I_{0} \left \{ \frac{d I^{2}}{d \psi}/I(x)) \right \}
```

When $`x \rightarrow 1`$, $`dI^{2}/d \psi \rightarrow 0`$ and $`I(x) \rightarrow 0`$.  
However, the 2nd term of right hand side has a value in limit of $`x \rightarrow 1`$.  
 For example, the l'Hôpital's rule can be used to calculate the value.  

----- Wrong description so far -----
## The least squares method

```math
E = \frac{1}{2}\sum_{i}(\sum_{j}a_{ij}x_{j}-b_{i})^{2}
```

Find $`x`$ that minimizes $`E`$.

```math
\begin{align}
\frac{\partial E}{\partial x_{k}}
&=\sum_{i}(\sum_{j}a_{ij}x_{j}-b_{i})a_{ik}\\
&=\sum_{i,j}a_{ik}a_{ij}x_{j}-\sum_{i}a_{ik}b_{i}\\
&=0
\end{align}
```

If you rewrite it in the form of a matrix, it becomes $`x`$ that satisfies the following equation.

```math
A^{T}Ax=A^{T}b
```

Here, $`b_{i}`$ assumes each point of $`j_{t0}`$. And, $`x_{j}`$ assumes the coefficient of the polynomial represented by the magnetic surface function.
Therefore, $`a_{ij} x_{j}`$ is a linear combination of coefficients of $`j_{t1}`$ at the $`i`$ point.

## Grad-Shafranov equation

### Each components of magnetic field

```math
\begin{align*}
&B_{r}=-\frac{1}{2 \pi r}\frac{\partial \Phi}{\partial z} \\ 
&B_{\theta}=\frac{\mu_{0} I}{2 \pi r}\\
&B_{z}=\frac{1}{2 \pi r}\frac{\partial \Phi}{\partial r} 
\end{align*}
```

$`I`$: poloidal current

### Each components of $`j`$

```math
\begin{align*}
&j_{r}=-\frac{1}{\mu_{0}}\frac{\partial B_{\theta}}{\partial z}\\
&j_{\theta}=\frac{1}{\mu_{0}}(\frac{\partial B_{r}}{\partial z}-\frac{\partial B_{z}}{\partial r})\\
&j_{z}=\frac{1}{\mu_{0}}\frac{1}{r}\frac{\partial (r B_{\theta})}{\partial r}
\end{align*}
```

```math
\because \mu_0 j= \operatorname{rot} \boldsymbol{B}
=-\frac{\partial B_{\theta}}{\partial z} e_{r}+(\frac{\partial B_{r}}{\partial z}-\frac{\partial B_{z}}{\partial r}) e_{\theta}+\frac{1}{r}\frac{\partial (r B_{\theta})}{\partial r} e_{z}\\
```

,where $`\space \partial/\partial \theta=0`$

### Equilibrium

r component of$`\boldsymbol{j}\times\boldsymbol{B}=\nabla p`$ is

```math
j_{\theta}B_{z}-j_{z}B_{\theta}=\frac{\partial p}{\partial r}
```

, where

```math
\begin{align*}
j_{z}B_{\theta} &= 
\frac{1}{\mu_{0}}\frac{1}{r}\frac{\partial (r B_{\theta})}{\partial r} B_{\theta}\\
&=\frac{1}{\mu_{0}}\frac{1}{r^{2}}\frac{\partial (r B_{\theta})}{\partial r} (r B_{\theta})\\
&=\frac{1}{2 \mu_{0}}\frac{1}{r^{2}}\frac{\partial (r B_{\theta})^{2}}{\partial r} \\
&=\frac{\mu_{0}}{8 \pi^{2}}\frac{1}{r^{2}}\frac{\partial I^{2}}{\partial r}
\end{align*}
```

Thus,

```math
j_{\theta}\frac{1}{2 \pi r}\frac{\partial \Phi}{\partial r}-\frac{\mu_{0}}{8 \pi^{2}}\frac{1}{r^{2}}\frac{\partial I^{2}}{\partial r}=\frac{\partial p}{\partial r}
```

Notice,

```math
\frac{\partial p}{\partial r}=\frac{dP}{d\Phi}\frac{\partial \Phi}{\partial r}
```

and,

```math
\frac{\partial I^{2}}{\partial r}=\frac{d I^{2}}{d \Phi} \frac{\partial \Phi}{\partial r}
```

Thus, finally,

```math
j_{\theta}=2 \pi r \frac{dP}{d\Phi}+\frac{\mu_{0}}{4 \pi r}\frac{dI^{2}}{d\Phi}
```

You can get the same equation from z-component.

The $`\theta`$-component becomes 0 = 0.

## Definitions of beta

poloidal beta：

```math
\beta_{p}=\frac{<p>}{B_{\theta}^{2}(a) /2 \mu_{0}}
```

$`\theta`$

toroidal beta：

```math
\beta_{t}=\frac{<p>}{B_{t}^{2}/2 \mu_{0}}
```

$`\theta`$

normalized beta：

```math
\beta_{t}[\%] = \beta_{N} \frac{I_{p}}{a B_{t}} [MA/m.T]
```

$`B_{t}`$: Toroidal magnetic field at the center of the plasma

$`<p>`$: volume averaged pressure

$`a`$: minor radius

## Safety factor

```math
q = \frac{d\phi}{d\psi}
```

$`\phi`$: toroidal flux , $`\psi`$: poloidal flux

The toroidal flux can be given by the following equation.

```math
\phi=\int B_{\phi}dS=\int dS\frac{\mu_{0}I}{2 \pi R }
```

```math
2 \pi R B_{\phi}=\mu_{0}I
```

Integration area is inside of flux surfaces. Thus, the $`\phi (x)`$ and its derivative function can be calculated numerically. And, the safety factor can be calculated as below.

```math
q = \frac{d\phi}{d\psi}=\frac{1}{\psi_{B}- \psi_{M}}\frac{d \phi (x)}{dx}
```

In other,

```math
\begin{align}
q = \frac{d\phi}{d\psi}
&=\frac{\mu_{0}}{2 \pi} \int dS \frac{1}{R} \frac{dI}{d\psi}\\
&=\frac{\mu_{0}}{4 \pi} \int dS \frac{1}{IR} \frac{dI^{2}}{d\psi}
\end{align}
```

Because,

```math
\frac{dI}{d\psi}=\frac{1}{2 I}\frac{dI^{2}}{d\psi}
```

$`d\psi = (\psi_{B}- \psi_{M}) dx`$ from $`x = (\psi- \psi_{M}) / (\psi_{B}- \psi_{M})`$.

Finally,

```math
q =\frac{1}{\psi_{B}- \psi_{M}}\frac{\mu_{0}}{4 \pi} \int dS \frac{1}{IR} \frac{dI^{2}}{dx}
```

## Reference

Lao, L. L.; John, H. S.; Stambaugh, R.; Kellman, A. & Pfeiffer, W.; Reconstruction of current profile parameters and plasma shapes in tokamaks; Nuclear Fusion, 1985, 25, 1611

<https://www.jstage.jst.go.jp/article/ieejfms/124/5/124_5_393/_pdf>

<https://www.jstage.jst.go.jp/article/jspf/79/2/79_2_123/_pdf>

<http://www.jspf.or.jp/Journal/PDF_JSPF/jspf2003_02/jspf2003_02-121.pdf>
