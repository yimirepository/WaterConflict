options(stringsAsFactors = FALSE)

# ----------------------------
# 0. Packages
# ----------------------------
required_pkgs <- c(
  "dplyr", "readr", "ggplot2", "ggrepel",
  "scales", "patchwork", "ragg"
)

to_install <- required_pkgs[!required_pkgs %in% installed.packages()[, "Package"]]
if (length(to_install) > 0) install.packages(to_install)

invisible(lapply(required_pkgs, library, character.only = TRUE))

# ----------------------------
# Fixed list of 25 countries to label
# ----------------------------
highlight_countries <- c(
  "Lesotho",
  "South Sudan",
  "Somalia",
  "Romania",
  "United States",
  "Afghanistan",
  "Iran",
  "Palestine",
  "Mexico",
  "Liberia",
  "Paraguay",
  "Austria",
  "Sudan",
  "Turkey",
  "Morocco",
  "Myanmar",
  "Lebanon",
  "Tunisia",
  "Saudi Arabia",
  "Libya",
  "Qatar",
  "United Arab Emirates",
  "Turkmenistan",
  "Zimbabwe",
  "Rwanda"
)

# ----------------------------
# 1. Path
# ----------------------------
data_dir <- "E:/AExperiment/11Water/R_Water/02_fit_score_outputs_v2"

SCENARIO <- "ssp5"

# ----------------------------
# 2. Read data
# ----------------------------
safe_read_csv <- function(path) {
  if (!file.exists(path)) stop("Missing file: ", path)
  readr::read_csv(path, show_col_types = FALSE)
}

stage6 <- safe_read_csv(file.path(data_dir, "stage6_fit_score_long_benchmarked.csv")) %>%
  filter(scenario == SCENARIO)

stage7 <- safe_read_csv(file.path(data_dir, "stage7_fit_country_summary.csv")) %>%
  filter(scenario == SCENARIO)

stage8_country <- safe_read_csv(file.path(data_dir, "stage8_bundle_country_summary.csv")) %>%
  filter(scenario == SCENARIO)

# --- stage3 / RDS
analysis_relevance <- NULL

stage3_path <- file.path(data_dir, "stage3_analysis_relevance.csv")
rds_path    <- file.path(data_dir, "final_bundle_ssp5_all.rds")

if (file.exists(stage3_path)) {
  analysis_relevance <- safe_read_csv(stage3_path) %>%
    filter(scenario == SCENARIO)
} else if (file.exists(rds_path)) {
  tmp <- readRDS(rds_path)
  if ("analysis_relevance" %in% names(tmp)) {
    analysis_relevance <- tmp$analysis_relevance %>%
      filter(scenario == SCENARIO)
  }
}

# ----------------------------
# 3. Build country_master
# ----------------------------
country_relevance <- stage6 %>%
  group_by(iso3, country, year, scenario) %>%
  summarise(
    rel_prescriptive = first(rel_prescriptive),
    rel_supportive = first(rel_supportive),
    rel_stress_relieving = first(rel_stress_relieving),
    .groups = "drop"
  )

country_master <- stage7 %>%
  left_join(
    stage8_country %>%
      select(
        iso3, country, year, scenario,
        first_mode, second_mode, third_mode,
        n_selected_modes, bundle_score
      ),
    by = c("iso3", "country", "year", "scenario")
  ) %>%
  left_join(country_relevance,
            by = c("iso3", "country", "year", "scenario"))

if (!is.null(analysis_relevance)) {
  country_master <- country_master %>%
    left_join(
      analysis_relevance %>%
        select(
          iso3, country, year, scenario,
          conflict_probability,
          gdp_constant_2015_us,
          bws_score,
          precipitation
        ) %>%
        distinct(),
      by = c("iso3", "country", "year", "scenario")
    )
}

# ----------------------------
# 4. Construct variables
# ----------------------------
country_master <- country_master %>%
  mutate(
    risk_value = coalesce(conflict_probability, rel_prescriptive),
    fit_value  = first_mode_benchmark_pct,
    water_stress = coalesce(bws_score, rel_stress_relieving),
    gdp_per_capita = coalesce(gdp_constant_2015_us, 1 - rel_supportive),
    is_highlight = country %in% highlight_countries  # Flag the 25 selected countries.
  )

# ----------------------------
# 5. Automatic selection of 20 countries has been removed.
# ----------------------------

# ----------------------------
# 6. Axis logic
# ----------------------------
if (all(c("precipitation", "gdp_constant_2015_us") %in% names(country_master))) {
  panelD_x <- "precipitation"
  panelD_y <- "gdp_constant_2015_us"
  panelD_x_lab <- "Projected precipitation (mm)"
  panelD_y_lab <- "Projected GDP per capita (constant 2015 US$)"
} else {
  panelD_x <- "water_stress"
  panelD_y <- "gdp_per_capita"
  panelD_x_lab <- "Water stress proxy (index)"
  panelD_y_lab <- "GDP proxy (higher = richer)"
}

