import os
import time
import streamlit as st
import folium
import osmnx as ox
import geopandas as gpd
import numpy as np
# Compatibility workaround for PySheds and newer NumPy
if not hasattr(np, "in1d"):
    np.in1d = np.isin
import networkx as nx
import rasterio

from rasterio.windows import from_bounds
from rasterio.transform import rowcol
from streamlit_folium import st_folium
from pysheds.grid import Grid

# =========================================================
# 1. SETTINGS
# =========================================================

st.set_page_config(
    page_title="Lahar Escape",
    page_icon="🌋",
    layout="wide",
)

CENTER = (-7.54, 110.446)
DISTANCE_M = 5000
PROJECTED_CRS = "EPSG:32749"
DEM_PATH = "s08_e110_1arc_v3.tif"

st.title("🌋 Lahar Escape")
st.subheader("Mount Merapi interactive route planner")

st.warning(
    "EDUCATIONAL PROTOTYPE ONLY. These routes are not verified "
    "safe evacuation routes. Do not use this app for real emergencies."
)


import time
import streamlit as st

# Initialise timer state
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False

if "timer_end_time" not in st.session_state:
    st.session_state.timer_end_time = None

if "timer_duration" not in st.session_state:
    st.session_state.timer_duration = 120  # 2 minutes

st.subheader("⏱️ Evacuation Challenge Timer")

timer_minutes = st.selectbox(
    "Choose your time limit",
    [1, 2, 3, 5],
    index=1,
    format_func=lambda x: f"{x} minute{'s' if x != 1 else ''}",
    key="timer_minutes_select",
)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ Start", key="start_timer"):
        st.session_state.timer_duration = timer_minutes * 60
        st.session_state.timer_end_time = (
            time.time() + st.session_state.timer_duration
        )
        st.session_state.timer_running = True

with col2:
    if st.button("🔄 Reset", key="reset_timer"):
        st.session_state.timer_running = False
        st.session_state.timer_end_time = None
        st.session_state.timer_duration = timer_minutes * 60

with col3:
    if st.button("⏹️ Stop", key="stop_timer"):
        if st.session_state.timer_running:
            st.session_state.timer_duration = max(
                0,
                int(st.session_state.timer_end_time - time.time())
            )
        st.session_state.timer_running = False
        st.session_state.timer_end_time = None

# Calculate remaining time
# Calculate remaining time
if st.session_state.timer_running:
    remaining = max(
        0,
        int(st.session_state.timer_end_time - time.time())
    )

    if remaining == 0:
        st.session_state.timer_running = False
        st.session_state.timer_end_time = None
        st.session_state.timer_duration = 0

        st.error(
            "🚨⏰ TIME IS UP!\n\n"
            "Your evacuation training challenge has ended."
        )

        st.warning(
            "Review your route choice and scenario decisions. "
            "This is a simulated exercise, not a real evacuation warning."
        )

        st.progress(1.0, text="Training time expired")


#### implemntation task - scenarios setput#####

st.header("Choose your lahar scenario")

scenario = st.selectbox(
    "Select a training scenario",
    [
        "Scenario 1 — Heavy rainfall warning",
        "Scenario 2 — Increased river-channel concern",
        "Scenario 3 — Multiple evacuation options",
    ],
)

scenario_details = {
    "Scenario 1 — Heavy rainfall warning": (
        "A training exercise begins after a heavy rainfall warning. "
        "Review the terrain and choose a route to a suitable destination."
    ),
    "Scenario 2 — Increased river-channel concern": (
        "For this fictional exercise, a river channel is flagged for "
        "closer attention. Consider how your route relates to waterways."
    ),
    "Scenario 3 — Multiple evacuation options": (
        "Compare alternative routes and consider the trade-offs "
        "between distance, slope and proximity to waterways."
    ),
}

# Scenario-specific emergency training alert
if scenario == "Scenario 1 — Heavy rainfall warning":
    st.error(
        "🚨 TRAINING ALERT: HEAVY RAINFALL WARNING\n\n"
        "Review the terrain, mapped waterways and route alternatives "
        "before completing the exercise."
    )

elif scenario == "Scenario 2 — Increased river-channel concern":
    st.warning(
        "⚠️ TRAINING ALERT: RIVER-CHANNEL CONCERN\n\n"
        "Pay attention to mapped waterways and compare the limitations "
        "of each route."
    )

