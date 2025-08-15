# app.py
import math
import io
import tempfile

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Duct Fabrication Cost Estimator", layout="wide")

########################################
# DATA INITIALIZATION
########################################
cost_centers = [
    "Plant & Machinery",
    "Heavy Tools",
    "Small Tools",
    "Consumables",
    "Safety Items",
    "Infrastructure",
    "LMB Staff Cost",
]

FREQ_OPTIONS = ["One time", "Monthly", "Quarterly", "Yearly"]

sample_data = {
    "Plant & Machinery": [
        ["Hydra Crane for Material Handling, Transport, & Fabrication", "Monthly", "Nos", 4, 145000],
        ["Trailer/Truck/Tractor/Water Tanker", "Monthly", "Nos", 1, 70000],
        ["Ambulance (Emergency Service)", "Monthly", "Nos", 1, 75000],
        ["Welding machines (MIG)", "One time", "Nos", 10, 90000],
        ["Welding Machine (ARC)", "One time", "Nos", 15, 45000],
        ["DG Set for fabrication 200 KVA (with maintenance & service)", "One time", "Nos", 1, 1000000],
    ],
    "Heavy Tools": [
        ["Plate rolling machine (250mm capacity)", "Monthly", "Nos", 1, 12000],
        ["Protector plate rolling machine", "Monthly", "Nos", 1, 10000],
        ["Plate bending machine (2500mm capacity)", "Monthly", "Nos", 1, 12000],
        ["Core Drilling Machine with Drill Bits", "One time", "Nos", 4, 32000],
        ["Pug cutting machines", "One time", "Nos", 7, 25000],
        ["Air Compressor and Blasting/painting Equipment", "One time", "Nos", 2, 1000000],
    ],
    "Small Tools": [
        ["Angle and Straight Grinding Machines (AG4, AG7, FF-2), incl. accessories", "One time", "Nos", 25, 8000],
        ["Portable Electrode Ovens", "One time", "Nos", 5, 3000],
        ["Electrode Holding Ovens", "One time", "Nos", 1, 35000],
        ["Central Mother Oven for Electrode Baking", "One time", "Nos", 1, 35000],
        ["Gas Cutting/Heating Set (with hoses, cables, regulators, torches)", "One time", "Nos", 4, 10000],
        ["PPE Kit: Welding Helmet, Spanner, Lighter, Mask, Gloves, Goggles, etc.", "One time", "Nos", 80, 400],
        ["Tool box with all required tools", "One time", "Set", 1, 40000],
        ["Main/Distribution Board Power Cabling and Distribution Accessories.", "One time", "nos", 1, 40000],
        ["Welding Cable Kits with Accessories (holder, cable lug, etc.)", "One time", "Bundle", 10, 9000],
        ["Syntex Water Storage Tanks / Drums", "One time", "Nos", 2, 5000],
    ],
    "Consumables": [
        ["Industrial Oxygen Cylinders", "Monthly", "Nos", 400, 350],
        ["Industrial LPG Cylinders", "Monthly", "Nos", 40, 2100],
        ["Industrial CO2 Cylinders", "Monthly", "Nos", 300, 720],
        ["Welding Electrodes (6013/7018 Grade)", "Monthly", "KG", 500, 140],
        ["Specialized Welding Electrodes (309N/308L Grade)", "Monthly", "KG", 600, 180],
        ["MIG Filler wire", "Monthly", "KG", 3000, 100],
        ["Consumable for NDT (i.e. DPT)", "Monthly", "set", 5, 450],
        ["Kerosene (For KLT)", "Monthly", "ltr", 80, 90],
        ["Grinding, Cutting, and Buffing Wheels", "Monthly", "nos", 500, 85],
        ["Drilling bits for Hand Drill machine", "Monthly", "nos", 5, 2200],
        ["Power Cables (4 core 4 mm)", "Monthly", "Mtr", 500, 140],
        ["Power Cables (3 core 2 mm)", "Monthly", "Mtr", 500, 70],
        ["Binding wire, Wooden Boards... and other Misc. consumable", "Monthly", "lumsum m", 1, 15000],
        ["Monthly Diesel Consumption for DG", "Monthly", "ltr", 1200, 90],
        ["Monthly Diesel Consumption for Trailer/tractor", "Monthly", "ltr", 150, 90],
        ["Copper Slag for Surface Blasting (7MT/250MT Fabrication)", "Monthly", "Nos", 7, 300],
        ["Electricity Consumption(100-kWh per MT)", "Monthly", "kWh", 25000, 8],
    ],
    "Safety Items": [
        ["First aid Boxes /Centre with Medical Attendant", "Monthly", "nos", 1, 20000],
        ["Safety Helmets- Karam(Ratchet Type PN-521/501)", "Quarterly", "nos", 100, 350],
        ["Safety Jackets- Axtion/karam/Reflectosafe", "Quarterly", "nos", 100, 80],
        ["Safety Shoe-Karam(FS 01)/Vudgyogi/Tiger/Acme", "Quarterly", "nos", 100, 1000],
        ["Nose Mask , Ear Plug & Muff-Venes V-410", "Quarterly", "nos", 100, 40],
        ["All types of Hand gloves, Apron, ...shield", "Quarterly", "nos", 25, 1000],
        ["Safety Googles-Karam(ES 006/007)", "Quarterly", "nos", 30, 200],
        ["Fire-fighting equipments like buckets, extinguishers etc.-safe-pro", "One time", "nos", 10, 5000],
    ],
    "Infrastructure": [
        ["Land on lease", "Monthly", "nos", 1, 200000],
        ["Land Development(Grading, cutting, filling compaction(95% PD)", "One time", "Sqm", 30000, 110],
        ["Internal Roads (1600 m x 3 m) (WBM)", "One time", "Sqm", 4800, 300],
        ["Internal Drain (1600 m x 2) (Both sides)", "One time", "Mtr", 3200, 300],
        ["Area Fencing, CCTV, watchtowers", "One time", "Nos", 1, 2500000],
        ["Maintenance of Area including Road & Drain ", "Yearly", "nos", 1, 500000],
        ["In general area Lighting - Light Mast", "One time", "nos", 1, 200000],
        ["Security Gaurd (3 Nos per shift)", "Monthly", "Nos", 9, 15000],
        ["Contractor staff wages (5 Nos)", "Monthly", "Nos", 5, 25000],
        ["Contractor staff accommodation", "Monthly", "nos", 5, 8000],
        ["Local conveyance for contractor Staff", "Monthly", "nos", 1, 40000],
        ["Contractor site office space (Porta Cabin)", "One time", "nos", 1, 400000],
        ["Contractor storage shed construction", "One time", "nos", 1, 25000],
        ["Labour rest shed", "One time", "nos", 1, 50000],
        ["Labour colony construction", "One time", "nos", 1, 1000000],
        ["Drinking water facilities", "Monthly", "nos", 1, 5000],
        ["Necessary job area lighting", "One time", "nos", 1, 25000],
        ["Sanitation facility at site etc.", "One time", "nos", 1, 250000],
        ["Labour attendance (Biometric machine )", "One time", "nos", 1, 50000],
    ],
    "LMB Staff Cost": [
        ["Site office containar", "One time", "nos", 1, 500000],
        ["LMB Staff (4 Nos)", "Monthly", "nos", 4, 75000],
        ["Local conveyance for LMB Staff", "Monthly", "nos", 1, 50000],
    ]
}

