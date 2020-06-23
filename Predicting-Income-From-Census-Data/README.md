# Predictive Modelling: The Census Income UCI Dataset
In this notebook we run through a basic prediction task using the [Census Income UCI Dataset](http://archive.ics.uci.edu/ml/datasets/Census+Income). The task is to predict whether income exceeds $50k/year based on census data.

### Dataset information

This dataset consists of 48842 instances and 15 features. The features take on a mix of categorical/numerical values:

1. **age**: 16+ (continuous).
2. **workclass**: Private, Self-emp-not-inc, Self-emp-inc, Federal-gov, Local-gov, State-gov, Without-pay, Never-worked.
3. **fnlwgt**: Final weight, see below (continuous).
4. **education**: Bachelors, Some-college, 11th, HS-grad, Prof-school, Assoc-acdm, Assoc-voc, 9th, 7th-8th, 12th, Masters, 1st-4th, 10th, Doctorate, 5th-6th, Preschool.
5. **education_num**: Total number of years of education (continuous).
6. **marital_status**: Married-civ-spouse, Divorced, Never-married, Separated, Widowed, Married-spouse-absent, Married-AF-spouse.
7. **occupation**: Tech-support, Craft-repair, Other-service, Sales, Exec-managerial, Prof-specialty, Handlers-cleaners, Machine-op-inspct, Adm-clerical, Farming-fishing, Transport-moving, Priv-house-serv, Protective-serv, Armed-Forces.
8. **relationship**: Wife, Own-child, Husband, Not-in-family, Other-relative, Unmarried.
9. **race**: White, Asian-Pac-Islander, Amer-Indian-Eskimo, Other, Black.
10. **sex**: Female, Male.
11. **capital_gain**: continuous.
12. **capital_loss**: continuous.
13. **hours_per_week**: Number of hours worked per week (continuous).
14. **native_country**: United-States, Cambodia, England, Puerto-Rico, Canada, Germany, Outlying-US(Guam-USVI-etc), India, Japan, Greece, South, China, Cuba, Iran, Honduras, Philippines, Italy, Poland, Jamaica, Vietnam, Mexico, Portugal, Ireland, France, Dominican-Republic, Laos, Ecuador, Taiwan, Haiti, Columbia, Hungary, Guatemala, Nicaragua, Scotland, Thailand, Yugoslavia, El-Salvador, Trinadad&Tobago, Peru, Hong, Holand-Netherlands.
15. **Income**: >50k, <=50k. 

The dataset is already split into train-test sets of sizes (2/3, 1/3). Both sets contain missing values, denoted by '?'.

#### Description of fnlwgt (final weight):
The UCI repository lists this additional information for the fnlwgt column:

"The weights on the Current Population Survey (CPS) files are controlled to independent estimates of the civilian noninstitutional population of the US. These are prepared monthly for us by Population Division here at the Census Bureau. We use 3 sets of controls. These are:

1. A single cell estimate of the population 16+ for each state.
2. Controls for Hispanic Origin by age and sex.
3. Controls by Race, age and sex."
### Dependencies
* Python 3+
* Pandas, numpy, scikit-learn
