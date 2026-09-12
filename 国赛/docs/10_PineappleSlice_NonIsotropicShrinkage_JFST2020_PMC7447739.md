JFoodSciTechnol(October2020)57(10):3748–3761
https://doi.org/10.1007/s13197-020-04407-4
| ORIGINAL     |       | ARTICLE         |             |            |               |        |            |           |        |     |     |
| ------------ | ----- | --------------- | ----------- | ---------- | ------------- | ------ | ---------- | --------- | ------ | --- | --- |
| Modelling    |       | of moisture     |             | migration  |               | during | convective |           | drying |     |     |
| of pineapple |       | slice           | considering |            | non-isotropic |        |            | shrinkage |        |     |     |
| and variable |       | transport       |             | properties |               |        |            |           |        |     |     |
| Poonam       | Rani1 | P. P. Tripathy1 |             |            |               |        |            |           |        |     |     |
•
Revised:21January2020/Accepted:2April2020/Publishedonline:22May2020
(cid:2)AssociationofFoodScientists&Technologists(India)2020
| Abstract |     |     |     |     |     |     | Keywords |     |     |     |     |
| -------- | --- | --- | --- | --- | --- | --- | -------- | --- | --- | --- | --- |
Thepresentworkaimstodevelopa3-dimensional Finite element model (cid:2) Drying (cid:2) Pineapple (cid:2)
finite element (FE) model to analyze moisture migration Diffusioncoefficient(cid:2)Shrinkage(cid:2)Masstransfercoefficient
| during    | drying    | of pineapple | ring | considering | moisture |       |         |         |     |     |     |
| --------- | --------- | ------------ | ---- | ----------- | -------- | ----- | ------- | ------- | --- | --- | --- |
| dependent | diffusion | coefficient  | (D)  | and mass    | transfer | coef- | List of | symbols |     |     |     |
ficient (h ) along with radial and longitudinal shrinkage. A Exposed surface area (m2)
m
Pineappleringsweredriedat70 (cid:3)Ctemperatureand0.6 m/s D Moisture diffusion coefficient (m2/s)
airvelocitytostudythemoisturelossandshrinkagekinetics oM=ot Slope of moisture vs. drying time curve
during drying. Thickness, outer radius and inner radius of DR Drying rate (kg/h.m2)
hollow cylindrical pineapple slices were reduced by 79.3%, d Outer diameter of pineapple slice (m)
o
32.2%, and 51.2%, respectively due to the occurrence of d Inner diameter of pineapple slice (m)
i
shrinkage during drying. Non-linear regression analysis l Thickness of pineapple slice (m)
showedthequadraticmodeltobestfittedtotheexperimental M Moisture content (kg water/kg dry weight)
moistureratiodataforexplainingtheshrinkagephenomenon M Equilibriummoisturecontent(kgwater/kgdry
e
in pineapple slice during drying. Shrinkage was accommo- weight)
datedintoFEmodellingusingthearbitrarylagrange-eulerian M Initial moisture content (kg water/kg dry
o
method. Consideration of variable D showed better agree- weight)
ment with the experimental data than consideration of con- M Moisture content at the sample surface
1
stant D, however constant and variable h predicted similar MR Moisture ratio
m
results. Incorporation of shrinkage phenomena during mod- N Number of observations
R2
elling led to prediction of more accurate result showing Coefficient of determination
0.06%deviationfromexperimentalcurve,butneglectingthe r Inner radius of slice (m)
i
shrinkage resulted in a 17% deviation. Hence, model devel- r Outer radius of slice (m)
o
oped with consideration of shrinkage along with variable D t Time (s)
and h presented best fit with experimental drying curve. wb Wet basis
m
Developed model allowed the visualization of spatial mois- W Weight of dry solid (kg)
s
tureprofilewithinthesampleduringdrying,whichwouldbe f Number of constants
usefulforestimatingthecorrectdryingtime,optimizingand V Volume of pineapple ring (m3)
| designing | of drying | process. |     |     |     |     | S   | Shrinkage | parameter |           |     |
| --------- | --------- | -------- | --- | --- | --- | --- | --- | --------- | --------- | --------- | --- |
|           |           |          |     |     |     |     | S   | Predicted | shrinkage | parameter |     |
pre,I
|     |     |     |     |     |     |     | S   | Experimental |     | shrinkage | parameter |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --- | --------- | --------- |
exp,I
| & P.P.Tripathy                                    |     |     |     |     |     |     | RMSE | Root mean  | square     | error    |                   |
| ------------------------------------------------- | --- | --- | --- | --- | --- | --- | ---- | ---------- | ---------- | -------- | ----------------- |
| punam@agfe.iitkgp.ac.in                           |     |     |     |     |     |     | v2   |            |            |          |                   |
|                                                   |     |     |     |     |     |     |      | Reduced    | chi-square | error    |                   |
|                                                   |     |     |     |     |     |     | h    | Convective | mass       | transfer | coefficient (m/s) |
| 1 AgriculturalandFoodEngineeringDepartment,Indian |     |     |     |     |     |     | m    |            |            |          |                   |
InstituteofTechnologyKharagpur,Kharagpur, SV Shrinkage velocity (m/s)
| WestBengal721302,India |     |     |     |     |     |     | B   | Biot Number |     |     |     |
| ---------------------- | --- | --- | --- | --- | --- | --- | --- | ----------- | --- | --- | --- |
i
123

JFoodSciTechnol(October2020)57(10):3748–3761 3749
MAE Mean absolute error along with visualization of moisture distribution inside the
MRE Mean relative error sample. In this regard, multi-physics modelling proves to
SE Standard error be highly useful, since it can combine many physics such
(cid:2) MR (cid:3) Averageexperimentalmoistureratiofortheith as heat and mass transfer, fluid dynamics, structural
exp;i
observation deformationsetc.inasinglecomputationalenvironmentto
(cid:2) (cid:3)
MR Modelpredictedaveragemoistureratioforthe visualize spatial moisture and temperature distribution
pre;i
ith observation along with the structural modifications taking place during
thedryingprocess(Kumaretal.2012).Severalresearchers
haveutilizedfiniteelement(FE)methodformodellingand
Introduction simulation of drying process (Dhalsamant et al. 2018;
Mahapatra and Tripathy 2018b).
Pineapple is one of the highly perishable fruits containing Removal of water from the solid matrix during drying
85–92% water content that leads to its faster spoilage. leads to changes in shape-size along with food transport
Preservation of this fruit can be done by drying process properties, which makes the drying process modelling
through the removal of moisture resulting in the inhibition complicated. Most of the researchers have assumed con-
of microbial growth and enzymatic reactions leading to its stant transport properties and negligible shrinkage during
enhanced shelf life. Several researchers have reported modellingthedryingprocess(Reddyetal.2017;Vallespir
differentdryingmethodsforpreservationofpineapplesuch et al. 2019). However, practically, sample dimensions
asconvectivedrying,vacuumdrying,osmoticdehydration, continuously change with time as the moisture content of
solar drying etc. (Rani and Tripathy 2019; Ramallo and sample is reduced with drying time. In some cases,
Mascheroni 2012; Bala et al. 2003). Out of these, con- shrinkage phenomena can be quite dominant and neglect-
vective dryers, being simple in their constructional design ingshrinkagecouldsignificantlylimitthemodelaccuracy.
andleastexpensiveonesaremostlypreferredforindustrial Consideration of shrinkage is important for accurate pre-
scale drying of different fruits and vegetables (Junqueira dictionofmoisture duringmodellingofthe dryingprocess
et al. 2017). assuggestedbypreviousresearches(Datta2007;Golestani
Drying is a complex phenomenon involving simultane- et al. 2013). The diffusion coefficient and mass transfer
ousheatandmasstransferbetweenthedryingmediumand coefficient are important parameters that significantly
thesample.Masstransferwithinthesampleisgovernedby affect the drying rate and are influenced by many factors
diffusion and water is lost to drying air from the sample like moisture content, temperature, shrinkage during the
surface through evaporation (Dhalsamant et al. 2017). drying process and hence play a major role in process
There is non-uniform moisture distribution inside the control, simulation and design (Khan et al. 2017). So,
sample during drying and therefore, it is necessary to incorporationofaccuratevaluesoftheseparametersduring
carefully analyze the spatial moisture distribution, so that FE modelling improves the model accuracy making the
moistureinsidethesamplecanbereducedtosafemoisture developed model more realistic for practical applications.
limit for long term storage of the commodity. However, Themajorityoftheworkdoneonpineappleislimitedto
through experimentation, it is not possible to assess the drying kinetics, thin layer mathematical modelling and
transient moisture variation within the sample. In this quality evaluation (Bala et al. 2003; Fasogbon 2013; Rani
context, mathematical modelling is one of the powerful and Tripathy 2019). Previous studies showed that no
tools proven useful to study the moisture transfer phe- computational FE model has been developed till date for
nomena for a better understanding of the drying process predictionofmoisturemigrationina3-dimensionalhollow
(Mahapatra and Tripathy 2018a). Aconsiderable work has cylindricalbodylikeinpineapplering.Furthermore,model
beenreportedondevelopmentofsemi-empiricalthinlayer development accounting shrinkage in radial and axial
mathematical models to analyze the drying behavior of direction has not been attempted yet and studies on con-
pineapple(Olanipekunetal.2015)andotherfruitssuchas sideration of variable diffusion coefficient and mass
gooseberry (Junqueira et al. 2017), apricot (Faal et al. transfer coefficient for mass transfer modelling are very
2015). Since they are empirical/semi-empirical in nature limited.Hence,themainobjectiveofthepresentstudyisto
and do not include drying process fundamentals; they developathree-dimensionalfiniteelementmodeltopredict
failed to provide physical explanation of moisture migra- transient mass transfer and visualize spatial moisture dis-
tion occurring inside food samples during drying (Khan tributioninside pineappleringsby incorporating shrinkage
et al. 2017). Hence, there is an urge toward the develop- phenomena.Furthermore,theeffectofmoisturedependent
ment of more realistic simulation model that accommo- diffusion coefficient and mass transfer coefficient on
dates the fundamentals and physics involved in heat and moisture migration mechanism during modelling has also
mass transfer andable to solve complexrealistic problems been studied.
123