elif scenario == "Scenario 3 — Multiple evacuation options":
    st.info(
        "📢 TRAINING ALERT: ROUTE ASSESSMENT\n\n"
        "Compare distance, slope and waterway proximity before "
        "explaining your decision."
    )
st.info(scenario_details[scenario])

if scenario == "Scenario 1 — Heavy rainfall warning":
    st.subheader("Exercise focus: River corridors")
    st.write(
        "Inspect waterways near your route and compare the available "
        "evacuation options."
    )
    st.markdown("**Your task**")
    st.write(
        "1. Select a starting point and destination.\n"
        "2. Turn on the mapped waterways and experimental drainage layers.\n"
        "3. Compare the three routes and note which ones pass near "
        "drainage corridors."
    )

elif scenario == "Scenario 2 — Increased river-channel concern":
    st.subheader("Exercise focus: Channel awareness")
    st.write(
        "Pay particular attention to routes that follow or cross "
        "mapped waterways."
    )
    st.markdown("**Your task**")
    st.write(
        "1. Inspect the mapped waterways and terrain drainage.\n"
        "2. Compare how close each route comes to mapped waterways.\n"
        "3. Identify the trade-offs between route distance and "
        "waterway proximity."
    )

elif scenario == "Scenario 3 — Multiple evacuation options":
    st.subheader("Exercise focus: Route comparison")
    st.write(
        "Compare the shortest route with alternatives that account "
        "for terrain slope and waterways."
    )
    st.markdown("**Your task**")
    st.write(
        "1. Calculate the available route alternatives.\n"
        "2. Compare distance, mean slope and waterway proximity.\n"
        "3. Explain which trade-offs matter most in this exercise."
    )

st.caption(
    "Training exercise only. Experimental drainage and route metrics "
    "do not establish real-world lahar safety."
)




st.subheader("Exercise progress")

if scenario == "Scenario 1 — Heavy rainfall warning":
    tasks = [
        "Select a start point and destination",
        "Inspect mapped waterways and terrain drainage",
        "Compare the three route alternatives",
    ]

elif scenario == "Scenario 2 — Increased river-channel concern":
    tasks = [
        "Inspect mapped waterways and terrain drainage",
        "Compare route proximity to waterways",
        "Identify route trade-offs",
    ]

else:
    tasks = [
        "Calculate the available route alternatives",
        "Compare distance, mean slope and waterway proximity",
        "Explain the trade-offs between routes",
    ]

completed = 0

for i, task in enumerate(tasks):
    if st.checkbox(
        task,
        key=f"exercise_{scenario}_{i}",
    ):
        completed += 1

total = len(tasks)
progress = completed / total

st.progress(progress)

st.write(
    f"**{completed} of {total} tasks completed** "
    f"({progress:.0%})"
)

if completed == total:
    st.success(
        "Scenario complete! You have finished all exercise tasks."
    )


# =========================================================
# 2. SESSION STATE
# =========================================================

