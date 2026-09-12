Excerpt from the Proceedings of the COMSOL Conference 2009 Milan
Model of Heat and Mass Transfer with Moving Boundary during
Roasting of Meat in Convection-Oven

A.H. Feyissa*1, 2, J. Adler-Nissen1 and K.V. Gernaey2
1 National Food Institute, Food production Engineering, Technical University of Denmark
2 Department of Chemical and Biochemical Engineering, Technical University of Denmark
*Corresponding author: Søltofts Plads, 2800, Kgs. Lyngby, DK (e-mail: abhfe@food.dtu.dk)

Abstract:  A  2D  mathematical  model  of  hypotheses  to  model  mass  transfer  during
coupled  heat  and  mass  transfer  describing  roasting,  mostly  from  the  perspective  of
oven roasting of meat was formulated from  diffusion [1]-[3] while disagreements are often
first principles. The current formulation of
seen with regard to other types of water transport
model  equations  incorporates  the  effect  of  mechanisms  [8]-[10].  Purely  diffusion  based
| shrinkage  | phenomena  |     | and  | water  | holding  |     |     |     |     |     |     |
| ---------- | ---------- | --- | ---- | ------ | -------- | --- | --- | --- | --- | --- | --- |
models do not adequately describe the moisture
capacity. The model equations are based on
|     |     |     |     |     |     | transport  | phenomena  | during  |     | meat  | cooking  |
| --- | --- | --- | --- | --- | --- | ---------- | ---------- | ------- | --- | ---------- | --- |
conservation  of  mass  and  energy.  The  because the effects of water binding capacity and
pressure driven transport of water in meat is
shrinkage phenomena are not considered. These
| expressed  | using  | Darcy’s  |     | equation.  | The  |     |     |     |     |     |     |
| ---------- | ------ | -------- | --- | ---------- | ---- | --- | --- | --- | --- | --- | --- |
are, however, main driving mechanisms for the
| arbitrary  | Lagrangian–Eulerian  |     |     |              | (ALE)  |            |            |         |      |          |     |
| ---------- | -------------------- | --- | --- | ------------ | ------ | ---------- | ---------- | ------- | ---- | -------- | --- |
|            |                      |     |     |              |        | exudation  | of  water  | during  | the  | cooking  | or  |
| method     | was  implemented     |     |     | to  capture  | the    |            |            |         |      |          |     |
roasting of meat, and some of the early studies
| moving  | boundary  | (product-air  |     |     | interface)  |     |     |     |     |     |     |
| ------- | --------- | ------------- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- |
on this topic agree with this fact [5],[8]-[10].
| during  | the  | roasting  |     | process.  | The  | model  |     |     |     |     |     |
| ------- | ---- | --------- | --- | --------- | ---- | ------ | --- | --- | --- | --- | --- |
Roasting of meat causes the muscle protein to
| equations  | were  | solved  | using  | the  | Finite  |     |     |     |     |     |     |
| ---------- | ----- | ------- | ------ | ---- | ------- | --- | --- | --- | --- | --- | --- |
denature, resulting in a decrease in water holding
Element Method (Multiphysics® version 3.5).
The state variables (temperature and water  capacity and leading to shrinkage of the protein
|     |     |     |     |     |     | network.  | Shrinkage  | of  the  | network  | ultimately  |     |
| --- | --- | --- | --- | --- | --- | --------- | ---------- | -------- | -------- | ----------- | --- |
content) were predicted. The effect shrinkage
on both predictions was evaluated.  induces a pressure gradient inside meat muscle.
|     |     |     |     |     |     | The excess pressure induces a transport of water  |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | ------------------------------------------------- | --- | --- | --- | --- | --- |
Keywords:  Coupled  heat  and  mass  transfer;  inside the meat [11], and in the end leads to
Evaporation;  Moving  boundary;  Multiphyics;  water loss from the meat.
Shrinkage.
Most of the published work on the modelling of

mass and heat transfer during meat roasting does
1. Introduction
|     |     |     |     |     |     | not  at  | all  consider  | shrinkage,  |     | and  thus  | the  |
| --- | --- | --- | --- | --- | --- | -------- | -------------- | ----------- | --- | ---------- | --- |