3750 JFoodSciTechnol(October2020)57(10):3748–3761
Materials and methods
V ¼
(cid:4)p(cid:5)(cid:2) d2(cid:3)d2(cid:3)
l ð3Þ
4 o i
Experimental study Where, d and d are the average outer and inner diameter
o i
ofthepineapplering(m),respectivelyandlisthethickness
Fresh pineapples were cut into ring-shaped slices having of the pineapple ring (m).
dimensions as thickness (l): 10 mm; outer diameter (d o ): Further, experimental data of inner radius, outer radius,
90 mmandinnerdiameter(d i ):30 mm.Theinitialmoisture thickness, and volume change during drying was fitted to
contentofpineapplesamplewasfoundintherangeof90–92% mathematical models for the establishment of a relation
(wb) as evaluated using standard AOAC (2002) method. betweenshrinkageandmoistureratio.Linearandquadratic
Pineappleslicesweredriedinalaboratory-scalehotairdryer models shown in Eqs. 4 and 5 were fitted using non-linear
(SD Instruments, India) at a temperature of 70 (cid:3)C with a regressionanalysisinOriginPro8.5softwareandshrinkage
constantairvelocityof0.6 m/sflowingparalleltothesample kinetics was analyzed (Ponkham et al. 2012).
surface.100 gsample(4cutslicesofpineapple)wasloaded
Linear model S¼aþbðM=M Þ ð4Þ
intothe dryer in asingle layeroverstainless-steeltrays and o
driedtillthefinalmoisturecontentof25%(wb)wasreached. Quadratic model S¼aþbðM=M ÞþcðM=M Þ2 ð5Þ
o o
Thesampleweightwasmeasuredatregulartimeintervalof
Where,Sistheshrinkageparameterorshrinkagedimension;
30 minfortheentiredryingperiod.Themoisturecontentdata
a,bandcaretheequationconstants.Statisticalanalysiswas
obtainedfromdryingexperimentswerefurtherconvertedinto
carried out tocheck the accuracyofthefitted models using
moistureratio(MR)inordertonormalizetheinitialmoisture
thecoefficientofdetermination(R2),rootmeansquareerror
content (M ). The surrounding hot air is considered to be
o (RMSE), and reduced chi-square (v2) as given in Eqs. 6, 7
completelydry, hence,M can betaken asnegligible while
e
and 8 respectively (Rani and Tripathy 2019).
calculatingMRusingEq. 1(Tripathy2015).
MR¼ ðM(cid:3)M e Þ ¼ M ð1Þ NP N S pre;i S exp;i(cid:3) P N S pre;i P N S exp;i
Where,
ðM
M
o
:
(cid:3)
mo
M
is
e
t
Þ
ure
M
co
o
ntent at any time during drying (kg
R2¼v
u u t
ffi ffiffiffi
N
ffiffiffiffiffi
P
ffi
N
ffiffiffiffiffi
S
ffiffi
2 p
ffiffi
r
ffi
e
ffi
;
ffi
i
ffiffiffi
(cid:3)
ffi
i
ffi
¼
ffiffi
(cid:7)
ffi
1
ffiffiffi
P
ffi
N
ffiffiffiffiffi
S
ffiffi
2 p
ffiffi
r
ffi
e
ffiffi
;
ffi
i
ffi
(cid:8)
ffiffiffi
2
ffiffi!ffiffiffiffi
i ¼
ffiffiffi
1
ffi
N
ffiffiffiffi
P
ffi
N
ffiffiffiffiffi
S
ffi
i
ffi
¼
2 e
ffiffi
x
ffi
1
ffi
p
ffi
;
ffi
i
ffiffiffi
(cid:3)
ffiffiffiffi
(cid:7)
ffiffiffiffi
P
ffi
N
ffiffiffiffiffi
S
ffiffi
2 e
ffiffi
x
ffi
p
ffiffi
;
ffi
i
ffi
(cid:8)
ffiffiffiffi
2
ffiffi!ffiffiffi
i¼1 i¼1 i¼1 i¼1
water/kgdryweight);M :equilibriummoisturecontent(kg
e
ð6Þ
water/kg dry weight) and M : Initial moisture content (kg
o
wa M ter o /k is g tu d re ry c w on e t i e g n h t t) ( . M) was plotted with drying time and RMSE ¼ v u u t " ffiffiffiffi 1 ffiffiffiffi X ffiffi N ffiffiffiffiffi (cid:2) ffiffi S ffiffiffiffiffiffiffiffiffiffi (cid:3) ffiffiffiffiffi S ffiffiffiffiffiffiffiffiffiffi (cid:3) ffiffi 2 ffiffi # ffiffi ð7Þ
N pre;i exp;i
differentiatedusingOriginPro8.5softwaretocalculatethe i¼1
slope of the curve. The instantaneous drying rate was
N
calculatedateverytimeintervalduringdryingusingEq. 2 P(cid:2) S (cid:3)S (cid:3)2
exp;i pre;i
(Geankoplis 1983). v2 ¼i¼1 ð8Þ
N(cid:3)f
(cid:3)W oM
DR¼ s ð2Þ
A ot Where, S pre,i : predicted shrinkage parameter; S exp,i :
experimental shrinkage parameter; N: number of observa-
Where,DR:dryingrate((kg/h.m2);W:weightofdrysolid
s tions; f: number of constants.
(kg);A:exposedsurfacearea(m2).Theaveragedryingrate
was estimated by taking the arithmetic mean of instanta-
Determination of mass transfer parameters
neous drying rate data.
during drying
Shrinkage study
The governing equation explaining the transient behavior
of moisture migration within the food sample for infinite
Duringdrying,thedimensionsofpineappleslices(l,d,d )
i o plate is given by Eq. 9.
were measured at regular time interval of 1 h using a
(cid:7) (cid:8) (cid:9) (cid:7) (cid:8)(cid:10)
digital vernier caliper (Moore and Wright, Europe, ± oM 1 o oM
¼D y ð9Þ
0.01 mm). Since, change in dimension during drying was ot y oy oy
not uniform at every point of boundary; hence dimensions
Where,y = thicknessoftheslice;yandtarethespaceand
weremeasuredatdifferentpositionsofthepineappleslice.
timecoordinates,respectively.Theinitialmoisturecontent
The average values of sample dimensions were used for
of the sample is considered to be uniformly distributed.
calculationofvolume(V)ofpineappleringaspresentedin
Duringdrying,moisturemigrationtakesplacebydiffusion
Eq. 3.
123

JFoodSciTechnol(October2020)57(10):3748–3761 3751
fromthesampletosurface,governedbyeffectivemoisture
Where, l is the diffusion path (m).
diffusivity and from the surface to drying air due to con- d
vection, which is governed by convective mass transfer
Finite element model development
coefficient. The term ‘‘effective moisture diffusivity (D)’’
is used to refer to overall transport coefficient which takes
A 3-D, FE model was developed for visualizing spatial
in to account all the moisture transport phenomena occur-
moisture distribution inside the sample and moisture
ring namely molecular diffusion, liquid diffusion, vapour
removal from the surface during convective drying of
diffusion, hydrodynamic flow etc.
pineapple slices. The pineapple slice was assumed as a
The integration of analytical solution of Eq. (9) with
hollow cylinder of finite thickness, inner and outer radius.
mentioned consideration provides the volume mean mois-
During finite element modelling and simulation of drying
ture content of the slice and the final solution for dimen-
process, following assumptions were considered for sim-
sionlessmeanmoisturecontentforinfinitesliceisgivenby
plification of the problem.
following expression (10), according to the methodology
developed by Tripathy and Kumar (2009). 1. Initial moisture content is uniform throughout the
M(cid:3)M 2sin2l (cid:7) Dt (cid:8) pineapple sample.
MR¼ e ¼ 1 exp (cid:3)l2 2. Pineapple sample is assumed to be isotropic and
M (cid:3)M l ðl þsinl cosl Þ 1 l2
o e 1 1 1 1 homogenous.
ð10Þ 3. Masstransfertakesplacewithinsolidsampleonlydue
todiffusionandevaporationoccursattopsurfacealong
The surrounding hot air is considered to be completely
with internal and external boundaries of pineapple
dry, hence, M can be taken as negligible, which gives
e
slice.
simplified MR as, MR¼ M. Further, after rearrangement,
Mo 4. Deformation of pineapple slice occurs in all directions
Eq. (10) can be expressed as (Dhalsamant et al. 2017).
except in bottom surface.
(cid:7) (cid:9)
MRl ½l þsinl cosl (cid:4)
(cid:10)(cid:8)(cid:7) (cid:3)l2(cid:8)
5. Air distribution is uniform throughout the dryer and
D¼ ln 1 1 1 1 ð11Þ
2sin2l tl2 drying takes place at isothermal conditions.
1 1
The parameter l is obtained using the following
1
expressions (Luikov 1968). Model formulation physics
1
l2 1 ¼ðl 1 Þ2 11þ A1 ð12Þ In convective drying of food, heat gets transferred from
Bip dryingairtosampleandmoisturegetstransportedfromthe
Where, Bi is the Biot number for mass transfer; ðl Þ A interior of the food matrix to the surface due to diffusion
1 1 1
and p, are constants whose values are 1.5708, 2.24 and and further, from the surface to drying air due to evapo-
1.02, respectively. ðl Þ is the value of l when ration. The rate of the moisture transfer is dependent upon
1 1 1
Bi¼1(Luikov 1968). the velocity field, temperature difference as well as mois-
The biot number for mass transfer is determined using ture concentration difference between sample and drying
the given Eq. 13 (Pflug and Blaisdell 1963). air(Sabarez2012).Masstransferwithinthefoodsampleis
explained by Fick’s second law of diffusion as given in
3:356lnðc Þ
Bi¼ o ð13Þ Eq. 15, which was used to model the transient moisture
1(cid:3)1:974lnðc Þ
o distribution inside the food sample (Valentas et al. 1997).
Where,c isthelagfactorofthinlayerequationdescribing
o oM
drying characteristics. ot þrð(cid:3)DrMÞþurM ¼R sam ð15Þ
Since, moisture diffusivity of the sample varies with
Where,M isthe moistureconcentrationofsample,D isthe
changingmoisturecontentduringdrying;thus,dryingtime
diffusioncoefficient(m2/s),uisthevelocityfieldofthespe-
was divided into several small segments while calculating
ciesandR istheproduction/consumptionofspeciesduring
the moisture dependent moisture diffusivity. sam
reaction.Inthepresentstudy,pineappleringwasconsideredat
Further, the convective mass transfer coefficient (h )
m
rest and no chemical reaction was involved during drying
was calculated using the following standard expression
experiment.Therefore,variablesu,R wereneglectedand
(Eq. 14) relating mass transfer coefficient, moisture diffu- sam
the simplified generalized equation for mass transfer due to
sivity and Biot number (Guine 2012).
diffusioninsidethefoodmatrixisgivenbyEq. 16.
D
h ¼Bi ð14Þ
m l oM
d ¼rðDrMÞ ð16Þ
ot
123

3752 JFoodSciTechnol(October2020)57(10):3748–3761
distancevaryingfrombottom(z = 0)totopsurface(z = l)
Fick’s second law of diffusion equation for transient
in longitudinal direction.
moisture transfer in three-dimensional hollow cylindrical
Shrinkage velocity: The samples undergone structural
body with an inner and outer radius as r and r respec-
i o changesinradialaswellasinlongitudinaldirectionduring
tively, is defined by Eq. 17 (Watson et al. 2010).
the drying process and the respective dimensional changes
oM (cid:7) 1 o (cid:7) oM (cid:8)(cid:8) (cid:7) 1o2M (cid:8) (cid:7) o2M (cid:8) measured during the experiment were explained in section
¼D r þD þD ;
ot ror or r ou2 oz2 ‘‘Shrinkage study’’. Shrinkage phenomena was accommo-
r (cid:5)r(cid:5)r ; 0(cid:5)u(cid:5)2p; 0(cid:5)z(cid:5)l dated into FE modelling by incorporating shrinkage
i o
velocity as an input parameter through moving mesh
ð17Þ
module. Shrinkage estimation in radial and longitudinal
Where, r, u and z are the distance in radial, angular and direction was followed by the establishment of a relation-
longitudinal direction, respectively. ship between shrinkage parameter and moisture content
using regression analysis for inner radius, outer radius and
Boundary conditions thickness for the pineapple sample. Further, shrinkage
velocity was calculated using the distance and time rela-
Inthepresentcase,pineapplesliceswereplacedonstainless tionship as shown in Eqs. 23 and 24, respectively.
steeltrayanddryingairwasflowingoverit.Hence,moisture S¼aM2þbMþc ð23Þ
transfer was taking place from top surface, internal and
S
external boundaries which were exposed to drying air. So SV ¼ ð24Þ
masstransferwasassumedtobetakingplaceintwodirec- t
tions, i.e., along the radius and thickness. The initial and Where, S is the shrinkage parameter (m) (inner radius,
boundary conditions applied during drying modelling are: outerradius,thickness);SVisshrinkagevelocity(m/s)and
moisture is homogeneous in the sample, convective mass t is time (s).
transfertakesplacefromtopsurface,innerandoutersidesof
the pineapple ring and null mass flux has been provided at Input parameters to model
bottom surface as shown in Fig. 1a. Initial and boundary
conditionsdefinedareexpressedinEqs.18–22. The initial moisture content of pineapple slice during FE
modelling was given as 12.76 kg water/kg dry solid, as
At t ¼ 0; M ¼M ðR;u;zÞ
0
r experimentally calculated. The density of the pineapple
0(cid:5)z(cid:5)l; i (cid:5)R(cid:5)1; 0(cid:5)u(cid:5)2p sample was kept as 980 kg/m3 (Ikegwu and Ekwu 2009).
r
o
r The diffusion coefficient and mass transfer coefficient
WhereR¼ ð18Þ
r estimated using Eq. 10–14 were used to model the mois-
o
ture migration mechanism considering constant and mois-
(cid:7) (cid:8)(cid:11)
oM (cid:11)
At t[ 0; D oz (cid:11) (cid:11) ¼h m ðM(cid:3)M 1 Þ ture dependent mass transfer parameters.
z¼l ð19Þ
r
z¼l; i (cid:5)R(cid:5)1; 0(cid:5)u(cid:5)2p Simulation procedure
r
o
(cid:7) (cid:8)(cid:11)
oM (cid:11) The 3-D model was developed to simulate the moisture
D oR (cid:11) (cid:11) R¼ri ¼h m ðM(cid:3)M 1 Þ ð20Þ migration mechanism of pineapple slice considering
0(cid:5)z(cid:5)l; ro R¼ r i; 0(cid:5)u(cid:5)2p structural changes occurring during drying. Along with
r shrinkage consideration, moisture dependent diffusion
o
(cid:7) (cid:8)(cid:11) coefficient and convective mass transfer coefficient were
oM (cid:11)
D oR (cid:11) (cid:11) ¼h m ðM(cid:3)M 1 Þ ð21Þ alsoincludedinthemodelformakingitmorerealistic.The
R¼1 partial differential equations governing the mass transfer
0(cid:5)z(cid:5)l; R¼1; 0(cid:5)u(cid:5)2p
process were solved using COMSOL Multiphysics 5.3, a
(cid:7) (cid:8)(cid:11)
D oM (cid:11) (cid:11) ¼0 z¼0; r i (cid:5)R(cid:5)1; 0(cid:5)u(cid:5)2p ð22Þ commercial computational software package. The 3-D
oR (cid:11) r geometryofpineappleslicewasformed andmeshed using
z¼0 o
finer meshing as shown in Fig. 1b, c. The domain was
Where, M is the moisture content of sample, M is the
1 consisted of 29,298 tetrahedral and 4360 triangular ele-
moisture content at the sample surface. R¼ r; where r is
ro ments with minimum element quality of 0.2083 and mesh
the distance in radial direction varying from inner radius volume as 5.644 9 10–5 m3. The stepwise procedure fol-
(r i ) to outer radius (r o ) and when r = r o , R = 1. z is the lowedduringFEmodellingofthedryingprocessisshown
inFig. 1d.Transportofdilutedspeciesmodulewasusedto
123

JFoodSciTechnol(October2020)57(10):3748–3761 3753
a
|     | b   |     |     | c   |
| --- | --- | --- | --- | --- |
d
Fig.1 Finiteelementmodellingprocedureacomputationaldomainofthemodelshowingboundaryconditions,b3-Dgeometryofpineapple
slice,cmeshingofgeometryinCOMSOLMultiphysicssoftware(d)flowchartshowingmodeldevelopmentstrategyinCOMSOLsoftware
model the mass transfer phenomena to predict spatial FE model validation
| moisture distribution | inside | the sample. | The Arbitrary |     |
| --------------------- | ------ | ----------- | ------------- | --- |
LagrangianEulerian (ALE)approachwasattemptedinthe TheFE masstransferCOMSOLmodelwas validated with
model to account shrinkage led structural changes occur- experimental drying results. The correctness of the devel-
ring in the sample during drying. In the ALE method, oped model was evaluated through extensively used sta-
equationswereadjustedtoaccountmeshmovementduring tistical error analysis: mean absolute error (MAE), mean
themodellingprocess.Themodelwassolvedusingatime- relative error (MRE) and standard error (SE) using
| dependent study | with time | step of 900 s | up to 37,800 s. | Eqs. 25–27. |
| --------------- | --------- | ------------- | --------------- | ----------- |
123

| 3754 |     |                 |         |                 |          |     |      |     |     | JFoodSciTechnol(October2020)57(10):3748–3761 |     |     |     |     |
| ---- | --- | --------------- | ------- | --------------- | -------- | --- | ---- | --- | --- | -------------------------------------------- | --- | --- | --- | --- |
|      | 1X  | N (cid:11)      |         |                 | (cid:11) |     |      |     | 14  | a                                            |     |     |     |     |
|      |     | (cid:11)(cid:2) | (cid:3) | (cid:2) (cid:3) |          |     |      |     |     |                                              |     |     |     |     |
| MAE¼ |     | MR              | (cid:3) | MR              | (cid:11) |     | ð25Þ |     |     |                                              |     |     |     |     |
|      | N   | (cid:11)        | exp;i   | pre;i(cid:11)   |          |     |      |     |     |                                              |     |     |     |     |
|      |     | i¼1             |         |                 |          |     |      |     | 12  |                                              |     |     |     |     |
)bd( tnetnoc erutsioM
|      |     | (cid:11) (cid:2) | (cid:3)         | (cid:2) (cid:3) | (cid:11) |     |      |     | 10  |     |     |     |     |     |
| ---- | --- | ---------------- | --------------- | --------------- | -------- | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
|      |     | N (cid:11) MR    | (cid:3)         | MR              | (cid:11) |     |      |     |     |     |     |     |     |     |
|      | 1X  | (cid:11)         | exp;i           | pre;i           | (cid:11) |     |      |     |     |     |     |     |     |     |
| MRE¼ |     |                  |                 |                 |          |     | ð26Þ |     | 8   |     |     |     |     |     |
|      | N   |                  | (cid:2) (cid:3) |                 |          |     |      |     |     |     |     |     |     |     |
MR
|     |                      | i¼1                                                        |                                          | exp;i                                                     |                  |     |     |     | 6   |     |     |     |     |     |
| --- | -------------------- | ---------------------------------------------------------- | ---------------------------------------- | --------------------------------------------------------- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|     | rffi ffiffiffiffiffi | ffiffiffiffiffiffi ffiffiffi ffiffi ffiffiffiffi ffiffiffi | ffiffiffiffiffiffiffiffiffi ffiffiffiffi | ffiffi ffiffiffiffi ffiffiffi ffiffiffiffiffiffiffiffiffi | ffiffiffi ffiffi |     |     |     |     |     |     |     |     |     |
|     |                      | (cid:4)                                                    |                                          |                                                           | (cid:5) 2        |     |     |     | 4   |     |     |     |     |     |
|     | P                    | N (cid:2) M R                                              | (cid:3) (cid:3)                          | (cid:2) M R (cid:3)                                       |                  |     |     |     |     |     |     |     |     |     |
i¼1
|     |     |     | exp;i | pre;i |     |     |      |     | 2   |     |     |     |     |     |
| --- | --- | --- | ----- | ----- | --- | --- | ---- | --- | --- | --- | --- | --- | --- | --- |
| SE¼ |     |     |       |       |     |     | ð27Þ |     |     |     |     |     |     |     |
N(cid:3)1
0
|        |            |            |     |         |              |     |          |     | 0   | 2   | 4   | 6   | 8   | 10 12 |
| ------ | ---------- | ---------- | --- | ------- | ------------ | --- | -------- | --- | --- | --- | --- | --- | --- | ----- |
| Where, | (cid:2) MR | (cid:3) is | the | average | experimental |     | moisture |     |     |     |     |     |     |       |
Drying time (h)
|          | (cid:2) | (cid:3) exp;i                         |     |     |     |     |     |     |     |     |     |     |     |     |
| -------- | ------- | ------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ratioand |         | MR isthemodelpredictedaveragemoisture |     |     |     |     |     |     |     |     |     |     |     |     |
pre;i
| ratio | for the | ith observation. |     | N   | is the total | number | of  |     | 1.6 b |     |     |     |     |     |
| ----- | ------- | ---------------- | --- | --- | ------------ | ------ | --- | --- | ----- | --- | --- | --- | --- | --- |
1.4
| observations. |     |     |     |     |     |     |     |  )h.2m/retaw gk( etar gniyrD |     |     |     |     |     |     |
| ------------- | --- | --- | --- | --- | --- | --- | --- | ---------------------------- | --- | --- | --- | --- | --- | --- |
1.2
1
| Results | and | discussion |     |     |     |     |     |     |     |     |     |     |     |     |
| ------- | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
0.8
0.6
Drying kinetics
0.4
0.2
Pineappleslicesweredriedfromaninitialmoisturecontent
0
of92%tofinalmoistureof25%(wb)inhotairdryer.The 0 2 4 6 8 10 12 14
totaldryingtimetakentoattaintherequiredfinalmoisture Moisture content (db)
| content | in  | the sample | was | 10.5 h. | The drying | kinetics | of  |     |     |     |     |     |     |     |
| ------- | --- | ---------- | --- | ------- | ---------- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
0.5 c
pineapple samples at a constant drying air temperature of Drying (cid:2)me (h)
0
70 (cid:3)CisshowninFig. 2a.Itcanbeobservedthattheslopeof -0.5 0 2 4 6 8 10 12
| themoisture-timecurve(oM=ot)washigherduringtheini- |       |                                            |          |              |     |          |        |        | -1   |     |     |     |     |     |
| -------------------------------------------------- | ----- | ------------------------------------------ | -------- | ------------ | --- | -------- | ------ | ------ | ---- | --- | --- | --- | --- | --- |
| tial                                               | hours | of drying                                  | and kept | on declining |     | with the | drying |        | -1.5 |     |     |     |     |     |
|                                                    |       |                                            |          |              |     |          |        | )RM(nl | -2   |     |     |     |     |     |
| time.Figure                                        |       | 2brepresentsthevariationindryingrateduring |          |              |     |          |        |        |      |     |     |     |     |     |
-2.5
| the | drying | of pineapple | samples. |     | It can be | observed | that |     |     |     |     |     |     |     |
| --- | ------ | ------------ | -------- | --- | --------- | -------- | ---- | --- | --- | --- | --- | --- | --- | --- |
-3
dryingratereducedwiththedecreaseinmoisturecontentand -3.5 y = -0.0204x2-0.134x -0.0986
the average drying rate of pineapple slice was found to be -4 R² = 0.99
-4.5
| 0.47 | ± 0.03 | kg water/m2.h. |     | Further, | a curve | was | drawn |     |     |     |     |     |     |     |
| ---- | ------ | -------------- | --- | -------- | ------- | --- | ----- | --- | --- | --- | --- | --- | --- | --- |
-5
| between | ln  | (MR) and | drying | time | as illustrated | in  | Fig. 2c, |     |     |     |     |     |     |     |
| ------- | --- | -------- | ------ | ---- | -------------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
which clearly depictedthedeviation ofthe curvefromlin- Fig. 2 Drying characteristics of pineapple slices under convective
earity.Asimilarkindofnon-linearitywasalsoobservedby dryingadryingkinetics,bdryingrate,cnon-linearityofln(MR)vs
dryingtime
Younisetal.(2018)duringinfra-reddryingofgarlicslices.
Suchtypeofnon-linearityofln(MR)andtimecurvemight
|     |     |     |     |     |     |     |     | Shrinkage |     | kinetics |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | --- | -------- | --- | --- | --- | --- |
bethecombinedeffectofdifferentfactorslikenon-unifor-
mityofinitialmoisture,shrinkageandchangingofthedif-
Shrinkageisthecommonphenomenonobservedduringhot
| fusion | coefficient |     | during | drying. | Therefore, | this | is an |     |     |     |     |     |     |     |
| ------ | ----------- | --- | ------ | ------- | ---------- | ---- | ----- | --- | --- | --- | --- | --- | --- | --- |
airdryingofmostfruits.Pineappleslicesdriedinthepresent
| indication |     | of the variation |     | of diffusion | coefficient |     | with the |     |     |     |     |     |     |     |
| ---------- | --- | ---------------- | --- | ------------ | ----------- | --- | -------- | --- | --- | --- | --- | --- | --- | --- |
studyshowedshrinkageinradialandlongitudinaldirections,
reductionofsamplemoisturecontentduringdrying.Asec-
respectively.Pictorialrepresentationofshrinkagephenom-
lnðMRÞ¼at2þbtþc;
ond-order quadratic equation, was ena in the radial direction is shown in Fig. 3a. Further,
| fitted | to experimental |     | data | using | non-linear | regression |     |      |      |          |               |     |           |             |
| ------ | --------------- | --- | ---- | ----- | ---------- | ---------- | --- | ---- | ---- | -------- | ------------- | --- | --------- | ----------- |
|        |                 |     |      |       |            |            |     | Fig. | 3b–e | depicted | the shrinkage |     | of hollow | cylindrical |
analysis.Itwasfoundthattherelationestablishedbyfitted
|     |     |     |     |     |     |     |     | pineappleslicesintermsofvariation |     |     |     |     | ofinnerradius, | outer |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------------------------- | --- | --- | --- | --- | -------------- | ----- |
second-orderquadraticequationbetweenln(MR)anddry-
radius,thicknessandsamplevolumeasafunctionofmois-
| ing | time was | in good | agreement | with | experimental |     | data as |     |     |     |     |     |     |     |
| --- | -------- | ------- | --------- | ---- | ------------ | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
tureratio.Externalradiusshowedareducingtrendfroman
| indicatedbyahighvalueofR2 |     |     |     | = 0.99. |     |     |     |             |        |                                          |        |     |            |           |
| ------------------------- | --- | --- | --- | ------- | --- | --- | --- | ----------- | ------ | ---------------------------------------- | ------ | --- | ---------- | --------- |
|                           |     |     |     |         |     |     |     | initial     | value  | of 4.51                                  | ± 0.02 | cm  | to a final | radius of |
|                           |     |     |     |         |     |     |     | 3.05        | ± 0.04 | cmwithrespecttodecreasingmoisturecontent |        |     |            |           |
|                           |     |     |     |         |     |     |     | ofthesample |        | asdryingprogressed.Itshouldbetakeninto   |        |     |            |           |
noticethatduringtheinitialhoursofdrying,innerradiusof
123

| JFoodSciTechnol(October2020)57(10):3748–3761 |     |     |     |     |     |     |     |     |     |     |     | 3755 |
| -------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- |
the pineapple slice was slightly increased by 0.04 cm, convectivemasstransfercoefficient for the pineapple slices
however, after 3 h of drying, inner radius started reducing during hot air drying were estimated as 1.90 9 10–9 m2/s
10–7
and sample was shrunk up to 0.7 ± 0.05 cm. Water was and 9.58 9 m/s, respectively. The moisture dependent
migratingfromthecentertowardstheboundariesofsample diffusioncoefficientandconvectivemasstransfercoefficient
and the sample was shrinking in the opposite direction of were determined as a function of moisture content (M) as
moisture removal. Shrinkage from the external boundaries represented by the following polynomial equations:
|     |     |     |     |     |     |     |     | 10–11 M2 |     | 10–10 |     | 10–10 |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | --- | ----- | --- | ----- |
wasintotheinwarddirectionandinnerradiuswasincreasing D = - 4 9 ? 6 9 M – 3 9
due to shrinkage in outward direction leading to slight (R2 = 0.81) and h = - 2 9 10–8 M2 ? 3 9 10–7
m
10–7 (R2
internalexpansion.FromFig. 3a,itcouldbeclearlyinferred M ? 4 9 = 0.83) respectively. These values
that intensity of shrinkage increased with time. However, were used for the development of FE modelto explain the
after3–4 hofdrying,shrinkagefromouterboundarieswas moisture migration mechanism.
| more dominated | and | hence whole | body | started | shrinking |     |     |     |     |     |     |     |
| -------------- | --- | ----------- | ---- | ------- | --------- | --- | --- | --- | --- | --- | --- | --- |
inward.Thicknessofthesamplewascontinuouslyreducing Moisture transfer model validation
withincreasingdryingtimeandreducingmoisturecontent.
Therewasa79.3%reductioninthicknessofpineappleslice Inthepresentwork,dryingkineticswasinvestigatedthrough
during the total drying period and thickness of the dried FE modelling under five different set of conditions namely:
sample was found as 0.21 ± 0.04 cm. Outer and inner withandwithoutshrinkageconsideration,usingconstantand
diameter showeda32.2%and51.28%reductioninsample moisture dependent diffusion coefficient and mass transfer
dimensions, respectively during the drying process. Ponk- coefficient. Drying kinetics was studied by developing dif-
hametal.(2012)alsoobservedasimilartrendofshrinkage ferent models and considering constant average diffusion
kinetics during far-infrared drying of pineapple rings. To coefficient (CD) and moisture dependent variable diffusion
explain the relationship between shrinkage and moisture coefficient (VD). Similarly, the effect of assuming constant
content during drying, linear and second-order polynomial masstransfercoefficient(Ch )andmoisturedependentmass
m
modelswerefittedtoexperimentaldata.Modelconstantsand transfer coefficient (Vh ) on drying kinetics was also ana-
m
statistical analysis of fitted model for inner radius, outer lyzedbydevelopingdifferentmodelsincorporatingshrinkage
radius,thicknessandvolumechangeisshowninTable1.It study. Developed moisture models were validated with
can be clearly stated that quadratic model showed higher experimental results by comparing the predicted average
valuesofR2andlowervaluesofRMSEandv2thanthatofa moisturecontentofthesampleandexperimentallyestimated
linear model for all shrinkage dimensions. It indicates the moisture content. The predicted average moisture content of
capabilityofthequadraticmodeltoestablishmoreaccurate thesamplewasestimatedbytakingthevolumetricaverageof
relation between shrinkage dimension and reducing mois- spatial moisture content as given by the model, calculated
tureratioascomparedtothelinearmodel.Theseresultsare using Eq. 28 (Golestani et al. 2013).
| ingoodagreementwiththeoutcomesofworkcarriedoutby |                |      |               |      |           |     | 1Z  |            |     |     |     |      |
| ------------------------------------------------ | -------------- | ---- | ------------- | ---- | --------- | --- | --- | ---------- | --- | --- | --- | ---- |
|                                                  |                |      |               |      |           | M ¼ |     | Mðr;z;tÞdV |     |     |     | ð28Þ |
| Ponkham                                          | et al. (2012). | They | also revealed | that | quadratic | pre |     |            |     |     |     |      |
V
| model was | best fitted    | for shrinkage | modelling |          | during far- |        |     |                |          |         |           |     |
| --------- | -------------- | ------------- | --------- | -------- | ----------- | ------ | --- | -------------- | -------- | ------- | --------- | --- |
|           |                |               |           |          |             | Where, | M   | is the average | moisture | content | predicted | by  |
| infrared  | and air drying | of pineapple  | rings.    | However, | con-        |        | pre |                |          |         |           |     |
themodel,Visthevolumeofthesample(m3);Mðr;z;tÞis
| tradictory | to it, linear      | relationship | between    | shrinkage | and       |              |     |         |                |          |     |            |
| ---------- | ------------------ | ------------ | ---------- | --------- | --------- | ------------ | --- | ------- | -------------- | -------- | --- | ---------- |
|            |                    |              |            |           |           | the moisture |     | content | at any spatial | position |     | inside the |
| moisture   | ratio was observed | during       | convective |           | drying of |              |     |         |                |          |     |            |
potatoslab(Aprajeetaetal.2015)carrotslab(Madioulietal. sample at any instant t.
2012)andpumpkin(Mayoretal.2011).
|               |            |     |     |     |     | Moisture    | migration | considering | variable    |     | mass | transfer |
| ------------- | ---------- | --- | --- | --- | --- | ----------- | --------- | ----------- | ----------- | --- | ---- | -------- |
|               |            |     |     |     |     | coefficient | and       | diffusion   | coefficient |     |      |          |
| Mass transfer | parameters |     |     |     |     |             |           |             |             |     |      |          |
Figure 4ashowsthecomparisonofmoistureratioobtained
| The diffusion | coefficient | and mass | transfer | coefficient | are |     |     |     |     |     |     |     |
| ------------- | ----------- | -------- | -------- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- |
important parameters that govern the moisture transfer from experimental and FE model predicted values for
|           |          |         |       |            |        | different | test | conditions | while considering |     | shrinkage: | with |
| --------- | -------- | ------- | ----- | ---------- | ------ | --------- | ---- | ---------- | ----------------- | --- | ---------- | ---- |
| mechanism | and were | used as | input | parameters | during |           |      |            |                   |     |            |      |
modelling of drying process. Average values of h and D (a) average h , variable D; (b) average h , average D;
|     |     |     |     |     | m   |              |     | m           |                 |     | m            |      |
| --- | --- | --- | --- | --- | --- | ------------ | --- | ----------- | --------------- | --- | ------------ | ---- |
|     |     |     |     |     |     | (c) variable |     | h , average | D; (d) variable |     | h , variable | D As |
were estimated by taking the arithmetic mean of all the m m .
values calculated for different time segments during the shown in the figure, reduction in moisture ratio during the
|                |          |           |           |     |              | initial | one hour | of drying | was almost |     | same under | all the |
| -------------- | -------- | --------- | --------- | --- | ------------ | ------- | -------- | --------- | ---------- | --- | ---------- | ------- |
| drying period. | Moisture | dependent | relations |     | of diffusion |         |          |           |            |     |            |         |
coefficient and convective mass transfer coefficient were conditions. However, it was observed that, after 1 h of
|          |                     |            |     |          |         | drying, | there | was more | difference | between |     | the experi- |
| -------- | ------------------- | ---------- | --- | -------- | ------- | ------- | ----- | -------- | ---------- | ------- | --- | ----------- |
| obtained | from the non-linear | regression |     | analysis | (Sharma |         |       |          |            |         |     |             |
and Prasad 2004). The average diffusion coefficient and mental values of moisture ratio and those predicted by
123

| 3756 |     |     | JFoodSciTechnol(October2020)57(10):3748–3761 |     |     |
| ---- | --- | --- | -------------------------------------------- | --- | --- |
a
| 2 b |     |     | c   |     |     |
| --- | --- | --- | --- | --- | --- |
5
| 1.5 |     |     | 4   |     |     |
| --- | --- | --- | --- | --- | --- |
)mc( suidar rennI
)mc( suidar retuO
3
1
|     |     | Experimental |     |     | Experimental |
| --- | --- | ------------ | --- | --- | ------------ |
2
|     |     | Linear Model |     |     | Linear Model |
| --- | --- | ------------ | --- | --- | ------------ |
0.5
Quadra(cid:2)c Model
|       |                     |       | 1     |                     | Quadra(cid:2)c Model |
| ----- | ------------------- | ----- | ----- | ------------------- | -------------------- |
| 0     |                     |       | 0     |                     |                      |
| 0 0.2 | 0.4 0.6             | 0.8 1 | 0 0.2 | 0.4 0.6             | 0.8 1                |
|       | Moisture ra(cid:2)o |       |       | Moisture ra(cid:2)o |                      |
| d     |                     |       | 1.2   |                     |                      |
1.2
e
1
1
| )mc( ssenkcihT |     | o(cid:2)ar emuloV | 0.8 |     |     |
| -------------- | --- | ----------------- | --- | --- | --- |
0.8
0.6
0.6
Experimental
0.4
| 0.4 | Experimental |     |     |     | Linear Model |
| --- | ------------ | --- | --- | --- | ------------ |
Linear Model
Quadra(cid:2)c Model
| 0.2 |     |     | 0.2 |     |     |
| --- | --- | --- | --- | --- | --- |
Quadra(cid:2)c Model
| 0     |                     |       | 0     |                     |       |
| ----- | ------------------- | ----- | ----- | ------------------- | ----- |
| 0 0.2 | 0.4 0.6             | 0.8 1 | 0 0.2 | 0.4 0.6             | 0.8 1 |
|       | Moisture ra(cid:2)o |       |       | Moisture ra(cid:2)o |       |
Fig.3 Shrinkagephenomenaduringpineappleslicedryingapictorialrepresentationofpineappleslicesshowingtheoccurrenceofshrinkage
throughoutthedryingperiod;dimensionalvariationsandmathematicalmodelsfittedtopineappleslicesduringhotairdryingforbinnerradius,
couterradius,dthicknessandevolumeofsample
assuming average moisture diffusivity. The finite element coefficient were not much different, which might be
model prediction using moisture dependent diffusion because of less variation in the value of mass transfer
coefficientwasfoundtobeveryclosetoexperimentaldata. coefficient during drying. These results were also con-
Itisnoteworthytomentionthatdryingcurvespredictedby firmed by the statistical analysis given in Table 2. Models
taking constant and moisture dependent mass transfer developed with the consideration of variable moisture
123

| JFoodSciTechnol(October2020)57(10):3748–3761 |     |     |     |     |     |     | 3757 |
| -------------------------------------------- | --- | --- | --- | --- | --- | --- | ---- |
Table1 Estimatedvaluesofequationconstantsandstatisticalerrorsofmodelsfittedtoshrinkagedimensionsofpineappleslices
| Shrinkagedimension | Model | Equationconstants |     |     | R2  | v2  | RMSE |
| ------------------ | ----- | ----------------- | --- | --- | --- | --- | ---- |
Innerradius Linearmodel a=0.00891,b=0.00856 0.76 2.20910–6 1.48910–3
|     |                |                                |     |     |      | 9.29910–8 | 3.05910–4 |
| --- | -------------- | ------------------------------ | --- | --- | ---- | --------- | --------- |
|     | Quadraticmodel | a=0.00701,b=0.02323,c=-0.01538 |     |     | 0.98 |           |           |
Outerradius Linearmodel a=0.03218,b=0.01527 0.91 2.20910–6 1.48910–3
|     |                |                                |     |     |      | 1.80910–7 | 4.24910–4 |
| --- | -------------- | ------------------------------ | --- | --- | ---- | --------- | --------- |
|     | Quadraticmodel | a=0.03031,b=0.02965,c=-0.01508 |     |     | 0.99 |           |           |
Thickness Linearmodel a=0.00246,b=0.00881 0.96 2.69910–6 5.47910–4
|        |                |                                |     |     |      | 8.55910–7 | 3.26910–4 |
| ------ | -------------- | ------------------------------ | --- | --- | ---- | --------- | --------- |
|        | Quadraticmodel | a=0.00187,b=0.01336,c=-0.00477 |     |     | 0.98 |           |           |
| Volume | Linearmodel    | a=0.08793,b=0.97188            |     |     | 0.96 | 0.01159   | 0.0355    |
Quadraticmodel a=0.06796,b=1.12556,c=-0.16112 0.98 0.00119 0.0344
Where,a,b,caretheregressionequationconstants
Fig.4 Validationofdeveloped
1 a
| finiteelementmodelfor |     |     |     |     | Experimental MR |     |     |
| --------------------- | --- | --- | --- | --- | --------------- | --- | --- |
moistureratio(MR)aaverage
|     |     | 0.9 |     |     | Predicted MR (VD, Vhm) |     |     |
| --- | --- | --- | --- | --- | ---------------------- | --- | --- |
andmoisturedependent
Predicted MR (CD, Vhm)
diffusioncoefficientandmass
0.8
| transfercoefficientwith   |     |     |     |     | Predicted MR (CD, Chm) |     |     |
| ------------------------- | --- | --- | --- | --- | ---------------------- | --- | --- |
| considerationofshrinkage, |     | 0.7 |     |     | Predicted MR (VD, Chm) |     |     |
bwithandwithoutshrinkage
| considerationwithvarying |     | o(cid:2)ar erutsioM 0.6 |     |     |     |     |     |
| ------------------------ | --- | ----------------------- | --- | --- | --- | --- | --- |
diffusioncoefficientandmass
| transfercoefficient;Spatial |     | 0.5 |     |     |     |     |     |
| --------------------------- | --- | --- | --- | --- | --- | --- | --- |
moisturedistributionwithin
0.4
pineapplesliceduringdryingas
predictedbyfiniteelement
0.3
modelconsideringshrinkage,
| variablediffusioncoefficient |     | 0.2 |     |     |     |     |     |
| ---------------------------- | --- | --- | --- | --- | --- | --- | --- |
andmasstransfercoefficient,
| c3-dimensionalview,dtop |     | 0.1 |     |     |     |     |     |
| ----------------------- | --- | --- | --- | --- | --- | --- | --- |
view
0
|     |     | 0 1 | 2 3 | 4 5 | 6 7 | 8   | 9 10 11 |
| --- | --- | --- | --- | --- | --- | --- | ------- |
Drying (cid:2)me (h)
1
|     |     | b   |     |     | Predicted MR (with Shrinkage) |     |     |
| --- | --- | --- | --- | --- | ----------------------------- | --- | --- |
0.9
Predicted MR (without shrinkage)
Experimental MR
0.8
0.7
o(cid:2)ar erutsioM
0.6
0.5
0.4
0.3
0.2
0.1
0
|     |     | 0 1 | 2 3 | 4 5 | 6 7 | 8 9 | 10 11 |
| --- | --- | --- | --- | --- | --- | --- | ----- |
Drying (cid:2)me (h)
123

3758 JFoodSciTechnol(October2020)57(10):3748–3761
c
MC (db) MC (db)
t=0 hour t=2 hours
MC (db)
MC (db)
t=4 hours t=6 hours
MC (db) MC (db)
t= 8 hours t=10 hours
Fig.4 continued
diffusivity presented lower values as compared to models Effect of shrinkage consideration on moisture migration
developedwithconstantdiffusivityassumption.Moreover, during modelling
modeldevelopedwithconsiderationofmoisturedependent
h and D, showed the lowest values of MAE, MRE and It was confirmed from the graphical representation
m
SE, representing the best fitting of model predicted result (Fig. 4a) and statistical analysis (Table 2) results that
withexperimentalvalues.Simaletal.(2006)alsoreported moisture migration was best predicted by the model con-
that the use of moisture dependent effective moisture dif- sidering shrinkage along with moisture dependent h and
m
fusivity during modelling of pineapple slices predicted D. Further, the effect of without shrinkage consideration
moresatisfactoryresult.Golestanietal.(2013)developeda along with variable h and D during modelling of drying
m
finite-difference analytical model for heat and mass trans- process was analyzed on moisture migration mechanism.
fer analysis of disc-shaped apples and concluded that the Figure 4b shows that variation of moisture ratio predicted
dryingkineticspredictedbyconsiderationofshrinkageand by FE model with and without shrinkage consideration. It
variable diffusion coefficient were in closest agreement can be clearly seen that without considering the shrinkage
with experimental data. phenomena during modelling, the predicted moisture ratio
showed a large deviation, up to 17%, from the experi-
mentalcurve,incontrastto0.06%deviationbyconsidering
the shrinkage effect. Hence, prediction of moisture
migration by FE model without involving shrinkage
123

JFoodSciTechnol(October2020)57(10):3748–3761 3759
d
MC (db)
MC (db)
t=0 hour t=2 hour
MC (db)
MC (db)
t=4 hour t=6 hour
MC (db)
MC (db)
t=8 hour
t=10 hour
Fig.4 continued
phenomena wasoverestimated. This wasfurther supported taking place towards the center of the body. Shrinkage of
by higher values of statistical errors between experimental food materials during drying leads to reduction in overall
and predicted model assuming no shrinkage as shown in dimensions. However, distance traveled by water mole-
Table 2. Moisture removal causes disturbance in mechan- cules to diffuse within the food sample (path length) may
ical equilibrium of plant cells resulting in deformation of increase or decrease depending upon the degree of tortu-
cells and tissues. This gives rise to shrinkage phenomena osity effect. In the present study, path length covered by
123

| 3760    |             |       |          |                |     |                |            | JFoodSciTechnol(October2020)57(10):3748–3761 |     |     |     |     |     |     |
| ------- | ----------- | ----- | -------- | -------------- | --- | -------------- | ---------- | -------------------------------------------- | --- | --- | --- | --- | --- | --- |
| Table 2 | Statistical | error | analysis | for validation | of  | finite element | Conclusion |                                              |     |     |     |     |     |     |
modelpredictionwithexperiments
FEmodel Statisticalerrors In the present study, a finite element approach has been
|     |     |     |     |     |     |     | presented | to develop  | a         | computational |                  | model | for       | the pre- |
| --- | --- | --- | --- | --- | --- | --- | --------- | ----------- | --------- | ------------- | ---------------- | ----- | --------- | -------- |
|     |     |     |     | MAE | MRE | SE  |           |             |           |               |                  |       |           |          |
|     |     |     |     |     |     |     | diction   | of moisture | migration |               | and distribution |       | mechanism |          |
Withshrinkage inside a 3-dimensional pineapple slice during convective
Avgh ,VariableD 0.0246 0.1320 0.0325 drying. Experimental analysis of drying and shrinkage
m
kineticsofpineappleslicesduringdryingwasalsostudied.
| Avgh m | ,AvgD |     |     | 0.0603 | 0.2724 | 0.0754 |     |     |     |     |     |     |     |     |
| ------ | ----- | --- | --- | ------ | ------ | ------ | --- | --- | --- | --- | --- | --- | --- | --- |
Variableh ,AvgD 0.0520 0.2541 0.0667 The total drying time to reduce the moisture from 92% to
m
|           |              |     |     |        |        |        | final moisture |     | content | of 25% | (wb) | was found | as  | 10.5 h. |
| --------- | ------------ | --- | --- | ------ | ------ | ------ | -------------- | --- | ------- | ------ | ---- | --------- | --- | ------- |
| Variableh | m ,VariableD |     |     | 0.0171 | 0.1075 | 0.0225 |                |     |         |        |      |           |     |         |
Withoutshrinkage Thickness, outer radius and inner radius of hollow cylin-
|           |              |     |     |        |        |        | drical pineapple |              | slices | were reduced |                | by 79.3%, | 32.2%        | and |
| --------- | ------------ | --- | --- | ------ | ------ | ------ | ---------------- | ------------ | ------ | ------------ | -------------- | --------- | ------------ | --- |
| Variableh | m ,VariableD |     |     | 0.0822 | 0.9897 | 0.1044 |                  |              |        |              |                |           |              |     |
|           |              |     |     |        |        |        | 51.2%,           | respectively | due    | to           | the occurrence |           | of shrinkage |     |
h convectivemasstransfercoefficient(m/s),Ddiffusioncoefficient
| m   |     |     |     |     |     |     | during drying. |     | Non-linear | regression |     | analysis | showed | that |
| --- | --- | --- | --- | --- | --- | --- | -------------- | --- | ---------- | ---------- | --- | -------- | ------ | ---- |
(m 2/s),Avgaverage
|                 |     |            |       |             |           |              | quadratic    | model     | was more | effective    |           | than linear | model     | for      |
| --------------- | --- | ---------- | ----- | ----------- | --------- | ------------ | ------------ | --------- | -------- | ------------ | --------- | ----------- | --------- | -------- |
|                 |     |            |       |             |           |              | representing | the       | change   | in           | shrinkage | parameter   |           | with     |
|                 |     |            |       |             |           |              | reducing     | moisture  | ratio    | during       | drying.   | The         | developed | FE       |
| water molecules |     | to diffuse |       | from inside | to sample | matrix       |              |           |          |              |           |             |           |          |
|                 |     |            |       |             |           |              | model was    | validated | with     | experimental |           | results     | in        | terms of |
| was relatively  |     | longer     | in no | shrinkage   | model     | than that of |              |           |          |              |           |             |           |          |
averagemoisturecontentandwasfoundingoodagreement
| considering | shrinkage. |           | It is | evident from | Fig.          | 4b that the |          |             |           |     |              |          |                 |     |
| ----------- | ---------- | --------- | ----- | ------------ | ------------- | ----------- | -------- | ----------- | --------- | --- | ------------ | -------- | --------------- | --- |
|             |            |           |       |              |               |             | with low | statistical | errors.   | It  | was observed |          | that considera- |     |
| effect of   | shrinkage  | dominates |       | the effect   | of tortuosity | thus        |          |             |           |     |              |          |                 |     |
|             |            |           |       |              |               |             | tion of  | shrinkage   | phenomena |     | and          | moisture | dependent       |     |
| enhancing   | the        | moisture  | loss. |              |               |             |          |             |           |     |              |          |                 |     |
transportproperties(diffusioncoefficientandmasstransfer
coefficient)allowedbetterpredictionofmoisturemigration
| Spatial   | moisture      | distribution |       |               |         |             |            |               |       |              |           |     |              |         |
| --------- | ------------- | ------------ | ----- | ------------- | ------- | ----------- | ---------- | ------------- | ----- | ------------ | --------- | --- | ------------ | ------- |
|           |               |              |       |               |         |             | mechanism. | FE            | model | demonstrated |           | the | significance | of      |
|           |               |              |       |               |         |             | shrinkage  | consideration |       | while        | modelling |     | the drying   | pro-    |
| Shrinkage | consideration |              | and   | incorporation |         | of moisture |            |               |       |              |           |     |              |         |
|           |               |              |       |               |         |             | cess, as   | assumption    | of    | negligible   | shrinkage |     | led to       | predict |
| dependent | variable      | h            | and D | in the model  | allowed | better      |            |               |       |              |           |     |              |         |
m
moisturewith17%deviationfromtheexperimentalresults.
| prediction    | of moisture |          | profile. | Figure        | 4c, d present | the 3-       |            |             |             |             |              |              |           |        |
| ------------- | ----------- | -------- | -------- | ------------- | ------------- | ------------ | ---------- | ----------- | ----------- | ----------- | ------------ | ------------ | --------- | ------ |
|               |             |          |          |               |               |              | It can     | be inferred | that        | deformation |              | occurring    |           | during |
| dimensional   | moisture    |          | profile  | and shrinkage |               | of pineapple |            |             |             |             |              |              |           |        |
|               |             |          |          |               |               |              | shrinkage  | strongly    | influences  |             | the moisture |              | migration | phe-   |
| slices during | convective  |          | drying   | as predicted  | by            | the model.   |            |             |             |             |              |              |           |        |
|               |             |          |          |               |               |              | nomena;    | hence       | shrinkage   | should      | not          | be neglected |           | while  |
| It can        | be clearly  | observed |          | that there    | is            | simultaneous |            |             |             |             |              |              |           |        |
|               |             |          |          |               |               |              | developing | a           | food drying | model.      |              | Developed    | FE        | model  |
reductioninareaalongwithmoisturelossthatenhancesthe
allowedthevisualizationandevaluationofspatialmoisture
| mass flux. | It is | also evident |     | that moisture | loss | was taking |                |     |            |        |        |         |     |       |
| ---------- | ----- | ------------ | --- | ------------- | ---- | ---------- | -------------- | --- | ---------- | ------ | ------ | ------- | --- | ----- |
|            |       |              |     |               |      |            | profile within |     | the sample | during | drying | process | and | anal- |
placefromthetopsurface,internalboundariesandexternal
|             |            |     |        |         |           |         | ysis of | slow | heating | zone | of the | sample, | which | would |
| ----------- | ---------- | --- | ------ | ------- | --------- | ------- | ------- | ---- | ------- | ---- | ------ | ------- | ----- | ----- |
| boundaries. | Therefore, |     | sample | surface | presented | compar- |         |      |         |      |        |         |       |       |
manifesttobearobusttoolforcorrectestimationofdrying
| atively                             | very low | moisture, | whereas, | higher | moisture        | was |               |     |              |     |           |          |     |     |
| ----------------------------------- | -------- | --------- | -------- | ------ | --------------- | --- | ------------- | --- | ------------ | --- | --------- | -------- | --- | --- |
|                                     |          |           |          |        |                 |     | time, control | and | optimization |     | of drying | process. |     |     |
| observedinsidethebody.Modelprovided |          |           |          |        | betterinsightof |     |               |     |              |     |           |          |     |     |
slowestheatingzonewhichremainedasthickness,z = 0in Compliancewithethicalstandards
| the longitudinal |     | direction, |     | and r ¼ro(cid:3)ri | in  | the radial |     |     |     |     |     |     |     |     |
| ---------------- | --- | ---------- | --- | ------------------ | --- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
2
|            |         |         |          |         |          |        | Conflict | of interest | The authors |     | declare | that there | is no | conflict of |
| ---------- | ------- | ------- | -------- | ------- | -------- | ------ | -------- | ----------- | ----------- | --- | ------- | ---------- | ----- | ----------- |
| direction. | In this | region, | moisture | content | remained | higher |          |             |             |     |         |            |       |             |
interest.
| as compared | to       | boundaries |             | at any instance | and      | moisture     |     |     |     |     |     |     |     |     |
| ----------- | -------- | ---------- | ----------- | --------------- | -------- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
| transfer    | is slow. | By         | visualizing | the             | sample   | surface, the |     |     |     |     |     |     |     |     |
| drying      | process  | may        | look        | complete,       | however, | higher       |     |     |     |     |     |     |     |     |
References
| moisture  | present   | inside | the sample | may         | still | give an invi- |     |     |     |     |     |     |     |     |
| --------- | --------- | ------ | ---------- | ----------- | ----- | ------------- | --- | --- | --- | --- | --- | --- | --- | --- |
| tation to | microbial | growth | leading    | to spoilage |       | (Khan et al.  |     |     |     |     |     |     |     |     |
AOAC(2002)Officialmethodsofanalysis,15thedn.Associationof
2017). However, the developed model allowed estimation OfficialAnalyticalChemists,Arlington
of moisture at any point/region of food sample at any AprajeetaJ,GopirajahR,AnandharamakrishnanC(2015)Shrinkage
|          |         |        |         |     |     |     | and | porosity | effects | on heat | and mass | transfer | during | potato |
| -------- | ------- | ------ | ------- | --- | --- | --- | --- | -------- | ------- | ------- | -------- | -------- | ------ | ------ |
| instance | of time | during | drying. |     |     |     |     |          |         |         |          |          |        |        |
drying.JFoodEng144:119–128
|     |     |     |     |     |     |     | Bala BK, | Mondol | MRA, | Biswas | BK, Das | Chowdury | BL, | Janjai S |
| --- | --- | --- | --- | --- | --- | --- | -------- | ------ | ---- | ------ | ------- | -------- | --- | -------- |
(2003)Solardryingofpineappleusingsolartunneldrier.Renew
Energy28(2):183–190
DattaAK(2007)Porousmediaapproachestostudyingsimultaneous
|     |     |     |     |     |     |     | heat | and mass | transfer | in food | processes. | I:  | problem | formula- |
| --- | --- | --- | --- | --- | --- | --- | ---- | -------- | -------- | ------- | ---------- | --- | ------- | -------- |
tions.JFoodEng80(1):80–95
123

JFoodSciTechnol(October2020)57(10):3748–3761 3761
DhalsamantK,TripathyPP,ShrivastavaSL(2017)Moisturetransfer Olanipekun BF, Tunde-Akintunde TY, Oyelade OJ, Adebisi MG,
modeling during solar drying of potato cylinders considering Adenaya TA (2015) Mathematical modeling of thin-layer
shrinkage.IntJGreenEnergy14(2):184–195 pineappledrying.JFoodProcessPreserv39(6):1431–1441
Dhalsamant K, Tripathy PP, Shrivastava SL (2018) Heat transfer PflugLJ,BlaisdellJL(1963)Methodsofanalysisofprecoolingdata.
analysis during mixed-mode solar drying of potato cylinders ASHRAEJ5:33–40
incorporatingshrinkage:numericalsimulationandexperimental Ponkham K, Meeso N, Soponronnarit S, Siriamornpun S (2012)
validation.FoodBioprodProcess109:107–121 Modelingofcombinedfar-infraredradiationandairdryingofa
FaalS,TavakoliT,GhobadianB(2015)Mathematicalmodellingof ring shaped-pineapple with/without shrinkage. Food Bioprod
thinlayerhotairdryingofapricotwithcombinedheatandpower Process90(2):155–164
dryer.JFoodSciTechnol52(May):2950–2957 RamalloLA,MascheroniRH(2012)Qualityevaluationofpineapple
Fasogbon(2013)Studiesontheosmoticdehydrationandrehydration fruit during drying process. Food Bioprod Process
characteristics of pineapple slices. J Food Process Technol. 90(2):275–283
https://doi.org/10.4172/2157-7110.1000220 Rani P, Tripathy PP (2019) Effect of ultrasound and chemical
GeankoplisCJ(1983)Transportprocessesandunitoperations.Allyn pretreatment on drying characteristics and quality attributes of
andBacon,Boston hotairdriedpineappleslices.JFoodSciTechnol.https://doi.org/
GolestaniR,RaisiA,AroujalianA(2013)Mathematicalmodelingon 10.1007/s13197-019-03961-w
airdryingofapplesconsideringshrinkageandvariablediffusion Reddy RS, Ravula PR, Arepally D (2017) Drying kinetics and
coefficient.DryTechnol31(1):40–51 modelling of mass transfer in thin layer convective drying of
Guine´ RPF, Henrriques F, Barroca MJ (2012) Mass transfer pineapple.ChemSciIntJ19(3):1–12
coefficients for the drying of pumpkin (Cucurbita moschata) Sabarez HT (2012) Computational modelling of the transport
and dried product quality. Food Bioprocess Technol phenomena occurring during convective drying of prunes.
5(1):176–183 JFoodEng111(2):279–288
IkegwuO,EkwuF(2009)Thermalandphysicalpropertiesofsome Sharma GP,Prasad S(2004)Effectivemoisture diffusivityofgarlic
tropical fruits and their juices in Nigeria. J Food Technol cloves undergoing microwave-convective drying. J Food Eng
7(2):38–42 65(4):609–617
deJunqueiraJRJ,CorreˆaJLG,deOliveiraHM,IvoSoaresAvelarR, Simal S, Garau MC, Femenia A, Rossello´ C (2006) A diffusional
Salles Pio LA (2017) Convective drying of cape gooseberry model with a moisture-dependent diffusion coefficient. Dry
fruits:effectofpretreatmentsonkineticsandqualityparameters. Technol24(11):1365–1372
LWTFoodSciTechnol82:404–410 TripathyPP(2015)Investigationintosolardryingofpotato:effectof
Khan MIH, Kumar C, Joardder MUH, Karim MA (2017) Determi- samplegeometryondryingkineticsandCO emissionsmitiga-
2
nation of appropriate effective diffusivity for different food tion.JFoodSciTechnol52(3):1383–1393
materials.DryTechnol35(3):335–346 Tripathy PP, Kumar S (2009) A methodology for determination of
KumarC,KarimA,SahaSC,JoardderMUH,BrownRJ,Biswas,D temperature dependent mass transfer coefficients from drying
(2012) Multiphysics Modelling of convective drying of food kinetics:applicationtosolardrying.JFoodEng90(2):212–218
materials. In: Proceedings of the Global Engineering, Science Valentas KJ, Rotstein E, Singh RP (1997) Handbook of food
andTechnologyConference(December):1–13 engineeringpractice.CRCPress,NewYork
LuikovAV(1968)Analyticalheatdiffusiontheory.AcademicPress, Vallespir F, Crescenzo L, Rodr´ıguez O´, Marra F, Simal S (2019)
NewYork Intensification of low-temperature drying of mushroom by
Madiouli J,SghaierJ, LecomteD,SammoudaH(2012)Determina- meansofpowerultrasound:effectondryingkineticsandquality
tionofporositychangefromshrinkagecurvesduringdryingof parameters.FoodBioprocessTechnol12(5):839–851
foodmaterial.FoodBioprodProcess90(1):43–51 WatsonEB,WanserKH,FarleyKA(2010)Anisotropicdiffusionina
Mahapatra A, Tripathy PP (2018a) Modeling and simulation of finite cylinder, with geochemical applications. Geochim Cos-
moisture transfer during solar drying of carrot slices. J Food mochimActa74(2):614–633
ProcessEng41(8):1–15 Younis M, Abdelkarim D, Zein El-Abdein A (2018) Kinetics and
Mahapatra A, Tripathy PP (2018b) Experimental investigation and mathematical modeling of infrared thin-layer drying of garlic
numericalmodelingofheattransferduringsolardryingofcarrot slices.JSaudiSocAgricSci25:332–338
slices.HeatMassTransf55(5):1287–1300
MayorL,MoreiraR,SerenoAM(2011)Shrinkage,density,porosity
Publisher’s Note Springer Nature remains neutral with regard to
and shape changes during dehydration of pumpkin (Cucurbita
jurisdictionalclaimsinpublishedmapsandinstitutionalaffiliations.
pepoL.)fruits.JFoodEng103(1):29–37
123