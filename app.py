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
    "Project Staff Cost",
]

FREQ_OPTIONS = ["One time", "Monthly", "Quarterly", "Yearly"]

sample_data = {
    "Plant & Machinery": [
        ["Hydra Crane for Material Handling, Transport, & Fabrication", "Monthly", "Nos", 4, 145000],
        ["Crawler Crane (55MT/75MT) for trail assembly", "Monthly", "Nos", 1, 400000],
        ["Trailer for transportation", "Monthly", "Nos", 1, 75000],
        ["Tractor with operator & diesel", "Monthly", "Nos", 1, 38000],
        ["Water Tanker", "Monthly", "Nos", 1, 20000],
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
    
    "Infrastructure": [
        ["Land on lease", "Monthly", "nos", 1, 120000],
        ["Land Development(Grading, cutting, filling compaction(95% PD)", "One time", "Sqm", 30000, 110],
        ["Internal Roads (1600 m x 3 m) (WBM)", "One time", "Sqm", 4800, 300],
        ["Internal Drain (1600 m x 2) (Both sides)", "One time", "Mtr", 3200, 300],
        ["Area Fencing, CCTV, watchtowers", "One time", "Nos", 1, 2500000],
        ["Maintenance of Area including Road & Drain ", "Yearly", "nos", 1, 500000],
        ["In general area Lighting - Light Mast", "One time", "nos", 2, 200000],
        ["Security Gaurd (3 Nos per shift)", "Monthly", "Nos", 9, 15000],
        ["Contractor staff wages (12 Nos)", "Monthly", "Nos", 12, 30000],
        ["Contractor staff accommodation", "Monthly", "nos", 12, 6000],
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
    "Project Staff Cost": [
        ["Site office containar", "One time", "nos", 1, 500000],
        ["Project Staff (4 Nos)", "Monthly", "nos", 4, 75000],
        ["Local conveyance for Project Staff", "Monthly", "nos", 1, 50000],
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
labours_per_month = st.sidebar.number_input("Expected No. of Labours/Month", min_value=1, value=120, step=1)
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
        f"**Total Labour Cost ({labours_per_month} x Rs.{labour_payment_per_month:,}/mo x {duration_months} mo): "
        f"Rs.{total_labour_cost:,.0f}**"
    )
    grand_total_incl_labour = grand_total + total_labour_cost
    st.markdown(
        f"### Grand Total Including Labour: <span style='color: darkgreen; font-weight:bold;'>Rs.{grand_total_incl_labour:,.0f}</span>",
        unsafe_allow_html=True
    )
    per_mt = (grand_total_incl_labour / total_mt) if total_mt else 0
    st.markdown(
        f"### <span style='background-color:#eaffea; padding:3px; border-radius:4px;'>"
        f"Estimated Fabrication Cost per MT = "
        f"Rs.{per_mt:,.0f}</span>",
        unsafe_allow_html=True
    )
else:
    st.warning("Fill at least one section above to see summary and totals below.")

########################################
# 📈 FABRICATION S-CURVE & LABOUR
########################################
st.markdown("---")
st.header("📈 Fabrication S-Curve: Progress & Manpower (Monthly + Cumulative)")

months = np.arange(1, duration_months + 1) if duration_months > 0 else np.array([], dtype=int)

def s_curve(total_mt, duration_months, start_mt=40, max_mt=0, end_mt=40):
    """
    Safe/logistic-ish monthly distribution that handles very short schedules.
    """
    if duration_months <= 0:
        return np.array([])
    # Default max_mt: assume target monthly rate if provided
    max_mt = max_mt if max_mt and max_mt > 0 else (total_mt / max(1, duration_months))

    # Start with a smooth logistic allocation
    m = np.arange(1, duration_months + 1)
    k = 4 / duration_months if duration_months > 4 else 1
    midpoint = duration_months / 2
    raw = 1 / (1 + np.exp(-k * (m - midpoint)))
    monthly = np.diff(np.insert(raw, 0, 0))
    monthly = monthly / monthly.sum() * total_mt

    # Edge shaping (guarded for short durations)
    if duration_months >= 1:
        monthly[0] = min(start_mt, total_mt) if duration_months > 1 else total_mt
    if duration_months >= 2:
        monthly[1] = max(monthly[1], max_mt * 0.6)
    if duration_months >= 3:
        monthly[2] = max(monthly[2], max_mt * 0.8)
    if duration_months >= 2:
        monthly[-1] = min(end_mt, total_mt - monthly[:-1].sum())
    if duration_months >= 3:
        monthly[-2] = max(monthly[-2], max_mt * 0.7)

    # Rebalance to hit total_mt exactly
    scale = total_mt / max(1e-9, monthly.sum())
    monthly *= scale

    # If plenty of middle months, distribute any residual evenly across them
    if duration_months > 6:
        middle = slice(3, duration_months - 2)
        residual = total_mt - monthly.sum()
        if middle.start < middle.stop:
            monthly[middle] += residual / (middle.stop - middle.start)
    else:
        # For short schedules, just set the last month to absorb rounding
        monthly[-1] += total_mt - monthly.sum()

    monthly = np.maximum(monthly, 0)
    return monthly

monthly_mt = s_curve(total_mt, duration_months, start_mt=40, max_mt=mt_per_month, end_mt=40)
cumulative_mt = np.cumsum(monthly_mt) if monthly_mt.size else np.array([])

# Labour: slow start, full after month 3, ramp down at end
monthly_labour = []
for i in range(duration_months):
    if i == 0:
        monthly_labour.append(int(labours_per_month * 0.23))
    elif i == 1:
        monthly_labour.append(int(labours_per_month * 0.60))
    elif 2 <= i < duration_months - 1:
        monthly_labour.append(labours_per_month)
    else:
        monthly_labour.append(int(labours_per_month * 0.33))

if duration_months > 0:
    fig = go.Figure()
    # Cumulative
    fig.add_trace(go.Scatter(
        x=months,
        y=cumulative_mt,
        mode='lines+markers+text',
        name='Cumulative MT',
        line=dict(color='blue', width=2),
        marker=dict(color='blue', size=9),
        text=[f"{int(cm)} MT / {lab} Lab" for cm, lab in zip(cumulative_mt, monthly_labour)],
        textposition="top center",
        textfont=dict(size=10, color="blue"),
        hovertemplate='Month %{x}<br>Cumulative: %{y:.0f} MT<br>Labour: %{customdata}',
        customdata=monthly_labour
    ))
    # Monthly
    fig.add_trace(go.Scatter(
        x=months,
        y=monthly_mt,
        mode='lines+markers+text',
        name='Monthly MT Output',
        line=dict(color='green', dash='dash', width=2),
        marker=dict(color='green', size=9, symbol='diamond'),
        text=[f"{int(mt)} MT / {lab} Lab" for mt, lab in zip(monthly_mt, monthly_labour)],
        textposition="bottom center",
        textfont=dict(size=10, color="green"),
        hovertemplate='Month %{x}<br>Monthly: %{y:.0f} MT<br>Labour: %{customdata}',
        customdata=monthly_labour
    ))

    fig.update_layout(
        title="S-Curve: Fabrication Progress and Labour Deployment",
        xaxis_title="Month",
        yaxis_title="MT (Monthly and Cumulative)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=480,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(
            tickmode='array',
            tickvals=months,
            ticktext=[str(m) for m in months]
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    # Show Data Table
    df_curve = pd.DataFrame({
        "Month": months,
        "Monthly MT": [f"{mt:.0f}" for mt in monthly_mt],
        "Cumulative MT": [f"{cm:.0f}" for cm in cumulative_mt],
        "Labours": monthly_labour
    })
    st.dataframe(df_curve, use_container_width=True)

########################################
# 📄 PDF REPORT GENERATION
########################################
def project_details_card(pdf, total_mt, mt_per_month, labours_per_month, labour_payment_per_month, duration_months):
    pdf.set_draw_color(120, 120, 120)
    pdf.set_fill_color(235, 239, 250)
    pdf.set_line_width(0.3)
    card_y = pdf.get_y()
    card_h = 22
    pdf.rect(10, card_y, 190, card_h, 'DF')
    pdf.set_xy(14, card_y + 2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, "Project Details", ln=1)
    pdf.set_font("Helvetica", "", 7)
    x_start = 15
    pdf.set_x(x_start)
    pdf.cell(55, 5, f"Total Project Scope:", ln=0)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(23, 5, f"{total_mt:,.2f} MT", ln=0)
    pdf.set_font("Helvetica", "", 7)
    pdf.cell(38, 5, f"Output (MT/month):", ln=0)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(21, 5, f"{mt_per_month:,.2f}", ln=1)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_x(x_start)
    pdf.cell(55, 5, f"Expected Labours/Month:", ln=0)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(23, 5, f"{labours_per_month}", ln=0)
    pdf.set_font("Helvetica", "", 7)
    pdf.cell(38, 5, f"Avg. Labour Payment (Rs/mo):", ln=0)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(21, 5, f"Rs.{labour_payment_per_month:,.2f}", ln=1)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_x(x_start)
    pdf.cell(55, 5, f"Duration (months):", ln=0)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(23, 5, f"{duration_months}", ln=0)
    pdf.set_font("Helvetica", "", 7)
    pdf.cell(38, 5, f"Total Area Required:", ln=0)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(21, 5, "30,000 Sqm", ln=1)
    pdf.set_font("Helvetica", "", 7)
    pdf.ln(1)
    pdf.set_y(card_y + card_h + 2)

def totals_card(pdf, grand_total, total_labour_cost, grand_total_incl_labour, per_mt):
    pdf.set_fill_color(233, 249, 235)
    card_y = pdf.get_y()
    card_h = 24
    pdf.set_draw_color(100, 170, 100)
    pdf.set_line_width(0.3)
    pdf.rect(10, card_y, 190, card_h, 'DF')
    pdf.set_xy(14, card_y + 2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, "Summary of Project Cost", ln=1)
    pdf.set_font("Helvetica", "", 7)
    x_start = 15
    pdf.set_x(x_start)
    pdf.cell(65, 5, "Grand Total (excluding Labour):", ln=0)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(30, 80, 180)
    pdf.cell(35, 5, f"Rs.{grand_total:,.2f}", ln=0)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 7)
    pdf.cell(40, 5, "Labour Cost:", ln=0)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(30, 120, 30)
    pdf.cell(35, 5, f"Rs.{total_labour_cost:,.2f}", ln=1)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(0, 0, 0)
    pdf.set_x(x_start)
    pdf.cell(65, 5, "Grand Total incl. Labour:", ln=0)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(30, 80, 180)
    pdf.cell(35, 5, f"Rs.{grand_total_incl_labour:,.2f}", ln=0)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 7)
    pdf.cell(40, 5, "Estimated Fabrication Cost per MT:", ln=0)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(40, 130, 50)
    pdf.cell(35, 5, f"Rs.{per_mt:,.2f}", ln=1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)
    pdf.set_y(card_y + card_h + 2)

def dataframe_to_pdf_table(pdf, df, title, columns, col_widths):
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 10, title, ln=1, align='C')
    pdf.set_font("Helvetica", "B", 7)
    for i, col in enumerate(columns):
        pdf.cell(col_widths[i], 6, col, border=1, align="C", fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 7)
    for _, row in df.iterrows():
        for i, col in enumerate(columns):
            val = str(row[col])
            if col in ["Quantity", "Rate", "Period x", "Amount"]:
                try:
                    val = f"{float(val):,.2f}"
                except Exception:
                    pass
            if col == "Amount":
                val = "Rs. " + val
            pdf.cell(
                col_widths[i], 6, val[:65],
                border=1,
                align="R" if col in ["Quantity", "Rate", "Period x", "Amount"] else "L",
                fill=False
            )
        pdf.ln()

def export_pdf_report(all_dfs, order, totals, grand_total, total_labour_cost, grand_total_incl_labour,
                      per_mt, total_mt, mt_per_month, labours_per_month, labour_payment_per_month, duration_months):
    pdf = FPDF(orientation='P', unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=14)
    columns = ["Description", "Frequency", "Unit", "Quantity", "Rate", "Period x", "Amount"]
    col_widths = [75, 19, 13, 18, 19, 17, 29]

    # PAGE 1
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 11, "Fabrication Detailed Estimate Report", ln=1, align='C')
    pdf.set_font("Arial", size=6)
    pdf.ln(-4)
    pdf.cell(0, 6, "Approx Scope/unit = 4000 MT | Total - 3 Units  | Total = 12000 MT (4-month Phase gap between units)", ln=1, align='C')
    pdf.set_font("Arial", size=10)
    project_details_card(pdf, total_mt, mt_per_month, labours_per_month, labour_payment_per_month, duration_months)

    for idx in range(0, min(3, len(order))):
        center = order[idx]
        df = all_dfs[center]
        dataframe_to_pdf_table(pdf, df, center, columns, col_widths)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(0, 6, f"Subtotal for {center}: Rs.{totals[center]:,.2f}", ln=1)
        pdf.ln(2)

    # PAGE 2
    pdf.add_page()
    for idx in range(3, len(order)):
        center = order[idx]
        df = all_dfs[center]
        dataframe_to_pdf_table(pdf, df, center, columns, col_widths)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 7, f"Subtotal for {center}: Rs.{totals[center]:,.2f}", ln=1)
        pdf.ln(2)

    pdf.ln(2)
    totals_card(pdf, grand_total, total_labour_cost, grand_total_incl_labour, per_mt)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(140, 0, 0)
    pdf.ln(4)
    pdf.multi_cell(0, 6, "Note: Above cost is considered excluding Duct Mock_up Assembly, local authority approvals & local Liasoning Cost.")
    pdf.set_text_color(0, 0, 0)
    return pdf

