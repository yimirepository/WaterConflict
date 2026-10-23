library(showtext)
font_add("Arial", "C:/Windows/Fonts/arial.ttf")
#showtext_auto()


# ================================
# Panel A standalone FULL script
# ================================

# ----------------------------
# 0. Libraries
# ----------------------------
required_pkgs <- c("dplyr", "purrr", "ggplot2", "tibble", "scales", "readr")

to_install <- required_pkgs[!required_pkgs %in% installed.packages()[, "Package"]]
if (length(to_install) > 0) install.packages(to_install)

invisible(lapply(required_pkgs, library, character.only = TRUE))

# ----------------------------
# 1. Parameters
# ----------------------------
SEED <- 1234
N_BOOT <- 1000
SCENARIO <- "ssp5"

data_dir <- "E:/AExperiment/11Water/R_Water/02_fit_score_outputs_v2"

# ----------------------------
# 2. Load data
# ----------------------------
stage7 <- read_csv(file.path(data_dir, "stage7_fit_country_summary.csv"), show_col_types = FALSE) %>%
  filter(scenario == SCENARIO)

stage8 <- read_csv(file.path(data_dir, "stage8_bundle_country_summary.csv"), show_col_types = FALSE) %>%
  filter(scenario == SCENARIO)

stage3 <- read_csv(file.path(data_dir, "stage3_analysis_relevance.csv"), show_col_types = FALSE) %>%
  filter(scenario == SCENARIO)

# ----------------------------
# 3. Build country_master
# ----------------------------
country_master <- stage7 %>%
  left_join(
    stage8 %>%
      select(iso3, country, year, scenario, n_selected_modes),
    by = c("iso3", "country", "year", "scenario")
  ) %>%
  left_join(
    stage3 %>%
      select(
        iso3, country, year, scenario,
        conflict_probability,
        bws_score,
        gdp_constant_2015_us
      ),
    by = c("iso3", "country", "year", "scenario")
  ) %>%
  mutate(
    # Define country-group indicators.
    high_conflict_risk = conflict_probability >= quantile(conflict_probability, 0.75, na.rm = TRUE),
    severe_water_stress = bws_score >= quantile(bws_score, 0.75, na.rm = TRUE),
    low_income = gdp_constant_2015_us <= quantile(gdp_constant_2015_us, 0.25, na.rm = TRUE)
  )

# ----------------------------
# 4. Bootstrap function
# ----------------------------
bootstrap_prop_ci <- function(data, metric_fun, n_boot = 1000, seed = 1234) {
  set.seed(seed)
  n <- nrow(data)
  
  if (n == 0) {
    return(tibble(estimate = NA_real_, ci_low = NA_real_, ci_high = NA_real_))
  }
  
  est <- metric_fun(data)
  
  boot_vals <- replicate(n_boot, {
    idx <- sample.int(n, size = n, replace = TRUE)
    metric_fun(data[idx, , drop = FALSE])
  })
  
  tibble(
    estimate = est,
    ci_low = quantile(boot_vals, 0.025, na.rm = TRUE),
    ci_high = quantile(boot_vals, 0.975, na.rm = TRUE)
  )
}

# ----------------------------
# 5. Panel A metric function
# ----------------------------
panelA_summary_fun <- function(df, n_boot = 1000, seed = 1234) {
  
  metric_specs <- tibble::tribble(
    ~metric_label, ~metric_fun,
    "Highly fitted measures identified", function(x) mean(x$any_mode_good_hist75, na.rm = TRUE),
    "Very highly fitted measures identified", function(x) mean(x$any_mode_very_good_hist80, na.rm = TRUE),
    "Combination of >1 modes recommended", function(x) mean(x$n_selected_modes > 1, na.rm = TRUE)
  )
  
  purrr::pmap_dfr(metric_specs, function(metric_label, metric_fun) {
    ci <- bootstrap_prop_ci(df, metric_fun, n_boot, seed)
    bind_cols(tibble(metric_label = metric_label), ci)
  })
}

# ----------------------------
# 6. Build summary table
# ----------------------------
summary_groups <- list(
  "All countries" = country_master,
  "High-conflict-risk countries" = country_master %>% filter(high_conflict_risk),
  "Severe-water-stress countries" = country_master %>% filter(severe_water_stress),
  "Low-income countries" = country_master %>% filter(low_income)
)

tbl_panelA <- purrr::imap_dfr(summary_groups, function(df, grp_name) {
  panelA_summary_fun(df, n_boot = N_BOOT, seed = SEED) %>%
    mutate(country_group = grp_name)
}) %>%
  mutate(
    country_group = factor(country_group,
                           levels = c(
                             "All countries",
                             "High-conflict-risk countries",
                             "Severe-water-stress countries",
                             "Low-income countries"
                           )
    ),
    metric_label = factor(metric_label,
                          levels = c(
                            "Highly fitted measures identified",
                            "Very highly fitted measures identified",
                            "Combination of >1 modes recommended"
                          )
    )
  )

# ----------------------------
# 7. Plot function (one metric per figure)
# ----------------------------
plot_panelA_single <- function(data_subset) {
  
  ggplot(
    data_subset,
    aes(x = metric_label, y = estimate, fill = country_group)
  ) +
    geom_col(
      position = position_dodge(width = 1.1),
      width = 0.50,
      colour = "white"
    ) +
    geom_errorbar(
      aes(ymin = ci_low, ymax = ci_high),
      position = position_dodge(width = 1.1),
      width = 0.25,
      linewidth = 0.70
    ) +
    # Flip the coordinate axes.
    coord_flip() +
    
    scale_fill_manual(
      values = c(
        "All countries" = "#8C3F74",
        "High-conflict-risk countries" = "#007A8A",
        "Severe-water-stress countries" = "#C75B12",
        "Low-income countries" = "#1F4E79"
      )
    ) +
    
    scale_y_continuous(
      labels = percent_format(accuracy = 1),
      limits = c(0, 1),
      expand = expansion(mult = c(0, 0.02))
    ) +
    
    theme_minimal(base_family = "Arial") +
    theme(
      text = element_text(family = "Arial", size = 28),
      
      legend.position = "none",
      
      axis.text.x = element_text(size = 18),
      axis.text.y = element_blank(),
      axis.title = element_text(size = 22),
      
      # Configure axis ticks.
      axis.ticks.x = element_line(color = "black"),  # Keep ticks on the x-axis only.
      axis.ticks.y = element_blank(),                # Remove y-axis ticks.
      axis.ticks.length = unit(3, "mm"),             # Set tick length.
      
      panel.grid.major.x = element_blank(),
      panel.grid.minor = element_blank(),
      panel.grid.major.y = element_blank(),
      
      panel.border = element_rect(
        colour = "black",
        fill = NA,
        linewidth = 1.5
      )
    )
}
# ----------------------------
# 8. Save + show
# ----------------------------
metrics <- levels(tbl_panelA$metric_label)

plot_list <- lapply(metrics, function(m) {
  plot_panelA_single(
    tbl_panelA %>% filter(metric_label == m)
  )
})

names(plot_list) <- metrics

ggsave(
  "C:/Users/Lenovo/Desktop/panelA_1_high_fit.png",
  plot_list[[1]],
  width = 6,
  height = 6,
  dpi = 300
)

ggsave(
  "C:/Users/Lenovo/Desktop/panelA_2_very_high_fit.png",
  plot_list[[2]],
  width = 6,
  height = 6,
  dpi = 300
)

ggsave(
  "C:/Users/Lenovo/Desktop/panelA_3_multi_modes.png",
  plot_list[[3]],
  width = 6,
  height = 6,
  dpi = 300
)