governing model equations were typically solved
Roasting in a convection oven is a common
using a fixed boundary, where the evaporation
| way  of  | frying  | whole  | meat  in  | households,  | in  |     |     |     |     |     |     |
| -------- | ------- | ------ | --------- | ------------ | --- | --- | --- | --- | --- | --- | --- |
interface and the material boundary remain the
| professional  | kitchens  | and  | in  | the  ready-meal  |     |     |     |     |     |     |     |
| ------------- | --------- | ---- | --- | ---------------- | --- | --- | --- | --- | --- | --- | --- |
same for the entire roasting period [1]-[3],[11].
| industry.  | Mass  | and  heat  | transfer  |     | play  an  |     |     |     |     |     |     |
| ---------- | ----- | ---------- | --------- | --- | --------- | --- | --- | --- | --- | --- | --- |
Usually, the reason for making such assumptions
| important  | role  | in  the  | roasting  | process.  | It  is  |           |                   |     |         |               |     |
| ---------- | ----- | -------- | --------- | --------- | ------- | --------- | ----------------- | --- | ------- | ------------- | --- |
|            |       |          |           |           |         | is  that  | model  equations  |     | become  | considerably  |     |
essential that their interaction and mechanisms
simpler and thus easier to solve. However, the
are well understood to allow for better control
|     |     |     |     |     |     | model  | based  | on  such  | fixed  | boundary  |     |
| --- | --- | --- | --- | --- | --- | ------ | ------ | --------- | ------ | --------- | --- |
and optimisation of the roasting process. The
assumptions may not be valid for meat that is
| effect  of  | shrinkage  | on  | meat  | roasting  | is  often  |         |        |                    |     |               |     |
| ----------- | ---------- | --- | ----- | --------- | ---------- | ------- | ------ | ------------------ | --- | ------------- | --- |
|             |            |     |       |           |            | heated  | above  | the  denaturation  |     | temperature,  |     |
neglected due to the complexity of the process
where the meat shrinks considerably, loses water
[1]-[4]. However, it is necessary to incorporate
and changes its dimensions. When temperatures
such effects into a heat and mass transfer model
exceed the denaturation temperature, shrinkage
| of  meat  | roasting,  | because  |     | shrinkage  | is  |            |         |            |     |        |       |
| --------- | ---------- | -------- | --- | ---------- | --- | ---------- | ------- | ---------- | --- | ------ | ----- |
|           |            |          |     |            |     | phenomena  | should  | therefore  | be  | taken  | into  |
considerable (7-19 % on a area basis [5], and 11-
account in the heat and mass transfer model, in
20.3 % on diameter basis [6]) and plays a key
|     |     |     |     |     |     | order to  | successfully  | describe  | heat  | and  | water  |
| --- | --- | --- | --- | --- | --- | --------- | ------------- | --------- | ----- | ---- | ------ |
role in the water transport during the roasting
transport inside the meat product. Therefore the
process) [7].
objective of this work is to develop a model of
| Several  | researchers  | have  | formulated  |     | different  |     |     |     |     |     |     |
| -------- | ------------ | ----- | ----------- | --- | ---------- | --- | --- | --- | --- | --- | --- |

heat and mass transfer by taking into account the  heat transfer. The heat is transferred from the
shrinkage effect (moving boundary and pressure  surface the product to the center of the product
driven transport) and ultimately to describe and  mainly by conduction. Meanwhile, moisture is
predict heat and mass transfer processes for meat  transported  within  the  product  via  convection
roasting in a convection oven.  and  diffusion  processes,  and  moves  from  the
|     |     |     |     | inside of the product to its surface. With increase  |     |     |     |     |     |     |
| --- | --- | --- | --- | ---------------------------------------------------- | --- | --- | --- | --- | --- | --- |
in temperature, muscle protein denatures, leading

