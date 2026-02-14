# The Black Tax: How Race Quietly Adds Months to Federal Prison Sentences — And It's Getting Worse

*By Bruno Beckman | February 2026 | [Justice Index](https://justiceindex.org)*

---

Two people walk into a federal courtroom. Same crime. Same criminal history. Same age. Same guideline range. Same everything the law says should matter.

One walks out with a four-to-five month longer sentence.

The difference? He's Black.

This isn't speculation. It's what 388,334 federal criminal cases — every sentence handed down in the US federal system from fiscal year 2019 through 2024 — tell us when we control for the factors that *should* determine a sentence. And the penalty isn't shrinking. It's growing.

[CHART: Overall Black sentencing penalty over time (2019-2024), showing increase from ~3.5 to ~5 months]

## The Numbers Don't Flinch

Using data from the US Sentencing Commission, we built a regression model controlling for offense type, guideline range, criminal history, defendant age, sex, citizenship status, and weapon involvement. The model explains 74% of the variance in sentence length — a strong fit for social science. We used robust standard errors to ensure our confidence intervals hold up under real-world messiness.

The result: **being Black adds approximately 4 to 5 extra months to a federal prison sentence**, all else being equal.

To put that in human terms: that's four to five extra months away from your children. Four to five extra months of lost wages. Four to five extra months in a cell that the legal system cannot explain by anything other than the color of your skin.

## It's Getting Worse

Perhaps the most alarming finding isn't the gap itself — disparities in federal sentencing have been documented for decades. It's the *trajectory*.

In fiscal year 2019, the controlled racial penalty was roughly 3.5 months. By 2024, it had climbed to approximately 5 months. That's not noise. That's a trend line moving in the wrong direction while the country debates whether systemic racism even exists.

Drug trafficking tells the starkest version of this story. **The racial sentencing gap in drug cases tripled** between 2019 and 2024. A category that already carried deep racial baggage — from the crack-powder cocaine disparity to mandatory minimums — is seeing its disparities accelerate, not retreat.

[CHART: Drug trafficking racial gap over time, showing tripling]

## The Leniency Door Doesn't Open Equally

Federal judges have discretion. They can sentence below the guidelines when circumstances warrant it — a cooperating defendant, an unusually sympathetic case, a guideline range that seems disproportionate. These "below-guideline" sentences are where mercy lives in the federal system.

But that door doesn't open equally.

**Black defendants are 25% less likely to receive a below-guideline sentence** compared to white defendants with the same legal profile (odds ratio: 0.75). The leniency gap sits at roughly 12 percentage points and has been remarkably stable across all six years of our data.

[CHART: Below-guideline sentence rates by race, 2019-2024]

That stability is its own kind of damning. It means this isn't a blip driven by one administration's policies or one year's caseload. It's baked in.

## Some Crimes Hit Harder Than Others

The racial penalty isn't uniform across offense types, and intellectual honesty demands we say so.

**Assault cases carry the largest Black sentencing penalty: roughly 20 extra months.** Robbery follows at about 11 extra months. These are enormous disparities — in assault cases, the racial tax alone exceeds many guideline ranges for lesser offenses.

But the pattern flips for some crimes. In sex offense cases, Black defendants actually receive *shorter* sentences than white defendants with comparable profiles. The reasons likely involve complex interactions between offense characteristics, victim demographics, and prosecutorial patterns that our model can't fully untangle.

This unevenness matters. It tells us the disparity isn't a simple, universal bias applied like a surcharge. It's woven into specific contexts and decisions in ways that demand granular investigation.

[CHART: Racial sentencing gap by offense type — horizontal bar chart]

## The Geographic Lottery

Where you're sentenced may matter as much as what you did.

Across federal districts, we found a **spread of approximately 100 months between the harshest and most lenient districts** for comparable offenses. One hundred months. That's more than eight years of difference based on which side of a state line you happened to commit a crime — or get caught.

Federal sentencing was supposed to reduce this kind of randomness. The Sentencing Reform Act of 1984 created the guidelines precisely to ensure that similar defendants received similar sentences regardless of geography. Four decades later, the disparity is staggering.

[CHART: Map or dot plot of median sentences by federal district, highlighting the spread]

## The Gender Gap Is Even Larger

Race isn't the only axis of disparity. **Women receive sentences 8 to 10 months shorter than men** after controlling for the same legal factors. This gender gap is actually larger than the racial gap, though it receives a fraction of the attention.

The interaction between race and gender compounds in predictable ways. A Black man faces the full weight of both disparities. A white woman benefits from both.

## The Trial Penalty Has a Racial Dimension

About 97% of federal cases end in plea bargains. The small percentage that go to trial face what's known as the "trial penalty" — substantially longer sentences compared to those who plead guilty.

That penalty is real, and it's expected to some degree (guilty pleas typically earn sentencing reductions for acceptance of responsibility). But **the trial penalty falls harder on Black defendants**. The racial gap widens dramatically when comparing trial outcomes versus plea outcomes, suggesting that the already-unequal system becomes more unequal at the moment defendants exercise their constitutional right to a jury.

[CHART: Racial sentencing gap at plea vs. trial]

## What Can Be Done

Data alone doesn't fix anything. But it can make the invisible visible, and visibility is the precondition for accountability. Here's where the levers are:

**For policymakers:** The geographic disparity alone justifies a serious review of how sentencing guidelines are applied across districts. The Sentencing Commission should investigate district-level outliers and issue targeted guidance.

**For judges:** Implicit bias training isn't enough when the data shows bias *increasing*. Courts should implement real-time demographic monitoring of sentencing outcomes at the district level, with regular reporting.

**For defense attorneys:** The below-guideline leniency gap suggests that advocacy for departures may be less effective for Black defendants. Public defenders' offices should audit their own motion practices for racial patterns.

**For prosecutors:** Charging decisions and plea offers happen before sentencing and shape the entire outcome. DOJ should mandate and publish demographic breakdowns of charging and plea practices by district.

**For citizens:** Demand that your federal district publishes sentencing data with demographic breakdowns. Support organizations working on sentencing reform. Use tools like [Justice Index](https://justiceindex.org) to see the data for yourself.

The federal sentencing system processes hundreds of thousands of lives. The least we owe those lives is honest measurement of whether the system treats them fairly.

The data says it doesn't. And it's getting worse.

---

## Methodology

This analysis uses individual-level data from the US Sentencing Commission's annual datafiles covering fiscal years 2019 through 2024, totaling 388,334 cases. We estimated the racial sentencing disparity using ordinary least squares (OLS) regression with sentence length in months as the dependent variable, controlling for: primary offense type, guideline minimum and maximum, criminal history category, defendant age, sex, citizenship status, and weapon involvement. Heteroskedasticity-consistent (HC1) robust standard errors were used throughout. The model achieves an R² of 0.74. Below-guideline analysis used logistic regression with the same controls, reporting odds ratios. Year-over-year and offense-specific analyses used the same specification on relevant subsets. Geographic analysis compared district-level median sentences for comparable offense and criminal history combinations.

All data and code are available at [justiceindex.org](https://justiceindex.org).

*Bruno Beckman is the creator of Justice Index, an open-source project making federal sentencing data accessible and accountable.*
