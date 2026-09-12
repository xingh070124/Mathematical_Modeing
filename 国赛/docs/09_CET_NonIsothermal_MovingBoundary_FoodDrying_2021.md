193
A publication of
CHEMICAL ENGINEERING TRANSACTIONS
V OL. 87, 2021 The Italian Association
of Chemical Engineering
Online at www.cetjournal.it
Guest Editors: Laura Piazza, Mauro Moresi, Francesco Donsì
Copyright © 2021, AIDIC Servizi S.r.l.
DOI: 10.3303/CET2187033
ISBN 978-88-95608-85-3; ISSN 2283-9216
Non-Isothermal Moving-Boundary Model for Food Drying
Antonio Brasiello *, Claudia Venditti, Alessandra Adrover
D ipartimento di Ingegneria Chimica Materiali Ambiente, Università degli Studi di Roma “La Sapienza”, via Eudossiana 18
00184 Roma, Italy
a ntonio.brasiello@uniroma1.it
Mathematical modeling of food drying represents a key research topic. Drying is one of the most used
processes in food technology. It is a complex process in which water concentration changes are very often
associated with volume and structural variations of materials. This phenomenon, known as shrinkage, limits
the possibility of using classical transport models to obtain reliable results for drying process analysis and
control. Drying is intrinsically a non-isothermal process, even when it is performed under “isothermal”
conditions, meaning when the air temperature in the drying chamber is kept constant. Indeed, thermal inertial
of food samples, as well as thermal effects due to water evaporation at the sample boundary, must be
necessarily taken into account for a deep understanding of the process and a reliable estimate of the effective
water diffusivity. Moreover, in many practical applications, food drying takes place in non-isothermal
conditions. The isothermal moving-boundary model for food dehydration and shrinkage, recently proposed by
Adrover et al. (2019b,c), is here improved to account for thermal effects. A convection-diffusion heat transport
equation, accounting for heat transfer, water evaporation, and shrinkage at the sample surface, is added to
the convection-diffusion water transport equation. Experimental dehydration curves, in continuous and
intermittent conditions, are accurately predicted by the model with an effective water diffusivity (cid:1830) (cid:4666)(cid:1846))
eff
d epending exclusively on the local temperature. The non-isothermal model is successfully applied to
e xperimental data of continuous and intermittent drying of Guava slices, reported by Chua et al. 2000a.