# ---- PDF + EXCEL Export Buttons (sidebar) ----
if all_details_df:
    cost_center_dfs = {}
    subtotals = {}
    cost_order = [df["Cost Center"].iloc[0] for df in all_details_df]
    for df in all_details_df:
        if not df.empty:
            center = df["Cost Center"].iloc[0]
            cost_center_dfs[center] = df[["Description", "Frequency", "Unit", "Quantity", "Rate", "Period x", "Amount"]]
            subtotals[center] = df["Amount"].sum()

    # Recompute key totals in case block above didn't run
    summary = pd.concat(all_details_df, ignore_index=True)
    grand_total = summary["Amount"].sum()
    total_labour_cost = labours_per_month * labour_payment_per_month * duration_months
    grand_total_incl_labour = grand_total + total_labour_cost
    per_mt = (grand_total_incl_labour / total_mt) if total_mt else 0

    if st.sidebar.button("Generate PDF Report"):
        pdf = export_pdf_report(
            cost_center_dfs, cost_order, subtotals,
            grand_total, total_labour_cost, grand_total_incl_labour,
            per_mt, total_mt, mt_per_month, labours_per_month, labour_payment_per_month, duration_months,
        )
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(tmp_file.name)
        with open(tmp_file.name, "rb") as f:
            st.sidebar.download_button(
                "Download PDF",
                f,
                file_name="Fabrication_Estimate_Report.pdf",
                mime="application/pdf"
            )

    # Excel Export
    export_df = pd.concat(all_details_df, ignore_index=True)
    export_columns = ["Cost Center", "Description", "Frequency", "Unit", "Quantity", "Rate", "Period x", "Amount"]
    export_df = export_df[export_columns]
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        export_df.to_excel(writer, index=False, sheet_name="Summary", startrow=1, header=False)
        workbook = writer.book
        worksheet = writer.sheets['Summary']
        # Headers
        for col_num, value in enumerate(export_columns):
            worksheet.write(0, col_num, value)
        # Amount formula
        for row_num in range(1, len(export_df) + 1):
            worksheet.write_formula(
                row_num,
                export_columns.index('Amount'),
                f"=F{row_num+1}*G{row_num+1}*H{row_num+1}"  # F=Qty, G=Rate, H=Period x
            )
    buffer.seek(0)
    st.sidebar.download_button(
        label="Download Report as Excel",
        data=buffer,
        file_name="Fabrication_Cost_Details.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