Nomenclature  to a decrease in its water holding capacity and
C  Moisture content (wet  Greek letters  shrinkage of the protein network. The shrinkage
basis) (kg /kg)  of network ultimately induces a pressure gradient
C   Water holding capacity  β Shrinkage  inside  the  meat  muscle  and  excess  water  is
| eq                        |     |     |                  |             |     |                  |          |         |             |     |
| ------------------------- | --- | --- | ---------------- | ----------- | --- | ---------------- | -------- | ------- | ----------- | --- |
| at equilibrium (kg /kg)   |     |     | coefficient      |             |     |                  |          |         |             |     |
|                           |     |     |                  | expelled    | to  | the              | surface  | by      | convection  |     |
| Specific heat (J/(kg.oC)  |     |     | Density (kg/m3)  |             |     |                  |          |         |             |     |
| c                         |     |     | ρ   |                  |     | phenomena.  |     | Simultaneously,  |          | liquid  | water       | is  |
| p                         |     |     |                  |             |     |                  |          |         |             |     |
D  Diffusion  coefficient  µ   Viscosity  evaporated at the product surface and diffuses to
w
(m2/s)  (kg/(m.s))  the  surrounding  fluid  (hot  air).  As  the  meat
| E  Elastic modulus(N/m2)  |     | ∇   | Gradient(1/m)  |     |     |     |     |     |     |     |
| ------------------------- | --- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- |
sample shrinks the interface or the surface at
|     |     |     | which water is evaporated changes with time.  |     |     |     |     |     |     |     |
| --- | --- | --- | --------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
f  Fraction of energy used
|     |     |     | The  | most  | important  | mechanisms  |     |     |     |     |
| --- | --- | --- | ---- | ----- | ---------- | ----------- | --- | --- | --- | --- |
for evaporation (J/kg)
occurring  during  the  convection  oven  roasting  process  are
H  Latent heat of  Subscripts
| vaporization (J/kg)  |     |     | described in Fig.1, as shown below.   |     |     |     |     |     |     |     |
| -------------------- | --- | --- | ------------------------------------- | --- | --- | --- | --- | --- | --- | --- |

| h  Heat  | transfer  | av  | Average  |     |     |     |     |     |     |     |
| -------- | --------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
coefficient (W/(m2 oC)
| K Permeability (m2)  |     | eq  | Equilibrium  |     |     |     |     |     |     |     |
| -------------------- | --- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- |

| k  Thermal  | conductivity  | c   | Carbohydrate   |     |     |     |     |     |     |     |
| ----------- | ------------- | --- | -------------- | --- | --- | --- | --- | --- | --- | --- |
(W/(m. oC))
| m  Mass (kg)       |     | d    | Solid        |     |     |     |     |     |     |     |
| ------------------ | --- | ---- | ------------ | --- | --- | --- | --- | --- | --- | --- |
| P  Pressure (Pa)   |     | evp  | evaporation  |     |     |     |     |     |     |     |
| q Heat flux (W/m2  |     | f    | Fat          |     |     |     |     |     |     |     |

| T  Temperature (oC)  |     | i   | Component   |     |     |     |     |     |     |     |
| -------------------- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- |
| t  Time (s)          |     | m   | Meat        |     |     |     |     |     |     |     |
| Tσ  Sigmoidal        |     | p   | Protein     |     |     |     |     |     |     |     |
temperature(oC)
| R  Radius (m)  |           | w      | Water          |                                                  |     |     |     |     |     |     |
| -------------- | --------- | ------ | -------------- | ------------------------------------------------ | --- | --- | --- | --- | --- | --- |
| y  Mass        | fraction  | of  0  | Initial value  |                                                  |     |     |     |     |     |     |
| i              |           |        |                | Figure 1: A schematic representation of coupled  |     |     |     |     |     |     |
component i  (kg/kg)
heat and mass transfer accompanied by shrinkage
| Z  Length (m)  |     | oven  | Oven   |     |     |     |     |     |     |     |
| -------------- | --- | ----- | ------ | --- | --- | --- | --- | --- | --- | --- |
and evaporation processes
| V  Volume (m3)               |     | s   | Surface            |                   |     |     |     |     |     |     |
| ---------------------------- | --- | --- | ------------------ | ----------------- | --- | --- | --- | --- | --- | --- |
| v  Interface velocity (m/s)  |     | r   | Radial direction   | 2.2 Assumptions:  |     |     |     |     |     |     |
u  velocity of water (m/s)  z  Length direction   In  this  study  the  following  basic
|     |     |     |     |     | assumptions  |     | are  made  | to  formulate  |     | the  |
| --- | --- | --- | --- | --- | ------------ | --- | ---------- | -------------- | --- | --- |

|     |     |     |     |     | governing coupled mass and heat transfer    |     |     |     |     |     |
| --- | --- | --- | --- | --- | ------------------------------------------- | --- | --- | --- | --- | --- |
|     |     |     |     |     | equations for a cylindrical body of meat:   |     |     |     |     |     |
a)  Fat transport is negligible (lean meat is

2. Mathematical Model of Heat and Mass
| Transfer   |     |     |     |     | considered having less than 2% fat)  |     |     |     |     |     |
| ---------- | --- | --- | --- | --- | ------------------------------------ | --- | --- | --- | --- | --- |
b)  The crust is thin (this is observed when

|     |     |     |     |     | inspecting  |     | a  cut  | through  | the  cooked  |     |
| --- | --- | --- | --- | --- | ----------- | --- | ------- | -------- | ------------ | --- |
meat) and does not hinder transport of

2.1 Process Descriptions and Problem
|     |     |     |     |     | water  | to  | the  | surface.  |     | Evaporation  |     |
| --- | --- | --- | --- | --- | ------ | --- | --- | -------------- | --- | ------------ | --- |
Formulation
|     |     |     |     |     | therefore  |     | takes  | place  | at  | the  | surface  |
| --- | --- | --- | --- | --- | ---------- | --- | -------------- | --- | --- | --- |

(moving interface)

The product (meat) is heated in a convection
oven by circulating hot air at 175oC. Heat is  c)   No  internal  heat  generation  and  no
chemical reaction.
supplied to the product surface by convective
d)  Dissolved matter lost with water can be

neglected  in  the  material  and  energy  For product subjected to convection roasting
balance [7].  (boundary 2, 3 and 4, see Fig.1), the governing
e)  The  process  can  be  represented  two  heat transfer equation (1) is solved using
|     |     |     |     |     |     | (   |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
dimensions,  due  to  symmetry  of  the  −n. k ∇T+u c ρT =h(T −T )−q
|     |     |     |     |     |     |     |     m w |     | pw w |     | oven |     | s   |     | evp (7)  |
| --- | --- | --- | --- | --- | --- | --- | ------- | --- | ---- | ---- | ---- | --- | --- | -------- |
cylindrical body that is modelled.
For the sample center line, boundary 1 (see

| f)  The initial distributions of water content  |     |     |     |     |     |     |     |                          |     |         |
| ------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- | ------------------------ | --- | ------- |
| and temperature are uniform.                     |     |     |     |     |     |     |     | Fig.1), axial symmetry boundary is applied: |     |         |
|                          |     |     |     |     |     | (    |      |       | )          |     |         |
| ------------------------ | --- | --- | --- | --- | --- | ---- | ---- | ----- | ---------- | --- | ------- |
|                          |     |     |     |     |     | −n.k | ∇T+u | c ρ T | =0  ;  t>0 |     |         |
|                          |     |     |     |     |     |      |     m w  |     | pw w      |     |            |
| 2.3 Governing equations  |     |     |     |     |     |      |      |       | r=0        |     |    (8)  |
Where the term on the left-hand side of equation