1.Introduction
Food drying processes are often carried out in non-isothermal conditions. In the case of natural drying, for
example, temperature strongly depends on the environmental conditions of the production sites (climate, day-
night temperature range, and seasonal variations). In some cases, natural drying ensures added value to the
final products from the point of view of organoleptic properties deeply influenced by the specific production
area. In many other cases, natural drying is chosen only for its economic advantage. In such cases, the main
drawback stands in being the characteristics of the final products highly heterogeneous.
Intermittent drying is a technical solution providing the advantage of increasing drying efficiency and product
quality, assuring uniform characteristics, through the suitable choice of the optimal temperature and humidity
profiles during the process. Moreover, several literature papers (see Yang et al., 2013 and reference therein)
highlight the possibility of reducing color degradation through intermittent drying.
The possibility of optimizing process conduction is directly connected to the availability of theoretical models
that provide the technical tools for the process evolution analysis as conditions vary.
Mathematical model development in this field is not an easy task due to the complexity of the materials
involved. During drying, foods undergo structural and volume variations not predictable with the classic
mathematical models (diffusive models based on Fick's law of diffusion). The phenomenon is known as
shrinkage. Two approaches are available in literature: in the first, based on mechanical equations for
deformable bodies, shrinkage is taken into account through constitutive equations for stress-deformation
tensor, depending on the internal structure of the material and process variables (as in the model of Curcio
and Aversa (2014) or the pore-mechanical model of Dhall and Datta (2011)); the second approach, borrowed
from polymer science (Papanu et al., 1989; Tu and Ouano, 1977), is the moving-boundary model developed
by Adrover et al. (2019b). In this case, shrinkage is taken into account through a suitable parameter,
describing the point-wise shrinkage velocity evolution as a function of the local water content gradient. Adrover
Paper Received: 2 September 2020; Revised: 19 March 2021; Accepted: 5 April 2021
Please cite this article as: Brasiello A., Venditti C., Adrover A., 2021, Non-isothermal Moving-boundary Model for Food Drying, Chemical
Engineering Transactions, 87, 193-198 DOI:10.3303/CET2187033

194
et al. (2019c) have shown that such a parameter can be easily derived from the experimental diagram of
volume vs. total water content evolution of drying sample. The moving-boundary model has been recently
extended to account for non-isothermal effects, see Adrover et al., 2020. Thermal effects are modeled through
the introduction of a convection-diffusion heat transport equation, accounting for sample shrinkage, heat
transfer, and water evaporation at the sample surface. When the spatio-temporal evolution of the temperature
field is properly accounted for, the experimental dehydration curves, in continuous and intermittent conditions,
can be accurately predicted by the moving-boundary model with an effective water diffusivity (cid:1830) (cid:4666)(cid:1846))
eff
depending exclusively on the local temperature.
In this paper, the non-isothermal model is applied to a case of non-isothermal drying available in literature
(Chua et al, 2000a,b). The interesting papers by Chua et al. (2000a,b) report a set of experimental data of
continuous and intermittent drying of Guava slices in which air temperature and relative humidity vary
cyclically in a climatic chamber. Guavas are characterized by high initial moisture content and exhibit a large
ideal shrinkage. The model, applied to continuous dehydration experiments, allows for a reliable estimate of
the effective water diffusivity, which is the only unknown parameter that enters the non-isothermal model. All
the other parameters have been estimated from independent measurements (e.g. water adsorption isotherms)
and reliable correlations for heat and mass transfer coefficients. The model is subsequently successfully
applied, in a fully predictive way, to capture all the salient features of the intermittent drying experiments,
highlighting the importance of accounting for thermal inertial of the food sample as well as thermal effects of
water evaporation at the sample boundary for a correct description of the drying process.
2.Drying experiments
Experimental data of continuous and intermittent dehydration of Guava fruit (Psidium Guajava) are taken from
the paper of Chua et al., 2000a. Guava samples were dried in a two-stage heat pump dryer in which the
drying chamber temperature and humidity profiles are imposed through PID controllers. Fresh guava fruits
were skinned, peeled, and cut to obtain square slices with thickness (cid:1834) =3 mm and side (cid:1838) =30mm. Guava
(cid:2868) (cid:2868)
slices were then placed in a single layer on the dryer’s tray. Details about the experimental setup can be found
in the original papers of Chua et al., 2000a,b. Two types of drying experiments were considered: continuous
(C), in which the air temperature and humidity were kept constant, and intermittent (I) in which square wave
(period 60 min) temperature profiles where imposed, corresponding to square wave humidity profiles, since
the air humidity and velocity were held constant at Ω=0.0089 kg/kg and (cid:1847) =2.5 m/s, respectively. The
(cid:2998)
operating temperature and humidity for continuous experiments C25, C30 and C40 as well as the maximum
and minimum values of temperature and humidity for the three intermittent experiments I25, I30, I40 are
summarized in Table 1.
Table 1: Continuous and intermittent experiments.
Type T∞ RH∞
C25 25°C 43.2
C30 30°C 32.5
C40 40°C 19.8
I25 30°C - 20°C 31.8 - 65.1
I30 35°C - 25°C 24.8 - 47.9
I40 40°C - 30°C 18.9 - 33.5
3.Mathematical model
The moving-boundary model developed in Adrover et al., 2020 for non-isothermal drying consists of a system
of two advection-diffusion partial differential equations for mass and energy transport, coupled with an
equation for the boundary evolution, the material being assumed homogeneous and isotropic.
In the one-dimensional formulation that can be adopted for Guava slices (heat and mass transport along the
thickness coordinate −H /2≤x≤H /2), the transport equations for the water content (cid:1855) (cid:4666)(cid:1876),(cid:1872)) [g water/m(cid:2871)]
(cid:2868) (cid:2868) (cid:3050)
and the sample temperature (cid:1846)(cid:4666)(cid:1876),(cid:1872)) read as:
(1)
(2)

