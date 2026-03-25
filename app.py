import streamlit as st
import pandas as pd
import numpy as np

# Page setup
st.set_page_config(page_title="VTCS Auditor", layout="wide")
st.title("🚛 VTCS & GPS Tracking Auditor")

# Sidebar Uploads
st.sidebar.header("Upload Data")

vtcs_file = st.sidebar.file_uploader("1. Upload VTCS Data", type=['xlsx','csv'])
tracking_file = st.sidebar.file_uploader("2. Upload Tracking Report", type=['xlsx','csv'])
coord_file = st.sidebar.file_uploader("3. Upload TCP/WE Coordinates", type=['xlsx','csv'])

# Distance formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(np.radians,[lat1, lon1, lat2, lon2])
    dlat = lat2-lat1
    dlon = lon2-lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return 2*R*np.arcsin(np.sqrt(a))

if vtcs_file and tracking_file and coord_file:

    # Read files
    vtcs = pd.read_excel(vtcs_file) if vtcs_file.name.endswith('xlsx') else pd.read_csv(vtcs_file)
    tracking = pd.read_excel(tracking_file) if tracking_file.name.endswith('xlsx') else pd.read_csv(tracking_file)
    coords = pd.read_excel(coord_file) if coord_file.name.endswith('xlsx') else pd.read_csv(coord_file)

    # Clean columns
    tracking.columns = tracking.columns.str.strip().str.lower()
    coords.columns = coords.columns.str.strip().str.lower()

    # Rename columns
    tracking = tracking.rename(columns={
        "vehicle":"vehicle",
        "lat":"t_lat",
        "long":"t_lon"
    })

    coords = coords.rename(columns={
        "name":"location",
        "lat":"c_lat",
        "long":"c_lon"
    })

    results = []

    # Matching logic
    for _, t in tracking.iterrows():
        for _, c in coords.iterrows():

            if pd.isna(t['t_lat']) or pd.isna(t['t_lon']):
                continue

            dist = haversine(t['t_lat'], t['t_lon'], c['c_lat'], c['c_lon'])

            if dist <= 0.2:
                results.append([t['vehicle'], c['location']])

    # Result DataFrame
    df = pd.DataFrame(results, columns=["Vehicle","Visited Location"]).drop_duplicates()

    st.success("✅ Matching Completed")

    st.dataframe(df)

    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Result", csv, "result.csv")

else:
    st.info("👈 Please upload all 3 files from sidebar")
