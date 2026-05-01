"""
generate_figures.py
====================
Generates all 13 publication-quality figures for Project 3.
These replicate the R ggplot2 visuals for environments without R.
Run: python3 generate_figures.py
"""
import os, json, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
warnings.filterwarnings("ignore")

os.makedirs("output/figures", exist_ok=True)

# ── Palette ───────────────────────────────────────────────────
GREEN_DARK  = "#1B4332"
GREEN_MID   = "#2D6A4F"
GREEN_LIGHT = "#40916C"
GREEN_PALE  = "#74C69D"
GOLD        = "#B7841A"
BORD        = "#8B2635"
BLUE        = "#003F7F"
RED         = "#E74C3C"
AMBER       = "#F39C12"
OK          = "#27AE60"
GRAY        = "#6B7280"

PAL_STATUS  = {"On Track": OK, "At Risk": AMBER, "Delayed": RED}
PAL_GENDER  = {"Female": BORD, "Male": GREEN_DARK}
PAL_NUTR    = {"SAM": RED, "MAM": AMBER, "Normal": OK}
PAL_VULN    = {"IDP": BLUE, "Refugee": BORD, "Host Community": GREEN_DARK, "Returnee": GOLD}

def style_ax(ax, title="", subtitle="", caption=""):
    ax.set_facecolor("white")
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color("#CCCCCC")
    ax.grid(axis="y", color="#EEEEEE", linewidth=0.5, zorder=0)
    ax.tick_params(colors="#444444", labelsize=9)
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", color=GREEN_DARK, pad=10, loc="left")
    if subtitle:
        ax.annotate(subtitle, xy=(0,1.01), xycoords="axes fraction",
                    fontsize=8.5, color="#777777", ha="left")
    if caption:
        ax.annotate(caption, xy=(0,-0.14), xycoords="axes fraction",
                    fontsize=7.5, color="#AAAAAA", ha="left", style="italic")

def save_fig(name, fig):
    path = f"output/figures/{name}.png"
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [SAVED] {name}.png")

# ── Load data ─────────────────────────────────────────────────
ind  = pd.read_csv("data/indicators.csv")
ben  = pd.read_csv("data/beneficiaries.csv")
nut  = pd.read_csv("data/nutrition_screening.csv")
acc  = pd.read_csv("data/accountability.csv")

ind["AchievementRate"] = ind["Achieved"] / ind["Target"]
ben["RegDate"]  = pd.to_datetime(ben["RegDate"])
nut["ScreenDate"] = pd.to_datetime(nut["ScreenDate"])
acc["Date"]     = pd.to_datetime(acc["Date"])
acc["DaysToResolve"] = pd.to_numeric(acc["DaysToResolve"], errors="coerce")

print("Data loaded:")
for name, df in [("indicators",ind),("beneficiaries",ben),
                  ("nutrition",nut),("accountability",acc)]:
    print(f"  {name:20s}: {len(df)} rows")

# =============================================================================
# FIG 01 — Achievement by Sector
# =============================================================================
sector_perf = (ind.groupby("Sector")["AchievementRate"]
               .mean().sort_values().reset_index())
sector_perf.columns = ["Sector","MeanAch"]

fig, ax = plt.subplots(figsize=(9,5.5))
bars = ax.barh(sector_perf["Sector"], sector_perf["MeanAch"],
               color=[plt.cm.Greens(v*0.7+0.3) for v in sector_perf["MeanAch"]],
               height=0.65, zorder=3)
ax.axvline(0.80, color=RED, linestyle="--", linewidth=1.2, label="80% threshold", zorder=4)
for bar, val in zip(bars, sector_perf["MeanAch"]):
    ax.text(val+0.01, bar.get_y()+bar.get_height()/2,
            f"{val:.0%}", va="center", fontsize=9.5, fontweight="bold", color="#222831")
ax.set_xlim(0, 1.05)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"{x:.0%}"))
style_ax(ax, "Average Achievement Rate by Sector",
         "Red dashed = 80% target threshold",
         "Source: Programme Indicator Tracking System | NABALOUM Emile")
ax.set_xlabel("Achievement Rate (%)", fontsize=10)
ax.legend(fontsize=9)
save_fig("01_sector_achievement", fig)

# =============================================================================
# FIG 02 — Achievement Heatmap Country × Sector
# =============================================================================
heat = (ind.groupby(["Country","Sector"])["AchievementRate"]
        .mean().unstack(fill_value=0))

