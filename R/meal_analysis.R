# =============================================================================
# meal_analysis.R — MEAL Impact Analysis Dashboard
# =============================================================================
# Project  : MEAL Impact Analysis — Sahel Humanitarian Programmes
# Author   : NABALOUM Emile | emi.nabaloum@gmail.com
# GitHub   : github.com/nabaloum-emile/portfolio
#
# Description:
#   Full MEAL analysis using real-world M&E frameworks.
#   Covers: indicator performance, beneficiary demographics,
#   nutrition clinical analysis, accountability metrics,
#   statistical tests and trend analysis.
#
# Output: output/figures/*.png + output/meal_report.html (via rmarkdown)
# =============================================================================

# ── 0. Setup & Libraries ──────────────────────────────────────────────────────
suppressPackageStartupMessages({
  library(tidyverse)     # dplyr, ggplot2, tidyr, readr, purrr, stringr
  library(scales)        # axis formatting
  library(lubridate)     # date handling
  library(ggtext)        # rich text in ggplot (markdown in titles)
  library(patchwork)     # combine multiple ggplots
  library(viridis)       # color-blind friendly palettes
  library(gt)            # beautiful tables
  library(broom)         # tidy statistical output
  library(ggrepel)       # avoid label overlap
})

# ── Project palette (consistent across all visuals) ──────────────────────────
PAL_MAIN    <- c("#1B4332","#2D6A4F","#40916C","#74C69D","#D8F3DC")
PAL_STATUS  <- c("On Track" = "#27AE60", "At Risk" = "#F39C12", "Delayed" = "#E74C3C")
PAL_GENDER  <- c("Female" = "#8B2635", "Male" = "#1B4332")
PAL_NUTR    <- c("SAM" = "#E74C3C", "MAM" = "#F39C12", "Normal" = "#27AE60")
PAL_VULN    <- c("IDP"="#003F7F","Refugee"="#6B1A2A","Host Community"="#1B4332","Returnee"="#C9973A")

# Output directory
dir.create("output/figures", recursive = TRUE, showWarnings = FALSE)

theme_meal <- function() {
  theme_minimal(base_size = 12) +
  theme(
    plot.title       = element_text(size = 14, face = "bold", color = "#1B4332"),
    plot.subtitle    = element_text(size = 11, color = "#555555"),
    plot.caption     = element_text(size = 9,  color = "#888888", hjust = 0),
    axis.title       = element_text(size = 11, color = "#333333"),
    axis.text        = element_text(size = 10, color = "#444444"),
    panel.grid.major = element_line(color = "#EEEEEE", linewidth = 0.4),
    panel.grid.minor = element_blank(),
    legend.position  = "bottom",
    legend.title     = element_text(size = 10, face = "bold"),
    legend.text      = element_text(size = 9),
    strip.text       = element_text(size = 11, face = "bold", color = "#1B4332"),
    plot.margin      = margin(12, 16, 12, 12)
  )
}

save_fig <- function(p, name, w = 10, h = 6.5) {
  ggsave(
    filename = paste0("output/figures/", name, ".png"),
    plot     = p, width = w, height = h, dpi = 180, bg = "white"
  )
  message("[SAVED] ", name, ".png")
}

# =============================================================================
# SECTION 1 — DATA LOADING & PREPARATION
# =============================================================================
message("\n=== LOADING DATA ===")

indicators <- read_csv("data/indicators.csv", show_col_types = FALSE) %>%
  mutate(
    AchievementRate = Achieved / Target,
    Period          = paste0(Year, " Q", Quarter),
    PeriodDate      = as.Date(paste0(Year, "-", Quarter * 3 - 2, "-01")),
  )

beneficiaries <- read_csv("data/beneficiaries.csv", show_col_types = FALSE) %>%
  mutate(
    RegDate     = as.Date(RegDate),
    RegYear     = year(RegDate),
    RegQuarter  = quarter(RegDate),
    RegYearMonth = floor_date(RegDate, "month"),
    AgeGroupOrder = factor(AgeGroup,
                           levels = c("0-5","6-17","18-59","60+"), ordered = TRUE)
  )

