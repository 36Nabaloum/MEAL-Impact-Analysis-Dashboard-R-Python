# 📊 MEAL Impact Analysis Dashboard — R / Python

> **Author:** NABALOUM Emile | emi.nabaloum@gmail.com
> **Stack:** R (ggplot2 · dplyr · patchwork · broom) + Python (fallback)
> **Figures:** 13 publication-quality visualisations ✅

---

## 📌 Overview

A comprehensive **MEAL (Monitoring, Evaluation, Accountability and Learning)** analysis covering 4 datasets from humanitarian programmes in the Sahel region (2023–2024). Replicates real analytical work delivered at **SPONG/OCHA**, **IRC** and **AUXFIN**.

| Dataset | Rows | Description |
|---------|------|-------------|
| `indicators.csv` | 480 | Programme KPIs by sector, country, donor |
| `beneficiaries.csv` | 1,200 | Individual beneficiary registry |
| `nutrition_screening.csv` | 800 | Clinical nutrition data (MUAC, weight, height) |
| `accountability.csv` | 400 | Feedback & complaint mechanism (CRM) |

---

## 📈 Analyses & Figures

### Section 1 — Indicator Performance
| Fig | Analysis | Key Insight |
|-----|----------|-------------|
| 01 | Achievement rate by sector (horizontal bar) | Mean achievement: **78.3%** |
| 02 | Country × Sector heatmap | Conditional formatting by threshold |
| 03 | Status distribution stacked bar | 45% On Track · 8% Delayed |
## 🖼️ Capture d’écran du tableau de bord

![image](https://github.com/user-attachments/assets/b41cf117-d065-4d55-b328-9efa517a5977)


> Ce visuel présente la répartition des loyers moyens par ville, les évolutions mensuelles, le taux d’occupation et les comparatifs entre quartiers populaires et quartiers résidentiels à Ouagadougou et Bobo-Dioulasso.

---

### Section 2 — Beneficiary Demographics
| Fig | Analysis | Key Insight |
|-----|----------|-------------|
| 04 | Vulnerability × Gender diverging bar | Female: **59.7%** |
| 05 | Age-gender population pyramid | Children (0–17): **48.8%** |
| 06 | Monthly registration trend (LOESS) | Seasonal patterns by sector |

### Section 3 — Nutrition Clinical Analysis
| Fig | Analysis | Key Insight |
|-----|----------|-------------|
| 07 | MUAC distribution by WHO classification | SAM rate: **30.9%** |
| 08 | SAM prevalence by country (2023 vs 2024) | Year-over-year comparison |
| 09 | MUAC vs Age scatter with linear trend | Age-MUAC relationship |

### Section 4 — Accountability
| Fig | Analysis | Key Insight |
|-----|----------|-------------|
| 10 | Resolution time violin + boxplot by severity | Mean: **23.2 days** |
| 11 | Resolution rate by type × channel | Hotline most effective |

### Section 5 — Statistical Tests
| Fig | Test | Result |
|-----|------|--------|
| 12 | Chi² Gender × Vulnerability | Significant (p < 0.05) |
| 12 | ANOVA MUAC ~ Country | Significant (p < 0.05) |
| 12 | Linear regression MUAC ~ Age | R² coefficient |
| 12 | Kruskal-Wallis Resolution ~ Severity | Significant (p < 0.05) |

### Dashboard
| Fig | Description |
|-----|-------------|
| 00 | Composite 6-panel dashboard (patchwork / GridSpec) |

---

## ⚡ Key Statistical Results

```
Chi-square test (Gender × Vulnerability):
  χ² = significant  |  p < 0.05  → Gender and vulnerability are NOT independent

ANOVA (MUAC across Countries):
  F = significant   |  p < 0.05  → Mean MUAC differs significantly across countries

Linear Regression (MUAC ~ Age + Gender + Country):
  Positive slope on Age  → MUAC increases with age (expected in under-5)
  R² meaningful          → Model explains variance in MUAC

Kruskal-Wallis (Resolution Days ~ Severity):
  H = significant   |  p < 0.05  → Severity level affects resolution time
```

---

## 🚀 How to Run

### Option A — R (recommended)
```r
# Install packages
install.packages(c("tidyverse","scales","lubridate","ggtext",
                   "patchwork","viridis","gt","broom","ggrepel","jsonlite"))

# Run analysis
setwd("project3_meal_r")
source("R/meal_analysis.R")

# Render full report
rmarkdown::render("R/meal_report.Rmd", output_dir = "output/")
```

### Option B — Python (no R required)
```bash
pip install pandas matplotlib scipy numpy
python3 generate_figures.py
```

### Output
```
output/
├── figures/
│   ├── 00_dashboard_panel.png       ← Composite 6-panel dashboard
│   ├── 01_sector_achievement.png
│   ├── 02_achievement_heatmap.png
│   ├── 03_status_distribution.png
│   ├── 04_vulnerability_gender.png
│   ├── 05_age_gender_pyramid.png
│   ├── 06_registration_trend.png
│   ├── 07_muac_distribution.png
│   ├── 08_sam_country_comparison.png
│   ├── 09_muac_age_scatter.png
│   ├── 10_resolution_time.png
│   ├── 11_resolution_by_channel.png
│   └── 12_statistical_tests.png
└── summary_statistics.json          ← Machine-readable KPIs
```

---

## 📂 File Structure

```
project3_meal_r/
│
├── R/
│   ├── meal_analysis.R         # Full R analysis (ggplot2, tidyverse, broom)
│   └── meal_report.Rmd         # RMarkdown HTML report
│
├── generate_figures.py         # Python fallback — all 13 figures
│
├── data/
│   ├── generate_data.py        # Python data generator
│   ├── indicators.csv          # 480 rows
│   ├── beneficiaries.csv       # 1,200 rows
│   ├── nutrition_screening.csv # 800 rows
│   └── accountability.csv      # 400 rows
│
├── output/
│   ├── figures/                # 13 PNG figures
│   └── summary_statistics.json
│
└── docs/
    └── README.md               # This file
```

---

## 🎯 Real-World Relevance

This analysis framework mirrors real MEAL deliverables from:
- **SPONG/OCHA** — inter-agency indicator reporting (2024–2025)
- **IRC** — NORAD/GFFO/BHA donor reporting (2023–2024)
- **MSI/USAID** — TPM performance analysis (2024–2025)

The nutrition analysis follows **WHO IMCI** protocols for MUAC classification and the accountability analysis follows **IASC CHS** standards for feedback mechanism monitoring.

---

## 🤝 Connect

| Channel | Link |
|---------|------|
| Email | emi.nabaloum@gmail.com |
| LinkedIn | [linkedin.com/in/nabaloum-emile](https://linkedin.com) |
| WhatsApp | +226 67 07 82 76 |

*Part of the [NABALOUM Emile Data Portfolio](../README.md)*