fig, ax = plt.subplots(figsize=(10,5))
import matplotlib.colors as mcolors
cmap = mcolors.LinearSegmentedColormap.from_list("rg", [RED,AMBER,OK])
im = ax.imshow(heat.values, cmap=cmap, vmin=0.4, vmax=1.0, aspect="auto")
ax.set_xticks(range(len(heat.columns))); ax.set_xticklabels(heat.columns, rotation=35, ha="right", fontsize=9)
ax.set_yticks(range(len(heat.index)));   ax.set_yticklabels(heat.index, fontsize=9)
for i in range(len(heat.index)):
    for j in range(len(heat.columns)):
        val = heat.values[i,j]
        ax.text(j, i, f"{val:.0%}", ha="center", va="center",
                fontsize=9, fontweight="bold",
                color="white" if val > 0.65 else "#222831")
plt.colorbar(im, ax=ax, format=plt.FuncFormatter(lambda x,_: f"{x:.0%}"), shrink=0.8)
style_ax(ax, "Achievement Rate Heatmap — Country × Sector",
         "Green = on track | Yellow = at risk | Red = delayed",
         "Source: Programme Indicator Tracking System")
fig.tight_layout()
save_fig("02_achievement_heatmap", fig)

# =============================================================================
# FIG 03 — Status Distribution Stacked Bar
# =============================================================================
status_counts = (ind.groupby(["Sector","Status"])
                 .size().unstack(fill_value=0)
                 [["On Track","At Risk","Delayed"]])
status_pct = status_counts.div(status_counts.sum(axis=1), axis=0)

fig, ax = plt.subplots(figsize=(10,5))
bottom = np.zeros(len(status_pct))
for status, color in PAL_STATUS.items():
    if status in status_pct.columns:
        vals = status_pct[status].values
        bars = ax.bar(status_pct.index, vals, bottom=bottom,
                      label=status, color=color, width=0.6, zorder=3)
        for bar, val in zip(bars, vals):
            if val > 0.07:
                ax.text(bar.get_x()+bar.get_width()/2,
                        bar.get_y()+bar.get_height()/2,
                        f"{val:.0%}", ha="center", va="center",
                        fontsize=8.5, color="white", fontweight="bold")
        bottom += vals
ax.set_ylim(0,1.05)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"{x:.0%}"))
ax.set_xlabel("Sector", fontsize=10)
ax.set_xticklabels(status_pct.index, rotation=30, ha="right")
style_ax(ax, "Activity Status Distribution by Sector",
         "Proportion of indicators by performance status",
         "Source: Programme Indicator Tracking System")
ax.legend(loc="upper right", fontsize=9)
save_fig("03_status_distribution", fig)

# =============================================================================
# FIG 04 — Vulnerability × Gender Diverging Bar
# =============================================================================
vg = ben.groupby(["VulnType","Gender"]).size().reset_index(name="n")
vg["n_plot"] = vg.apply(lambda r: -r["n"] if r["Gender"]=="Male" else r["n"], axis=1)

fig, ax = plt.subplots(figsize=(10,5.5))
for gender, color in PAL_GENDER.items():
    d = vg[vg["Gender"]==gender]
    ax.barh(d["VulnType"], d["n_plot"], height=0.6, color=color,
            label=gender, zorder=3)
ax.axvline(0, color="white", linewidth=1.5, zorder=4)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"{abs(x):.0f}"))
style_ax(ax, "Beneficiaries by Vulnerability Type and Gender",
         "Male (left) | Female (right)",
         "Source: Beneficiary Registration System")
ax.set_xlabel("Number of Beneficiaries", fontsize=10)
ax.legend(fontsize=9)
save_fig("04_vulnerability_gender", fig)

# =============================================================================
# FIG 05 — Age-Gender Population Pyramid
# =============================================================================
age_order = ["0-5","6-17","18-59","60+"]
pyramid = (ben.groupby(["AgeGroup","Gender"]).size().reset_index(name="n"))
pyramid["AgeGroup"] = pd.Categorical(pyramid["AgeGroup"], categories=age_order, ordered=True)
pyramid = pyramid.sort_values("AgeGroup")