input_columns = ['Description', 'Frequency', 'Unit', 'Quantity', 'Rate']
edited_dfs = {}

# Store each Consumable's base monthly quantity (for 250 MT/month):
CONSUMABLES_BASE_MT = 250  # base reference
consumable_base_qty_map = {
    (row[0], row[1], row[2]): row[3]
    for row in sample_data['Consumables']
}

########################################
# SIDEBAR INPUTS
########################################
st.sidebar.header("Project Size Inputs")
total_mt = st.sidebar.number_input("Total Fabrication Scope (MT)", min_value=1, value=4000, step=1)
mt_per_month = st.sidebar.number_input("Expected Fabrication Output (MT/month)", min_value=1, value=250, step=1)
labours_per_month = st.sidebar.number_input("Expected No. of Labours/Month", min_value=1, value=110, step=1)
labour_payment_per_month = st.sidebar.number_input("Avg. Labour Payment per Month (Rs/month)", min_value=1, value=21000, step=100)
duration_months = math.ceil(total_mt / mt_per_month) if mt_per_month > 0 else 0
st.sidebar.markdown(f"**Estimated Duration:** `{duration_months}` months")

########################################
# MAIN PAGE
########################################
st.title("Duct Fabrication Cost Estimator")
st.write(
    f"**Total Scope:** {total_mt} MT | "
    f"Output/Month:** {mt_per_month} MT | "
    f"**Estimated Months:** {duration_months}"
)