Using conservation of energy, the heat transfer  (7) refers to heat transferred by conduction and
within meat is assumed to be given by (1)  convection from the outer surface to the inside of
the meat sample, the first term on the right-hand

∂T
ρc +∇(−k ∇T)+ρc u ∇T =0   side is heat penetrating from the oven (hot air) to
| m   | pm  |     | m   | w pw | w     |     |     |     |     |     |     |
| --- | --- | --- | --- | ---- | ----- | --- | --- | --- | --- | --- | --- |
|     | ∂t  |     |     |      |   (1) |     |     |     |     |     |     |
the product by means of convection, and the
From the conservation of mass, the governing  second term on the right-hand side denotes heat
equation for water transport within the product is  dissipation for evaporation of the water at the
given by (2)  interface. The initial condition has the following
| ∂C  |       |        |     |     |            | form (9):  |                         |     |     |     |       |
| --- | ----- | ------ | --- | --- | ---------- | ---------- | ----------------------- | --- | --- | --- | ----- |
|     | +∇(Cu | )=∇D∇C |     |     |            |            |                         |     |     |     |       |
|     |       | w      |     |     |            | T(r,z)=T   | =const       at   t=0   |     |     |     |   (9) |
| ∂t  |       |        |     |     |       (2)  |            | 0                       |     |     |     |       |

The  relationship  between  the  velocity  and  2.4.2 Mass Transfer Boundary Condition
| pressure  |     | gradient  | (that  | drives  | the  moisture  |     |     |     |     |     |     |
| --------- | --- | --------- | ------ | ------- | -------------- | --- | --- | --- | --- | --- | --- |
transport) inside the meat can be expressed using
For product subjected to convection roasting
Darcy’s law of porous media :
(boundary 2, 3 and 4), the governing mass
|                                                   | −K     |     |     |     |            | transfer equation (2) is solved using (10)   |     |       |     |      |         |
| ------------------------------------------------- | ------ | --- | --- | --- | ---------- | -------------------------------------------- | --- | ----- | --- | ---- | ------- |
| u                                                 |   ∇P   |     |     |     |       (3)  |                                              |     |       |     |      |         |
| w                                                 | =      |     |     |     |            |                                              |     | q     |     |      |         |
|                                                   | µ      |     |     |     |            | (                                            |     | ) evp | (   | )    |         |
|                                                   | w      |     |     |     |            | n..−D∇C+u                                    |     | C   | =   | C−C |      |         |
|                                                   |        |     |     |     |            |                                              | w   | H ρ   | eq  |      |   (10)  |
| The pressure (swelling pressure) is proportional  |     |     |     |     |     |                                              |     | evp   |     |      |         |
to the excess moisture concentration within the  For boundary 1(at r = 0), the axial symmetry
meat [11]-[10] and the expression for swelling  boundary condition applies:
|                         |               |     |     |     |            | n.(−D∇C+u                                           | C)  |          |     |      |         |
| ----------------------- | ------------- | --- | --- | --- | ---------- | --------------------------------------------------- | --- | -------- | --- | ---- | ------- |
| pressureP is given as   |               |     |     |     |            |                                                     |     | =0  ;  t | >0  |      |         |
|                         |               |     |     |     |            |                                                     | w   | r=0      |     |      |   (11)  |
|                         | E(C −Ceq(T))  |     |     |     |       (4)  |                                                     |     |          |     |      |         |
| P                       | =             |     |     |     |            | The initial condition has the following form (12):  |     |          |     |      |         |
C(r,z)=C
The expression for the water holding capacity is  =const       at   t =0       (12)
0
| given  | by  | an  empirical,  |     | sigmoid  | relation  [11],  |                 |     |     |     |     |     |
| ------ | --- | --------------- | --- | -------- | ---------------- | --------------- | --- | --- | --- | --- | --- |
| [13]   |     |                 |     |          |                  | 2.4 Shrinkage   |     |     |     |     |     |

0.345
The methods used to consider material shrinkage
Ceq(T)=0.745−
(1+30exp(−0.25(T−Tσ)))
differ greatly throughout the literature [14]. It is
                    (5)  often considered that the change of dimensions
|     |     |     |     |     |     | (shrinkage)  | is  | proportional  | to  | the  volume  | of  |
| --- | --- | --- | --- | --- | --- | ------------ | --- | ------------- | --- | ------------ | --- |
The expression for velocity can be re-written
liquid water removed [14]. For meat cooking,
using Eq. (3-5)
Sun and Du found a good correlation between
the shrinkage (volume based dimensions change)