195
Where ρ(cid:3043) is the sample density, (cid:1829)(cid:3043) the specific heat at constant pressure, (cid:1863)(cid:3043) the thermal conductivity and
(cid:3043)
(cid:1830) (cid:4666)(cid:1846)) the effective water diffusivity. The velocity (cid:1874) (cid:4666)(cid:1876),(cid:1872)) is the point-wise shrinkage velocity
eff (cid:3046)
(3)
affecting both the heat and mass transport equations and controlling the temporal evolution of the sample
surface (cid:1876) (cid:4666)(cid:1872)). The shrinkage proportionality factor α(cid:4666)(cid:1855) ), entering the shrinkage velocity and depending on
(cid:3029) (cid:3050)
the point-wise water content (cid:1855) (cid:4666)(cid:1876),(cid:1872)), is the fingerprint of the specific food material under investigation. The
(cid:3050)
simplest case is that of a constant shrinkage factor, α(cid:4666)(cid:1855) )=α . Specifically, α =0 represents the case of a
(cid:3050) (cid:2868) (cid:2868)
rigid solid (no shrinkage), while (cid:2009) =1 represents the case of ideal shrinkage, in which volume reduction
(cid:2868)
corresponds exactly to the volume of water flowing outside the sample.
The two transport equations (1) and (2) are linked together and must be solved simultaneously by further
enforcing the symmetry boundary conditions at and the mixed boundary conditions at (cid:1876) (cid:4666)(cid:1872)) also referred
(cid:3029)
to as Robin or “evaporative” or third order boundary condition (da Silva et al., 2015)
(4)
(5)
where (cid:1839) is the water molecular weight, (cid:1868) (cid:4666)(cid:1846)) the saturated vapor pressure at temperature (cid:1846), ℎ and ℎ are
(cid:3050) (cid:3049) (cid:3040) (cid:3021)
the mass and heat transport coefficients, (cid:1844)(cid:1834) and (cid:1846) the relative humidity and the temperature at the sample
(cid:3029) (cid:3029)
boundary (cid:1876) (cid:4666)(cid:1872)), (cid:1844)(cid:1834) and (cid:1846) the air relative humidity and the temperature in the drying chamber.
(cid:3029) (cid:2998) (cid:2998)
The boundary condition (5) takes into account both heat transfer resistance and heat subtracted for water
evaporation at the air/sample interface (Carslaw and Jaeger, 1959), λ (cid:4666)(cid:1846) ) being the heat of water
(cid:3049) (cid:3029)
evaporation evaluated at (cid:1846) .
(cid:3029)
The heat and mass transfer coefficients ℎ and ℎ can be evaluated from well-known correlation functions for
(cid:3040) (cid:3021)
the Sherwood ((cid:1845)ℎ) and Nusselt ((cid:1840)(cid:1873)) numbers, specific for the sample geometry (slab) under investigation,
(6)
(7)
with all the physical parameters of the wet air evaluated at the average film temperature (cid:1846) =(cid:4666)(cid:1846) +(cid:1846) )/2.
av (cid:2998) (cid:3029)
All the physical parameters of the food sample, namely (cid:2025)(cid:3043), (cid:1829)(cid:3043), and (cid:1863)(cid:3043), are functions of the local water
(cid:3043)
concentration (cid:1855) . Specifically, the sample density (cid:2025)(cid:3043) is evaluated as the average of the water and solid (pulp)
(cid:3050)
densities, averaged with respect to their volume fractions ρ(cid:3043)=ρ(cid:3050) ϕ +ρ(cid:3046)(cid:4666)1−ϕ ), with ρ(cid:3020) ≃1.5 g/cm(cid:2871) for
(cid:3050) (cid:3050)
carbohydrates. The product heat capacity (cid:1829)(cid:3043) is evaluated as the average of the water and solid specific heat
(cid:3043)
capacity (cid:1829)(cid:3043)=(cid:1829)(cid:3050) (cid:1876) +(cid:1829)(cid:3020) (cid:4666)1−(cid:1876) ), averaged with respect to their weight fractions (cid:1876) =ϕ (cid:4666)ρ(cid:3050)/ρ(cid:3043)). The
(cid:3043) (cid:3043) (cid:3050) (cid:3043) (cid:3050) (cid:3050) (cid:3050)
sample thermal conductivity (cid:1863)(cid:3043) is evaluated from a parallel model 1/(cid:1863)(cid:3043) =ϕ /(cid:1863)(cid:3050)+(cid:4666)1−ϕ )/(cid:1863)(cid:3020) where (cid:1863)(cid:3050)
(cid:3050) (cid:3050)
and (cid:1863)(cid:3020) are the water and solid thermal conductivities, respectively. Since Guava fruits contain mainly water
and carbohydrate (Rahman et al., 1997), the thermal conductivity (cid:1863)(cid:3020) and the specific heat capacity (cid:1829)(cid:3020) of the
(cid:3043)
solid are estimated from that of carbohydrate (Becker and Fricke, 2003)
(cid:1863)(cid:3046)[W/((cid:4666)m K)]=2.01×10(cid:2879)(cid:2869)+1.39×10(cid:2879)(cid:2871)(cid:1846)−4.33×10(cid:2879)(cid:2874)(cid:1846)(cid:2870) , (cid:1846)[(cid:3042)(cid:1829)] (8)
(cid:1829)(cid:3046)[J/((cid:4666)g K)]=1.5488+1.9625×10(cid:2879)(cid:2871)(cid:1846)−5.9399×10(cid:2879)(cid:2874)(cid:1846)(cid:2870) , (cid:1846)[(cid:3042)(cid:1829)] (9)
(cid:3043)
The relative humidity at the air/sample interface (cid:1844)(cid:1834) evolves in time because both (cid:1855) (cid:4666)(cid:1876) ) and (cid:1846) change
(cid:3029) (cid:3050) (cid:3029) (cid:3029)
during the course of the dehydration process. The relationship (cid:1844)(cid:1834) =(cid:1858)(cid:4666)(cid:1846) ,(cid:1855) ) can be estimated from water
(cid:3029) (cid:3029) (cid:3050)
vapor adsorption isotherms of Guava reported from (Hubinger et al., 1992). Adsorption isotherms in the range
[25(cid:3042)(cid:1829),50(cid:3042)(cid:1829)] are almost independent of temperature and well fitted ((cid:1844)(cid:2870)=0.999) with the modified Anderson
model (Guinè, 2009) relating the equilibrium relative humidity (cid:1844)(cid:1834) to the equilibrium moisture content (cid:1850)
(cid:3032)(cid:3044) (cid:3032)(cid:3044)
(10)

