import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

plt.style.use('default')  
sns.set_palette("husl")

def load_and_prepare_data():
    df = pd.read_csv('deepu.csv')
    
    df['dataDate'] = pd.to_datetime(df['dataDate'], format='%B -%Y')
    
    return df

def generate_basic_stats(df):
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
    
    basic_stats = df[numerical_cols].describe()
    
    basic_stats.to_csv('basic_statistics.csv')
    
    return basic_stats

def analyze_missing_values(df):
    missing_values = df.isnull().sum()
    missing_percentages = (missing_values / len(df)) * 100
    
    missing_report = pd.DataFrame({
        'Missing Values': missing_values,
        'Percentage Missing': missing_percentages
    })
    
    missing_report.to_csv('missing_values_report.csv')
    
    return missing_report

def create_categorical_distributions(df):

    plt.figure(figsize=(15, 6))
    district_counts = df['districtName'].value_counts()
    district_counts.plot(kind='bar')
    plt.title('Distribution of Records by District')
    plt.xlabel('District')
    plt.ylabel('Number of Records')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('district_distribution.png')
    plt.close()
    
    plt.figure(figsize=(15, 6))
    mandal_counts = df['mandalName'].value_counts().head(20)
    mandal_counts.plot(kind='bar')
    plt.title('Distribution of Records by Mandal (Top 20)')
    plt.xlabel('Mandal')
    plt.ylabel('Number of Records')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('mandal_distribution.png')
    plt.close()
    
    return district_counts, mandal_counts

def analyze_healthcare_metrics(df):

    plt.figure(figsize=(12, 6))
    metrics = ['pwRegCnt', 'delCnt']
    df[metrics].sum().plot(kind='bar')
    plt.title('Total Registrations vs Deliveries')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig('reg_vs_del.png')
    plt.close()
    
    plt.figure(figsize=(12, 6))
    anc_cols = ['anc1Cnt', 'anc2Cnt', 'anc3Cnt', 'anc4Cnt']
    df[anc_cols].sum().plot(kind='bar')
    plt.title('ANC Visits Distribution')
    plt.ylabel('Number of Visits')
    plt.tight_layout()
    plt.savefig('anc_visits.png')
    plt.close()
    
    return df[metrics].sum(), df[anc_cols].sum()

def generate_summary_report(df, basic_stats, missing_report, district_counts, healthcare_metrics):
    """Generate a comprehensive summary report"""
    
    report = f"""
    Mother and Child Health Kit Data Analysis Report
    =============================================
    Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    Dataset Overview
    ---------------
    Total Records: {len(df)}
    Time Period: {df['dataDate'].min().strftime('%B %Y')} to {df['dataDate'].max().strftime('%B %Y')}
    Number of Districts: {df['districtName'].nunique()}
    Number of Mandals: {df['mandalName'].nunique()}
    
    Key Statistics
    -------------
    Total Registrations: {int(df['pwRegCnt'].sum()):,}
    Total Deliveries: {int(df['delCnt'].sum()):,}
    High Risk Cases: {int(df['highRiskCnt'].sum()):,}
    Kits Distributed: {int(df['kitsCnt'].sum()):,}
    
    ANC Visit Statistics
    ------------------
    1st ANC Visits: {int(df['anc1Cnt'].sum()):,}
    2nd ANC Visits: {int(df['anc2Cnt'].sum()):,}
    3rd ANC Visits: {int(df['anc3Cnt'].sum()):,}
    4th ANC Visits: {int(df['anc4Cnt'].sum()):,}
    
    Top 5 Districts by Registration
    ---------------------------
    {district_counts.head().to_string()}
    
    Data Quality
    -----------
    Columns with Missing Values:
    {missing_report[missing_report['Missing Values'] > 0].to_string()}
    
    Key Insights
    -----------
    1. Registration to Delivery Ratio: {(df['delCnt'].sum() / df['pwRegCnt'].sum() * 100):.2f}%
    2. Average High Risk Cases per District: {df.groupby('districtName')['highRiskCnt'].mean().mean():.2f}
    3. ANC Visit Completion Rate: {(df['anc4Cnt'].sum() / df['anc1Cnt'].sum() * 100):.2f}%
    
    Generated Files
    --------------
    1. basic_statistics.csv - Detailed statistical measures
    2. missing_values_report.csv - Missing value analysis
    3. district_distribution.png - District-wise distribution plot
    4. mandal_distribution.png - Mandal-wise distribution plot
    5. reg_vs_del.png - Registration vs Delivery comparison
    6. anc_visits.png - ANC visits analysis
    """
    with open('data_analysis_report.txt', 'w') as f:
        f.write(report)
    
    return report

def main():
    print("Loading data...")
    df = load_and_prepare_data()
    
    print("Calculating basic statistics...")
    basic_stats = generate_basic_stats(df)
    
    print("Analyzing missing values...")
    missing_report = analyze_missing_values(df)
    
    print("Creating distribution plots...")
    district_counts, mandal_counts = create_categorical_distributions(df)
    
    print("Analyzing healthcare metrics...")
    reg_del_metrics, anc_metrics = analyze_healthcare_metrics(df)
    
    print("Generating summary report...")
    report = generate_summary_report(df, basic_stats, missing_report, district_counts, reg_del_metrics)
    
    print("\nAnalysis complete! Check the generated files for detailed insights.")
    print("\nSummary Report:")
    print(report)

if __name__ == "__main__":
    main()
