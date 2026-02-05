# -*- coding: utf-8 -*-

from influxdb import InfluxDBClient
import pandas as pd
from datetime import datetime


# =====================================================
# EXPERIMENT PARAMETERS (CONFIGURE HERE)
# =====================================================

EXPERIMENT_MODE = "intrabinding"  # intrabinding | crossbinding
DISTANCE_M = 1  # e.g. 1 | 5 | 10
MAX_SUCCESS_MS = 250  # maximum latency for successful switching
MAX_ASSOCIATION_MS = 1000  # maximum latency for causal association
MAX_OBSERVATION_MS = 5000  # maximum observation window
CSV_OUTPUT_PATH = "/home/georg/Shared"


# =====================================================
# CONFIGURATIONS (ONLY ONE MUST BE ACTIVE AT A TIME!)
# =====================================================

# ---------- INTRA-BINDING: ZIGBEE ----------
BUTTON_MEASUREMENT = "Zigbee_Smart_Button_01_Button_Action"
BUTTON_TRIGGER_VALUE = "single"
PLUG_MEASUREMENT = "ZigbeePlugE2_Switch"
PLUG_TARGET_VALUE = 1

# ---------- INTRA-BINDING: Z-WAVE ----------
# BUTTON_MEASUREMENT = "Z_Wave_Button"
# BUTTON_TRIGGER_VALUE = 0
# PLUG_MEASUREMENT = "ZWave_Plug_OnOff"
# PLUG_TARGET_VALUE = 1

# ---------- CROSS-BINDING: ZIGBEE / Z-WAVE ----------
# BUTTON_MEASUREMENT = "Zigbee_Smart_Button_01_Button_Action"
# BUTTON_TRIGGER_VALUE = "single"
# PLUG_MEASUREMENT = "ZWave_Plug_OnOff"
# PLUG_TARGET_VALUE = 1

# ---------- CROSS-BINDING: Z-WAVE / ZIGBEE ----------
# BUTTON_MEASUREMENT = "Z_Wave_Button"
# BUTTON_TRIGGER_VALUE = 0
# PLUG_MEASUREMENT = "ZigbeePlugE2_Switch"
# PLUG_TARGET_VALUE = 1


# =====================================================
# HELPER FUNCTIONS
# =====================================================
def prepare_measurement_data(data):
    """
    Prepare measurement data:
    - parse timestamps
    - keep only time/value
    - sort chronologically
    - normalize values (string vs numeric)
    """
    data["time"] = pd.to_datetime(data["time"], utc=True, format="ISO8601")

    data = data[["time", "value"]].sort_values("time")

    data["value"] = (
        data["value"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
    )

    return data


def filter_button_trigger_events(button_data, trigger_value):
    """
    Keep only relevant button trigger events.
    """
    return button_data[button_data["value"] == str(trigger_value)]


def classify_latency(latency_ms):
    """
    Map latency to status label.
    """
    if latency_ms <= MAX_SUCCESS_MS:
        return "SUCCESS"
    elif latency_ms <= MAX_ASSOCIATION_MS:
        return "DELAYED"
    return "TIMEOUT"


def export_results_to_csv(measurement_results):
    """
    Write measurement results to CSV file and return filename.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

    csv_file = (
        f"{CSV_OUTPUT_PATH}/"
        f"latency_{EXPERIMENT_MODE}_{DISTANCE_M}m_{timestamp}.csv"
    )

    measurement_results.to_csv(
        csv_file,
        index=False,
        sep=";",
        decimal=",",
        date_format="%Y-%m-%d %H:%M:%S.%f"
    )

    return csv_file


def print_summary(measurement_results, csv_file):
    """
    Console overview of measurement results.
    """

    print(f"\nCSV written to: {csv_file}")

    total = len(measurement_results)

    print("\nStatus overview:")
    print(f"  Total: {total}")

    for status, count in measurement_results["status"].value_counts().items():
        percentage = (count / total) * 100
        print(f"  {status}: {count} ({percentage:.1f} %)")


# =====================================================
# MAIN CALCULATION
# =====================================================

def run_latency_calculation():

    client = InfluxDBClient(host="localhost", port=8086)
    client.switch_database("openhab_db")

    # ---------- Load data ----------
    button_data = pd.DataFrame(
        client.query(f'SELECT * FROM "{BUTTON_MEASUREMENT}"').get_points()
    )

    plug_data = pd.DataFrame(
        client.query(f'SELECT * FROM "{PLUG_MEASUREMENT}"').get_points()
    )

    if button_data.empty or plug_data.empty:
        print("No data available.")
        return


    # ---------- Preparation ----------
    button_data = prepare_measurement_data(button_data)
    plug_data = prepare_measurement_data(plug_data)

    button_data = filter_button_trigger_events(
        button_data,
        BUTTON_TRIGGER_VALUE
    )


    # ---------- Calculation ----------
    target_plug_value = str(PLUG_TARGET_VALUE)
    used_plug_event_times = set()

    measurement_rows = []
    attempt_counter = 1

    for _, button_event in button_data.iterrows():

        # ---- setup attempt ----
        button_time = button_event["time"]

        attempt_id = f"{EXPERIMENT_MODE}_{DISTANCE_M}m_{attempt_counter:03d}"
        attempt_counter += 1

        observation_deadline = button_time + pd.Timedelta(
            milliseconds=MAX_OBSERVATION_MS
        )

        # ---- find valid plug event ----
        after_button = plug_data["time"] > button_time
        within_window = plug_data["time"] <= observation_deadline
        correct_state = plug_data["value"] == target_plug_value
        unused = ~plug_data["time"].isin(used_plug_event_times)

        valid_plug_events = plug_data[
            after_button
            & within_window
            & correct_state
            & unused
        ]

        # ---- no valid plug event found ----
        if valid_plug_events.empty:
            measurement_rows.append({
                "attempt_id": attempt_id,
                "experiment_mode": EXPERIMENT_MODE,
                "distance_m": DISTANCE_M,
                "button_label": BUTTON_MEASUREMENT,
                "plug_label": PLUG_MEASUREMENT,
                "button_time": button_time,
                "plug_time": None,
                "latency_ms": None,
                "status": "NO_REACTION"
            })
            continue

        # ---- valid plug event found ----
        plug_time = valid_plug_events.iloc[0]["time"]
        used_plug_event_times.add(plug_time)

        latency_ms = int(
            (plug_time - button_time).total_seconds() * 1000
        )

        status = classify_latency(latency_ms)

        measurement_rows.append({
            "attempt_id": attempt_id,
            "experiment_mode": EXPERIMENT_MODE,
            "distance_m": DISTANCE_M,
            "button_label": BUTTON_MEASUREMENT,
            "plug_label": PLUG_MEASUREMENT,
            "button_time": button_time,
            "plug_time": plug_time,
            "latency_ms": latency_ms,
            "status": status
        })

    # ---------- Export measurement results ----------
    measurement_results = pd.DataFrame(measurement_rows)
    csv_file = export_results_to_csv(measurement_results)

    # ---------- Console output ----------
    print_summary(measurement_results, csv_file)


if __name__ == "__main__":
    run_latency_calculation()
