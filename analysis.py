import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from .models import ScanResult
from . import db

def get_open_ports_chart():
    # Fetch all scan results
    results = ScanResult.query.all()
    
    # Prepare data for analysis
    data = []
    for result in results:
        for port in result.ports:
            if port['state'] == 'open':
                data.append({
                    'host': result.host,
                    'port': port['port'],
                    'service': port['service']
                })
    
    # Create a DataFrame
    df = pd.DataFrame(data)
    
    # Count open ports
    port_counts = df['port'].value_counts().head(10)
    
    # Create a bar chart
    plt.figure(figsize=(10, 6))
    port_counts.plot(kind='bar')
    plt.title('Top 10 Open Ports')
    plt.xlabel('Port Number')
    plt.ylabel('Count')
    plt.tight_layout()
    
    # Save the plot to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    
    # Encode the image to base64
    graph_url = base64.b64encode(img.getvalue()).decode()
    
    return f"data:image/png;base64,{graph_url}"

def get_service_distribution_chart():
    # Fetch all scan results
    results = ScanResult.query.all()
    
    # Prepare data for analysis
    data = []
    for result in results:
        for port in result.ports:
            if port['state'] == 'open':
                data.append({
                    'host': result.host,
                    'port': port['port'],
                    'service': port['service']
                })
    
    # Create a DataFrame
    df = pd.DataFrame(data)
    
    # Count services
    service_counts = df['service'].value_counts().head(10)
    
    # Create a pie chart
    plt.figure(figsize=(10, 6))
    plt.pie(service_counts.values, labels=service_counts.index, autopct='%1.1f%%')
    plt.title('Top 10 Services Distribution')
    plt.axis('equal')
    plt.tight_layout()
    
    # Save the plot to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    
    # Encode the image to base64
    graph_url = base64.b64encode(img.getvalue()).decode()
    
    return f"data:image/png;base64,{graph_url}"

def get_vulnerability_analysis():
    # Fetch all scan results
    results = ScanResult.query.all()
    
    # Prepare data for analysis
    vulnerabilities = []
    for result in results:
        for port in result.ports:
            if port['state'] == 'open':
                # This is a simple example. In a real-world scenario, you would
                # check against a database of known vulnerabilities.
                if port['port'] in [21, 23, 80]:
                    vulnerabilities.append({
                        'host': result.host,
                        'port': port['port'],
                        'service': port['service'],
                        'severity': 'High' if port['port'] in [21, 23] else 'Medium'
                    })
    
    return vulnerabilities