|     | −KE | (    |     | )     |           |                                                 |     |     |     |     |     |
| --- | --- | ---- | --- | ----- | --------- | ----------------------------------------------- | --- | --- | --- | --- | --- |
|     | u = | ∇C−C |     |       |           |                                                 |     |     |     |     |     |
|     | w µ |      |     | eq    |       |           |                                                 |     |     |     |     |
|     |     | w    |     |       |       (6) |                                                 |     |     |     |     |     |
and cooking loss, (a higher shrinkage leads to
action of roasting causes denaturation of meat
more cooking loss, and vice versa) [15]. The
proteins,  which  allows  for  dehydration  and
2.4 Boundary Conditions
|     |     |     |     |     |     | shrinkage  | of  the  | meat,  | and  | the  simultaneous  |     |
| --- | --- | --- | --- | --- | --- | ---------- | -------- | ------ | ---- | ------------------ | --- |
2.4.1 Heat Transfer Boundary Condition   formation of air filled pores [6]. By assuming
that the relationship between volume of water
|     |     |     |     |     |     | removed  | and  shrinkage  |     | holds  | for  roasting  | of  |
| --- | --- | --- | --- | --- | --- | -------- | --------------- | --- | ------ | -------------- | --- |

meat, with an additional consideration for the and the rate change of V is given by (20) :
w,l
effect of pore formation, the following dV , ρV(1−C )⎛ 1 ⎞ 2 dC
theoretical expressions are formulated. wl =− 0 0 0 ⎜ ⎟ av
The volume of a cylindrical meat sample at any ⎜ ⎟
dt ρ w ⎝1−C av⎠ dt (20)
given time is expressed in terms of the initial
volume (V ) and volume of water lost (V ) as at the sample center (boundary r = 0)
o w,l
V =V 0 −βV w , l (13) v r =0 (21)
The coefficient β is used to describe the effect of
3. Numerical Method
pore formation during roasting process. For
shrinkage, the value of β varies between 0 and 1.
If β is 1, there is no pore formation (i.e. the The above model equations (system of partial
volume of water removed is equal to the volume differential equations) describing coupled heat
deformation) and if β = 0, then there is no and mass transfer in convection roasting of meat
shrinkage (i.e the volume water lost is entirely were solved using the finite element software,
replaced by air and no deformation occurs). The COMSOL Multiphyics®version3.5. A 2D
fraction (1-β) is the fraction of the volume of cylindrical geometry of dimensions (radius of 20
water removed from the meat during roasting mm and length of 54 mm) was built in
that is replaced by pore space (filled with air). COMSOL for numerical simulations. The
For minced meat, this value is roughly estimated coupled partial differential equations for heat and
(for a mass loss of 15%, the corresponding pore mass transfer along with the boundary condition
formation is 3%) to be around 0.2, and in that that were solved using the Chemical Engineering
case β = 0.8 [6]. module (transient heat transfer and transient
For isotropic shrinkage [16], Eq. (13) can be re- mass transfer) and the moving mesh module
written as: (ALE). The incorporation of ALE gives the
⎛ βV , ⎞ ability to track the position of the product-air
V=V 0⎜ ⎜
⎝
1−
V 0
wl ⎟ ⎟
⎠
i
a
n
lg
te
e
r
b
fa
ra
i
c
e
.
.
e T
x
h
p
e
r es
in
si
p
o
u
n
t
s
p
in
a ra
th
m
e
e t
m
er
o d
v
e
a
l
u
re
e
g
s
a
i
v
n
e
d n
t h
in
e
⎛ βV , ⎞ 2/3 ⎛ βV , ⎞ 1/3 (14) table 1.
=πR
0
2
⎜
⎜
⎝
1−
V 0
wl
⎟
⎟
⎠
Z
0⎜
⎜
⎝
1−
V
w
0
l
⎟
⎟
⎠
=πR2.Z
From (14) the expressions for Z and R are given 4. Result and Discussion
as:
1/3
⎛ βV , ⎞
Z =Z ⎜1− w l ⎟
0⎜ ⎝ V 0 ⎟ ⎠ (15) 4 d . i 1 st T ri e b m ut p io er n a t s ure and water content
⎛ βV , ⎞ 1/3 In the meat roasting process, temperature and
R=R 0⎜ ⎜1− V w l ⎟ ⎟ (16) water content distributions are important factors
⎝ 0 ⎠ which determine the quality of the product. The
Differentiating (15) and (16) with respect to water content distribution is influenced by the
time, the interface velocity components can be temperature distribution. Fig 2a and 2b show
obtained as: simulated spatial temperature and moisture
dZ Z β⎛ βV , ⎞ −2/3 d distribution, respectively, for 2D cylindrical meat
v = =− 0 ⎜1− w l ⎟ (V , )
z dt 3V 0 ⎜ ⎝ V 0 ⎟ ⎠ dt w l (17) sample at different times of roasting process (t =
0, 500, 1000, 1500, 2000, 2500, 3000, and 3500
−2/3
dR R β⎛ βV , ⎞ d s). Generally, inside the meat sample, the
v = =− 0 ⎜1− w l ⎟ (V , )
r dt 3V 0 ⎜ ⎝ V 0 ⎟ ⎠ dt w l (18) temperature increases with increase in time,
whereas water content and dimensions are
V can be expressed as function of water
w,l decrease with increase in time. From that the
content as in Eq. (19) :
figure, a change of dimensions - a moving
m(X −X) ρV(1−C)⎛ C C ⎞
V,= d 0 = 0 0 0 ⎜ 0 − av ⎟
boundary - can be noticed.
wl ρ w ρ w ⎜ ⎝1−C 0 1−C av ⎟ ⎠ (19)

