# The equation for the magnetic field of 

## Maxwell's equations

```math
\begin{align*}
&\operatorname{div} \boldsymbol{D}=\rho\\

&\operatorname{div} \boldsymbol{B}=0\\

&\operatorname{rot} \boldsymbol{E} = -\frac{\partial \boldsymbol{B}}{\partial t}\\

&\operatorname{rot} \boldsymbol{H}=\boldsymbol{j}+ \frac{\partial \boldsymbol{D}}{\partial t}\\

\end{align*}
```

, where

```math
\begin{align*}
&\boldsymbol{D}=\epsilon_{0}\boldsymbol{E}+\boldsymbol{P}\\

&\boldsymbol{B}=\mu_{0}\boldsymbol{H}+\boldsymbol{M}\\

\end{align*}
```

## Lorentz gauge condition

```math
\begin{align*}

&\boldsymbol{E} = -\frac{\partial \boldsymbol{A_{L}}}{\partial t}-\operatorname{grad} \phi_L\\

&\boldsymbol{B}=\operatorname{rot}\boldsymbol{A_{L}}\\

&\Bigl(\Delta-\frac{1}{c^2}\frac{\partial^{2}}{\partial t^{2}}\Bigr)\boldsymbol{A_{L}}=-\mu_{0}\boldsymbol{i}\\

&\Bigl(\Delta-\frac{1}{c^2}\frac{\partial^{2}}{\partial t^{2}}\Bigr)\phi_L=-\frac{1}{\epsilon_{0}}\rho\\

&\operatorname{div}\boldsymbol{A_{L}}+\frac{1}{c^2}\frac{\partial \phi_L}{\partial t}=0
\end{align*}
```

The following two formulas are used in the calculation of the static magnetic field.

```math
\begin{align*}

&\Delta\boldsymbol{A}=-\mu_{0}\boldsymbol{i}\\

&\boldsymbol{B}=\operatorname{rot}\boldsymbol{A}
\end{align*}
```

Rewrite these equations in integral form.

```math
\begin{align*}
&\boldsymbol{A(r)}=\frac{\mu_0}{4 \pi}\int d^{3}x \frac{\boldsymbol i(x)}{|\boldsymbol{r-x}|} \\
&\boldsymbol{B(r)}=\frac{\mu_0}{4 \pi}\int d^{3}x \frac{\boldsymbol i(x) \times (\boldsymbol{r-x})}{|\boldsymbol{r-x}|^3}
\end{align*}
```

Further rewrite it in the form of a line integral.

```math
\begin{align*}
&\boldsymbol{A(r)}=\frac{\mu_{0}I}{4 \pi}\int d\boldsymbol{l} \frac{1}{|\boldsymbol{r-x}|} \\
&\boldsymbol{B(r)}=\frac{\mu_{0}I}{4 \pi}\int  \frac{d\boldsymbol{l} \times (\boldsymbol{r-x})}{|\boldsymbol{r-x}|^3}
\end{align*}
```

Let the ring current position vector $`\boldsymbol{x}`$ and the position vector $`\boldsymbol{r}`$ to calculate the static magnetic field .  

```math
\boldsymbol{x}=\begin{pmatrix}
R \cos\theta\\
R \sin\theta\\
0
\end{pmatrix}
```

```math
\boldsymbol{r}=\begin{pmatrix}
r\\
0\\
z
\end{pmatrix}
```

At this time, the following equation holds.

```math
d \boldsymbol{l}=\begin{pmatrix}
-R \sin\theta\\
R \cos\theta\\
0
\end{pmatrix}d\theta
```

```math
d \boldsymbol{l}\times(\boldsymbol{r-x})=\begin{pmatrix}
R z \cos\theta\\
R z \sin\theta\\
R(R-r\cos\theta)
\end{pmatrix}d\theta
```

```math
\begin{align*}
|\boldsymbol{r-x}|&=\sqrt{(r-R\cos\theta)^{2}+(0-R\sin\theta)^{2}+z^{2}}\\
&=\sqrt{r^{2}+R^{2}+z^{2}-2Rr\cos\theta}
\end{align*}
```