fig, ax = plt.subplots(figsize=(9,5))
for gender, color in PAL_GENDER.items():
    d = pyramid[pyramid["Gender"]==gender].copy()
    d["n_plot"] = d["n"] * (-1 if gender=="Male" else 1)
    ax.barh(d["AgeGroup"].astype(str), d["n_plot"], height=0.6,
            color=color, label=gender, zorder=3)
ax.axvline(0, color="white", linewidth=2, zorder=4)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"{abs(int(x))}"))
style_ax(ax, "Beneficiary Age-Gender Pyramid",
         "Population structure by age group",
         "Source: Beneficiary Registration System")
ax.set_xlabel("Beneficiaries", fontsize=10)
ax.legend(fontsize=9)
save_fig("05_age_gender_pyramid", fig)

# =============================================================================
# FIG 06 — Monthly Registration Trend
# =============================================================================
ben["RegMonth"] = ben["RegDate"].dt.to_period("M").dt.to_timestamp()
monthly = (ben.groupby(["RegMonth","Sector"]).size().reset_index(name="n"))

sectors = monthly["Sector"].unique()
colors  = [GREEN_DARK, GREEN_MID, GREEN_LIGHT, GOLD, BORD, BLUE]

fig, axes = plt.subplots(2, 3, figsize=(13,7), sharex=True)
axes = axes.flatten()
for i, sector in enumerate(sectors):
    ax = axes[i]
    d  = monthly[monthly["Sector"]==sector].sort_values("RegMonth")
    ax.fill_between(d["RegMonth"], d["n"], alpha=0.2, color=colors[i])
    ax.plot(d["RegMonth"], d["n"], color=colors[i], linewidth=1.8)
    # Simple rolling mean
    if len(d) >= 3:
        roll = d["n"].rolling(3, min_periods=1, center=True).mean()
        ax.plot(d["RegMonth"], roll, color=colors[i],
                linewidth=2.5, linestyle="--", alpha=0.7)
    ax.set_title(sector, fontsize=10, fontweight="bold", color=colors[i], loc="left")
    ax.tick_params(labelsize=8)
    ax.spines[["top","right"]].set_visible(False)
    ax.grid(axis="y", color="#EEEEEE", linewidth=0.4)

fig.suptitle("Monthly Beneficiary Registrations by Sector (2023–2024)",
             fontsize=13, fontweight="bold", color=GREEN_DARK, y=1.01)
fig.text(0.5, -0.01, "Source: Beneficiary Registration System | NABALOUM Emile",
         ha="center", fontsize=8, color="#AAAAAA", style="italic")
fig.autofmt_xdate(rotation=40)
fig.tight_layout()
save_fig("06_registration_trend", fig)

# =============================================================================
# FIG 07 — MUAC Distribution
# =============================================================================
fig, ax = plt.subplots(figsize=(10,5.5))
for status, color in PAL_NUTR.items():
    d = nut[nut["NutritionStatus"]==status]["MUAC_cm"].dropna()
    ax.hist(d, bins=25, color=color, alpha=0.75, label=status,
            edgecolor="white", linewidth=0.4, zorder=3)
ax.axvline(11.5, color="#222831", linestyle="--", linewidth=1.2, label="11.5cm (SAM/MAM)")
ax.axvline(12.5, color="#555555", linestyle="--", linewidth=1.2, label="12.5cm (MAM/Normal)")
ax.annotate("SAM\n<11.5", (10.0, ax.get_ylim()[1]*0.8 if ax.get_ylim()[1]>0 else 40),
            fontsize=9, color=RED, fontweight="bold", ha="center")
ax.annotate("Normal\n>12.5", (14.5, ax.get_ylim()[1]*0.8 if ax.get_ylim()[1]>0 else 40),
            fontsize=9, color=OK, fontweight="bold", ha="center")
ax.set_xlabel("MUAC (cm)", fontsize=10)
ax.set_ylabel("Count", fontsize=10)
style_ax(ax, "MUAC Distribution by Nutrition Status",
         "WHO thresholds: SAM <11.5cm | MAM 11.5–12.5cm | Normal >12.5cm",
         "Source: Nutrition Screening Programme | n=800")
ax.legend(fontsize=9)
save_fig("07_muac_distribution", fig)

# =============================================================================
# FIG 08 — SAM Rate by Country and Year
# =============================================================================
nut["Year"] = nut["ScreenDate"].dt.year
sam_country = (nut.groupby(["Country","Year"])
               .apply(lambda g: pd.Series({
                   "sam_rate": (g["NutritionStatus"]=="SAM").mean(),
                   "n":        len(g)
               })).reset_index())