uniform.
Fig. 2b, illustrates the progress of the water
|     |     |     |     |     |     | content  |     | distribution  |     | within  | the  | meat  | product  |
| --- | --- | --- | --- | --- | --- | -------- | --- | ------------- | --- | ------- | ---- | -------- |
during the roasting process. The water content
|     |     |     |     |     |     | distribution  | changes  |     | from  | being  | uniform  | (=  |
| --- | --- | --- | --- | --- | --- | ------------- | -------- | --- | ------------ | -------- | -------- | --- |
initial condition) to a non-uniform profile. The
|     |     |     |     |     |     | increase  | in  temperature  |     | (to  | the  | denaturation  |     |
| --- | --- | --- | --- | --- | --- | --------- | ---------------- | --- | ---- | ------------------ | --- |
temperature zone) causes the meat to reduce its
|     |     |     |     |     |     | water holding capacity and induces shrinkage.  |     |     |     |     |     |
The reduction of the water holding capacity and
the shrinkage of the meat protein network cause
the meat to exudate water to the surface, which is
lost by evaporation at the surface. As a result, the
a)
water content gradient is developed within the

meat, as shown by iso-concentration lines at t =
|     |     |     |     |     |     | 500  s  (Fig.  | 4).  | A  large  | water  | concentration  |     |
| --- | --- | --- | --- | --- | --- | -------------- | ---- | --------- | ------ | -------------- | --- |
gradient is observed near the surface and the
gradient gradually shifts towards the interior of
|     |     |     |     |     |     | the  product   | (Fig.  | 2b).  | The       | water  transport  |      |
| --- | --- | --- | --- | --- | --- | -------------- | ------ | ----- | --------- | ----------------- | ---- |
|     |     |     |     |     |     | depends        | upon   | the   | material  | properties        |      |
|     |     |     |     |     |     | (permeability  |        | and   | elastic   | modulus),         | the  |
diffusivity coefficient and the pressure gradient.
b)
Figure 2. a) Temperature distribution, and b) water
content distribution at (t = 0, 500, 1000, 1500, 2500,
2000, 3000, and 3500 s)

| Fig.  | 2a,  illustrates  |     | the  progress  |     | of  the  |     |     |     |     |     |     |
| ----- | ----------------- | --- | -------------- | --- | -------- | --- | --- | --- | --- | --- | --- |
temperature distribution during meat roasting in

| a  convection  |     | oven.  |     | Initially,  | there  | is  | a  sharp  |     |     |     |     |     |     |     |     |
| -------------- | --- | ------ | --- | ----------- | ------ | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
Figure 3 Temperature profile across cylindrical
increase in surface temperature because of the
sample (Z = 0)
| large  temperature  |     |     | difference  |     | between  |     | hot  air  |     |     |     |     |     |     |     |
| ------------------- | --- | --- | ----------- | --- | -------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- |
(175oC) and the meat (13oC). At t = 500 s, the
| surface      |     | the  | meat   | is  at  a     | much      | higher     |     |     |     |     |     |     |     |     |
| ------------ | --- | ---- | ------ | ------------- | --------- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
| temperature  |     | than | the    | inside  part  | of        | the  meat  |     |     |     |     |     |     |     |     |
| sample,      |     | and  | a      | large         | temperature | gradient   | is  |           |     |     |     |     |     |     |
developed in the region close to the surface,(see
Fig. 2a and Fig. 3). When the roasting process
proceeds, this large temperature gradient shifts
gradually from near the surface to inside of the
product. Moreover, its magnitude decreases as a
function of time, as the heat energy is slowly
| penetrating  |     | into  | the  | centre  | of  | the  | product,  |     |     |     |     |     |     |
| ------------ | --- | ----- | ---- | ------- | --- | ---- | --------- | --- | --- | --- | --- | --- | --- |

thereby raising its temperature (Fig. 3). In the
Figure 4 .Iso-concentration, C (kg/kg) at t = 500 s
final period of this roasting experiment, at time t
= 3000 s, the temperature of the meat is almost

