## Lorentzゲージ表式

```math
\begin{align*}

&\boldsymbol{E} = -\frac{\partial \boldsymbol{A_{L}}}{\partial t}-\operatorname{grad} \phi_L\\

&\boldsymbol{B}=\operatorname{rot}\boldsymbol{A_{L}}\\

&\Bigl(\Delta-\frac{1}{c^2}\frac{\partial^{2}}{\partial t^{2}}\Bigr)\boldsymbol{A_{L}}=-\mu_{0}\boldsymbol{i}\\

&\Bigl(\Delta-\frac{1}{c^2}\frac{\partial^{2}}{\partial t^{2}}\Bigr)\phi_L=-\frac{1}{\epsilon_{0}}\rho\\

&\operatorname{div}\boldsymbol{A_{L}}+\frac{1}{c^2}\frac{\phi_L}{t}=0
\end{align*}
```

静磁場の計算式では次の２式を用いる。

$$
\begin{align*}

&\Delta\boldsymbol{A}=-\mu_{0}\boldsymbol{i}\\

&\boldsymbol{B}=\operatorname{rot}\boldsymbol{A}
\end{align*}
$$
この式を積分形式で書き直す。

$$
\begin{align*}
&\boldsymbol{A(r)}=\frac{\mu_0}{4 \pi}\int d^{3}x \frac{\boldsymbol i(x)}{|\boldsymbol{r-x}|} \\
&\boldsymbol{B(r)}=\frac{\mu_0}{4 \pi}\int d^{3}x \frac{\boldsymbol i(x) \times (\boldsymbol{r-x})}{|\boldsymbol{r-x}|^3}
\end{align*}
$$

更に線積分の形に書き直す。

$$
\begin{align*}
&\boldsymbol{A(r)}=\frac{\mu_{0}I}{4 \pi}\int d\boldsymbol{l} \frac{1}{|\boldsymbol{r-x}|} \\
&\boldsymbol{B(r)}=\frac{\mu_{0}I}{4 \pi}\int  \frac{d\boldsymbol{l} \times (\boldsymbol{r-x})}{|\boldsymbol{r-x}|^3}
\end{align*}
$$

円環電流の位置ベクトル$\boldsymbol{x}$、静磁場を計算する場所の位置ベクトルを$\boldsymbol{r}$とする。

$$
\boldsymbol{x}=\begin{pmatrix}
R \cos\theta\\
R \sin\theta\\
0
\end{pmatrix}
$$

$$
\boldsymbol{r}=\begin{pmatrix}
r\\
0\\
z
\end{pmatrix}
$$

このとき次のような関係式が成り立つ。

$$
d \boldsymbol{l}=\begin{pmatrix}
-R \sin\theta\\
R \cos\theta\\
0
\end{pmatrix}d\theta
$$

$$
d \boldsymbol{l}\times(\boldsymbol{r-x})=\begin{pmatrix}
R z \cos\theta\\
R z \sin\theta\\
R(R-r\cos\theta)
\end{pmatrix}d\theta
$$

$$
\begin{align*}
|\boldsymbol{r-x}|&=\sqrt{(r-R\cos\theta)^{2}+(0-R\sin\theta)^{2}+z^{2}}\\
&=\sqrt{r^{2}+R^{2}+z^{2}-2Rr\cos\theta}
\end{align*}
$$

これらの関係式を用いて線積分を実行する。

$$
A_y(\boldsymbol{r})=\frac{\mu_{0}I}{\pi k}\sqrt{\frac{R}{r}}\Bigl((1-\frac{k^{2}}{2})K(k^{2})-E(k^{2})\Bigr)
$$

$$
B_x(r)=\frac{\mu_{0}I}{4 \pi}\frac{z}{k\sqrt{Rr}}\Bigl(\frac{2(2-k^{2})R E(k^{2})}{d^{2}}-\frac{k^{2}K(k^2)}{r}\Bigr)

$$

$$
B_{z}(r)=\frac{\mu_{0}I}{4 \pi}\frac{k}{\sqrt{Rr}}\Bigl(K(k^{2})-\frac{(r^{2}-R^{2}+z^2)E(k^2)}{d^{2}}\Bigr)
$$
ただし、

$$
k^{2}=\frac{4 r R}{(r+R)^{2}+z^{2}}, d^{2}=(r-R)^{2}+z^{2}
$$

他の成分$A_x$、$A_z$、$B_y$はゼロ。
ここでの系は軸対象なので、円筒座標系での表記に変更して、且つコイルの位置を$Z$とすると下の式になる。

$$
A_\theta(\boldsymbol{r})=\frac{\mu_{0}I}{\pi k}\sqrt{\frac{R}{r}}\Bigl((1-\frac{k^{2}}{2})K(k^{2})-E(k^{2})\Bigr)

$$

$$
B_r(\boldsymbol{r})=\frac{\mu_{0}I}{4 \pi}\frac{z-Z}{k\sqrt{Rr}}\Bigl(\frac{2(2-k^{2})R E(k^{2})}{d^{2}}-\frac{k^{2}K(k^2)}{r}\Bigr)

$$

$$
B_{z}(\boldsymbol{r})=\frac{\mu_{0}I}{4 \pi}\frac{k}{\sqrt{Rr}}\Bigl(K(k^{2})-\frac{(r^{2}-R^{2}+(z-Z)^2)E(k^2)}{d^{2}}\Bigr)
$$
ただし、

$$
k^{2}=\frac{4 r R}{(r+R)^{2}+(z-Z)^{2}}, d^{2}=(r-R)^{2}+(z-Z)^{2}
$$

## 磁束の式
$$
\Phi=\int\boldsymbol{B}\cdot d\boldsymbol{S}=\int\operatorname{rot}\boldsymbol{A}\cdot d\boldsymbol{S}=\int \boldsymbol{A}\cdot d\boldsymbol{l}
$$
という関係が成り立つので、下の式になる。

$$
\Phi=2\pi r \times (線積分方向の\boldsymbol{A}の長さ)
$$