defaults = {
    "selection_mode": None,
    "start_point": None,
    "end_point": None,
    "last_processed_click": None,
    "routes": None,
    "route_origin": None,
    "route_destination": None,
    "route_error": None,
    "selected_route": "Shortest route",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# 3. OPENSTREETMAP DATA
# ===================================================



def keep_lines(gdf):
    if gdf.empty:
        return gpd.GeoDataFrame(
            geometry=[],
            crs="EPSG:4326",
        )

    gdf = gdf[
        gdf.geometry.notna()
        & gdf.geometry.geom_type.isin(
            ["LineString", "MultiLineString"]
        )
    ].copy()

    return gdf.to_crs("EPSG:4326").reset_index(drop=True)


@st.cache_resource
def get_road_graph():
    # retain_all=False asks OSMnx to keep the largest weakly
    # connected component of the drivable network.
    return ox.graph_from_point(
        CENTER,
        dist=DISTANCE_M,
        network_type="drive",
        simplify=True,
        retain_all=False,
    )


# =========================================================
# 4. TERRAIN DATA
# =========================================================
@st.cache_data(ttl=86400)
def get_features():
    try:
        tags_highway = {"highway": True}
        tags_water = {"waterway": True}

        highways = ox.features_from_point(
            CENTER,
            tags=tags_highway,
            dist=DISTANCE_M
        )

        waterways = ox.features_from_point(
            CENTER,
            tags=tags_water,
            dist=DISTANCE_M
        )

        return highways, waterways

    except Exception as e:
        st.error(
            "Could not download map features from OpenStreetMap. "
            "Please check your internet connection and try again."
        )
        st.caption(f"Technical details: {e}")
        st.stop()

@st.cache_data
def load_terrain(path):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Cannot find {path}. Put it beside app.py."
        )

    with rasterio.open(path) as src:
        window = from_bounds(
            CENTER[1] - 0.10,
            CENTER[0] - 0.10,
            CENTER[1] + 0.10,
            CENTER[0] + 0.10,
            src.transform,
        ).round_offsets().round_lengths()

        masked = src.read(
            1,
            window=window,
            masked=True,
        ).astype("float32")

        # Convert integer elevation data before filling missing pixels.
        elevation = masked.filled(np.nan)
        transform = src.window_transform(window)

        left, bottom, right, top = src.window_bounds(window)
        bounds = [[bottom, left], [top, right]]

        px = (
            abs(transform.a)
            * 111320
            * np.cos(np.radians(CENTER[0]))
        )
        py = abs(transform.e) * 111320

    valid = np.isfinite(elevation)

    if not valid.any():
        raise ValueError("No valid elevation pixels were found.")

    elevation = np.where(
        valid,
        elevation,
        np.nanmedian(elevation),
    ).astype("float32")

    gy, gx = np.gradient(elevation, py, px)

    slope = np.degrees(
        np.arctan(np.sqrt(gx**2 + gy**2))
    )

    slope_rad = np.arctan(np.sqrt(gx**2 + gy**2))
    aspect = np.arctan2(-gx, gy)

    altitude = np.radians(45)
    azimuth = np.radians(315)

    shade = (
        np.sin(altitude) * np.cos(slope_rad)
        + np.cos(altitude)
        * np.sin(slope_rad)
        * np.cos(azimuth - aspect)
    )

    grey = (np.clip(shade, 0, 1) * 255).astype("uint8")

    hill_rgba = np.dstack([
        grey,
        grey,
        grey,
        np.full(grey.shape, 115, dtype="uint8"),
    ])

    slope_rgba = np.zeros(
        (*slope.shape, 4),
        dtype="uint8",
    )

    slope_rgba[slope < 5] = [60, 180, 75, 105]
    slope_rgba[(slope >= 5) & (slope < 15)] = [255, 220, 50, 115]
    slope_rgba[(slope >= 15) & (slope < 30)] = [255, 140, 30, 125]
    slope_rgba[slope >= 30] = [220, 40, 40, 140]

    return hill_rgba, slope_rgba, slope, transform, bounds


######calculating terrain drainage#####

@st.cache_data(show_spinner="Calculating terrain drainage...")
def load_drainage(path):
    """Calculate experimental drainage and return geographic bounds."""
    import rasterio
    from rasterio.warp import transform_bounds

    grid = Grid.from_raster(path)
    dem = grid.read_raster(path)

    pit_filled = grid.fill_pits(dem)
    flooded = grid.fill_depressions(pit_filled)
    conditioned = grid.resolve_flats(flooded)
    flow_dir = grid.flowdir(conditioned)
    accumulation = grid.accumulation(flow_dir)

    # Get the DEM's actual bounds and convert them to latitude/longitude.
    with rasterio.open(path) as src:
        left, bottom, right, top = src.bounds
        source_crs = src.crs

        west, south, east, north = transform_bounds(
            source_crs,
            "EPSG:4326",
            left, bottom, right, top,
        )

    return np.asarray(accumulation), [west, south, east, north]




def sample_slope(geometry, transform, slope_grid):
    point = geometry.representative_point()

    row, col = rowcol(
        transform,
        point.x,
        point.y,
    )

    if (
        row < 0 or col < 0
        or row >= slope_grid.shape[0]
        or col >= slope_grid.shape[1]
    ):
        return 10.0

    value = float(slope_grid[row, col])

    return value if np.isfinite(value) else 10.0

#### Load teh shapefilew for lahars####
@st.cache_data
def load_lahar_hazard():
    hazard_path = "merapi_hazard_zones.shp"

    hazard = gpd.read_file(hazard_path)

    if hazard.crs is None:
        raise ValueError(
            "The hazard shapefile has no coordinate reference system."
        )

    return hazard.to_crs(epsg=4326)



# =========================================================
# 5. PREPARE ROUTE COSTS
# =========================================================

