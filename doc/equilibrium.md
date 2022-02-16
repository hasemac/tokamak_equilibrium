# 平衡計算コードの基本手順

1. $j_{t}(R, z)$を仮定する。
1. コイル電流、プラズマ電流の総和の磁束$\psi(R, z)$を計算する。
1. 最外殻磁気面を決定する。
1. 最外殻磁気面内にある各点における$j_{t}$を、$j_{t0}(i,j)$としておく。
1. 対応する点における$j_{t}$を、$dP/d\psi$と$dI^{2}/d\psi$の係数の線形結合で表し、$j_{t1}(i, j)$とする。
1. 最小二乗法でもっともらしい係数を求める。次の値を最も小さくする係数。
評価する式：

```math
error = \frac{1}{2}\sum_{(i, j)}(j_{t1}(i, j)-j_{t0}(i, j))^{2}
```
プラズマ電流密度は次の式で与えられる。

```math
j_{\psi} = 2 \pi R \frac{dP(\psi)}{d\psi}+\frac{\mu_{0}}{4 \pi R} \frac{dI^{2}(\psi)}{d\psi}
```

ただし
$P(\psi)$：プラズマ圧力
$I(\psi)$：ポロイダル電流

# 磁気面の関数について

多項式の変数を$x$として、$0 \leqq x \leqq 1$の範囲にあり、
$x = (\psi-\psi_{M})/(\psi_B-\psi_{M})$
の関係にある。
つまり$x=0$で磁気軸、$x=1$で最外殻磁気面となる。

```math
\frac{dP(\psi)}{d \psi}=\sum_{n=0}^{n_p}\alpha_{n}x^{n}- x^{n_{p}+1} \sum_{n=0}^{n_{p}}\alpha_{n}
```

```math
\frac{dI^{2}(\psi)}{d \psi}=\sum_{n=0}^{n_I}\alpha_{n}x^{n}- x^{n_{I}+1} \sum_{n=0}^{n_{I}}\alpha_{n}
```

という形であり、具体的に$n=2$の時を書き下すと、
$a_{0}+a_{1} x+a_{2}x^{2} -x^{3}(a_{0}+a_{1}+a{2})$
という形になり、$x=0$のときに$a_{0}$、$x=1$の時にゼロになる。
ただし、実際の計算の際は係数ごとにまとめて次のような式が便利だろう。
$(1-x^{3})a_{0}+(x-x^{3})a_{1}+(x^{2}-x^{3})a_{2}$
一般化すると$a_{n}$の係数は$x^{n}-x^{p}$で与えられる。

これは$dP/d\psi(=dP/dx)$、$dI^{2}/d\psi$は$\psi$で微分したものであって、実際は圧力の値などを求めたい。この時は積分操作が必要になる。
各項について積分して、かつx=1でゼロになるようにすると、それぞれの項は次の式になる。

```math
\frac{x^{n+t}-1}{n+1} - \frac{x^{p+1}-1}{p+1}
```

# 最小二乗法について

```math
E = \frac{1}{2}\sum_{i}(\sum_{j}a_{ij}x_{j}-b_{i})^{2}
```
を最小にする$x_{j}$を求める。

```math
\begin{align}
\frac{\partial E}{\partial x_{k}}
&=\sum_{i}(\sum_{j}a_{ij}x_{j}-b_{i})a_{ik}\\
&=\sum_{i,j}a_{ik}a_{ij}x_{j}-\sum_{i}a_{ik}b_{i}\\
&=0
\end{align}
```
行列の形で書きあらためると次の式を満たす$x$になる。
$A^{T}Ax=A^{T}b$
ここで、$b_{i}$は最初に仮定した$j_{t0}$の各点を想定している。
$x_{j}$は磁気面関数で表される多項式の係数を想定している。
従って、$a_{ij}x_{j}$は$i$点における$j_{t1}$を係数の線形結合で表したものになる。

# ベータ値の定義
ポロイダルベータ：

```math
\beta_{p}=\frac{<p>}{B_{\theta}^{2}(a) /2 \mu_{0}}
```


トロイダルベータ：

```math
\beta_{t}=\frac{<p>}{B_{t}^{2}/2 \mu_{0}}
```

規格化ベータ：

```math
\beta_{t}[\%] = \beta_{N} \frac{I_{p}}{a B_{t}} [MA/m.T]
```

$B_{t}$: プラズマ中心でのトロイダル磁場

$<p> $: 体積平均プラズマ圧力

$a$: プラズマ小半径


# 参考文献
Lao, L. L.; John, H. S.; Stambaugh, R.; Kellman, A. & Pfeiffer, W.; Reconstruction of current profile parameters and plasma shapes in tokamaks; Nuclear Fusion, 1985, 25, 1611
https://www.jstage.jst.go.jp/article/ieejfms/124/5/124_5_393/_pdf
https://www.jstage.jst.go.jp/article/jspf/79/2/79_2_123/_pdf