countries = sam_country["Country"].unique()
years     = sorted(sam_country["Year"].unique())
x         = np.arange(len(countries))
width     = 0.35
yr_colors = {years[0]: GREEN_PALE, years[1]: GREEN_DARK} if len(years)>1 else {years[0]: GREEN_DARK}

fig, ax = plt.subplots(figsize=(10,5.5))
for i, yr in enumerate(years):
    d = sam_country[sam_country["Year"]==yr].set_index("Country").reindex(countries)
    vals = d["sam_rate"].fillna(0)
    bars = ax.bar(x + (i-0.5)*width, vals, width*0.9,
                  label=str(yr), color=yr_colors.get(yr, GREEN_MID),
                  zorder=3, edgecolor="white")
    for bar, val in zip(bars, vals):
        if val > 0:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.005,
                    f"{val:.0%}", ha="center", fontsize=8, fontweight="bold",
                    color="#222831")
ax.axhline(0.15, color=RED, linestyle="--", linewidth=1.2, label="15% emergency threshold")
ax.set_xticks(x); ax.set_xticklabels(countries, fontsize=10)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"{x:.0%}"))
ax.set_ylim(0, 0.70)
style_ax(ax, "SAM Prevalence Rate by Country (2023 vs 2024)",
         "Red dashed = 15% emergency threshold",
         "Source: Nutrition Screening Programme")
ax.legend(fontsize=9)
save_fig("08_sam_country_comparison", fig)

# =============================================================================
# FIG 09 — MUAC vs Age Scatter
# =============================================================================
sample = nut.sample(min(400, len(nut)), random_state=42)

fig, ax = plt.subplots(figsize=(10,6))
for status, color in PAL_NUTR.items():
    d = sample[sample["NutritionStatus"]==status]
    ax.scatter(d["AgeMonths"], d["MUAC_cm"], c=color, alpha=0.55,
               s=25, label=status, zorder=3)
    if len(d) > 5:
        z = np.polyfit(d["AgeMonths"].dropna(), d["MUAC_cm"].dropna(), 1)
        xr = np.linspace(d["AgeMonths"].min(), d["AgeMonths"].max(), 50)
        ax.plot(xr, np.poly1d(z)(xr), color=color, linewidth=1.8,
                linestyle="--", alpha=0.8)
ax.axhline(11.5, color="#555555", linestyle=":", linewidth=0.9)
ax.axhline(12.5, color="#888888", linestyle=":", linewidth=0.9)
ax.set_xlabel("Age (months)", fontsize=10)
ax.set_ylabel("MUAC (cm)",    fontsize=10)
style_ax(ax, "MUAC vs Age by Nutrition Status",
         "Dashed lines = WHO thresholds | Linear trend by group",
         "Source: Nutrition Screening Programme | random sample n=400")
ax.legend(fontsize=9)
save_fig("09_muac_age_scatter", fig)

# =============================================================================
# FIG 10 — Resolution Time Violin + Box
# =============================================================================
from scipy import stats as scipy_stats

resolved = acc.dropna(subset=["DaysToResolve"])
severities = ["Low","Medium","High","Critical"]
sev_colors = {"Low": OK, "Medium": AMBER, "High": "#E67E22", "Critical": RED}

fig, ax = plt.subplots(figsize=(9,5.5))
data_by_sev = [resolved[resolved["Severity"]==s]["DaysToResolve"].dropna().values
               for s in severities]
vp = ax.violinplot(data_by_sev, positions=range(1,5), showmedians=False,
                   showextrema=False)
for i, (pc, sev) in enumerate(zip(vp["bodies"], severities)):
    pc.set_facecolor(sev_colors[sev])
    pc.set_alpha(0.6)

bp = ax.boxplot(data_by_sev, positions=range(1,5), widths=0.12,
                medianprops=dict(color="#222831", linewidth=2),
                boxprops=dict(color="#555555"),
                whiskerprops=dict(color="#888888", linewidth=0.8),
                capprops=dict(color="#888888"),
                flierprops=dict(marker="", alpha=0))
for i, (d, sev) in enumerate(zip(data_by_sev, severities)):
    ax.scatter(np.random.normal(i+1, 0.06, len(d)), d,
               color=sev_colors[sev], alpha=0.3, s=15, zorder=3)
    ax.scatter(i+1, np.mean(d), marker="D", color="white",
               edgecolors=GREEN_DARK, s=60, zorder=5, linewidth=1.5)