def prepare_route_weights(graph, waterways, slope, transform):
    edges = ox.graph_to_gdfs(
        graph,
        nodes=False,
        edges=True,
    )

    edges_projected = edges.to_crs(PROJECTED_CRS)
    water_projected = waterways.to_crs(PROJECTED_CRS)
    water_union = water_projected.geometry.unary_union

    for edge_id, edge in edges.iterrows():
        u, v, key = edge_id
        data = graph[u][v][key]

        length = max(
            float(data.get("length", 1)),
            1.0,
        )

        geom = edge.geometry
        projected_geom = edges_projected.loc[edge_id].geometry

        if geom is None or geom.is_empty:
            data["length_cost"] = length
            data["slope_cost"] = length * 2
            data["water_cost"] = length * 2
            continue

        slope_value = sample_slope(
            geom,
            transform,
            slope,
        )

        water_distance = projected_geom.distance(water_union)

        data["length_cost"] = length

        # Preference for gentler slopes; not a safety rating.
        data["slope_cost"] = length * (
            1 + slope_value / 15
        )

        # Experimental penalty near mapped waterways.
        proximity_penalty = max(
            0,
            (500 - water_distance) / 500,
        )

        data["water_cost"] = length * (
            1 + 4 * proximity_penalty
        )

        data["slope_deg"] = slope_value
        data["water_distance_m"] = water_distance

    return graph


# =========================================================
# 6. MAP DRAWING
# =========================================================


def make_map(
    center,
    zoom,
    roads,
    water,
    hill,
    slope_image,
    bounds,
    start=None,
    end=None,
    routes=None,
    drainage_percentile=90,
    drainage_checkbox_key="drainage_checkbox",
):
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    # Terrain hillshade
    hill_layer = folium.FeatureGroup(
        name="Terrain hillshade",
        show=True,
    )

    folium.raster_layers.ImageOverlay(
        image=hill,
        bounds=bounds,
        opacity=1,
        interactive=False,
        cross_origin=False,
    ).add_to(hill_layer)

    hill_layer.add_to(m)

    # Terrain slope
    slope_layer = folium.FeatureGroup(
        name="Terrain slope",
        show=False,
    )

    folium.raster_layers.ImageOverlay(
        image=slope_image,
        bounds=bounds,
        opacity=1,
        interactive=False,
        cross_origin=False,
    ).add_to(slope_layer)

    slope_layer.add_to(m)

    # Roads
    folium.GeoJson(
        roads.to_json(),
        name="Mapped roads",
        style_function=lambda f: {
            "color": "#E69528",
            "weight": 2,
            "opacity": 0.65,
        },
    ).add_to(m)

    # Waterways
    folium.GeoJson(
        water.to_json(),
        name="Mapped waterways",
        style_function=lambda f: {
            "color": "#1688E8",
            "weight": 3,
        },
    ).add_to(m)

    # Published hazard zone
    try:
        hazard = load_lahar_hazard()

        hazard_layer = folium.FeatureGroup(
            name="Published KRB I Hazard Zone",
            show=False,
        )

        folium.GeoJson(
            hazard.to_json(),
            name="KRB I reference zone",
            style_function=lambda feature: {
                "fillColor": "#ff7800",
                "color": "#b45309",
                "weight": 2,
                "fillOpacity": 0.25,
            },
            tooltip="Published KRB I volcanic hazard zone",
        ).add_to(hazard_layer)

        hazard_layer.add_to(m)

    except Exception as e:
        st.warning(
            f"Could not load the KRB I hazard layer: {e}"
        )

    
    # Optional experimental drainage overlay
    show_drainage = st.checkbox(
        "Show experimental terrain drainage",
        value=False,
	key=drainage_checkbox_key,
        help=(
            "Displays terrain-derived drainage pathways. "
            "This is not a validated lahar prediction."
        ),
    )

    if show_drainage:
        try:
            with st.spinner("Calculating terrain drainage..."):
                accumulation, drainage_extent = load_drainage(DEM_PATH)

            accumulation = np.asarray(accumulation)

            threshold = np.nanpercentile(
		accumulation,
		drainage_percentile,
	    )

            drainage_mask = (
                np.isfinite(accumulation)
                & (accumulation >= threshold)
            )

            drainage_rgba = np.zeros(
                (*accumulation.shape, 4),
                dtype=np.uint8,
            )

            drainage_rgba[drainage_mask] = [255, 0, 255, 255]

            folium.raster_layers.ImageOverlay(
                image=drainage_rgba,
                bounds=[
                    [drainage_extent[1], drainage_extent[0]],
                    [drainage_extent[3], drainage_extent[2]],
                ],
                opacity=0.75,
                name="Experimental terrain drainage",
                interactive=False,
                cross_origin=False,
            ).add_to(m)

        except Exception as e:
            st.warning(f"Could not calculate terrain drainage: {e}")


    # Route colours
    colours = {
        "Shortest route": "#D7191C",
        "Slope-aware route": "#7B3294",
        "Waterway-aware route": "#008837",
    }

    # Evacuation routes
    if routes:
        for name, route in routes.items():
            if route is None or route.empty:
                continue

            route_wgs = route.to_crs("EPSG:4326")

            folium.GeoJson(
                route_wgs.to_json(),
                name=name,
                style_function=lambda f, n=name: {
                    "color": colours[n],
                    "weight": 5,
                    "opacity": 0.95,
                },
                tooltip=name,
            ).add_to(m)

    # Start marker
    if start:
        folium.Marker(
            start,
            tooltip="Start point",
            icon=folium.Icon(
                color="blue",
                icon="play",
            ),
        ).add_to(m)

    # Destination marker
    if end:
        folium.Marker(
            end,
            tooltip="Destination",
            icon=folium.Icon(
                color="green",
                icon="flag",
            ),
        ).add_to(m)

    # One layer control for all map layers
    folium.LayerControl(
        collapsed=False
    ).add_to(m)

    return m



