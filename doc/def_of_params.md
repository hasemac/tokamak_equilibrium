# Definition of parameters

## Decay index

```math
n = -\frac{R}{B_{z}} \frac{\partial B_{z}}{\partial R}
```

## Definitions of beta

### poloidal beta

```math
\beta_{p}=\frac{<p>}{B_{\theta}^{2}(a) /2 \mu_{0}}
```

where, 

```math
2 \pi a B_{\theta}(a) = \mu_{0} I, \pi a^{2} = S
```

$`S`$: Cross section of Plasma  
and,  

```math
B_{\theta}(a) = \frac{\mu_{0}I}{2 \sqrt{\pi S}}
```

thus, 

```math
\beta_{p} = \frac{8 \pi <p> S}{\mu_{0} I^{2}}
```

### toroidal beta

```math
\beta_{t}=\frac{<p>}{B_{t}^{2}/2 \mu_{0}}
```

### normalized beta

```math
\beta_{t}[\%] = \beta_{N} \frac{I_{p}}{a B_{t}} [MA/m.T]
```

$`B_{t}`$: Toroidal magnetic field at the center of the plasma.  
Note that it is not a vacuum magnetic field

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

```math
d\psi = (\psi_{B}- \psi_{M}) dx`$ from $`x = (\psi- \psi_{M}) / (\psi_{B}- \psi_{M})
```

Finally,

```math
q =\frac{1}{\psi_{B}- \psi_{M}}\frac{\mu_{0}}{4 \pi} \int dS \frac{1}{IR} \frac{dI^{2}}{dx}
```

## Magnetic shear and normalized pressure gradient

```math
S = \frac{\partial q}{\partial \psi}, \quad \alpha = \frac{\partial p}{\partial \psi}
```

For large aspect ratio, it can be rewritten as:

```math
S=\frac{r}{q} \frac{\partial q}{\partial r}, \quad \alpha = \frac{2 \mu_{0}Rq^{2}}{B^{2}} \frac{\partial p}{\partial r}
```

ref: <https://www.jstage.jst.go.jp/article/ieejfms/124/5/124_5_393/_pdf>

## Internal inductance

```math
l_{i} = \frac{<B_{\theta}^{2}>_{p}}{B_{\theta}(a)^{2}}
```

$`<>_{p}`$: poloidal cross section average
