# ================================
# Generate mode points shapefile
# ================================

library(dplyr)
library(tidyr)
library(sf)
library(rnaturalearth)
library(readr)

# ----------------------------
# 1. Read the existing selected-country data
# ----------------------------
# Load the selected-country table.
selected_tbl <- readr::read_csv("E:/AExperiment/11Water/R_Water/selected_countries_consistent.csv")

# ----------------------------
# 2. Reshape the first, second, and third recommended modes
# ----------------------------
panelE_modes_df <- selected_tbl %>%
  transmute(
    iso3,
    country,
    risk_value,
    mode_1 = first_mode_short,
    mode_2 = second_mode_short,
    mode_3 = third_mode_short
  ) %>%
  pivot_longer(
    cols = c(mode_1, mode_2, mode_3),
    names_to = "mode_rank",
    values_to = "mode_short"
  ) %>%
  filter(!is.na(mode_short), mode_short != "(none)")

# ----------------------------
# 3. Load world boundaries for centroid calculation
# ----------------------------
world_sf <- rnaturalearth::ne_countries(scale = "medium", returnclass = "sf") %>%
  st_as_sf()

# Use a compatible ISO3 country-code field.
if (!"iso3" %in% names(world_sf) && "iso_a3" %in% names(world_sf)) {
  world_sf$iso3 <- world_sf$iso_a3
}

# ----------------------------
# 4. Calculate country centroids
# ----------------------------
country_centroids_sf <- world_sf %>%
  filter(iso3 %in% panelE_modes_df$iso3) %>%
  st_transform(3857) %>%
  st_centroid() %>%
  st_transform(4326)

centroids_df <- cbind(
  st_drop_geometry(country_centroids_sf),
  st_coordinates(country_centroids_sf)
) %>%
  select(iso3, X, Y)

# ----------------------------
# 5. Join coordinates and offset mode points
# ----------------------------
panelE_modes_df <- panelE_modes_df %>%
  left_join(centroids_df, by = "iso3") %>%
  group_by(iso3) %>%
  arrange(mode_rank, .by_group = TRUE) %>%
  mutate(
    n_modes = n(),
    idx = row_number(),
    
    x_jit = case_when(
      n_modes == 1 ~ X,
      n_modes == 2 & idx == 1 ~ X - 1.8,
      n_modes == 2 & idx == 2 ~ X + 1.8,
      n_modes == 3 & idx == 1 ~ X - 2.2,
      n_modes == 3 & idx == 2 ~ X,
      n_modes == 3 & idx == 3 ~ X + 2.2,
      TRUE ~ X
    ),
    
    y_jit = case_when(
      n_modes == 1 ~ Y,
      n_modes == 2 ~ Y,
      n_modes == 3 & idx == 2 ~ Y + 1.3,
      TRUE ~ Y - 0.7
    )
  ) %>%
  ungroup()

# ----------------------------
# 6. Convert to sf point features
# ----------------------------
points_sf <- panelE_modes_df %>%
  filter(!is.na(x_jit), !is.na(y_jit)) %>%
  st_as_sf(coords = c("x_jit", "y_jit"), crs = 4326)

# ----------------------------
# 7. Export the shapefile
# ----------------------------
st_write(points_sf, "C:/Users/Lenovo/Desktop/mode_points.shp", delete_dsn = TRUE)

message("✅ Shapefile exported: mode_points.shp")