4.2 Effect of Moving Boundary   slowly from t = 300 s to 500 s. In the second
|     |     |     |     | period (between t = 500 s to t = 2000 s), the  |     |     |     |     |     |
| --- | --- | --- | --- | ---------------------------------------------- | --- | --- | --- | --- | --- |
The  temperature  profiles  with  moving  relative  change  of  dimension  is  large  (steep
boundary  (MB)  and  fixed  boundary  (FB)  are  profile). In this zone, a major part of the meat is
in the denaturation zone (where a reduction of
compared in Fig. 5a and 5b. From Fig. 5a, the
center  and  the  surface  temperature  values  water holding capacity and shrinkage of protein
network take place). In the third period, (after t =
predicted by both methods coincide well at the
|     |     |     |     | 2000  s),  | the  relative  | change  |     | of  deformations  |     |
| --- | --- | --- | --- | ---------- | -------------- | ------- | --- | ----------------- | --- |
beginning of the process (t = 0 to t = 1000 s). But
later one, (t > 1000 s), the two predictions start  (shrinkage rate) is reduced. After t = 3500 s, the
|     |     |     |     | rate  of  | change  | of  the  relative  |     | dimension  | has  |
| --- | --- | --- | --- | --------- | ------- | ------------------ | --- | ---------- | ---- |
deviating from each other. The FB predicts lower
|     |     |     |     | clearly  | diminished.  | The  | probable  | reasons  | for  |
| --- | --- | --- | --- | -------- | ------------ | ---- | --------- | -------- | ---- |
center temperature than MB. However, the FB
such situation are; 1) the mechanical properties
predicts higher water content than MB (Fig 5b).
of the meat have changed (e.g. elastic modulus

increase) and 2) reduction of the water content
near the surface, which make the product more
rigid and less susceptible to deformations.

| Figure  | 5a  Temperature  | profile  –MB  | --  FB  |     |     |     |     |     |     |
| ------- | ---------------- | ------------- | ------- | --- | --- | --- | --- | --- | --- |

(blue) center (0, 0) (green) surface (R = 0.02, Z
Figure 6 Relative length of cylinder as function of
= 0)
time (R/R0)

5. Conclusions

A first-principles-based model of heat and mass
transfer with moving boundary is developed for
a convection meat roasting process. The model
|     |     |     |     | equations  | were  | solved  | using  |     | COMSOL  |
| --- | --- | --- | --- | ---------- | ----- | ------- | ------ | --- | ------- |
Multiphyics®version3.5. Temperature and water
content distributions as function of position and
|     |     |     |     | time  were  | predicted.  | Using  | the  | model  | better  |
| --- | --- | --- | --- | ----------- | ----------- | ------ | ---- | ------ | ------- |
insight of the process mechanisms is obtained,

Figure 5b Water content profile – (MB), -- (FB),  which  would  otherwise  not  be  possible.  The
novelty of the developed model is its capability
blue is center (0, 0), red is at (0.017, 0), green is at
to incorporate the effect of the shrinkage and
(0.019, 0), and      is surface (0.02, 0).
|     |     |     |     | water  holding  | capacity.          |     |     | Such          | model  | can  be   |
| --- | --- | --- | --- | --------------- | ------------------ | --- | --- | ------------- | ------ | --------- |
|     |     |     |     | helpful         | in  understanding  |     | the  | physics  |        | of  meat  |
4.3 Relative Change of Dimension   roasting, and can be used to improve prediction

of temperature and moisture loss.
| Fig. 6 shows the plot of the relative dimension  |                                          |     |     |     |     |     |     |     |     |
| ------------------------------------------------ | ---------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- |
change, R/R                                      , in the r-direction. In the first part
o
of the roasting process (until t = 300 s), there is

| no shrinkage. The product (meat) starts shrinking  |     |     |     | 6. References   |     |     |     |     |     |
| -------------------------------------------------- | --- | --- | --- | --------------- | --- | --- | --- | --- | --- |