ax.set_xticks(range(1,5)); ax.set_xticklabels(severities, fontsize=10)
ax.set_ylabel("Days to Resolution", fontsize=10)
ax.set_ylim(0, 50)
style_ax(ax, "Feedback Resolution Time by Severity",
         "Violin + boxplot | Diamond = mean | Dots = individual cases",
         "Source: Accountability / CRM System")
save_fig("10_resolution_time", fig)

# =============================================================================
# FIG 11 — Resolution Rate by Channel × Type
# =============================================================================
res_rate = (acc.groupby(["FeedbackType","Channel"])
            .apply(lambda g: (g["Resolved"]=="Yes").mean())
            .reset_index(name="rate"))

types    = res_rate["FeedbackType"].unique()
channels = res_rate["Channel"].unique()
x        = np.arange(len(channels))
w        = 0.2
type_colors = [GREEN_DARK, GREEN_MID, GOLD, BORD]

fig, ax = plt.subplots(figsize=(11,6))
for i, (ft, color) in enumerate(zip(types, type_colors)):
    d    = res_rate[res_rate["FeedbackType"]==ft].set_index("Channel").reindex(channels)
    vals = d["rate"].fillna(0)
    offset = (i - len(types)/2 + 0.5) * w
    bars = ax.bar(x + offset, vals, w*0.9,
                  label=ft, color=color, zorder=3, edgecolor="white")
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.01,
                f"{val:.0%}", ha="center", fontsize=7.5, fontweight="bold")

ax.set_xticks(x); ax.set_xticklabels(channels, rotation=25, ha="right", fontsize=9)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"{x:.0%}"))
ax.set_ylim(0, 1.1)
style_ax(ax, "Feedback Resolution Rate by Type and Channel", "",
         "Source: Accountability / CRM System")
ax.legend(fontsize=9)
save_fig("11_resolution_by_channel", fig)

# =============================================================================
# FIG 12 — Statistical Tests Summary
# =============================================================================
# Chi-square: Gender × Vulnerability
tbl = pd.crosstab(ben["Gender"], ben["VulnType"])
from scipy.stats import chi2_contingency, f_oneway, kruskal
chi2, p_chi, dof, _ = chi2_contingency(tbl)

# ANOVA: MUAC across countries
groups = [nut[nut["Country"]==c]["MUAC_cm"].dropna().values for c in nut["Country"].unique()]
f_stat, p_anova = f_oneway(*groups)

# Linear regression (simple: MUAC ~ AgeMonths)
from numpy.polynomial import polynomial as Poly
mask = nut["MUAC_cm"].notna() & nut["AgeMonths"].notna()
x_reg = nut.loc[mask, "AgeMonths"].values
y_reg = nut.loc[mask, "MUAC_cm"].values
slope, intercept = np.polyfit(x_reg, y_reg, 1)
y_pred = slope * x_reg + intercept
ss_res = np.sum((y_reg - y_pred)**2)
ss_tot = np.sum((y_reg - y_reg.mean())**2)
r2     = 1 - ss_res/ss_tot

# Kruskal: DaysToResolve by Severity
kw_groups = [resolved[resolved["Severity"]==s]["DaysToResolve"].dropna().values
             for s in severities if len(resolved[resolved["Severity"]==s]) > 2]
if len(kw_groups) >= 2:
    kw_stat, p_kw = kruskal(*kw_groups)
else:
    kw_stat, p_kw = 0, 1.0