Perform line integrals using these relations.

```math
A_y(\boldsymbol{r})=\frac{\mu_{0}I}{\pi \sqrt{k}}\sqrt{\frac{R}{r}}\Bigl((1-\frac{k}{2})K(k)-E(k)\Bigr)
```

```math
B_x(r)=\frac{\mu_{0}I}{4 \pi}\frac{z}{\sqrt{k}\sqrt{Rr}}\Bigl(\frac{2(2-k)R E(k)}{d^{2}}-\frac{k K(k)}{r}\Bigr)

```

```math
B_{z}(r)=\frac{\mu_{0}I}{4 \pi}\frac{\sqrt{k}}{\sqrt{Rr}}\Bigl(K(k)-\frac{(r^{2}-R^{2}+z^2)E(k)}{d^{2}}\Bigr)
```

definitions:

```math
k=\frac{4 r R}{(r+R)^{2}+z^{2}}, d^{2}=(r-R)^{2}+z^{2}
```

Other components $`A_x`$, $`A_z`$, $`B_y`$ are zero.

Since the system here is an axisymmetric system, if the notation is changed to the cylindrical coordinate system and the coil position is $`Z`$, the following formulas are obtained.

```math
A_\theta(\boldsymbol{r})=\frac{\mu_{0}I}{\pi \sqrt{k}}\sqrt{\frac{R}{r}}\Bigl((1-\frac{k}{2})K(k)-E(k)\Bigr)

```

```math
B_r(\boldsymbol{r})=\frac{\mu_{0}I}{4 \pi}\frac{z-Z}{\sqrt{k}\sqrt{Rr}}\Bigl(\frac{2(2-k)R E(k)}{d^{2}}-\frac{k K(k)}{r}\Bigr)

```

```math
B_{z}(\boldsymbol{r})=\frac{\mu_{0}I}{4 \pi}\frac{\sqrt{k}}{\sqrt{Rr}}\Bigl(K(k)-\frac{(r^{2}-R^{2}+(z-Z)^2)E(k)}{d^{2}}\Bigr)
```

definitions:

```math
k=\frac{4 r R}{(r+R)^{2}+(z-Z)^{2}}, d^{2}=(r-R)^{2}+(z-Z)^{2}
```

## Magnetic flux

```math
\Phi=\int\boldsymbol{B}\cdot d\boldsymbol{S}=\int\operatorname{rot}\boldsymbol{A}\cdot d\boldsymbol{S}=\int \boldsymbol{A}\cdot d\boldsymbol{l}
```

Thus, the following formula is obtained.

```math
\Phi=2\pi r \times A_\theta(\boldsymbol{r})
```

## Vector operator with cylindrical coordinates

```math
\nabla \times \boldsymbol{A} = 
\bigl(\frac{1}{r} \frac{\partial A_{z}}{\partial \theta} -\frac{\partial A_{\theta}}{\partial z}\bigr) \boldsymbol{e_{r}}

+\bigl(\frac{\partial A_{r}}{\partial z} -\frac{\partial A_z}{\partial r}\bigr) \boldsymbol{e_{\theta}}

+\frac{1}{r}\bigl(\frac{\partial (r A_{\theta})}{\partial r} -\frac{\partial A_{r}}{\partial \theta}\bigr) \boldsymbol{e_{z}}

```

$`A_{r} = A_{z}=0`$, if $`A`$ is vector potential of axisymetric circuler coils.

```math
\begin{align*}
\boldsymbol{B} = \nabla \times \boldsymbol{A} &= 
 -\frac{\partial A_{\theta}}{\partial z} \boldsymbol{e_{r}}

+\frac{1}{r} \frac{\partial (r A_{\theta})}{\partial r}  \boldsymbol{e_{z}}\\

&=-\frac{1}{2 \pi r}\frac{\partial \Phi}{\partial z} \boldsymbol{e_{r}} 
+ \frac{1}{2 \pi r}\frac{\partial \Phi}{\partial r} \boldsymbol{e_{z}}
\end{align*}
```