nutrition <- read_csv("data/nutrition_screening.csv", show_col_types = FALSE) %>%
  mutate(
    ScreenDate = as.Date(ScreenDate),
    NutritionStatus = factor(NutritionStatus, levels = c("SAM","MAM","Normal")),
    ScreenMonth = floor_date(ScreenDate, "month")
  )

accountability <- read_csv("data/accountability.csv", show_col_types = FALSE) %>%
  mutate(
    Date         = as.Date(Date),
    DaysToResolve = as.numeric(DaysToResolve),
    Severity     = factor(Severity, levels = c("Low","Medium","High","Critical"))
  )

message("  indicators   : ", nrow(indicators),   " rows")
message("  beneficiaries: ", nrow(beneficiaries), " rows")
message("  nutrition    : ", nrow(nutrition),     " rows")
message("  accountability: ",nrow(accountability), " rows")


# =============================================================================
# SECTION 2 — INDICATOR PERFORMANCE ANALYSIS
# =============================================================================
message("\n=== SECTION 2: INDICATOR PERFORMANCE ===")

# ── 2.1 Achievement rate by sector ───────────────────────────────────────────
sector_perf <- indicators %>%
  group_by(Sector) %>%
  summarise(
    n_indicators      = n(),
    mean_achievement  = mean(AchievementRate, na.rm = TRUE),
    median_achievement= median(AchievementRate, na.rm = TRUE),
    pct_on_track      = mean(Status == "On Track", na.rm = TRUE),
    pct_delayed       = mean(Status == "Delayed",  na.rm = TRUE),
    .groups = "drop"
  ) %>%
  arrange(desc(mean_achievement))

p1 <- ggplot(sector_perf,
             aes(x = reorder(Sector, mean_achievement),
                 y = mean_achievement,
                 fill = mean_achievement)) +
  geom_col(width = 0.7, show.legend = FALSE) +
  geom_hline(yintercept = 0.80, linetype = "dashed",
             color = "#E74C3C", linewidth = 0.7) +
  geom_text(aes(label = percent(mean_achievement, accuracy = 1)),
            hjust = -0.15, size = 3.5, fontface = "bold", color = "#222831") +
  scale_y_continuous(labels = percent_format(), limits = c(0, 1.05)) +
  scale_fill_gradient(low = "#74C69D", high = "#1B4332") +
  coord_flip() +
  labs(
    title    = "Average Achievement Rate by Sector",
    subtitle = "Red dashed line = 80% target threshold",
    caption  = "Source: Programme Indicator Tracking System | NABALOUM Emile",
    x = NULL, y = "Achievement Rate (%)"
  ) +
  theme_meal()

save_fig(p1, "01_sector_achievement", w = 9, h = 5.5)

# ── 2.2 Status distribution heatmap (Country × Sector) ───────────────────────
heatmap_data <- indicators %>%
  group_by(Country, Sector) %>%
  summarise(
    mean_achievement = mean(AchievementRate, na.rm = TRUE),
    pct_on_track     = mean(Status == "On Track"),
    .groups = "drop"
  )

p2 <- ggplot(heatmap_data,
             aes(x = Sector, y = Country, fill = mean_achievement)) +
  geom_tile(color = "white", linewidth = 0.8) +
  geom_text(aes(label = percent(mean_achievement, accuracy = 1)),
            size = 3.2, fontface = "bold",
            color = ifelse(heatmap_data$mean_achievement > 0.65, "white", "#222831")) +
  scale_fill_gradient2(
    low = "#E74C3C", mid = "#F39C12", high = "#27AE60",
    midpoint = 0.70, labels = percent_format(), name = "Achievement"
  ) +
  labs(
    title    = "Achievement Rate Heatmap — Country × Sector",
    subtitle = "Green = on track | Yellow = at risk | Red = delayed",
    caption  = "Source: Programme Indicator Tracking System",
    x = NULL, y = NULL
  ) +
  theme_meal() +
  theme(axis.text.x = element_text(angle = 35, hjust = 1))

