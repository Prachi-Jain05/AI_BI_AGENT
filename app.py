import streamlit as st
# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1f2e 100%);
    }
    h1 {
        background: linear-gradient(90deg, #00d2ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 800 !important;
    }
    h2 {
        color: #00d2ff !important;
        border-bottom: 2px solid #7b2ff7;
        padding-bottom: 5px;
    }
    h3 {
        color: #a78bfa !important;
    }
    .stMetric {
        background: linear-gradient(135deg, #1e2a3a, #2d1b69);
        border-radius: 15px;
        padding: 15px;
        border: 1px solid #7b2ff7;
    }
    .stButton > button {
        background: linear-gradient(90deg, #00d2ff, #7b2ff7);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 30px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(123, 47, 247, 0.5);
    }
    .stDataFrame {
        border-radius: 10px;
        border: 1px solid #7b2ff7;
    }
    .stSelectbox, .stRadio {
        background-color: #1e2a3a;
        border-radius: 10px;
    }
    .stSuccess {
        background: linear-gradient(90deg, #00b09b, #96c93d);
        border-radius: 10px;
    }
    div[data-testid="stFileUploader"] {
        background: linear-gradient(135deg, #1e2a3a, #2d1b69);
        border-radius: 15px;
        border: 2px dashed #7b2ff7;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)
import pandas as pd
import matplotlib.pyplot as plt
from groq import Groq

st.set_page_config(page_title="AI BI Agent", layout="wide")
st.title("🤖 AI Business Intelligence Agent")
st.subheader("Upload your data and get instant insights!")

# Groq API setup
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "your-api-key-here")
client = Groq(api_key=GROQ_API_KEY)

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    st.success("✅ File uploaded successfully!")
    
    # Data Preview
    st.header("📋 Data Preview")
    st.dataframe(df.head())
    
    # Data Profiling
    st.header("🔍 Data Profiling")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", df.shape[0])
    col2.metric("Total Columns", df.shape[1])
    col3.metric("Missing Values", df.isnull().sum().sum())
    
    st.subheader("Column Info")
    st.dataframe(df.dtypes.reset_index().rename(columns={"index": "Column", 0: "Data Type"}))
    
    st.subheader("Basic Statistics")
    st.dataframe(df.describe())

    # Auto Charts
    st.header("📊 Auto-Generated Charts")
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
     
    # KPI Cards
    st.subheader("📈 Key Performance Indicators")
    if len(numeric_cols) >= 1:
        kpi_cols = st.columns(len(numeric_cols[:4]))
        for i, col in enumerate(numeric_cols[:4]):
            kpi_cols[i].metric(
                label=col,
                value=round(df[col].sum(), 2),
                delta=f"Avg: {round(df[col].mean(), 2)}"
            )
    

    if len(numeric_cols) == 0:
        st.warning("No numeric columns found for charts!")
    else:
        selected_col = st.selectbox("Select column to visualize", numeric_cols)
        chart_type = st.radio("Select chart type", ["Histogram", "Bar Chart", "Box Plot" , "Line Chart", "Scatter Plot", "Pie Chart"])
        
        fig, ax = plt.subplots()
        
        if chart_type == "Histogram":
            ax.hist(df[selected_col], color='skyblue', edgecolor='black')
            ax.set_title(f"Histogram of {selected_col}")
            ax.set_xlabel(selected_col)
            ax.set_ylabel("Frequency")
        elif chart_type == "Bar Chart":
            df[selected_col].value_counts().head(10).plot(kind='bar', ax=ax, color='coral')
            ax.set_title(f"Bar Chart of {selected_col}")
            ax.set_xlabel("Categories")
            ax.set_ylabel("Count")
        elif chart_type == "Box Plot":
            ax.boxplot(df[selected_col].dropna())
            ax.set_title(f"Box Plot of {selected_col}")
            ax.set_xlabel(selected_col)
            ax.set_ylabel("Values")
        elif chart_type == "Line Chart":
            ax.plot(df[selected_col].reset_index(drop=True), color='green')
            ax.set_title(f"Line Chart of {selected_col}")
            ax.set_xlabel("Index")
            ax.set_ylabel(selected_col)
        elif chart_type == "Scatter Plot":
            if len(numeric_cols) > 1:
                second_col = st.selectbox("Select second column", [c for c in numeric_cols if c != selected_col])
                ax.scatter(df[selected_col], df[second_col], color='purple', alpha=0.5)
                ax.set_title(f"Scatter Plot: {selected_col} vs {second_col}")
            else:
                st.warning("Scatter plot needs 2 numeric columns!")
        elif chart_type == "Pie Chart":
            df[selected_col].value_counts().head(6).plot(kind='pie', ax=ax, autopct='%1.1f%%')
            ax.set_title(f"Pie Chart of {selected_col}")
        
        st.pyplot(fig)
        # Chart Stats
        st.subheader(f"📊 {selected_col} — Quick Stats")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Mean", round(df[selected_col].mean(), 2))
        c2.metric("Max", round(df[selected_col].max(), 2))
        c3.metric("Min", round(df[selected_col].min(), 2))
        c4.metric("Std Dev", round(df[selected_col].std(), 2))

    # AI Q&A
    st.header("🤖 Ask AI About Your Data")
    user_question = st.text_input("Ask anything about your data!")
    
    if user_question:
        with st.spinner("AI is thinking..."):
            data_summary = df.describe().to_string()
            columns = df.columns.tolist()
            
            prompt = f"""You are a data analyst. Here is the dataset info:
Columns: {columns}
Summary Statistics:
{data_summary}

User Question: {user_question}

Answer in simple, clear language."""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            
            st.write("**AI Answer:**")
            st.write(response.choices[0].message.content)

# AI Data Cleaning
    st.header("🧹 AI Data Cleaning")
    
    if st.button("Auto Clean My Data"):
        with st.spinner("AI is cleaning your data..."):
            original_shape = df.shape
            cleaned_df = df.copy()
            
            # Remove duplicates
            cleaned_df = cleaned_df.drop_duplicates()
            duplicates_removed = original_shape[0] - cleaned_df.shape[0]
            
            # Fill missing values
            for col in cleaned_df.columns:
                if cleaned_df[col].dtype in ['float64', 'int64']:
                    cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
                else:
                    cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mode()[0])
            
            missing_filled = df.isnull().sum().sum()
            
            st.success("✅ Data Cleaned Successfully!")
            
            col1, col2 = st.columns(2)
            col1.metric("Duplicates Removed", duplicates_removed)
            col2.metric("Missing Values Filled", missing_filled)
            
            st.subheader("Cleaned Data Preview")
            st.dataframe(cleaned_df.head())
            
            # Download button
            csv = cleaned_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download Cleaned CSV",
                data=csv,
                file_name="cleaned_data.csv",
                mime="text/csv"
            )

# AI Business Report
    st.header("📊 AI Business Report & Recommendations")
    
    if st.button("Generate AI Report"):
        with st.spinner("AI is analyzing your data..."):
            data_summary = df.describe().to_string()
            columns = df.columns.tolist()
            missing = df.isnull().sum().to_string()
            
            prompt = f"""You are a senior business analyst. Analyze this dataset and provide a professional report.

Dataset Columns: {columns}
Summary Statistics:
{data_summary}

Missing Values:
{missing}

Please provide:
1. **Dataset Overview** - What kind of data is this?
2. **Key Insights** - Top 3-5 important findings
3. **Business Recommendations** - Actionable suggestions
4. **Data Quality Assessment** - Is the data reliable?

Be specific, professional, and use simple language."""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            
            st.markdown(response.choices[0].message.content)
            
            # Download Report
            report_text = response.choices[0].message.content
            st.download_button(
                label="⬇️ Download Report",
                data=report_text,
                file_name="ai_business_report.txt",
                mime="text/plain"
            )

# python -m streamlit run c:/Users/aditi/AI_BI_AGENT/app.py