# =========================================================
# 7. LOAD DATA
# =========================================================

with st.spinner("Loading roads and waterways..."):
    try:
        raw_roads, raw_water = get_features()
        roads = keep_lines(raw_roads)
        water = keep_lines(raw_water)

        if roads.empty:
            st.error("No mapped roads were found.")
            st.stop()

        if water.empty:
            st.error("No mapped waterways were found.")
            st.stop()

    except Exception as error:
        st.error("Could not load OpenStreetMap data.")
        st.code(str(error))
        st.stop()

with st.spinner("Loading terrain..."):
    try:
        hill, slope_image, slope_grid, dem_transform, dem_bounds = (
            load_terrain(DEM_PATH)
        )
    except Exception as error:
        st.error("Could not load the SRTM terrain file.")
        st.code(str(error))
        st.stop()

with st.spinner("Preparing the road network..."):
    try:
        graph = get_road_graph()

        graph = prepare_route_weights(
            graph,
            water,
            slope_grid,
            dem_transform,
        )

    except Exception as error:
        st.error("Could not prepare the road network.")
        st.code(str(error))
        st.stop()


# =========================================================
# 8. CHOOSE START AND DESTINATION ON THE MAP
# =========================================================

st.header("1. Select points on the map")

st.write(
    "Click a button below, then click the map to place that point. "
    "You do not need to enter coordinates."
)

col_start, col_end, col_reset = st.columns(3)

with col_start:
    if st.button("📍 Set start point", use_container_width=True):
        st.session_state.selection_mode = "start"

with col_end:
    if st.button("🏁 Set destination", use_container_width=True):
        st.session_state.selection_mode = "end"

with col_reset:
    if st.button("↩ Reset points", use_container_width=True):
        st.session_state.start_point = None
        st.session_state.end_point = None
        st.session_state.routes = None
        st.session_state.route_error = None
        st.session_state.selection_mode = None
        st.session_state.last_processed_click = None
        st.rerun()

if st.session_state.selection_mode == "start":
    st.info("Start point mode: click the map where your journey begins.")
elif st.session_state.selection_mode == "end":
    st.info("Destination mode: click the map where you want to go.")
else:
    st.info("Choose a point-setting button, then click the map.")

start = st.session_state.start_point
end = st.session_state.end_point

if start:
    st.write(f"Start selected: {start[0]:.5f}, {start[1]:.5f}")

if end:
    st.write(f"Destination selected: {end[0]:.5f}, {end[1]:.5f}")

#####slider####

drainage_percentile = st.slider(
    "Drainage network detail",
    min_value=70,
    max_value=99,
    value=90,
    step=1,
    help=(
        "Lower values show more terrain drainage pathways. "
        "This is a display setting, not a lahar-risk score."
    ),
)




selection_map = make_map(
    center=CENTER,
    zoom=12,
    roads=roads,
    water=water,
    hill=hill,
    slope_image=slope_image,
    bounds=dem_bounds,
    start=start,
    end=end,
    routes=st.session_state.routes,
    drainage_percentile=drainage_percentile,
    drainage_checkbox_key="selection_drainage_checkbox",
)