save_fig(p2, "02_achievement_heatmap", w = 10, h = 5)

# ── 2.3 Quarterly trend by year ───────────────────────────────────────────────
trend_data <- indicators %>%
  group_by(Year, Quarter, Sector) %>%
  summarise(mean_ach = mean(AchievementRate, na.rm = TRUE), .groups = "drop") %>%
  mutate(Period = paste0(Year, " Q", Quarter))

p3 <- ggplot(trend_data,
             aes(x = Quarter, y = mean_ach,
                 color = Sector, group = interaction(Year, Sector),
                 linetype = factor(Year))) +
  geom_line(linewidth = 0.9) +
  geom_point(size = 2.5) +
  geom_hline(yintercept = 0.80, linetype = "dotted", color = "#E74C3C", alpha = 0.8) +
  scale_y_continuous(labels = percent_format(), limits = c(0.3, 1.05)) +
  scale_x_continuous(breaks = 1:4, labels = paste0("Q", 1:4)) +
  scale_color_manual(values = c("#1B4332","#2D6A4F","#40916C","#B7841A","#8B2635","#003F7F")) +
  scale_linetype_manual(values = c("2023" = "dashed", "2024" = "solid"), name = "Year") +
  labs(
    title    = "Quarterly Achievement Trend by Sector (2023–2024)",
    subtitle = "Solid = 2024 | Dashed = 2023 | Dotted red = 80% threshold",
    caption  = "Source: Programme Indicator Tracking System",
    x = "Quarter", y = "Achievement Rate (%)", color = "Sector"
  ) +
  facet_wrap(~Sector, ncol = 3) +
  theme_meal() +
  theme(legend.position = "none")

save_fig(p3, "03_quarterly_trend", w = 12, h = 7)


# =============================================================================
# SECTION 3 — BENEFICIARY DEMOGRAPHIC ANALYSIS
# =============================================================================
message("\n=== SECTION 3: BENEFICIARY DEMOGRAPHICS ===")

# ── 3.1 Gender × Vulnerability pyramid ───────────────────────────────────────
vuln_gender <- beneficiaries %>%
  count(VulnType, Gender) %>%
  mutate(n_display = ifelse(Gender == "Male", -n, n))

p4 <- ggplot(vuln_gender,
             aes(x = n_display, y = reorder(VulnType, abs(n_display)),
                 fill = Gender)) +
  geom_col(width = 0.65) +
  geom_vline(xintercept = 0, color = "white", linewidth = 0.8) +
  geom_text(
    aes(label = comma(abs(n_display)),
        hjust = ifelse(Gender == "Male", 1.15, -0.15)),
    size = 3.2, color = "#222831"
  ) +
  scale_x_continuous(
    labels = function(x) comma(abs(x)),
    limits = c(-500, 700)
  ) +
  scale_fill_manual(values = PAL_GENDER) +
  labs(
    title    = "Beneficiary Population by Vulnerability Type and Gender",
    subtitle = "Diverging bar chart — Male (left) | Female (right)",
    caption  = "Source: Beneficiary Registration System",
    x = "Number of Beneficiaries", y = NULL, fill = "Gender"
  ) +
  theme_meal()

save_fig(p4, "04_vulnerability_gender", w = 10, h = 5.5)

# ── 3.2 Age-gender pyramid ────────────────────────────────────────────────────
pyramid_data <- beneficiaries %>%
  count(AgeGroup, Gender) %>%
  mutate(
    AgeGroup = factor(AgeGroup, levels = c("0-5","6-17","18-59","60+")),
    n_plot   = ifelse(Gender == "Male", -n, n)
  )