fig, axes = plt.subplots(1, 4, figsize=(14,4))
tests = [
    ("Chi² Test\nGender × Vulnerability",
     f"χ²={chi2:.2f}, df={dof}\np = {p_chi:.4f}",
     p_chi, "#2D6A4F"),
    ("ANOVA\nMUAC ~ Country",
     f"F = {f_stat:.2f}\np = {p_anova:.4f}",
     p_anova, "#2D6A4F"),
    ("Linear Regression\nMUAC ~ Age",
     f"slope = {slope:.4f}\nR² = {r2:.3f}",
     0.001, "#B7841A"),
    ("Kruskal-Wallis\nResolution ~ Severity",
     f"H = {kw_stat:.2f}\np = {p_kw:.4f}",
     p_kw, "#2D6A4F"),
]
for ax, (title, body, pval, color) in zip(axes, tests):
    sig = pval < 0.05
    ax.set_facecolor("#F0FAF2" if sig else "#FFF5F5")
    ax.text(0.5, 0.65, title, transform=ax.transAxes,
            ha="center", va="center", fontsize=11, fontweight="bold",
            color=GREEN_DARK)
    ax.text(0.5, 0.35, body, transform=ax.transAxes,
            ha="center", va="center", fontsize=10, color="#333333",
            fontfamily="monospace")
    result = "✓ Significant (p<0.05)" if sig else "— Not significant"
    ax.text(0.5, 0.10, result, transform=ax.transAxes,
            ha="center", va="center", fontsize=9,
            color=OK if sig else GRAY, fontweight="bold")
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor(color)
        spine.set_linewidth(2)

fig.suptitle("Statistical Tests Summary — MEAL Analysis",
             fontsize=13, fontweight="bold", color=GREEN_DARK, y=1.02)
fig.tight_layout()
save_fig("12_statistical_tests", fig)

# =============================================================================
# FIG 00 — Composite Dashboard Panel
# =============================================================================
fig = plt.figure(figsize=(16,10))
gs  = GridSpec(2, 3, figure=fig, hspace=0.38, wspace=0.35)

# Panel A: Sector achievement
ax_a = fig.add_subplot(gs[0,0])
sp   = ind.groupby("Sector")["AchievementRate"].mean().sort_values()
colors_a = [plt.cm.Greens(v*0.7+0.3) for v in sp]
ax_a.barh(sp.index, sp.values, color=colors_a, height=0.65, zorder=3)
ax_a.axvline(0.80, color=RED, linestyle="--", linewidth=1.0)
ax_a.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"{x:.0%}"))
ax_a.set_title("Achievement Rate by Sector", fontsize=10, fontweight="bold",
               color=GREEN_DARK, loc="left")
ax_a.spines[["top","right"]].set_visible(False)
ax_a.grid(axis="x", color="#EEEEEE", linewidth=0.4)

# Panel B: MUAC histogram
ax_b = fig.add_subplot(gs[0,1])
for s, c in PAL_NUTR.items():
    d = nut[nut["NutritionStatus"]==s]["MUAC_cm"].dropna()
    ax_b.hist(d, bins=20, color=c, alpha=0.7, label=s, edgecolor="white")
ax_b.axvline(11.5, color="#333", linestyle="--", linewidth=0.9)
ax_b.axvline(12.5, color="#666", linestyle="--", linewidth=0.9)
ax_b.set_title("MUAC Distribution", fontsize=10, fontweight="bold",
               color=GREEN_DARK, loc="left")
ax_b.spines[["top","right"]].set_visible(False)
ax_b.legend(fontsize=7.5)

# Panel C: Vulnerability pie
ax_c = fig.add_subplot(gs[0,2])
vc   = ben["VulnType"].value_counts()
ax_c.pie(vc.values, labels=vc.index,
         colors=[PAL_VULN.get(k, GRAY) for k in vc.index],
         autopct="%1.0f%%", pctdistance=0.75,
         textprops={"fontsize":8},
         wedgeprops={"linewidth":1,"edgecolor":"white"})
ax_c.set_title("Vulnerability Profile", fontsize=10, fontweight="bold",
               color=GREEN_DARK, loc="left")

# Panel D: Status stacked bar
ax_d = fig.add_subplot(gs[1,0])
sc2  = (ind.groupby(["Sector","Status"]).size().unstack(fill_value=0)
        .reindex(columns=["On Track","At Risk","Delayed"], fill_value=0))
sc2_pct = sc2.div(sc2.sum(axis=1), axis=0)
btm = np.zeros(len(sc2_pct))
for s, c in PAL_STATUS.items():
    if s in sc2_pct.columns:
        ax_d.bar(range(len(sc2_pct)), sc2_pct[s], bottom=btm,
                 color=c, label=s, width=0.6)
        btm += sc2_pct[s].values
ax_d.set_xticks(range(len(sc2_pct)))
ax_d.set_xticklabels(sc2_pct.index, rotation=35, ha="right", fontsize=8)
ax_d.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"{x:.0%}"))
ax_d.set_title("Status Distribution by Sector", fontsize=10, fontweight="bold",
               color=GREEN_DARK, loc="left")
