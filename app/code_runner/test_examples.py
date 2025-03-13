"""
Test Examples Module

Provides test case examples
"""
import time
import random


def get_hello_world_example():
    """
    Get Hello World example code
    
    Returns:
        Hello World example code
    """
    return '''
import time
import random

# Print welcome message
print("Hello, World!")
print("This is a test script that will generate a lot of logs to test real-time logging functionality")

# Simulate a long-running task
total_steps = 50
for step in range(1, total_steps + 1):
    # Generate random delay
    delay = random.uniform(0.1, 0.5)
    
    # Print progress
    print(f"[{step}/{total_steps}] Processing step {step}...")
    
    # Simulate some random logs
    log_count = random.randint(1, 3)
    for i in range(log_count):
        log_type = random.choice(["INFO", "DEBUG", "WARNING"])
        if log_type == "INFO":
            print(f"INFO: Step {step} - Executing subtask {i+1}")
        elif log_type == "DEBUG":
            print(f"DEBUG: Step {step} - Memory usage: {random.randint(100, 500)}MB, CPU usage: {random.randint(10, 90)}%")
        else:
            print(f"WARNING: Step {step} - Performance may be poor, response time: {random.randint(100, 1000)}ms")
    
    # Randomly generate some calculation results
    if step % 5 == 0:
        result = random.random() * 100
        print(f"Calculation result: {result:.2f}")
        
        # Simulate data processing
        print("Processing data...")
        for j in range(3):
            print(f"  - Processing data block {j+1}/3: {'Completed' if random.random() > 0.2 else 'Partially completed'}")
    
    # Delay for a while
    time.sleep(delay)
    
    # Print completion message
    print(f"Step {step} completed, time taken: {delay:.2f} seconds")

# Print summary
print("All steps completed!")
print("Generating final report...")
time.sleep(1)

# Generate random statistics
stats = {
    "Processed items": random.randint(100, 500),
    "Success rate": random.uniform(90, 99.9),
    "Average processing time": random.uniform(0.1, 0.5),
    "Total time": sum([random.uniform(0.1, 0.5) for _ in range(total_steps)])
}

# Print statistics
print("\\nStatistics:")
for key, value in stats.items():
    if isinstance(value, float):
        print(f"  - {key}: {value:.2f}")
    else:
        print(f"  - {key}: {value}")

print("\\nTest script execution completed!")
'''


def get_data_processing_example():
    """
    Get data processing example code
    
    Returns:
        Data processing example code
    """
    return '''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import random

# Create sample data
print("Generating sample data...")
np.random.seed(42)
data_size = 10000
data = {
    'id': range(1, data_size + 1),
    'value': np.random.normal(100, 15, data_size),
    'category': np.random.choice(['A', 'B', 'C', 'D'], data_size),
    'timestamp': pd.date_range(start='2023-01-01', periods=data_size, freq='H')
}

# Create DataFrame
print("Creating DataFrame...")
df = pd.DataFrame(data)
print(f"Dataset size: {df.shape}")
print("First 5 rows of dataset:")
print(df.head())

# Data processing
print("\\nStarting data processing...")
steps = [
    "Data cleaning",
    "Feature engineering",
    "Data transformation",
    "Statistical analysis",
    "Data visualization"
]

for i, step in enumerate(steps, 1):
    print(f"\\n[{i}/{len(steps)}] Executing: {step}")
    
    # Simulate processing time
    process_time = random.uniform(1, 2)
    
    if step == "Data cleaning":
        print("Checking for missing values...")
        missing = df.isnull().sum()
        print(f"Missing values statistics:\\n{missing}")
        
        print("Checking for outliers...")
        q1 = df['value'].quantile(0.25)
        q3 = df['value'].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = df[(df['value'] < lower_bound) | (df['value'] > upper_bound)]
        print(f"Detected {len(outliers)} outliers")
        
        # Remove outliers
        df = df[(df['value'] >= lower_bound) & (df['value'] <= upper_bound)]
        print(f"Dataset size after removing outliers: {df.shape}")
    
    elif step == "Feature engineering":
        print("Creating new features...")
        df['log_value'] = np.log1p(df['value'])
        df['value_squared'] = df['value'] ** 2
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['hour_of_day'] = df['timestamp'].dt.hour
        print("New features created, first 5 rows of new dataset:")
        print(df.head())
    
    elif step == "Data transformation":
        print("One-hot encoding categorical features...")
        df_encoded = pd.get_dummies(df, columns=['category'])
        print(f"Dataset size after encoding: {df_encoded.shape}")
        print("First 5 rows after encoding:")
        print(df_encoded.head())
        
        print("\\nStandardizing numerical features...")
        for col in ['value', 'log_value', 'value_squared']:
            mean = df[col].mean()
            std = df[col].std()
            df[f'{col}_scaled'] = (df[col] - mean) / std
        print("Standardization completed")
    
    elif step == "Statistical analysis":
        print("Calculating basic statistics...")
        stats = df['value'].describe()
        print(f"Basic statistics:\\n{stats}")
        
        print("\\nGrouping statistics by category...")
        group_stats = df.groupby('category')['value'].agg(['count', 'mean', 'std', 'min', 'max'])
        print(f"Group statistics:\\n{group_stats}")
        
        print("\\nCalculating correlations...")
        numeric_cols = ['value', 'log_value', 'value_squared', 'day_of_week', 'hour_of_day']
        corr = df[numeric_cols].corr()
        print(f"Correlation matrix:\\n{corr}")
    
    elif step == "Data visualization":
        print("Generating data visualizations...")
        print("(Note: In API environment, graphics won't be displayed, just simulating the process)")
        
        print("Generating histogram...")
        time.sleep(0.5)
        
        print("Generating box plot...")
        time.sleep(0.5)
        
        print("Generating scatter plot...")
        time.sleep(0.5)
        
        print("Generating time series plot...")
        time.sleep(0.5)
        
        print("Visualization completed")
    
    # Simulate processing time
    time.sleep(process_time)
    print(f"{step} completed, time taken: {process_time:.2f} seconds")

print("\\nAll data processing steps completed!")
print("Generating final report...")
time.sleep(1)

# Generate final statistics
print("\\nFinal statistics:")
print(f"- Original dataset size: {data_size}")
print(f"- Processed dataset size: {df.shape[0]}")
print(f"- Number of features: {df.shape[1]}")
print(f"- Number of categories: {df['category'].nunique()}")
print(f"- Mean value: {df['value'].mean():.2f}")
print(f"- Standard deviation: {df['value'].std():.2f}")
print(f"- Minimum value: {df['value'].min():.2f}")
print(f"- Maximum value: {df['value'].max():.2f}")

print("\\nData processing example execution completed!")
'''


def get_examples():
    """
    Get all example codes
    
    Returns:
        Dictionary of example codes
    """
    return {
        'hello_world': {
            'name': 'Hello World Example',
            'description': 'A simple Hello World example that generates a lot of logs to test real-time logging functionality',
            'code': get_hello_world_example()
        },
        'data_processing': {
            'name': 'Data Processing Example',
            'description': 'A data processing example using pandas and numpy',
            'code': get_data_processing_example()
        }
    } 