p5 <- ggplot(pyramid_data, aes(x = n_plot, y = AgeGroup, fill = Gender)) +
  geom_col(width = 0.65) +
  geom_vline(xintercept = 0, color = "white", linewidth = 1) +
  geom_text(
    aes(label = comma(abs(n_plot)),
        hjust = ifelse(Gender == "Male", 1.2, -0.2)),
    size = 3.5, color = "#222831"
  ) +
  scale_x_continuous(labels = function(x) comma(abs(x))) +
  scale_fill_manual(values = PAL_GENDER) +
  labs(
    title    = "Beneficiary Age-Gender Pyramid",
    subtitle = "Population structure by age group",
    caption  = "Source: Beneficiary Registration System",
    x = "Beneficiaries", y = "Age Group", fill = "Gender"
  ) +
  theme_meal()

save_fig(p5, "05_age_gender_pyramid", w = 9, h = 5)

# ── 3.3 Registration trend by month ──────────────────────────────────────────
monthly_reg <- beneficiaries %>%
  count(RegYearMonth, Sector) %>%
  group_by(Sector) %>%
  mutate(rolling_avg = zoo::rollmean(n, k = 3, fill = NA, align = "right"))

p6 <- ggplot(monthly_reg, aes(x = RegYearMonth, y = n, color = Sector)) +
  geom_line(alpha = 0.35, linewidth = 0.6) +
  geom_smooth(method = "loess", se = TRUE, span = 0.5,
              linewidth = 1.2, alpha = 0.15) +
  scale_x_date(date_labels = "%b %Y", date_breaks = "3 months") +
  scale_color_manual(values = c("#1B4332","#2D6A4F","#40916C",
                                "#B7841A","#8B2635","#003F7F")) +
  labs(
    title    = "Monthly Beneficiary Registrations by Sector (2023–2024)",
    subtitle = "Lines = raw data | Shaded bands = LOESS smoothing (95% CI)",
    caption  = "Source: Beneficiary Registration System",
    x = NULL, y = "New Registrations", color = "Sector"
  ) +
  facet_wrap(~Sector, ncol = 3, scales = "free_y") +
  theme_meal() +
  theme(
    axis.text.x  = element_text(angle = 45, hjust = 1, size = 8),
    legend.position = "none"
  )

save_fig(p6, "06_registration_trend", w = 13, h = 7)


# =============================================================================
# SECTION 4 — NUTRITION CLINICAL ANALYSIS
# =============================================================================
message("\n=== SECTION 4: NUTRITION CLINICAL ANALYSIS ===")

# ── 4.1 MUAC distribution by nutrition status ────────────────────────────────
p7 <- ggplot(nutrition, aes(x = MUAC_cm, fill = NutritionStatus)) +
  geom_histogram(binwidth = 0.5, color = "white", alpha = 0.85,
                 position = "identity") +
  geom_vline(xintercept = c(11.5, 12.5), linetype = "dashed",
             color = "#222831", linewidth = 0.7) +
  annotate("text", x = 10.5,  y = 55, label = "SAM\n<11.5cm",
           size = 3, color = "#E74C3C", fontface = "bold") +
  annotate("text", x = 12.0,  y = 55, label = "MAM\n11.5-12.5",
           size = 3, color = "#F39C12", fontface = "bold") +
  annotate("text", x = 14.5,  y = 55, label = "Normal\n>12.5cm",
           size = 3, color = "#27AE60", fontface = "bold") +
  scale_fill_manual(values = PAL_NUTR, name = "Status") +
  scale_x_continuous(breaks = seq(8, 20, by = 1)) +
  labs(
    title    = "MUAC Distribution by Nutrition Status",
    subtitle = "WHO thresholds: SAM < 11.5 cm | MAM 11.5–12.5 cm | Normal > 12.5 cm",
    caption  = "Source: Nutrition Screening Programme | n = 800",
    x = "MUAC (cm)", y = "Count"
  ) +
  theme_meal()

save_fig(p7, "07_muac_distribution", w = 10, h = 5.5)