A latter observation regarding the shrinkage proportionality factor α(cid:4666)(cid:1855) ) adopted for Guava fruits: Guavas, as
(cid:3050)
pears and carrots, are characterized by very high-water content (cid:1876) ∈(cid:4666)80%,82%) [g water/g product] (USDA,
(cid:3050)
2020). All fruits with high initial moisture content exhibit an almost ideal shrinkage, that implies α(cid:4666)(cid:1855) )=α =1
(cid:3050) (cid:2868)
and (cid:1848) /(cid:1848) ≃1−ϕ (cid:4666)0), (cid:1848) being the asymptotic sample volume at the end of the dehydration process and
(cid:2998) (cid:2868) (cid:3050) (cid:2998)
the initial water volume fraction, supposed uniform within the sample. For a slice sample with aspect
ratio (cid:1827)(cid:1844)=(cid:1838) /(cid:1834) =10, shrinkage affects all the three slice dimensions, even if the most affected is the slice
(cid:2868) (cid:2868)
thickness, and the asymptotic rescaled slice thickness (cid:1834) /(cid:1834) can be approximately related to the asymptotic
(cid:2998) (cid:2868)
volume ratio (cid:1848) /(cid:1848) by the relation (Adrover et al., 2019a)
(cid:2998) (cid:2868)
(11)
This implies that an asymptotic thickness reduction (cid:1834) /(cid:1834) ≃1/3 corresponds to an asymptotic volume
(cid:2998) (cid:2868)
reduction (cid:1848) /(cid:1848) ≃0.2. Therefore, in a one-dimensional model of the drying process in which only thickness
(cid:2998) (cid:2868)
reduction is accounted for, it is necessary to introduce a constant shrinkage factor α ≃0.83<1 to guarantee
(cid:2868)
(cid:1834) /(cid:1834) ≃1/3, corresponding to the ideal volume shrinkage, and therefore to have a correct estimate of the
(cid:2998) (cid:2868)
diffusional lengths along the principal transport/shrinkage direction.
4.Results and discussion
The only parameter, entering the non-isothermal model, that needs to be estimated is the effective water
diffusivity (cid:1830) (cid:4666)(cid:1846)) and its dependence on temperature (cid:1846). (cid:1830) (cid:4666)(cid:1846)) can be estimated from continuous dehydration
eff eff
curves C25, C30 and C40, reported in Figure 1A, showing the temporal decay of the moisture content (cid:1850)(cid:4666)(cid:1872))
[kg w/kg dry basis] rescaled onto the initial moisture content (cid:1850) , for the three temperatures (cid:1846) =25,30,40(cid:3042)(cid:1829).
(cid:2868) (cid:2998)
1
A
0.8
0.6
0.4
0.2
0
0 50 100 150 200 250 300 350
Figure 1. A) Rescaled moisture ratio vs time for the three continuous drying experiments at T=25, 30, 40°C.
Continuous lines represent model predictions with the effective water diffusion coefficient (cid:1830) (cid:4666)(cid:1846)) reported in
eff
Figure B.
Continuous lines in Figure 1A represent best-fit non-isothermal model curves obtained with the best-fitted
Arrhenius-type curve for the effective water diffusivity (cid:1830) (cid:4666)(cid:1846))
eff
(cid:1830) (cid:4666)(cid:1846)) [m(cid:2870)/s]=(cid:1830) exp(cid:4666)−(cid:1831)/(cid:1844)(cid:1846)) (cid:1830) =exp(cid:4666)14.63) [m(cid:2870)/s] (cid:1831)/(cid:1844)=11095[(cid:1837)] (12)
eff (cid:2868) (cid:2868)
reported in figure 1B. It can be observed that the estimated effective water diffusivity is highly sensitive to
temperature as it exhibits a significant increase with temperature (Table 2.). These values of the water
diffusivity are in agreement with those of other vegetables and fruits with high initial moisture ratio, although
it has to be pointed out that a one-dimensional model, like the one adopted, tends to overestimate the effective
diffusivity (Adrover et al., 2019a).
Table 2: Estimated effective water diffusivity D .
eff
T [°C] D [m2/s]
eff
25 1.557x10-10
30 2.877x10-10
40 9.258x10-10
X/)t(X 0
18
16 B
14
12
C25 10
C30
C40 8
6
4
2
0
20 25 30 35 40 45
t [min]
2
01
]s/
m[
01
x
D
ffe
196
o T C

197
The estimate of (cid:1830) (cid:4666)(cid:1846)) from continuous drying experiments permits to verify the potentialities of the non-
eff
isothermal model by comparing experimental intermittent dehydration curves I25, I30 and I40 with model
predictions (with no adjustable parameters) as shown in Figure 2.
|  1  |     | I25 |     |     |     |
| --- | --- | --- | --- | --- | --- |
I30
I40
 0.8
