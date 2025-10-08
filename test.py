import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Filter & Pivot Tool", layout="wide")

st.title("Filter & Pivot Tool (CSV Kapal)")

st.markdown("""""
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
""")

uploaded_file = st.file_uploader("Upload file CSV", type=["csv"])

if uploaded_file is not None:
    try:
        # Baca file
        df = pd.read_csv(uploaded_file, skiprows=3)

        # preview data awal
        st.subheader("🔍 Data Awal (Preview)")
        st.dataframe(df.head(10))

        # Proses filter data
        df_filtered = df[
            df["BAPOL1"].astype(str).str.startswith("ID") &
            df["BAPOD"].astype(str).str.startswith("ID")
        ]
        df_filtered = df_filtered[~df_filtered["BLSTATUS"].isin(["Manifested", "Listed"])]

        # Rename kolom
        rename_cols = {
            "textbox53": "BOOKING NO",
            "BOOOKSTATUS1": "BOOKING STATUS",
            "BAVESS": "VES",
            "BAVOY": "VOY",
            "BAPOL1": "POL",
            "BAPOD": "POD",
            "BASLDT": "ETD",
            "TYBLNO": "BL NO",
            "BLSTATUS": "BL STATUS"
        }
        df_filtered = df_filtered.rename(columns=rename_cols)
        df_filtered = df_filtered[[c for c in rename_cols.values() if c in df_filtered.columns]]

        st.subheader("✅ Data Setelah Difilter")
        st.dataframe(df_filtered.head(20))

        # Pivot table
        pivot_df = df_filtered.pivot_table(
            index=["POL", "POD", "VES", "VOY"],
            values=["BOOKING NO", "BL NO", "ETD"],
            aggfunc={"BOOKING NO": "count", "BL NO": "count", "ETD": "count"},
            fill_value=0
        ).reset_index()

        pivot_df = pivot_df.rename(columns={
            "BOOKING NO": "TOTAL BOOKING",
            "BL NO": "TOTAL BL PAGI",
            "ETD": "Count of ETD"
        })

        st.subheader("📈 Pivot Table")
        st.dataframe(pivot_df)

        # Tombol download hasil
        def convert_to_excel(df_filtered, pivot_df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_filtered.to_excel(writer, index=False, sheet_name="Filtered Data")
                pivot_df.to_excel(writer, index=False, sheet_name="Pivot Table")
            return output.getvalue()

        excel_data = convert_to_excel(df_filtered, pivot_df)

        st.download_button(
            label="Download Hasil",
            data=excel_data,
            file_name="hasil_filter_pivot.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Terjadi error saat memproses file: {e}")
else:
    st.info("Silakan upload file CSV terlebih dahulu.")