# ----------------------------
# 7. Build Panel D data
# ----------------------------
winsorize_vec <- function(x, probs = c(0.02, 0.98)) {
  qs <- quantile(x, probs = probs, na.rm = TRUE)
  pmin(pmax(x, qs[1]), qs[2])
}

tbl_panelD <- country_master %>%
  transmute(
    iso3, country, is_highlight,
    x_value = .data[[panelD_x]],
    y_value = .data[[panelD_y]],
    risk_value
  ) %>%
  filter(!is.na(x_value), !is.na(y_value), !is.na(risk_value)) %>%
  mutate(
    x_plot = winsorize_vec(x_value),
    y_plot = winsorize_vec(y_value)
  )

tbl_panelD_zoom <- tbl_panelD %>%
  filter(x_value < 2000, y_value < 50000)

# ----------------------------
# 8. Theme
# ----------------------------
theme_future <- function() {
  theme_minimal(base_size = 12.5) +
    theme(
      plot.title = element_text(size = 16, face = "bold", colour = "#444444"),
      plot.subtitle = element_text(size = 11, colour = "#444444"),
      axis.title = element_text(size = 11.5, face = "bold", colour = "#444444"),
      axis.text = element_text(size = 10.5, colour = "#444444"),
      panel.grid.minor = element_blank(),
      panel.grid.major = element_line(colour = "#D9D9D9", linewidth = 0.25),
      panel.border = element_rect(colour = "black", fill = NA, linewidth = 1.0)
    )
}

LABEL_SIZE <- 3.4

# ----------------------------
# 9. Main plot (label only the 25 selected countries)
# ----------------------------
p_main <- ggplot() +
  geom_point(
    data = tbl_panelD %>% filter(!is_highlight),
    aes(x = x_plot, y = y_plot, size = risk_value, color = risk_value),
    alpha = 0.20
  ) +
  geom_point(
    data = tbl_panelD %>% filter(is_highlight),
    aes(x = x_plot, y = y_plot, size = risk_value, color = risk_value),
    alpha = 0.99
  ) +
  ggrepel::geom_text_repel(
    data = tbl_panelD %>% filter(is_highlight),
    aes(x = x_plot, y = y_plot, label = country),
    #alpha = 0,   # Hide text labels when this option is enabled.
    size = LABEL_SIZE,
    fontface = "bold",
    color = "black",
    box.padding = 0.24,
    point.padding = 0.16,
    segment.color = "#444444",
    max.overlaps = Inf
  ) +
  scale_color_gradientn(colours = c("#AFC6DD", "#EDC2A8", "#C75B12", "#8C3F74")) +
  scale_size_continuous(range = c(1.8, 6.2)) +
  #scale_x_continuous(labels = scales::label_number(big.mark = ",")) +
  scale_x_continuous(labels = scales::label_number(big.mark = ","), limits = c(NA, 5000)) +
  scale_y_continuous(labels = scales::label_number(big.mark = ",")) +
  labs(x = panelD_x_lab, y = panelD_y_lab) +
  theme_future() +
  theme(legend.position = "none")

# ----------------------------
# 10. Zoom plot (label only the 25 selected countries)
# ----------------------------
p_zoom <- ggplot() +
  geom_point(
    data = tbl_panelD_zoom %>% filter(!is_highlight),
    aes(x = x_value, y = y_value, size = risk_value, color = risk_value),
    alpha = 0.25
  ) +
  geom_point(
    data = tbl_panelD_zoom %>% filter(is_highlight),
    aes(x = x_value, y = y_value, size = risk_value, color = risk_value),
    alpha = 0.95
  ) +
  ggrepel::geom_text_repel(
    data = tbl_panelD_zoom %>% filter(is_highlight),
    aes(x = x_value, y = y_value, label = country),
    #alpha = 0,   # Hide text labels when this option is enabled.
    size = LABEL_SIZE - 0.2,
    fontface = "bold",
    color = "black",
    box.padding = 0.20,
    point.padding = 0.14,
    segment.color = "#444444",
    max.overlaps = Inf
  ) +
  scale_color_gradientn(colours = c("#AFC6DD", "#EDC2A8", "#C75B12", "#8C3F74")) +
  scale_size_continuous(range = c(1.8, 6.2), guide = "none") +
  scale_x_continuous(limits = c(0, 2000), expand = c(0.05, 0), labels = scales::label_number(big.mark = ",")) +
  scale_y_continuous(limits = c(0, 51000), expand = c(0, 0.02), labels = scales::label_number(big.mark = ",")) +
  labs(x = panelD_x_lab, y = panelD_y_lab) +
  theme_future() +
  theme(legend.position = "none")

# ----------------------------
# 11. Save
# ----------------------------
ggsave("C:/Users/Lenovo/Desktop/panelD_main_25_labels.png", p_main, width = 9, height = 5.8, dpi = 600, device = ragg::agg_png)
ggsave("C:/Users/Lenovo/Desktop/panelD_zoom_25.png", p_zoom, width = 7, height = 5.8, dpi = 600, device = ragg::agg_png)

# Show
p_main
p_zoom