based on Flory–Rehner theory, Meat Sci., 76:
730-738, 2007.
[1] Huang, E. and Mittal, G.S., Meatball
Cooking - Modeling and Simulation, J. Food [12] Barriere, B., and Leibler, L., Kinetics of
Eng., 24: 87-100, 1995. solvent absorption and permeation through a
highly swellable elastomeric network, J. Polymer
Sci. Part B-Polymer Physics, 41:166-182, 2003.
[2] Ngadi, M.O., Watts, K.C. and Correia, L.R.,
Finite element method modelling of moisture
transfer in chicken drum during deep-fat frying, [13] Bengtsson N.E., Jakobsson B., and
J. Food Eng., 32: 11-20, 1997. Dagerskog M., Cooking of Beef by Oven
Roasting - Stuy of Heat and Mass-Transfer, J.
Food Sci., 41: 1047-1053, 1976.
[3] Chen, H., Marks, B.P. and Murphy, R.Y.,
Modeling coupled heat and mass transfer for
convection cooking of chicken patties, J. Food [14] Katekawa, M.E. and Silva, M.A..A
Eng., 42: 139-146, 1999. review of drying models including shrinkage
effects , Drying Technol. , 24: 5-20, 2006.
[4] Skjoeldebrand, C., and Hallström, B.,
[15] Sun D.-W. and DU C.-J., Correlating
Convection oven frying Heat and mass transport
shrinkage with yield, water content and texture
in the product, J. Food Sci. 45 :1347-1353, 1980.
of the pork ham by computer vision, Journal
Food Process Engineering, 28 :219-232, 2005.
[5] Tornberg, E. , Effects of heat on meat
proteins – Implications on structure and quality [16] Pham, Q.T., Trujilo, F.J., and
of meat products, Meat Sci.,70: 493-508, 2005. Wiangkaew, C., Drying modeling and water
diffusivity in beef meat, J. Food Eng., 78: 74-85,
[7] Feyissa, A.H., Adler-Nissen, J., and. 2007.
Gernaey, K.V., Mechanism of water transport in [17] Rao, M.A., Syed, S.H.R, and Datta, A.K.,
meat during the roasting process, Icomst Engineering properties of foods, 3rd ed. Talyor
Conference, 11-15, Copenhagen, 2009. and Francis.
[18] Datta, A.K., Hydraulic permeability of
[6] Oroszvari, B.K., Bayod, B.E., Sjoholm, I.
food tissues., Int. J. Food., 9:767-780, 2006
and Tornberg, E. The mechanisms controlling
heat and mass transfer of the frying of beef
[19] Hodgman, C.D., Handbook of chemistry
burgers. III. Mass transfer evolution during
and physics, The chemical rubber publishing
frying, J. Food Eng., 76: 169-178.
Co., Cleveland, Ohio, 2257.
[8] Godsalve, E.W. Davis, E.A. , Gordon, J. ,and
7. Acknowledgement
Davis, H.T., Water loss rates and temperature
profiles of dry cooked bovine muscle, J. Food
The Author would like to thank DTU for a Ph.D.
Sci., 42: 1038-1045, 1977.
grant under the aegis of Food-DTU.
[9] Thorvaldsson, K. , and Skjöldebrand, C.,
8. Appendix
Water transport in meat during reheating, J.
Food Eng., 29: 13-21, 1996.
Table 1: Parameters values, thermophysical
properties and other expression.
[10] Wählby, U., and Skjöldebrand, C. , NIR- Value or expression Reference
measurements of moisture changes in foods, J. y p 0.2 kg/kg [5]
Food Eng., 47: 303-312, 2001. y c 0.02 kg/kg Initial
y 0.03 kg/kg mass
f
y 0.75 kg/kg fraction
[11] Van der Sman, R.G.M., Moisture w
ρ 920 kg/m3 [17]
transport during cooking of meat: An analysis f
ρ 1320 kg/m3 [17]
p

| ρ   |     | 1600 kg/m3  |     | [17]  |
| --- | --- | ----------- | --- | ----- |
1000 kg/m3
| ρ w  |     |     |     | [17]  |
| --- | --- | --- | --- | ----- |
0.47 W/(m. oC)
| k   |     |     |     | [17]  |
| --- | --- | --- | --- | ----- |
m
| c   |     | 4170 J/(kg. oC   |     | [17]  |
| --- | --- | ---------------- | --- | ----- |
p,w
| H   |     | 2.3 106 J/kg  |     |     |
| --- | --- | ------------- | --- | --- |
evap
| h   |     | 33.4 (W/(m2. oC)        |     | Measured  |
| --- | --- | ----------------------- | --- | --------- |
|     |     | 10-17-10-19 (raw meat)  |     | [18]      |
K
10-17m2
| T 0ven   |     | 175 °C  |     | Set  |
| -------- | --- | ------- | --- | ---- |
| T        |     | 13 °C   |     | Set  |
0
| C   |     | 0.75 kg /kg  |     | [5][7]  |
| --- | --- | ------------ | --- | ------- |
0
| β                          |     | 0.8  |     | [6]   |
| -------------------------- | --- | ---- | --- | ----- |
| D=2.23e-5exp(-3382.212/T)  |     |      |     | [16]  |
Using data
| −log µ | = 0.0072 | T + 2.8658 |     |       |
| ------ | -------- | ---------- | --- | ----- |
|        | w        |            |     | [19]  |
|        | 1        |            |     | [17]  |
ρ =
m
y
|     | ∑ i |     |     |     |
| --- | --- | --- | --- | --- |
ρ
i
| c =(1.6y | +2y | +2y +4.2y | ).103 | [17]  |
| -------- | --- | --------- | ----- | ----- |
| pm       | c   | p f       | w     |       |

|     |     | E   |     | Using data  |
| --- | --- | --- | --- | ----------- |
mx
| E (T) =E | +          |     |         | [5]   |
| -------- | ---------- | --- | ------- | ----- |
|          | o (1+exp−E | ( ( | T −E )) |      |
|          |            | n   | D       |      |

| For whole meat, E |             | =12 kpa, E | =83 kpa  |     |
| ----------------- | ----------- | ---------- | -------- | --- |
|                   |             | 0          | mx       |     |
| at T=80 oC; E     | =0.3, and E | =60        |          |     |
|                   | n           | D          |          |     |
|                   | (           | )          |          |     |
| q =               | fh T        | −T         |          |     |
| evp               | oven        | s          |          |     |