# ── 4.2 SAM rate by country and year ─────────────────────────────────────────
sam_country <- nutrition %>%
  mutate(Year = year(ScreenDate)) %>%
  group_by(Country, Year) %>%
  summarise(
    n_screened  = n(),
    sam_rate    = mean(NutritionStatus == "SAM"),
    mam_rate    = mean(NutritionStatus == "MAM"),
    oedema_rate = mean(Oedema == "Yes"),
    referral_rate = mean(Referred == "Yes"),
    .groups = "drop"
  )

p8 <- ggplot(sam_country,
             aes(x = Country, y = sam_rate,
                 fill = factor(Year), group = factor(Year))) +
  geom_col(position = position_dodge(0.75), width = 0.65) +
  geom_errorbar(
    aes(ymin = sam_rate - 1.96 * sqrt(sam_rate*(1-sam_rate)/n_screened),
        ymax = sam_rate + 1.96 * sqrt(sam_rate*(1-sam_rate)/n_screened)),
    position = position_dodge(0.75), width = 0.2, color = "#555555"
  ) +
  geom_hline(yintercept = 0.15, linetype = "dashed",
             color = "#E74C3C", linewidth = 0.7) +
  scale_y_continuous(labels = percent_format(), limits = c(0, 0.65)) +
  scale_fill_manual(values = c("2023" = "#74C69D", "2024" = "#1B4332"),
                    name = "Year") +
  labs(
    title    = "SAM Prevalence Rate by Country (2023 vs 2024)",
    subtitle = "Error bars = 95% CI | Red dashed = 15% emergency threshold",
    caption  = "Source: Nutrition Screening Programme",
    x = NULL, y = "SAM Prevalence Rate (%)"
  ) +
  theme_meal()

save_fig(p8, "08_sam_country_comparison", w = 10, h = 5.5)

# ── 4.3 MUAC scatter: Age vs MUAC colored by status ──────────────────────────
set.seed(42)
nutr_sample <- nutrition %>% sample_n(min(400, nrow(nutrition)))

p9 <- ggplot(nutr_sample,
             aes(x = AgeMonths, y = MUAC_cm,
                 color = NutritionStatus, shape = Gender)) +
  geom_point(alpha = 0.65, size = 2) +
  geom_smooth(aes(group = NutritionStatus), method = "lm",
              se = FALSE, linewidth = 0.9, linetype = "dashed") +
  geom_hline(yintercept = c(11.5, 12.5), linetype = "dotted",
             color = "#555555", linewidth = 0.5) +
  scale_color_manual(values = PAL_NUTR, name = "Status") +
  scale_shape_manual(values = c("M" = 16, "F" = 17), name = "Gender") +
  labs(
    title    = "MUAC vs Age: Scatter by Nutrition Status",
    subtitle = "Dashed lines = WHO thresholds | Linear trend by status group",
    caption  = "Source: Nutrition Screening Programme | random sample n=400",
    x = "Age (months)", y = "MUAC (cm)"
  ) +
  theme_meal()

save_fig(p9, "09_muac_age_scatter", w = 10, h = 6)


# =============================================================================
# SECTION 5 — ACCOUNTABILITY & FEEDBACK MECHANISM
# =============================================================================
message("\n=== SECTION 5: ACCOUNTABILITY ===")

# ── 5.1 Resolution time by severity ──────────────────────────────────────────
resolved <- accountability %>%
  filter(!is.na(DaysToResolve))

p10 <- ggplot(resolved,
              aes(x = Severity, y = DaysToResolve, fill = Severity)) +
  geom_violin(alpha = 0.6, color = "white", trim = TRUE) +
  geom_boxplot(width = 0.2, fill = "white", outlier.shape = NA, alpha = 0.9) +
  geom_jitter(width = 0.08, alpha = 0.3, size = 1.5) +
  stat_summary(fun = mean, geom = "point", shape = 23,
               size = 4, fill = "#1B4332", color = "white") +
  scale_fill_manual(
    values = c("Low"="#27AE60","Medium"="#F39C12","High"="#E67E22","Critical"="#E74C3C")
  ) +
  scale_y_continuous(limits = c(0, 50)) +
  labs(
    title    = "Feedback Resolution Time by Severity",
    subtitle = "Violin + boxplot | Diamond = mean | Dots = individual cases",
    caption  = "Source: Accountability / CRM System",
    x = "Severity Level", y = "Days to Resolution"
  ) +
  theme_meal() +
  theme(legend.position = "none")