0  0.6
X/)t(X
 0.4
 0.2
 0
|  0  60 |  120  180 |  240  300 |  360 |     |     |
| ------ | --------- | --------- | ---- | --- | --- |
t [min]
Figure 2: Model predictions of the three intermittent experiments (square wave, (cid:1986)(cid:1846)=10(cid:3042)(cid:1829), time period 60
min). Arrow indicates increasing values of the average processing temperature ( 25,30,40(cid:3042)(cid:1829), respectively).
It can be clearly observed the excellent capability of the model to follow accurately the step changes in the
operating air and relative humidity conditions, by perfectly reproducing the periodic sudden changes in the
slope of the curve for the rescaled moisture content (cid:1850)(cid:4666)(cid:1872))/(cid:1850) . The model allows us to estimate the spatio-
(cid:2868)
temporal evolution of all the basic quantities controlling the drying process. As an instance, Figure 3A-D show
the time-behavior of the rescaled slab thickness (A), temperature (B) and relative humidity (C) at the
air/sample interface as well as the heat and mass transfer coefficients (D) for the case I25. In Figure 3B it can
be observed that the boundary temperature exhibits a sudden decrease at the beginning of the drying process
induced by water surface evaporation. Moreover, the Guava slice has a significant thermal inertia so that the
boundary temperature needs at least five periods to follow closely the square-wave air temperature.
 1