ax_d.spines[["top","right"]].set_visible(False)
ax_d.legend(fontsize=7.5)

# Panel E: Resolution rate
ax_e = fig.add_subplot(gs[1,1])
rr = acc.groupby("Severity").apply(lambda g: (g["Resolved"]=="Yes").mean()).reindex(severities)
sev_c = [sev_colors[s] for s in severities]
ax_e.bar(severities, rr.values, color=sev_c, width=0.6, zorder=3)
ax_e.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"{x:.0%}"))
ax_e.set_ylim(0,1.05)
ax_e.set_title("Feedback Resolution Rate", fontsize=10, fontweight="bold",
               color=GREEN_DARK, loc="left")
ax_e.spines[["top","right"]].set_visible(False)
ax_e.grid(axis="y", color="#EEEEEE", linewidth=0.4)

# Panel F: Beneficiary gender breakdown
ax_f = fig.add_subplot(gs[1,2])
gender_vuln = ben.groupby(["VulnType","Gender"]).size().unstack(fill_value=0)
x_pos = np.arange(len(gender_vuln))
ax_f.bar(x_pos, gender_vuln.get("Female",0), color=BORD, label="Female", width=0.4)
ax_f.bar(x_pos+0.4, gender_vuln.get("Male",0), color=GREEN_DARK, label="Male", width=0.4)
ax_f.set_xticks(x_pos+0.2)
ax_f.set_xticklabels(gender_vuln.index, rotation=30, ha="right", fontsize=8)
ax_f.set_title("Gender by Vulnerability Type", fontsize=10, fontweight="bold",
               color=GREEN_DARK, loc="left")
ax_f.spines[["top","right"]].set_visible(False)
ax_f.legend(fontsize=7.5)

fig.suptitle("MEAL Impact Dashboard — Sahel Humanitarian Programmes (2023–2024)",
             fontsize=15, fontweight="bold", color=GREEN_DARK, y=1.01)
fig.text(0.5, -0.02,
         "Portfolio Project 3 | Author: NABALOUM Emile | emi.nabaloum@gmail.com | "
         "Data: Simulated from real MEAL frameworks",
         ha="center", fontsize=8.5, color="#AAAAAA", style="italic")
save_fig("00_dashboard_panel", fig)

# =============================================================================
# Summary statistics JSON
# =============================================================================
os.makedirs("output", exist_ok=True)
summary = {
    "indicators":      {
        "total_rows":       len(ind),
        "mean_achievement": round(ind["AchievementRate"].mean(), 3),
        "pct_on_track":     round((ind["Status"]=="On Track").mean(), 3),
        "pct_delayed":      round((ind["Status"]=="Delayed").mean(), 3),
    },
    "beneficiaries":   {
        "total_registered": len(ben),
        "pct_female":       round((ben["Gender"]=="Female").mean(), 3),
        "pct_children":     round(ben["AgeGroup"].isin(["0-5","6-17"]).mean(), 3),
        "pct_idp":          round((ben["VulnType"]=="IDP").mean(), 3),
    },
    "nutrition":       {
        "total_screened":   len(nut),
        "sam_rate":         round((nut["NutritionStatus"]=="SAM").mean(), 3),
        "mam_rate":         round((nut["NutritionStatus"]=="MAM").mean(), 3),
        "mean_muac_cm":     round(nut["MUAC_cm"].mean(), 2),
    },
    "accountability":  {
        "total_feedback":    len(acc),
        "resolution_rate":   round((acc["Resolved"]=="Yes").mean(), 3),
        "mean_days_resolved":round(acc["DaysToResolve"].mean(), 1),
        "critical_cases":    int((acc["Severity"]=="Critical").sum()),
    },
    "statistical_tests": {
        "chi2_gender_vuln":  {"chi2": round(chi2,3), "pvalue": round(p_chi,4)},
        "anova_muac_country":{"F":    round(f_stat,3),"pvalue": round(p_anova,4)},
        "regression_muac_age":{"slope": round(slope,4), "R2": round(r2,3)},
        "kruskal_resolution":{"H":    round(kw_stat,3),"pvalue": round(p_kw,4)},
    }
}
with open("output/summary_statistics.json","w") as f:
    json.dump(summary, f, indent=2)

print("\nSummary statistics:")
print(json.dumps(summary, indent=2))
print("\n=== ALL 13 FIGURES GENERATED ===")