save_fig(p10, "10_resolution_time", w = 9, h = 5.5)

# ── 5.2 Resolution rate by type and channel ──────────────────────────────────
resolution_rate <- accountability %>%
  group_by(FeedbackType, Channel) %>%
  summarise(
    total      = n(),
    resolved   = sum(Resolved == "Yes"),
    rate       = resolved / total,
    .groups    = "drop"
  )

p11 <- ggplot(resolution_rate,
              aes(x = Channel, y = rate, fill = FeedbackType)) +
  geom_col(position = position_dodge(0.75), width = 0.65) +
  geom_text(
    aes(label = percent(rate, accuracy = 1)),
    position = position_dodge(0.75),
    vjust = -0.4, size = 2.8, fontface = "bold"
  ) +
  scale_y_continuous(labels = percent_format(), limits = c(0, 1.05)) +
  scale_fill_manual(
    values = c("#1B4332","#40916C","#B7841A","#8B2635"), name = "Type"
  ) +
  labs(
    title    = "Feedback Resolution Rate by Type and Channel",
    subtitle = "Proportion of feedback items resolved within reporting period",
    caption  = "Source: Accountability / CRM System",
    x = "Channel", y = "Resolution Rate (%)", fill = "Feedback Type"
  ) +
  theme_meal() +
  theme(axis.text.x = element_text(angle = 30, hjust = 1))

save_fig(p11, "11_resolution_by_channel", w = 11, h = 6)


# =============================================================================
# SECTION 6 — STATISTICAL TESTS
# =============================================================================
message("\n=== SECTION 6: STATISTICAL TESTS ===")

# ── 6.1 Chi-square: Gender independence from Vulnerability type ───────────────
tbl_gender_vuln <- table(beneficiaries$Gender, beneficiaries$VulnType)
chi_test <- chisq.test(tbl_gender_vuln)

message("Chi-square test — Gender × Vulnerability Type:")
message("  chi² = ", round(chi_test$statistic, 3))
message("  df   = ", chi_test$parameter)
message("  p    = ", round(chi_test$p.value, 4))
message("  → ", ifelse(chi_test$p.value < 0.05,
                       "Significant association (p < 0.05)",
                       "No significant association (p ≥ 0.05)"))

# ── 6.2 ANOVA: MUAC differences across countries ──────────────────────────────
anova_muac <- aov(MUAC_cm ~ Country, data = nutrition)
anova_tidy  <- tidy(anova_muac)

message("\nANOVA — MUAC across Countries:")
message("  F-statistic = ", round(anova_tidy$statistic[1], 3))
message("  p-value     = ", round(anova_tidy$p.value[1], 4))
message("  → ", ifelse(anova_tidy$p.value[1] < 0.05,
                       "Significant differences in MUAC across countries (p < 0.05)",
                       "No significant differences"))

# ── 6.3 Linear regression: MUAC predicted by age ─────────────────────────────
lm_muac <- lm(MUAC_cm ~ AgeMonths + Gender + Country, data = nutrition)
lm_tidy  <- tidy(lm_muac, conf.int = TRUE)

message("\nLinear Regression — MUAC ~ Age + Gender + Country:")
print(lm_tidy %>%
  select(term, estimate, std.error, p.value) %>%
  mutate(across(c(estimate, std.error, p.value), ~round(.x, 4))))

# ── 6.4 Coefficient plot ──────────────────────────────────────────────────────
lm_plot_data <- lm_tidy %>%
  filter(term != "(Intercept)") %>%
  mutate(
    Significant = p.value < 0.05,
    term = str_replace_all(term, c("Country" = "", "Gender" = "Gender: "))
  )

