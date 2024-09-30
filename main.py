import streamlit as st
import pandas as pd
import io
from datetime import datetime

def process_ups_data(df):
    cols_keep = ['Account Number', 'Invoice Number', 'Invoice Date', 'Tracking Number', 'Receiver Name',
       'Billed Charge', 'Receiver Company Name', 'Invoice Section', 'Invoice Due Date']

    data = df[cols_keep]
    data = data[(data['Invoice Section'].str.contains('Outbound', na=False)) & (data['Billed Charge'] > 0)]

    return data

def process_fedex_data(df):
    # Placeholder function for FedEx invoice processing
    st.warning("FedEx invoice processing is not yet implemented.")
    return df

def process_files(uploaded_files, invoice_type):
    processed_dfs = []

    for uploaded_file in uploaded_files:
        df = pd.read_excel(uploaded_file)
        
        if invoice_type == "UPS":
            processed_df = process_ups_data(df)
        else:  # FedEx
            processed_df = process_fedex_data(df)
        
        processed_df['Source File'] = uploaded_file.name
        processed_dfs.append(processed_df)

    combined_df = pd.concat(processed_dfs, ignore_index=True)
    return combined_df

def main():
    st.title("Invoice Data Processor")

    # Sidebar for user inputs
    with st.sidebar:
        st.header("Settings")
        invoice_type = st.selectbox("Select Invoice Type", ["UPS", "FedEx"])
        uploaded_files = st.file_uploader(f"Choose {invoice_type} Excel files", type="xlsx", accept_multiple_files=True)
        custom_message = st.text_area("Enter custom email message template", "Here is the processed invoice data as requested.")

    if uploaded_files:
        st.write(f"{len(uploaded_files)} file(s) uploaded")
        
        # Process all uploaded files
        combined_df = process_files(uploaded_files, invoice_type)
        
        # Display the processed dataframe
        st.subheader("Processed Data")
        st.dataframe(combined_df)
        
        # Provide download link for the combined Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            combined_df.to_excel(writer, index=False, sheet_name='Processed Data')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"processed_{invoice_type}_data_{timestamp}.xlsx"
        
        st.download_button(
            label="Download Processed Data",
            data=output.getvalue(),
            file_name=excel_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Display email template
        st.subheader("Email Template")
        email_template = f"""
        Subject: Processed {invoice_type.upper()} Invoice Data

        {custom_message}

        Please find attached the processed {invoice_type.upper()} invoice data.

        Attachment: {excel_filename}
        """
        st.text_area("Email Content (Copy and paste this into your email client)", email_template, height=200)

if __name__ == "__main__":
    main()