map_result = st_folium(
    selection_map,
    width=None,
    height=650,
    key="point_selection_map",
)

clicked = map_result.get("last_clicked") if map_result else None

if clicked and st.session_state.selection_mode:
    click_signature = (
        round(clicked["lat"], 6),
        round(clicked["lng"], 6),
    )

    if click_signature != st.session_state.last_processed_click:
        selected_point = (
            float(clicked["lat"]),
            float(clicked["lng"]),
        )

        if st.session_state.selection_mode == "start":
            st.session_state.start_point = selected_point
        elif st.session_state.selection_mode == "end":
            st.session_state.end_point = selected_point

        st.session_state.last_processed_click = click_signature
        st.session_state.selection_mode = None
        st.session_state.routes = None
        st.session_state.route_error = None
        st.rerun()


# =========================================================
# 9. GENERATE THREE ROUTES
# =========================================================



st.header("2. Generate route options")

if not start or not end:
    st.caption(
        "Select both points on the map before generating routes."
    )

if st.button(
    "Generate three routes",
    type="primary",
    disabled=not (start and end),
):
    try:
        start_node = ox.distance.nearest_nodes(
            graph,
            X=start[1],
            Y=start[0],
        )

        end_node = ox.distance.nearest_nodes(
            graph,
            X=end[1],
            Y=end[0],
        )

        # Find nodes in the same weakly connected component.
        # This helps avoid selecting a disconnected road fragment.
        components = list(nx.weakly_connected_components(graph))

        node_component = {}
        for component_index, component in enumerate(components):
            for node in component:
                node_component[node] = component_index

        start_component = node_component.get(start_node)

        if start_component is None:
            raise ValueError("The start point did not snap to a road node.")

        if node_component.get(end_node) != start_component:
            # Find the nearest destination node within the start node's
            # component, rather than using a disconnected component.
            component_nodes = list(components[start_component])

            end_x, end_y = end[1], end[0]

            end_node = min(
                component_nodes,
                key=lambda node: (
                    (graph.nodes[node]["x"] - end_x) ** 2
                    + (graph.nodes[node]["y"] - end_y) ** 2
                ),
            )

            snapped_destination = (
                graph.nodes[end_node]["y"],
                graph.nodes[end_node]["x"],
            )

            st.warning(
                "The destination was not connected to the same road "
                "network as the start. The app selected the nearest "
                "connected road node instead. Check the destination "
                "marker on the map."
            )

            st.session_state.end_point = snapped_destination
            end = snapped_destination

        if start_node == end_node:
            raise ValueError(
                "Start and destination snapped to the same road node. "
                "Choose points farther apart."
            )

        route_options = [
            ("Shortest route", "length_cost"),
            ("Slope-aware route", "slope_cost"),
            ("Waterway-aware route", "water_cost"),
        ]

        calculated = {}
        errors = []

        with st.spinner("Finding connected road paths..."):
            for route_name, weight in route_options:
                try:
                    path = ox.routing.shortest_path(
                        graph,
                        start_node,
                        end_node,
                        weight=weight,
                    )

                    if not path or len(path) < 2:
                        calculated[route_name] = None
                        errors.append(
                            f"{route_name}: no path found."
                        )
                        continue

                    calculated[route_name] = ox.routing.route_to_gdf(
                        graph,
                        path,
                        weight=weight,
                    )

                except Exception as error:
                    calculated[route_name] = None
                    errors.append(f"{route_name}: {error}")

        st.session_state.routes = calculated
        st.session_state.route_origin = (
            graph.nodes[start_node]["y"],
            graph.nodes[start_node]["x"],
        )
        st.session_state.route_destination = (
            graph.nodes[end_node]["y"],
            graph.nodes[end_node]["x"],
        )
        st.session_state.route_error = errors
        st.rerun()

    except Exception as error:
        st.session_state.route_error = [str(error)]
        st.error("Route calculation failed.")
        st.code(str(error))


st.subheader("Understanding the Results")

st.markdown("""
- **Distance:** The total length of the route.
- **Average slope:** The average terrain slope sampled along the route.
- **Waterway proximity:** How close the route is to mapped waterways.

A shorter route is not necessarily safer. These measurements
do not predict lahar inundation or account for road closures,
bridge failures, or actual road conditions. Follow official
emergency instructions during an emergency.
""")


