
# Grad-Shafranov equation

## Each components of magnetic field

```math
\begin{align*}
&B_{r}=-\frac{1}{2 \pi r}\frac{\partial \Phi}{\partial z} \\ 
&B_{\theta}=\frac{\mu_{0} I}{2 \pi r}\\
&B_{z}=\frac{1}{2 \pi r}\frac{\partial \Phi}{\partial r} 
\end{align*}
```

$`I`$: poloidal current

## Each components of $`j`$

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

## Equilibrium

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
\frac{\partial p}{\partial r}=\frac{dp}{d\Phi}\frac{\partial \Phi}{\partial r}
```

and,

```math
\frac{\partial I^{2}}{\partial r}=\frac{d I^{2}}{d \Phi} \frac{\partial \Phi}{\partial r}
```

Thus, finally,

```math
j_{\theta}=2 \pi r \frac{dp}{d\Phi}+\frac{\mu_{0}}{4 \pi r}\frac{dI^{2}}{d\Phi}
```

You can get the same equation from z-component.

The $`\theta`$-component becomes 0 = 0.  
