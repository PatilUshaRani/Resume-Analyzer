import base64

def download_link(df, filename="User_Data.csv"):
    """Generate CSV download link"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download Report</a>'