# =========================================================
# 10. COMPARE ROUTES AND SHOW FULL + CLOSE-UP MAPS
# =========================================================

routes = st.session_state.routes

if st.session_state.route_error:
    for message in st.session_state.route_error:
        st.warning(message)

if routes:
    available_routes = [
        name
        for name, route in routes.items()
        if route is not None and not route.empty
    ]

    st.header("3. Compare routes")

    if not available_routes:
        st.error(
            "No route could be generated. Try choosing start and "
            "destination points closer to connected mapped roads."
        )
    else:
        for name in available_routes:
            route = routes[name]
            metric_route = route.to_crs(PROJECTED_CRS)

            length_km = metric_route.geometry.length.sum() / 1000

            slopes = route["slope_deg"].dropna()
            mean_slope = (
                slopes.mean() if not slopes.empty else float("nan")
            )

            water_distances = route["water_distance_m"].dropna()
            nearest_water = (
                water_distances.min()
                if not water_distances.empty
                else float("nan")
            )

            st.subheader(name)

            a, b, c = st.columns(3)

            a.metric("Route length", f"{length_km:.2f} km")
            b.metric(
                "Mean sampled slope",
                f"{mean_slope:.1f}°"
                if np.isfinite(mean_slope)
                else "Unavailable",
            )
            c.metric(
                "Nearest mapped waterway",
                f"{nearest_water:.0f} m"
                if np.isfinite(nearest_water)
                else "Unavailable",
            )

        selected_route_name = st.selectbox(
            "Choose a route for the close-up map",
            available_routes,
            key="selected_route_name",
        )

        st.header("4. Route maps")

        origin = st.session_state.route_origin
        destination = st.session_state.route_destination

        full_map = make_map(
            center=origin,
            zoom=12,
            roads=roads,
            water=water,
            hill=hill,
            slope_image=slope_image,
            bounds=dem_bounds,
            start=origin,
            end=destination,
            routes=routes,
	    drainage_checkbox_key="full_drainage_checkbox",
        )

        selected_route = routes[selected_route_name].to_crs(
            "EPSG:4326"
        )

        route_union = selected_route.geometry.union_all()
        minx, miny, maxx, maxy = route_union.bounds

        close_map = make_map(
            center=[
                (miny + maxy) / 2,
                (minx + maxx) / 2,
            ],
            zoom=14,
            roads=roads,
            water=water,
            hill=hill,
            slope_image=slope_image,
            bounds=dem_bounds,
            start=origin,
            end=destination,
            routes=routes,
        )

        full_col, close_col = st.columns(2, gap="medium")

        with full_col:
            st.subheader("Full study area")
            st_folium(
                full_map,
                width=None,
                height=600,
                key="route_full_map",
            )

        with close_col:
            st.subheader(f"Close-up: {selected_route_name}")
            st_folium(
                close_map,
                width=None,
                height=600,
                key=f"route_close_map_{selected_route_name}",
            )


st.subheader("Justify your route choice")

route_reason = st.radio(
    "Why did you choose this route?",
    [
        "It is the shortest route",
        "It has gentler slopes",
        "It avoids mapped waterways",
        "I considered the current scenario and route trade-offs",
    ],
    key="route_justification"
)

extra_reason = st.text_area(
    "Explain your decision (optional)",
    placeholder="Explain how the route metrics influenced your choice...",
    key="route_explanation"
)

if st.button("Evaluate my decision", key="evaluate_route"):
    st.session_state["route_feedback_requested"] = True