p12 <- ggplot(lm_plot_data,
              aes(x = estimate, y = reorder(term, estimate),
                  color = Significant, shape = Significant)) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "#888888") +
  geom_errorbarh(aes(xmin = conf.low, xmax = conf.high), height = 0.25,
                 linewidth = 0.8) +
  geom_point(size = 4) +
  scale_color_manual(values = c("TRUE" = "#1B4332", "FALSE" = "#AAAAAA"),
                     name = "p < 0.05") +
  scale_shape_manual(values = c("TRUE" = 16, "FALSE" = 4), name = "p < 0.05") +
  labs(
    title    = "Regression Coefficients: MUAC ~ Age + Gender + Country",
    subtitle = "Points = estimate | Bars = 95% CI | Green = statistically significant",
    caption  = "OLS regression | NABALOUM Emile",
    x = "Coefficient Estimate (cm)", y = NULL
  ) +
  theme_meal()

save_fig(p12, "12_regression_coefficients", w = 10, h = 5.5)

# ── 6.5 Kruskal-Wallis: Resolution time across severity levels ────────────────
kw_test <- kruskal.test(DaysToResolve ~ Severity, data = resolved)
message("\nKruskal-Wallis — Resolution Days by Severity:")
message("  chi² = ", round(kw_test$statistic, 3))
message("  df   = ", kw_test$parameter)
message("  p    = ", round(kw_test$p.value, 4))


# =============================================================================
# SECTION 7 — SUMMARY DASHBOARD PANEL (patchwork)
# =============================================================================
message("\n=== SECTION 7: COMPOSITE DASHBOARD ===")

# Mini sector achievement bars
mini_sector <- ggplot(sector_perf,
                      aes(x = reorder(Sector, mean_achievement),
                          y = mean_achievement, fill = mean_achievement)) +
  geom_col(width = 0.7, show.legend = FALSE) +
  geom_hline(yintercept = 0.80, linetype = "dashed",
             color = "#E74C3C", linewidth = 0.6) +
  scale_y_continuous(labels = percent_format()) +
  scale_fill_gradient(low = "#74C69D", high = "#1B4332") +
  coord_flip() +
  labs(title = "Achievement Rate", x = NULL, y = NULL) +
  theme_meal() + theme(plot.title = element_text(size = 11))

# Mini MUAC histogram
mini_muac <- ggplot(nutrition, aes(x = MUAC_cm, fill = NutritionStatus)) +
  geom_histogram(binwidth = 0.5, color = "white", alpha = 0.85, position = "identity") +
  geom_vline(xintercept = c(11.5, 12.5), linetype = "dashed",
             color = "#555555", linewidth = 0.6) +
  scale_fill_manual(values = PAL_NUTR) +
  labs(title = "MUAC Distribution", x = "MUAC (cm)", y = NULL) +
  theme_meal() + theme(plot.title = element_text(size = 11), legend.position = "none")

# Mini vulnerability pie (waffle-style bar)
vuln_summary <- beneficiaries %>%
  count(VulnType) %>%
  mutate(pct = n / sum(n))

mini_vuln <- ggplot(vuln_summary, aes(x = "", y = pct, fill = VulnType)) +
  geom_col(width = 0.5) +
  scale_fill_manual(values = PAL_VULN, name = NULL) +
  scale_y_continuous(labels = percent_format()) +
  labs(title = "Vulnerability Profile", x = NULL, y = NULL) +
  theme_meal() + theme(plot.title = element_text(size = 11),
                       legend.position = "right")

# Mini resolution rate
res_summary <- accountability %>%
  group_by(Severity) %>%
  summarise(rate = mean(Resolved == "Yes"), .groups = "drop")