|     |     | A   |  30 |     |     |
| --- | --- | --- | --- | --- | --- |
 0.8
 25
Co
0  0.6
| H/)t(H |     |     | T ,Co b |     |     |
| ------ | --- | --- | ------- | --- | --- |
 20
|  0.4 |     |     | ∞T  |     |     |
| ---- | --- | --- | --- | --- | --- |
|  0.2 |     |     |  15 |     |     |
|      |     |     | B   | T b |     |
T∞
|  0     |                |           |  10         |                |           |
| ------ | -------------- | --------- | ----------- | -------------- | --------- |
|  0  60 |  120  180 240 |  300 360 |  0  60      |  120  180 240 |  300 360 |
|        | t [min]        |           |             | t [min]        |           |
|  100   |                |           |  36         |                |           |
|        |                | C         | ])K 2m(/W[  |                |           |
 35.5
 80
 35
%
| HR ,% ∞HR b  60 |     |     |  34.5 |     |     |
| --------------- | --- | --- | ----- | --- | --- |
h
|     |     |     | h ,]s/m[ 301x T | m   |     |
| --- | --- | --- | --------------- | --- | --- |
|     |     |     |  34             | h   |     |
T
|  40 |     |     |  33.5 |     |     |
| --- | --- | --- | ----- | --- | --- |
 33
 20
|        | RH             |           |  32.5  |                |           |
| ------ | -------------- | --------- | ------ | -------------- | --------- |
|        | b              |           |        |                |           |
|        | RH∞            |           | h      |                |           |
|  0     |                |           |  32    |                |           |
|  0  60 |  120  180 240 |  300 360 |  0  60 |  120 180 240  |  300 360 |
|        | t[min]         |           |        | t [min]        |           |
Figure 3. Model predictions of the I25 intermittent experiment (square wave, time period 60 min).

198
A similar observation can be done for the boundary relative humidity (see Figure 3C). Specifically, it can be
observed that partial rehydration of the sample may occur when the moisture content is low. These effects are
extremely important and must be accounted for when degradation kinetics of nutrients and vitamins are
investigated. In this context, a reliable estimate of the internal sample temperature is extremely useful to
optimize intermittent dehydration protocols to obtain low water activity while keeping significant amounts of
vitamins, e.g. ascorbic acid.
Conclusions
The one-dimensional non-isothermal formulation of the moving-boundary model for food dehydration, recently
proposed by Adrover et al. (2019 b,c) is here applied for the case of Guava slices. The model accounts for
sample shrinkage via the introduction of the pointwise shrinkage velocity dependent on the local volumetric
water flux. A suitable convection-diffusion heat transport equation, affected by sample shrinkage, heat
transfer, and water evaporation at the sample surface, is added to the convection-diffusion transport equation
for water concentration. The advantage of the model lies in the possibility of obtaining reliable data without
huge experimental efforts. The excellent predictive capability of the non-isothermal model makes it a useful
tool for non-isothermal process optimization and control at both laboratory and industrial scales.
References
Adrover A., Brasiello A., 2019a, A Moving Boundary Model for Isothermal Drying and Shrinkage of Chayote
Discoid Samples: Comparison between the Fully Analytical and the Shortcut Numerical Approaches,
International Journal of Chemical Engineering, 2019, 3926897.
Adrover A., Brasiello A., Ponso G., 2019b, A moving boundary model for food isothermal drying and
shrinkage: General setting, Journal of Food Engineering, 244, 178-191.
Adrover A., Brasiello A., Ponso G., 2019c, A moving boundary model for food isothermal drying and
shrinkage: A shortcut numerical method for estimating the shrinkage factor, Journal of Food Engineering,
244, 212-219.
Adrover A., Venditti C., Brasiello A., 2020, A Non-Isothermal Moving-Boundary Model for Continuous and
Intermittent Drying of Pears, Foods, 9, 1577.
Becker B., Fricke B., 2003, Freezing Principles. In Encyclopedia of Food Sciences and Nutrition, 2nd ed.;
Caballero, B., Ed.; Academic Press, Oxford, UK, 2706–2711.
Carslaw H., Jaeger J., 1959, Conduction of Heat in Solids, Oxford University Press, Oxford, UK.
Chua K.J., Mujumdar A.S., Chou S.K., Hawlander M.N.A., Ho J.C., 2000b, Convective drying of banana,
guava and potato pieces: effect of cyclical variations of air temperature on drying kinetics and color
change, 18, 907-936.
Chua K.J., Chou S.K., Ho J.C., Mujumdar A.S., Hawlander M.N.A., 2000a, Cyclic air temperature drying of
guava pieces: effects on moisture and ascorbic acid content, Trans IChemE, 78, 72-78.
Curcio S., Aversa M., 2014, Influence of shrinkage on convective drying of fresh vegetables: A theoretical
model, Journal of Food Engineering, 123, 36-49.
da Silva W.P., Rodrigues A.F., e Silva C.M.D.P.S., de Castro D.S., Gomes J.P., 2015, Comparison between
continuous and intermittent drying of whole bananas using empirical and diffusion models to describe the
processes, Journal of Food Engineering, 166, 230-236.
Dhall A., Datta A., 2011, Transport in deformable food materials: A poromechanics approach, Chemical
Engineering Science, 66, 6482-6497.
Guiné R.P.F., 2009, Sorption isotherms of pears using different models, International Journal of fruit science,
9, 11–22.
Hubinger M., Menegalli F.C., Aguerre R.J., Suarez C., 1992, Water Vapor Adsorption Isotherms of Guava,
Mango and Pineapple, Journal of Food Science, 57, 1405-1407.
Papanu J., Soane (Soong) D., Bell A., Hess D., 1989, Transport models for swelling and dissolution of thin
polymer films, Journal of Applied Polymer Science, 38, 859-885.
Rahman M.S., Chen X.D., Perera C.O., 1997, An improved thermal conductivity prediction model for fruits
and vegetables as a function of temperature, water content and porosity, Journal of Food Engineering, 31,
163-170.
Tu Y. O., Ouano A.C., 1977, Model for the kinematics of polymer dissolution, IBM Journal of Research and
Development, 21, 131-142.
USDA, 2020, Food Composition Databases, Department of Agriculture, <https:// ndb.nal.usda.gov/ndb>
(9/18/2020).
Yang Z., Zhu E., Zhu Z., Wang J., Li S., 2013, A comparative study on intermittent heat pump drying process
of Chinese cabbage (Brassica Campestris L. SSP) seeds, Food and Bioproducts Processing, 91, 381-388.
