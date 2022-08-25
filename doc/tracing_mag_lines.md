# Tracing magnetic field lines

## Runge-kutta 4th order method

Solve differential equation

```math
\frac{d \boldsymbol{x}}{dt} = \boldsymbol{f}(t, \boldsymbol{x}) \\
\boldsymbol{x}_{1} = \boldsymbol{x}_{0}+\boldsymbol{k} \quad ,when \; t_{1} = t_{0}+h
```

```math
\begin{align*}
\boldsymbol{k}&=\frac{\boldsymbol{k}_{1}+2 \boldsymbol{k}_{2}+2 \boldsymbol{k}_{3} + \boldsymbol{k}_{4}}{6}\\
\boldsymbol{k}_{1}&=h \boldsymbol{f}(t_{0}, x_{0})\\
\boldsymbol{k}_{2}&=h \boldsymbol{f}(t_{0}+h/2, x_{0}+\boldsymbol{k}_{1}/2)\\
\boldsymbol{k}_{3}&=h \boldsymbol{f}(t_{0}+h/2, x_{0}+\boldsymbol{k}_{2}/2)\\
\boldsymbol{k}_{4}&=h \boldsymbol{f}(t_{0}+h, x_{0}+\boldsymbol{k}_{3})\\
\end{align*} 
```

## Equation of tracing

```math
\frac{d \boldsymbol{x}}{ds} = \boldsymbol{b}_{0}(\boldsymbol{x})
```

$`\boldsymbol{b}_{0}`$ : unit vector of magnetic field, which doesn't depend on $`s`$.

## Representation of the magnetic field in Cartesian coordinates

![relation](tracing_mag_fig.drawio.svg)

```math
\begin{align*}
&r = \sqrt{x^{2}+y^{2}}\\
&\cos \theta = x/r\\
&\sin \theta = y/r
\end{align*}
```

```math
\begin{align*}
&Bx = Br \cos \theta - Bt \sin \theta\\
&By = Br \sin \theta + Bt \cos \theta\\
&Bz = Bz
\end{align*}
```