mini_res <- ggplot(res_summary, aes(x = Severity, y = rate, fill = Severity)) +
  geom_col(width = 0.65) +
  scale_y_continuous(labels = percent_format(), limits = c(0, 1)) +
  scale_fill_manual(
    values = c("Low"="#27AE60","Medium"="#F39C12","High"="#E67E22","Critical"="#E74C3C")
  ) +
  labs(title = "Feedback Resolution", x = NULL, y = NULL) +
  theme_meal() + theme(legend.position = "none",
                       plot.title = element_text(size = 11))

# Combine with patchwork
dashboard_panel <- (mini_sector | mini_muac) / (mini_vuln | mini_res) +
  plot_annotation(
    title    = "MEAL Impact Dashboard — Sahel Humanitarian Programmes (2023–2024)",
    subtitle = "Portfolio Project 3 | Author: NABALOUM Emile | emi.nabaloum@gmail.com",
    caption  = "Data: Simulated from real MEAL frameworks (SPONG/OCHA, IRC, AUXFIN)",
    theme    = theme(
      plot.title    = element_text(size = 16, face = "bold", color = "#1B4332"),
      plot.subtitle = element_text(size = 11, color = "#555555"),
      plot.caption  = element_text(size = 9,  color = "#888888", hjust = 0)
    )
  )

save_fig(dashboard_panel, "00_dashboard_panel", w = 14, h = 9)

# =============================================================================
# SECTION 8 — SAVE SUMMARY STATISTICS
# =============================================================================
message("\n=== SECTION 8: SAVING SUMMARY ===")

summary_stats <- list(
  indicators = list(
    total_rows          = nrow(indicators),
    mean_achievement    = round(mean(indicators$AchievementRate), 3),
    pct_on_track        = round(mean(indicators$Status == "On Track"), 3),
    pct_delayed         = round(mean(indicators$Status == "Delayed"), 3),
    sectors             = n_distinct(indicators$Sector),
    countries           = n_distinct(indicators$Country)
  ),
  beneficiaries = list(
    total_registered    = nrow(beneficiaries),
    pct_female          = round(mean(beneficiaries$Gender == "Female"), 3),
    pct_children        = round(mean(beneficiaries$AgeGroup %in% c("0-5","6-17")), 3),
    pct_idp             = round(mean(beneficiaries$VulnType == "IDP"), 3)
  ),
  nutrition = list(
    total_screened      = nrow(nutrition),
    sam_rate            = round(mean(nutrition$NutritionStatus == "SAM"), 3),
    mam_rate            = round(mean(nutrition$NutritionStatus == "MAM"), 3),
    oedema_rate         = round(mean(nutrition$Oedema == "Yes"), 3),
    referral_rate       = round(mean(nutrition$Referred == "Yes"), 3),
    mean_muac           = round(mean(nutrition$MUAC_cm, na.rm = TRUE), 2)
  ),
  accountability = list(
    total_feedback      = nrow(accountability),
    resolution_rate     = round(mean(accountability$Resolved == "Yes"), 3),
    mean_days_resolved  = round(mean(resolved$DaysToResolve, na.rm = TRUE), 1),
    critical_cases      = sum(accountability$Severity == "Critical")
  ),
  statistical_tests = list(
    chisq_gender_vuln   = list(
      statistic = round(chi_test$statistic[[1]], 3),
      pvalue    = round(chi_test$p.value, 4)
    ),
    anova_muac_country  = list(
      F_stat  = round(anova_tidy$statistic[1], 3),
      pvalue  = round(anova_tidy$p.value[1], 4)
    ),
    kruskal_resolution  = list(
      chi2   = round(kw_test$statistic[[1]], 3),
      pvalue = round(kw_test$p.value, 4)
    )
  )
)

jsonlite::write_json(summary_stats,
                     "output/summary_statistics.json",
                     pretty = TRUE, auto_unbox = TRUE)

message("  Summary JSON saved → output/summary_statistics.json")
message("\n=== ALL ANALYSES COMPLETE ===")
message("Figures saved to output/figures/ (12 plots + 1 dashboard)")