if st.session_state.get("route_feedback_requested", False):
    st.markdown("### Feedback on your decision")

    # Scenario-specific feedback
    if scenario == "Scenario 1 — Heavy rainfall warning":
        st.info(
            "Heavy rainfall scenario: consider how terrain, mapped "
            "hazard zones, and uncertainty affect your reasoning. "
            "Do not assume that the shortest route is automatically "
            "the safest."
        )

        if route_reason == "It has gentler slopes":
            st.write(
                "You prioritised terrain. Consider the displayed "
                "slope metrics, but remember that slope alone cannot "
                "predict lahar exposure."
            )
        elif route_reason == "It is the shortest route":
            st.write(
                "A shorter route may reduce distance, but your "
                "reasoning should also acknowledge the rainfall "
                "scenario and the limitations of the hazard data."
            )
        elif route_reason == "It avoids mapped waterways":
            st.write(
                "You considered waterways, which is relevant to "
                "your exercise. However, mapped waterways do not "
                "represent every possible lahar pathway."
            )
        else:
            st.write(
                "You considered several factors. Strengthen your "
                "justification by referring to specific route metrics "
                "and explaining the uncertainties."
            )

    elif scenario == "Scenario 2 — Increased river-channel concern":
        st.info(
            "River-channel concern scenario: pay particular attention "
            "to mapped waterways and explain how they influence your "
            "route choice. The drainage overlay is experimental, "
            "not a validated lahar forecast."
        )

        if route_reason == "It avoids mapped waterways":
            st.write(
                "Your reasoning addresses the main concern in this "
                "scenario. Explain which mapped features support your "
                "choice and acknowledge that the map may be incomplete."
            )
        elif route_reason == "It is the shortest route":
            st.write(
                "Distance is useful, but it does not tell you whether "
                "the route approaches mapped waterways. Compare the "
                "available route information before justifying your choice."
            )
        elif route_reason == "It has gentler slopes":
            st.write(
                "Slope is one consideration, but it does not establish "
                "whether a route avoids river-channel areas. Explain "
                "how you considered the waterway information too."
            )
        else:
            st.write(
                "Good start: explain how you balanced distance, slope, "
                "and waterway information, and identify what remains uncertain."
            )

    elif scenario == "Scenario 3 — Multiple evacuation options":
        st.info(
            "Multiple-options scenario: compare the available routes "
            "and explain the trade-offs between distance, slope, and "
            "mapped waterways rather than relying on one metric alone."
        )

        if route_reason == "I considered the current scenario and route trade-offs":
            st.write(
                "Your reasoning considers multiple factors. Make it "
                "stronger by citing specific differences in the displayed "
                "route metrics and explaining why they matter."
            )
        elif route_reason == "It is the shortest route":
            st.write(
                "You have a clear priority. Compare the selected route "
                "with the alternatives to identify what you gain or "
                "give up in distance, slope, and waterway considerations."
            )
        elif route_reason == "It has gentler slopes":
            st.write(
                "You prioritised terrain. Compare the distance and "
                "waterway information too, and explain why that trade-off "
                "matters in this scenario."
            )
        else:
            st.write(
                "You considered waterways. Compare the other route "
                "metrics as well, and explain how they influenced "
                "your final choice."
            )

    else:
        st.warning(
            "Scenario not recognised. Review the selected scenario "
            "and explain your route choice using the displayed metrics."
        )

    if extra_reason.strip():
        st.markdown("**Your explanation**")
        st.write(extra_reason)
        st.caption(
            "Review whether your explanation refers to evidence from "
            "the map and acknowledges uncertainty."
        )

    st.warning(
        "This is educational, rule-based feedback. It does not "
        "verify real-world route safety or predict lahar movement."
    )



st.subheader("Understanding the Results")

st.markdown("""
- **Distance:** The total length of the route.
- **Average slope:** The average terrain slope sampled along the route.
- **Waterway proximity:** How close the route is to mapped waterways.

A shorter route is not necessarily safer. These measurements
do not predict lahar inundation or account for road closures,
bridge failures, or actual road conditions. Follow official
emergency instructions during an emergency.
""")

# =========================================================
# 11. LIMITATIONS
# =========================================================

st.divider()

st.subheader("Important limitations")

st.markdown(
    """
    - The shortest option prioritises mapped road distance.
    - The slope-aware option penalises steeper sampled terrain.
    - The waterway-aware option penalises proximity to mapped waterways.
    - The waterway penalty is an experimental setting, not an official
      lahar hazard boundary.
    - The app does not model lahar flow, inundation, debris, road closures,
      bridge failures, or actual road passability.
    - Snapping a point to a road does not mean that the road is safe.
    """
)

st.error(
    "These routes are experimental and must not be used as real "
    "evacuation instructions. Real planning requires official hazard "
    "maps, validated destinations, and local emergency-authority guidance."
)

st.divider()
st.subheader("About this simulation")

st.info(
    "Lahar Escape is an educational prototype for exploring "
    "terrain, alternative routes, and hypothetical evacuation scenarios "
    "around Mount Merapi. Routes and terrain-derived drainage paths "
    "are experimental and have not been validated for real emergencies. "
    "Mapped hazard information may not be complete or current. "
    "Do not use this prototype to make real-world evacuation decisions. "
    "Follow official guidance from local authorities."
)