for center in cost_centers:
    with st.expander(center, expanded=False):
        data = sample_data.get(center, [["", FREQ_OPTIONS[0], "", 0, 0]])
        df = pd.DataFrame(data, columns=input_columns)
        df['Frequency'] = df['Frequency'].apply(lambda x: x if x in FREQ_OPTIONS else FREQ_OPTIONS[0])

        # Only for 'Consumables' and only for 'Monthly' frequency rows, adjust qty linearly.
        if center == "Consumables":
            for idx, row in df.iterrows():
                key = (row['Description'], row['Frequency'], row['Unit'])
                if row['Frequency'] == "Monthly" and key in consumable_base_qty_map:
                    base_qty = consumable_base_qty_map[key]
                    adj_qty = base_qty * (mt_per_month / CONSUMABLES_BASE_MT)
                    df.at[idx, 'Quantity'] = round(adj_qty, 2)

        col_config = {
            'Description': st.column_config.TextColumn('Description'),
            'Frequency': st.column_config.SelectboxColumn('Frequency', options=FREQ_OPTIONS),
            'Unit': st.column_config.TextColumn('Unit'),
            'Quantity': st.column_config.NumberColumn('Quantity', min_value=0, step=1),
            'Rate': st.column_config.NumberColumn('Rate', min_value=0, step=1)
        }
        user_df = st.data_editor(
            df,
            column_config=col_config,
            num_rows="dynamic",
            hide_index=True,
            use_container_width=True,
            key=f"{center}_input"
        )
        edited_dfs[center] = user_df

st.markdown("---")

def multiplier_for_frequency(freq, months):
    if freq == "Monthly":
        return months
    elif freq == "Quarterly":
        return months / 3
    elif freq == "Yearly":
        return months / 12
    elif freq == "One time":
        return 1
    else:
        return 1

########################################
# SUMMARY TABLES
########################################
st.header("📋 Grand Detailed Sheet")
all_details_df = []
for center in cost_centers:
    df = edited_dfs[center].copy()
    df = df[(df['Description'] != "") & (df['Quantity'] > 0) & (df['Rate'] > 0)]
    if not df.empty:
        df["Period x"] = df['Frequency'].apply(lambda x: multiplier_for_frequency(x, duration_months))
        df["Amount"] = df["Quantity"] * df["Rate"] * df["Period x"]
        st.subheader(center)
        st.dataframe(
            df[["Description", "Frequency", "Unit", "Quantity", "Rate", "Period x", "Amount"]],
            use_container_width=True, hide_index=True
        )
        st.info(f"Subtotal for {center}: Rs.{df['Amount'].sum():,.0f}")
        df["Cost Center"] = center
        all_details_df.append(df)

if all_details_df:
    summary = pd.concat(all_details_df, ignore_index=True)
    grand_total = summary["Amount"].sum()
    st.markdown("## GRAND TOTAL (excluding Labour): " + f"Rs.{grand_total:,.0f}", unsafe_allow_html=True)
    total_labour_cost = labours_per_month * labour_payment_per_month * duration_months
    st.success(
        f"**Total Labour Cost ({labours_per_month} x R**
