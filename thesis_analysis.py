"""
Thesis Analysis Script
Generates graphs and tables for Strategic Intelligence Analysis Thesis
Author: Analysis Assistant
Date: 2025-11-15
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class ThesisAnalyzer:
    def __init__(self):
        """Initialize the analyzer and load data"""
        self.system_logs = None
        self.agent_performance = None
        self.analysis_sessions = None
        self.agent_results = None
        self.output_dir = Path("thesis_outputs")
        self.output_dir.mkdir(exist_ok=True)
        
    def load_data(self):
        """Load all Excel files"""
        print("=" * 80)
        print("LOADING DATA FROM EXCEL FILES")
        print("=" * 80)
        
        try:
            self.system_logs = pd.read_excel("system_logs.xlsx")
            print(f"✓ Loaded system_logs.xlsx: {len(self.system_logs)} rows")
        except Exception as e:
            print(f"✗ Error loading system_logs.xlsx: {e}")
            
        try:
            self.agent_performance = pd.read_excel("agent_performance.xlsx")
            print(f"✓ Loaded agent_performance.xlsx: {len(self.agent_performance)} rows")
        except Exception as e:
            print(f"✗ Error loading agent_performance.xlsx: {e}")
            
        try:
            self.analysis_sessions = pd.read_excel("analysis_sessions.xlsx")
            print(f"✓ Loaded analysis_sessions.xlsx: {len(self.analysis_sessions)} rows")
        except Exception as e:
            print(f"✗ Error loading analysis_sessions.xlsx: {e}")
            
        try:
            self.agent_results = pd.read_excel("agent_results_cleaned_v2.xlsx")
            print(f"✓ Loaded agent_results_cleaned_v2.xlsx: {len(self.agent_results)} rows")
        except Exception as e:
            print(f"✗ Error loading agent_results_cleaned_v2.xlsx: {e}")
        
        print()
        
    def inspect_data(self):
        """Inspect the structure and content of loaded data"""
        print("=" * 80)
        print("DATA INSPECTION")
        print("=" * 80)
        
        datasets = {
            "system_logs": self.system_logs,
            "agent_performance": self.agent_performance,
            "analysis_sessions": self.analysis_sessions,
            "agent_results": self.agent_results
        }
        
        for name, df in datasets.items():
            if df is not None:
                print(f"\n{name.upper()}")
                print("-" * 80)
                print(f"Shape: {df.shape}")
                print(f"Columns: {list(df.columns)}")
                print(f"\nFirst few rows:")
                print(df.head(3))
                print(f"\nData types:")
                print(df.dtypes)
                print(f"\nMissing values:")
                print(df.isnull().sum())
                print()
        
    def check_missing_data(self):
        """Check what data is missing for each analysis"""
        print("=" * 80)
        print("MISSING DATA ANALYSIS")
        print("=" * 80)
        
        missing_report = []
        
        # Check analysis_sessions requirements
        if self.analysis_sessions is not None:
            print("\n1. ANALYSIS SESSIONS DATA")
            print("-" * 80)
            required_cols = ['architecture', 'status', 'total_processing_time', 'total_token_usage']
            for col in required_cols:
                if col not in self.analysis_sessions.columns:
                    missing_report.append(f"analysis_sessions.xlsx is missing column: {col}")
                    print(f"  ✗ Missing column: {col}")
                else:
                    null_count = self.analysis_sessions[col].isnull().sum()
                    if null_count > 0:
                        missing_report.append(f"analysis_sessions.{col} has {null_count} null values")
                        print(f"  ⚠ Column '{col}' has {null_count} null values")
                    else:
                        print(f"  ✓ Column '{col}' is complete")
            
            # Check for architecture types (case-insensitive)
            if 'architecture' in self.analysis_sessions.columns:
                archs = self.analysis_sessions['architecture'].unique()
                print(f"\n  Available architectures: {archs}")
                # Normalize to lowercase for comparison
                archs_lower = [str(a).lower() for a in archs]
                expected_archs = ['sequential', 'parallel', 'hierarchical']
                for arch in expected_archs:
                    if arch not in archs_lower:
                        missing_report.append(f"Missing architecture type: {arch}")
                        print(f"  ✗ Missing architecture: {arch.capitalize()}")
        else:
            missing_report.append("analysis_sessions.xlsx not loaded")
            
        # Check agent_results requirements
        if self.agent_results is not None:
            print("\n2. AGENT RESULTS DATA")
            print("-" * 80)
            required_cols = ['session_id', 'agent_name', 'status', 'processing_time', 'token_usage']
            for col in required_cols:
                if col not in self.agent_results.columns:
                    missing_report.append(f"agent_results.xlsx is missing column: {col}")
                    print(f"  ✗ Missing column: {col}")
                else:
                    null_count = self.agent_results[col].isnull().sum()
                    if null_count > 0:
                        missing_report.append(f"agent_results.{col} has {null_count} null values")
                        print(f"  ⚠ Column '{col}' has {null_count} null values")
                    else:
                        print(f"  ✓ Column '{col}' is complete")
        else:
            missing_report.append("agent_results_cleaned_v2.xlsx not loaded")
            
        # Check agent_performance requirements
        if self.agent_performance is not None:
            print("\n3. AGENT PERFORMANCE DATA")
            print("-" * 80)
            required_cols = ['agent_name', 'total_executions', 'successful_executions', 
                           'failed_executions', 'timeout_executions', 'average_processing_time']
            for col in required_cols:
                if col not in self.agent_performance.columns:
                    missing_report.append(f"agent_performance.xlsx is missing column: {col}")
                    print(f"  ✗ Missing column: {col}")
                else:
                    print(f"  ✓ Column '{col}' exists")
        else:
            missing_report.append("agent_performance.xlsx not loaded")
        
        # Summary
        print("\n" + "=" * 80)
        print("MISSING DATA SUMMARY")
        print("=" * 80)
        if missing_report:
            print("\nISSUES FOUND:")
            for i, issue in enumerate(missing_report, 1):
                print(f"{i}. {issue}")
        else:
            print("\n✓ All required data appears to be present!")
        
        return missing_report
    
    def figure_1_performance_distribution_boxplot(self):
        """
        Figure 1: Performance Distribution by Architecture (Box Plot)
        Shows distribution of execution time and token usage across architectures
        """
        print("\n" + "=" * 80)
        print("FIGURE 1: Performance Distribution by Architecture (Box Plots)")
        print("=" * 80)
        
        if self.analysis_sessions is None or len(self.analysis_sessions) == 0:
            print("✗ Cannot generate: analysis_sessions data not available")
            return
        
        # Check required columns
        required = ['architecture', 'total_processing_time', 'total_token_usage', 'status']
        missing = [col for col in required if col not in self.analysis_sessions.columns]
        if missing:
            print(f"✗ Cannot generate: Missing columns {missing}")
            return
        
        # Filter only completed sessions
        df = self.analysis_sessions[self.analysis_sessions['status'] == 'completed'].copy()
        
        if len(df) == 0:
            print("✗ Cannot generate: No completed sessions found")
            return
        
        print(f"✓ Analyzing {len(df)} completed sessions")
        print(f"  Architectures found: {df['architecture'].unique()}")
        
        # Create figure with two subplots
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Processing Time Distribution
        sns.boxplot(data=df, x='architecture', y='total_processing_time', ax=axes[0])
        axes[0].set_title('Total Processing Time by Architecture', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Architecture Type', fontsize=12)
        axes[0].set_ylabel('Total Processing Time (seconds)', fontsize=12)
        axes[0].grid(True, alpha=0.3)
        
        # Add mean markers
        means = df.groupby('architecture')['total_processing_time'].mean()
        positions = range(len(means))
        axes[0].scatter(positions, means, color='red', s=100, zorder=3, label='Mean', marker='D')
        axes[0].legend()
        
        # Plot 2: Token Usage Distribution
        sns.boxplot(data=df, x='architecture', y='total_token_usage', ax=axes[1])
        axes[1].set_title('Total Token Usage by Architecture', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Architecture Type', fontsize=12)
        axes[1].set_ylabel('Total Token Usage', fontsize=12)
        axes[1].grid(True, alpha=0.3)
        
        # Add mean markers
        means = df.groupby('architecture')['total_token_usage'].mean()
        positions = range(len(means))
        axes[1].scatter(positions, means, color='red', s=100, zorder=3, label='Mean', marker='D')
        axes[1].legend()
        
        plt.tight_layout()
        output_path = self.output_dir / "figure_1_performance_distribution_boxplot.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
        
        # Print statistics
        print("\nStatistics:")
        for arch in df['architecture'].unique():
            arch_data = df[df['architecture'] == arch]
            print(f"\n{arch}:")
            print(f"  Processing Time - Mean: {arch_data['total_processing_time'].mean():.2f}s, "
                  f"Median: {arch_data['total_processing_time'].median():.2f}s, "
                  f"Std: {arch_data['total_processing_time'].std():.2f}s")
            print(f"  Token Usage - Mean: {arch_data['total_token_usage'].mean():.0f}, "
                  f"Median: {arch_data['total_token_usage'].median():.0f}, "
                  f"Std: {arch_data['total_token_usage'].std():.0f}")
    
    def figure_2_cost_vs_time_scatter(self):
        """
        Figure 2: Cost vs. Time Efficiency Plot (Scatter Plot)
        Shows the trade-off between speed and cost
        """
        print("\n" + "=" * 80)
        print("FIGURE 2: Cost vs. Time Efficiency (Scatter Plot)")
        print("=" * 80)
        
        if self.analysis_sessions is None or len(self.analysis_sessions) == 0:
            print("✗ Cannot generate: analysis_sessions data not available")
            return
        
        required = ['architecture', 'total_processing_time', 'total_token_usage', 'status']
        missing = [col for col in required if col not in self.analysis_sessions.columns]
        if missing:
            print(f"✗ Cannot generate: Missing columns {missing}")
            return
        
        df = self.analysis_sessions[self.analysis_sessions['status'] == 'completed'].copy()
        
        if len(df) == 0:
            print("✗ Cannot generate: No completed sessions found")
            return
        
        print(f"✓ Analyzing {len(df)} completed sessions")
        
        # Create scatter plot
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Get unique architectures and create color map
        architectures = df['architecture'].unique()
        colors = sns.color_palette("husl", len(architectures))
        color_map = dict(zip(architectures, colors))
        
        # Plot each architecture
        for arch in architectures:
            arch_data = df[df['architecture'] == arch]
            ax.scatter(arch_data['total_processing_time'], 
                      arch_data['total_token_usage'],
                      label=arch, 
                      s=100, 
                      alpha=0.6,
                      color=color_map[arch],
                      edgecolors='black',
                      linewidth=0.5)
        
        ax.set_xlabel('Total Processing Time (seconds)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Token Usage', fontsize=12, fontweight='bold')
        ax.set_title('Cost vs. Time Efficiency Trade-off by Architecture', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(title='Architecture', fontsize=10, title_fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # Add annotations for ideal regions
        ax.text(0.02, 0.98, '← Faster, Cheaper (Ideal)', 
               transform=ax.transAxes, fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
        ax.text(0.98, 0.02, 'Slower, Expensive →', 
               transform=ax.transAxes, fontsize=10, horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.3))
        
        plt.tight_layout()
        output_path = self.output_dir / "figure_2_cost_vs_time_scatter.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
        
        # Calculate efficiency metrics
        print("\nEfficiency Analysis (lower is better):")
        for arch in architectures:
            arch_data = df[df['architecture'] == arch]
            avg_time = arch_data['total_processing_time'].mean()
            avg_tokens = arch_data['total_token_usage'].mean()
            efficiency = avg_time * avg_tokens  # Combined metric
            print(f"{arch}: Avg Time={avg_time:.2f}s, Avg Tokens={avg_tokens:.0f}, "
                  f"Efficiency Score={efficiency:.0f}")
    
    def figure_3_granular_cost_breakdown(self):
        """
        Figure 3: Granular Cost Breakdown (Stacked Bar Chart)
        Shows which agents are responsible for costs in each architecture
        """
        print("\n" + "=" * 80)
        print("FIGURE 3: Granular Cost Breakdown by Agent (Stacked Bar Chart)")
        print("=" * 80)
        
        if self.agent_results is None or self.analysis_sessions is None:
            print("✗ Cannot generate: Required data not available")
            return
        
        # Merge agent results with session architecture
        if 'session_id' not in self.agent_results.columns or 'architecture' not in self.analysis_sessions.columns:
            print("✗ Cannot generate: Missing required columns")
            return
        
        # Merge data
        df = self.agent_results.merge(
            self.analysis_sessions[['id', 'architecture', 'status']], 
            left_on='session_id', 
            right_on='id',
            how='left'
        )
        
        # Filter completed sessions and successful agent runs
        df = df[(df['status_y'] == 'completed') & (df['status_x'] == 'completed')]
        
        if len(df) == 0:
            print("✗ Cannot generate: No completed data found")
            return
        
        print(f"✓ Analyzing {len(df)} agent executions")
        
        # Calculate token usage by architecture and agent
        pivot_data = df.groupby(['architecture', 'agent_name'])['token_usage'].sum().unstack(fill_value=0)
        
        # Create stacked bar chart
        fig, ax = plt.subplots(figsize=(12, 8))
        pivot_data.plot(kind='bar', stacked=True, ax=ax, width=0.7)
        
        ax.set_title('Token Usage Breakdown by Architecture and Agent', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Architecture Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Token Usage', fontsize=12, fontweight='bold')
        ax.legend(title='Agent Name', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=0)
        
        plt.tight_layout()
        output_path = self.output_dir / "figure_3_granular_cost_breakdown.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
        
        # Print breakdown
        print("\nToken Usage by Architecture:")
        print(pivot_data.sum(axis=1))
    
    def figure_4_system_reliability(self):
        """
        Figure 4: System Reliability by Architecture (Bar Chart)
        Shows success rate of each architecture
        """
        print("\n" + "=" * 80)
        print("FIGURE 4: System Reliability by Architecture (Bar Chart)")
        print("=" * 80)
        
        if self.analysis_sessions is None or len(self.analysis_sessions) == 0:
            print("✗ Cannot generate: analysis_sessions data not available")
            return
        
        required = ['architecture', 'status']
        missing = [col for col in required if col not in self.analysis_sessions.columns]
        if missing:
            print(f"✗ Cannot generate: Missing columns {missing}")
            return
        
        print(f"✓ Analyzing {len(self.analysis_sessions)} sessions")
        
        # Calculate success rates
        success_data = []
        for arch in self.analysis_sessions['architecture'].unique():
            arch_data = self.analysis_sessions[self.analysis_sessions['architecture'] == arch]
            total = len(arch_data)
            completed = len(arch_data[arch_data['status'] == 'completed'])
            failed = len(arch_data[arch_data['status'] == 'failed'])
            timeout = len(arch_data[arch_data['status'] == 'timeout'])
            success_rate = (completed / total * 100) if total > 0 else 0
            
            success_data.append({
                'Architecture': arch,
                'Success Rate (%)': success_rate,
                'Total': total,
                'Completed': completed,
                'Failed': failed,
                'Timeout': timeout
            })
        
        df_success = pd.DataFrame(success_data)
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(df_success['Architecture'], df_success['Success Rate (%)'], 
                     color=['#2ecc71', '#3498db', '#e74c3c'])
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontweight='bold')
        
        ax.set_title('System Reliability by Architecture', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Architecture Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
        ax.set_ylim(0, 110)
        ax.grid(True, alpha=0.3, axis='y')
        ax.axhline(y=100, color='green', linestyle='--', alpha=0.3, label='100% Reliability')
        
        plt.tight_layout()
        output_path = self.output_dir / "figure_4_system_reliability.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
        
        # Print statistics
        print("\nReliability Statistics:")
        print(df_success.to_string(index=False))
    
    def table_1_detailed_failure_analysis(self):
        """
        Table 1: Detailed Failure Analysis
        Breaks down failures by type and identifies problematic agents
        """
        print("\n" + "=" * 80)
        print("TABLE 1: Detailed Failure Analysis")
        print("=" * 80)
        
        if self.analysis_sessions is None or self.agent_results is None:
            print("✗ Cannot generate: Required data not available")
            return
        
        # Merge data
        df = self.agent_results.merge(
            self.analysis_sessions[['id', 'architecture']], 
            left_on='session_id', 
            right_on='id',
            how='left'
        )
        
        # Create failure analysis table
        failure_data = []
        for arch in self.analysis_sessions['architecture'].unique():
            # Session-level statistics
            arch_sessions = self.analysis_sessions[self.analysis_sessions['architecture'] == arch]
            total_runs = len(arch_sessions)
            successful = len(arch_sessions[arch_sessions['status'] == 'completed'])
            failed = len(arch_sessions[arch_sessions['status'] == 'failed'])
            timeout = len(arch_sessions[arch_sessions['status'] == 'timeout'])
            
            # Agent-level statistics
            arch_agents = df[df['architecture'] == arch]
            failed_agents = arch_agents[arch_agents['status'].isin(['failed', 'timeout'])]
            
            if len(failed_agents) > 0:
                most_common_failing = failed_agents['agent_name'].mode()[0]
                fail_count = len(failed_agents[failed_agents['agent_name'] == most_common_failing])
            else:
                most_common_failing = "None"
                fail_count = 0
            
            failure_data.append({
                'Architecture': arch,
                'Total Runs': total_runs,
                'Successful': successful,
                'Failed (Logic Error)': failed,
                'Failed (Timeout)': timeout,
                'Most Common Failing Agent': most_common_failing,
                'Failure Count': fail_count
            })
        
        df_failure = pd.DataFrame(failure_data)
        
        # Save as CSV
        output_path = self.output_dir / "table_1_detailed_failure_analysis.csv"
        df_failure.to_csv(output_path, index=False)
        print(f"✓ Saved: {output_path}")
        
        # Print table
        print("\n" + df_failure.to_string(index=False))
        
        return df_failure
    
    def table_2_performance_summary_statistics(self):
        """
        Table 2: Performance Summary Statistics
        Comprehensive statistics for each architecture
        """
        print("\n" + "=" * 80)
        print("TABLE 2: Performance Summary Statistics")
        print("=" * 80)
        
        if self.analysis_sessions is None:
            print("✗ Cannot generate: analysis_sessions data not available")
            return
        
        df = self.analysis_sessions[self.analysis_sessions['status'] == 'completed'].copy()
        
        if len(df) == 0:
            print("✗ Cannot generate: No completed sessions found")
            return
        
        # Calculate statistics
        stats_data = []
        for arch in df['architecture'].unique():
            arch_data = df[df['architecture'] == arch]
            
            stats_data.append({
                'Architecture': arch,
                'N (Sessions)': len(arch_data),
                'Avg Time (s)': arch_data['total_processing_time'].mean(),
                'Median Time (s)': arch_data['total_processing_time'].median(),
                'Std Time (s)': arch_data['total_processing_time'].std(),
                'Min Time (s)': arch_data['total_processing_time'].min(),
                'Max Time (s)': arch_data['total_processing_time'].max(),
                'Avg Tokens': arch_data['total_token_usage'].mean(),
                'Median Tokens': arch_data['total_token_usage'].median(),
                'Std Tokens': arch_data['total_token_usage'].std(),
                'Min Tokens': arch_data['total_token_usage'].min(),
                'Max Tokens': arch_data['total_token_usage'].max()
            })
        
        df_stats = pd.DataFrame(stats_data)
        
        # Format numbers
        for col in df_stats.columns:
            if 'Time' in col:
                df_stats[col] = df_stats[col].round(2)
            elif 'Tokens' in col or 'N' in col:
                df_stats[col] = df_stats[col].round(0).astype(int)
        
        # Save as CSV
        output_path = self.output_dir / "table_2_performance_summary_statistics.csv"
        df_stats.to_csv(output_path, index=False)
        print(f"✓ Saved: {output_path}")
        
        # Print table
        print("\n" + df_stats.to_string(index=False))
        
        return df_stats
    
    def figure_5_agent_performance_comparison(self):
        """
        Figure 5: Agent Performance Comparison Across Architectures (Grouped Bar Chart)
        Shows how each individual agent performs across different architectures
        """
        print("\n" + "=" * 80)
        print("FIGURE 5: Agent Performance Comparison Across Architectures")
        print("=" * 80)
        
        if self.agent_results is None or self.analysis_sessions is None:
            print("✗ Cannot generate: Required data not available")
            return
        
        # Merge data
        df = self.agent_results.merge(
            self.analysis_sessions[['id', 'architecture', 'status']], 
            left_on='session_id', 
            right_on='id',
            how='left'
        )
        
        # Filter completed
        df = df[(df['status_y'] == 'completed') & (df['status_x'] == 'completed')]
        
        if len(df) == 0:
            print("✗ Cannot generate: No completed data found")
            return
        
        print(f"✓ Analyzing {len(df)} agent executions")
        
        # Calculate average processing time by agent and architecture
        pivot_data = df.groupby(['architecture', 'agent_name'])['processing_time'].mean().unstack(fill_value=0)
        
        # Create grouped bar chart
        fig, ax = plt.subplots(figsize=(14, 8))
        pivot_data.T.plot(kind='bar', ax=ax, width=0.8)
        
        ax.set_title('Average Processing Time by Agent and Architecture', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Agent Name', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Processing Time (seconds)', fontsize=12, fontweight='bold')
        ax.legend(title='Architecture', fontsize=10, title_fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        output_path = self.output_dir / "figure_5_agent_performance_comparison.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
    
    def figure_6_token_efficiency(self):
        """
        Figure 6: Token Efficiency by Architecture (Bar Chart)
        Shows tokens per second for each architecture
        """
        print("\n" + "=" * 80)
        print("FIGURE 6: Token Efficiency by Architecture")
        print("=" * 80)
        
        if self.analysis_sessions is None:
            print("✗ Cannot generate: analysis_sessions data not available")
            return
        
        df = self.analysis_sessions[self.analysis_sessions['status'] == 'completed'].copy()
        
        if len(df) == 0:
            print("✗ Cannot generate: No completed sessions found")
            return
        
        # Calculate efficiency (tokens per second)
        df['token_efficiency'] = df['total_token_usage'] / df['total_processing_time']
        
        # Calculate average by architecture
        efficiency_data = df.groupby('architecture')['token_efficiency'].agg(['mean', 'std']).reset_index()
        
        print(f"✓ Analyzing {len(df)} sessions")
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(efficiency_data['architecture'], efficiency_data['mean'], 
                     yerr=efficiency_data['std'], capsize=10,
                     color=['#3498db', '#2ecc71', '#e74c3c'], alpha=0.8)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontweight='bold')
        
        ax.set_title('Token Efficiency by Architecture\n(Lower is Better - Less Computation Per Token)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Architecture Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Tokens per Second', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        output_path = self.output_dir / "figure_6_token_efficiency.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
        
        print("\nEfficiency Statistics (tokens/second):")
        print(efficiency_data.to_string(index=False))
    
    def figure_7_agent_contribution_pie(self):
        """
        Figure 7: Agent Contribution to Total Cost (Pie Charts)
        Three pie charts showing token distribution by agent for each architecture
        """
        print("\n" + "=" * 80)
        print("FIGURE 7: Agent Contribution to Total Cost (Pie Charts)")
        print("=" * 80)
        
        if self.agent_results is None or self.analysis_sessions is None:
            print("✗ Cannot generate: Required data not available")
            return
        
        # Merge data
        df = self.agent_results.merge(
            self.analysis_sessions[['id', 'architecture', 'status']], 
            left_on='session_id', 
            right_on='id',
            how='left'
        )
        
        df = df[(df['status_y'] == 'completed') & (df['status_x'] == 'completed')]
        
        if len(df) == 0:
            print("✗ Cannot generate: No completed data found")
            return
        
        architectures = df['architecture'].unique()
        n_archs = len(architectures)
        
        # Create subplots
        fig, axes = plt.subplots(1, n_archs, figsize=(6 * n_archs, 6))
        if n_archs == 1:
            axes = [axes]
        
        for idx, arch in enumerate(architectures):
            arch_data = df[df['architecture'] == arch]
            token_by_agent = arch_data.groupby('agent_name')['token_usage'].sum()
            
            # Create pie chart
            axes[idx].pie(token_by_agent.values, labels=token_by_agent.index, 
                         autopct='%1.1f%%', startangle=90)
            axes[idx].set_title(f'{arch} Architecture\nToken Distribution', 
                              fontsize=12, fontweight='bold')
        
        plt.suptitle('Agent Contribution to Total Token Usage by Architecture', 
                    fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        output_path = self.output_dir / "figure_7_agent_contribution_pie.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
    
    def figure_8_processing_time_breakdown(self):
        """
        Figure 8: Processing Time Breakdown by Agent (Stacked Horizontal Bar)
        Shows which agents take the most time in each architecture
        """
        print("\n" + "=" * 80)
        print("FIGURE 8: Processing Time Breakdown by Agent")
        print("=" * 80)
        
        if self.agent_results is None or self.analysis_sessions is None:
            print("✗ Cannot generate: Required data not available")
            return
        
        # Merge data
        df = self.agent_results.merge(
            self.analysis_sessions[['id', 'architecture', 'status']], 
            left_on='session_id', 
            right_on='id',
            how='left'
        )
        
        df = df[(df['status_y'] == 'completed') & (df['status_x'] == 'completed')]
        
        if len(df) == 0:
            print("✗ Cannot generate: No completed data found")
            return
        
        print(f"✓ Analyzing {len(df)} agent executions")
        
        # Calculate average processing time by architecture and agent
        pivot_data = df.groupby(['architecture', 'agent_name'])['processing_time'].mean().unstack(fill_value=0)
        
        # Create stacked horizontal bar chart
        fig, ax = plt.subplots(figsize=(12, 6))
        pivot_data.plot(kind='barh', stacked=True, ax=ax, width=0.7)
        
        ax.set_title('Processing Time Breakdown by Architecture and Agent', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel('Architecture Type', fontsize=12, fontweight='bold')
        ax.set_xlabel('Average Processing Time (seconds)', fontsize=12, fontweight='bold')
        ax.legend(title='Agent Name', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        output_path = self.output_dir / "figure_8_processing_time_breakdown.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
    
    def figure_9_failure_rate_by_agent(self):
        """
        Figure 9: Failure Rate by Agent (Horizontal Bar Chart)
        Shows which agents fail most frequently
        """
        print("\n" + "=" * 80)
        print("FIGURE 9: Failure Rate by Agent")
        print("=" * 80)
        
        if self.agent_results is None:
            print("✗ Cannot generate: agent_results data not available")
            return
        
        df = self.agent_results.copy()
        
        # Calculate failure rate by agent
        failure_data = []
        for agent in df['agent_name'].unique():
            agent_data = df[df['agent_name'] == agent]
            total = len(agent_data)
            failed = len(agent_data[agent_data['status'].isin(['failed', 'timeout'])])
            failure_rate = (failed / total * 100) if total > 0 else 0
            
            failure_data.append({
                'Agent': agent,
                'Failure Rate (%)': failure_rate,
                'Total': total,
                'Failed': failed
            })
        
        df_failure = pd.DataFrame(failure_data).sort_values('Failure Rate (%)', ascending=True)
        
        print(f"✓ Analyzing {len(df)} agent executions")
        
        # Create horizontal bar chart
        fig, ax = plt.subplots(figsize=(10, 8))
        bars = ax.barh(df_failure['Agent'], df_failure['Failure Rate (%)'], 
                      color=['#2ecc71' if x < 10 else '#e74c3c' for x in df_failure['Failure Rate (%)']])
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{width:.1f}%',
                   ha='left', va='center', fontweight='bold', fontsize=9)
        
        ax.set_title('Failure Rate by Agent', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Failure Rate (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Agent Name', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        ax.set_xlim(0, max(df_failure['Failure Rate (%)']) * 1.15)
        
        plt.tight_layout()
        output_path = self.output_dir / "figure_9_failure_rate_by_agent.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
        
        print("\nFailure Statistics:")
        print(df_failure.to_string(index=False))
    
    def figure_10_performance_variance(self):
        """
        Figure 10: Performance Variance/Consistency (Coefficient of Variation)
        Shows which architecture is most predictable
        """
        print("\n" + "=" * 80)
        print("FIGURE 10: Performance Variance (Coefficient of Variation)")
        print("=" * 80)
        
        if self.analysis_sessions is None:
            print("✗ Cannot generate: analysis_sessions data not available")
            return
        
        df = self.analysis_sessions[self.analysis_sessions['status'] == 'completed'].copy()
        
        if len(df) == 0:
            print("✗ Cannot generate: No completed sessions found")
            return
        
        # Calculate Coefficient of Variation (CV = std/mean * 100%)
        cv_data = []
        for arch in df['architecture'].unique():
            arch_data = df[df['architecture'] == arch]
            
            time_mean = arch_data['total_processing_time'].mean()
            time_std = arch_data['total_processing_time'].std()
            time_cv = (time_std / time_mean * 100) if time_mean > 0 else 0
            
            token_mean = arch_data['total_token_usage'].mean()
            token_std = arch_data['total_token_usage'].std()
            token_cv = (token_std / token_mean * 100) if token_mean > 0 else 0
            
            cv_data.append({
                'Architecture': arch,
                'Time CV (%)': time_cv,
                'Token CV (%)': token_cv
            })
        
        df_cv = pd.DataFrame(cv_data)
        
        print(f"✓ Analyzing {len(df)} sessions")
        
        # Create grouped bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(df_cv))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, df_cv['Time CV (%)'], width, label='Time CV', alpha=0.8)
        bars2 = ax.bar(x + width/2, df_cv['Token CV (%)'], width, label='Token CV', alpha=0.8)
        
        ax.set_xlabel('Architecture Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Coefficient of Variation (%)', fontsize=12, fontweight='bold')
        ax.set_title('Performance Consistency by Architecture\n(Lower CV = More Consistent)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(df_cv['Architecture'])
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        output_path = self.output_dir / "figure_10_performance_variance.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
        
        print("\nCoefficient of Variation (lower = more consistent):")
        print(df_cv.to_string(index=False))
    
    def figure_11_parallel_efficiency(self):
        """
        Figure 11: Parallel Efficiency Analysis
        Shows if parallel architecture achieves theoretical speedup
        """
        print("\n" + "=" * 80)
        print("FIGURE 11: Parallel Efficiency Analysis")
        print("=" * 80)
        
        if self.analysis_sessions is None:
            print("✗ Cannot generate: analysis_sessions data not available")
            return
        
        df = self.analysis_sessions[self.analysis_sessions['status'] == 'completed'].copy()
        
        # Check for Sequential (case-insensitive)
        archs_lower = [str(a).lower() for a in df['architecture'].unique()]
        if 'sequential' not in archs_lower:
            print("✗ Cannot generate: Sequential architecture baseline not available")
            return
        
        # Get baseline (case-insensitive match)
        sequential_mask = df['architecture'].str.lower() == 'sequential'
        t_sequential = df[sequential_mask]['total_processing_time'].mean()
        
        # Calculate speedup and efficiency
        efficiency_data = []
        for arch in df['architecture'].unique():
            t_arch = df[df['architecture'] == arch]['total_processing_time'].mean()
            actual_speedup = t_sequential / t_arch if t_arch > 0 else 0
            
            # Assuming 9 agents can run in parallel
            theoretical_speedup = 9 if str(arch).lower() == 'parallel' else 1
            efficiency = (actual_speedup / theoretical_speedup * 100) if theoretical_speedup > 0 else 0
            
            efficiency_data.append({
                'Architecture': arch,
                'Actual Speedup': actual_speedup,
                'Theoretical Speedup': theoretical_speedup,
                'Efficiency (%)': efficiency
            })
        
        df_eff = pd.DataFrame(efficiency_data)
        
        print(f"✓ Sequential baseline: {t_sequential:.2f}s")
        
        # Create visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Speedup comparison
        x = np.arange(len(df_eff))
        width = 0.35
        ax1.bar(x - width/2, df_eff['Actual Speedup'], width, label='Actual', alpha=0.8)
        ax1.bar(x + width/2, df_eff['Theoretical Speedup'], width, label='Theoretical', alpha=0.8)
        ax1.set_xlabel('Architecture Type', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Speedup Factor', fontsize=12, fontweight='bold')
        ax1.set_title('Actual vs. Theoretical Speedup', fontsize=12, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(df_eff['Architecture'])
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Plot 2: Efficiency
        bars = ax2.bar(df_eff['Architecture'], df_eff['Efficiency (%)'], 
                      color=['#2ecc71' if x > 50 else '#e74c3c' for x in df_eff['Efficiency (%)']])
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
        ax2.set_xlabel('Architecture Type', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Efficiency (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Parallel Efficiency', fontsize=12, fontweight='bold')
        ax2.axhline(y=100, color='green', linestyle='--', alpha=0.5, label='100% Efficient')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.suptitle('Parallel Efficiency Analysis', fontsize=14, fontweight='bold')
        plt.tight_layout()
        output_path = self.output_dir / "figure_11_parallel_efficiency.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
        
        print("\nEfficiency Analysis:")
        print(df_eff.to_string(index=False))
    
    def figure_12_time_cost_correlation(self):
        """
        Figure 12: Time vs. Cost Correlation (Regression Line)
        Shows relationship between processing time and token usage
        """
        print("\n" + "=" * 80)
        print("FIGURE 12: Time vs. Cost Correlation Analysis")
        print("=" * 80)
        
        if self.analysis_sessions is None:
            print("✗ Cannot generate: analysis_sessions data not available")
            return
        
        df = self.analysis_sessions[self.analysis_sessions['status'] == 'completed'].copy()
        
        if len(df) < 3:
            print("✗ Cannot generate: Not enough data points for correlation")
            return
        
        print(f"✓ Analyzing {len(df)} sessions")
        
        # Create scatter plot with regression lines
        fig, ax = plt.subplots(figsize=(12, 8))
        
        architectures = df['architecture'].unique()
        colors = sns.color_palette("husl", len(architectures))
        
        for idx, arch in enumerate(architectures):
            arch_data = df[df['architecture'] == arch]
            
            # Scatter plot
            ax.scatter(arch_data['total_processing_time'], 
                      arch_data['total_token_usage'],
                      label=arch, s=100, alpha=0.6, color=colors[idx])
            
            # Regression line
            if len(arch_data) > 1:
                z = np.polyfit(arch_data['total_processing_time'], 
                              arch_data['total_token_usage'], 1)
                p = np.poly1d(z)
                x_line = np.linspace(arch_data['total_processing_time'].min(), 
                                    arch_data['total_processing_time'].max(), 100)
                ax.plot(x_line, p(x_line), "--", color=colors[idx], linewidth=2, alpha=0.8)
                
                # Calculate correlation
                corr = arch_data['total_processing_time'].corr(arch_data['total_token_usage'])
                print(f"{arch}: Correlation = {corr:.3f}")
        
        ax.set_xlabel('Total Processing Time (seconds)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Token Usage', fontsize=12, fontweight='bold')
        ax.set_title('Time vs. Token Usage Correlation by Architecture\n(with Regression Lines)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_path = self.output_dir / "figure_12_time_cost_correlation.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
    
    def figure_13_agent_execution_heatmap(self):
        """
        Figure 13: Agent Execution Heatmap
        Shows success rate of each agent in each architecture
        """
        print("\n" + "=" * 80)
        print("FIGURE 13: Agent Execution Success Rate Heatmap")
        print("=" * 80)
        
        if self.agent_results is None or self.analysis_sessions is None:
            print("✗ Cannot generate: Required data not available")
            return
        
        # Merge data
        df = self.agent_results.merge(
            self.analysis_sessions[['id', 'architecture']], 
            left_on='session_id', 
            right_on='id',
            how='left'
        )
        
        # Calculate success rate
        heatmap_data = []
        for agent in df['agent_name'].unique():
            row_data = {'Agent': agent}
            for arch in df['architecture'].unique():
                agent_arch_data = df[(df['agent_name'] == agent) & (df['architecture'] == arch)]
                if len(agent_arch_data) > 0:
                    success_rate = len(agent_arch_data[agent_arch_data['status'] == 'completed']) / len(agent_arch_data) * 100
                else:
                    success_rate = 0
                row_data[arch] = success_rate
            heatmap_data.append(row_data)
        
        df_heatmap = pd.DataFrame(heatmap_data).set_index('Agent')
        
        print(f"✓ Analyzing {len(df)} agent executions")
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(df_heatmap, annot=True, fmt='.1f', cmap='RdYlGn', 
                   vmin=0, vmax=100, cbar_kws={'label': 'Success Rate (%)'}, ax=ax)
        
        ax.set_title('Agent Success Rate by Architecture', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Architecture Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Agent Name', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        output_path = self.output_dir / "figure_13_agent_execution_heatmap.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
        
        print("\nSuccess Rate Matrix:")
        print(df_heatmap)
    
    def figure_14_financial_cost_comparison(self):
        """
        Figure 14: Comparative Financial Cost ($) by Architecture
        Shows actual dollar costs instead of just token counts
        """
        print("\n" + "=" * 80)
        print("FIGURE 14: Comparative Financial Cost ($) by Architecture")
        print("=" * 80)
        
        if self.analysis_sessions is None:
            print("✗ Cannot generate: analysis_sessions data not available")
            return
        
        # Check if cost columns exist (handle both naming conventions)
        cost_col = None
        if 'total_cost' in self.analysis_sessions.columns:
            cost_col = 'total_cost'
        elif 'total_cost_usd' in self.analysis_sessions.columns:
            cost_col = 'total_cost_usd'
        
        if cost_col is None:
            print("✗ Cannot generate: 'total_cost' or 'total_cost_usd' column not found")
            print("  Please add a cost column with dollar amounts")
            return
        
        df = self.analysis_sessions[self.analysis_sessions['status'] == 'completed'].copy()
        
        if len(df) == 0:
            print("✗ Cannot generate: No completed sessions found")
            return
        
        print(f"✓ Analyzing {len(df)} sessions with cost data")
        
        # Create figure with box plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Financial Cost Box Plot
        sns.boxplot(data=df, x='architecture', y=cost_col, ax=ax1)
        ax1.set_title('Financial Cost Distribution by Architecture', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Architecture Type', fontsize=12)
        ax1.set_ylabel('Total Cost ($)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # Add mean markers
        means = df.groupby('architecture')[cost_col].mean()
        positions = range(len(means))
        ax1.scatter(positions, means, color='red', s=100, zorder=3, label='Mean', marker='D')
        ax1.legend()
        
        # Plot 2: Average Cost Bar Chart with values
        avg_costs = df.groupby('architecture')[cost_col].mean().sort_values(ascending=False)
        bars = ax2.bar(avg_costs.index, avg_costs.values, color=['#e74c3c', '#3498db', '#2ecc71'], alpha=0.8)
        
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:.4f}',
                   ha='center', va='bottom', fontweight='bold')
        
        ax2.set_title('Average Financial Cost by Architecture', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Architecture Type', fontsize=12)
        ax2.set_ylabel('Average Cost ($)', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        output_path = self.output_dir / "figure_14_financial_cost_comparison.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
        
        # Print statistics
        print("\nFinancial Cost Statistics:")
        for arch in df['architecture'].unique():
            arch_data = df[df['architecture'] == arch]
            print(f"\n{arch}:")
            print(f"  Mean: ${arch_data[cost_col].mean():.4f}")
            print(f"  Median: ${arch_data[cost_col].median():.4f}")
            print(f"  Std: ${arch_data[cost_col].std():.4f}")
            print(f"  Total: ${arch_data[cost_col].sum():.4f}")
    
    def figure_15_input_vs_output_tokens(self):
        """
        Figure 15: Input vs Output Token Breakdown
        Shows the ratio of input (prompt) to output (completion) tokens
        """
        print("\n" + "=" * 80)
        print("FIGURE 15: Input vs Output Token Breakdown by Architecture")
        print("=" * 80)
        
        if self.analysis_sessions is None:
            print("✗ Cannot generate: analysis_sessions data not available")
            return
        
        # Check if input/output token columns exist (handle both naming conventions)
        input_col = None
        output_col = None
        
        if 'input_tokens' in self.analysis_sessions.columns:
            input_col = 'input_tokens'
            output_col = 'output_tokens'
        elif 'input_token' in self.analysis_sessions.columns:
            input_col = 'input_token'
            output_col = 'output_token'
        
        if input_col is None:
            print("✗ Cannot generate: Missing input/output token columns")
            print("  Please add 'input_tokens' and 'output_tokens' (or 'input_token'/'output_token') columns")
            return
        
        df = self.analysis_sessions[self.analysis_sessions['status'] == 'completed'].copy()
        
        if len(df) == 0:
            print("✗ Cannot generate: No completed sessions found")
            return
        
        print(f"✓ Analyzing {len(df)} sessions")
        
        # Calculate averages by architecture
        token_breakdown = df.groupby('architecture')[[input_col, output_col]].mean()
        
        # Create stacked bar chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Stacked bar chart
        token_breakdown.plot(kind='bar', stacked=True, ax=ax1, color=['#3498db', '#e74c3c'])
        ax1.set_title('Average Input vs Output Tokens by Architecture', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Architecture Type', fontsize=12)
        ax1.set_ylabel('Average Token Count', fontsize=12)
        ax1.legend(['Input Tokens (Prompt)', 'Output Tokens (Completion)'], loc='upper left')
        ax1.grid(True, alpha=0.3, axis='y')
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=0)
        
        # Plot 2: Percentage breakdown
        token_breakdown_pct = token_breakdown.div(token_breakdown.sum(axis=1), axis=0) * 100
        token_breakdown_pct.plot(kind='bar', stacked=True, ax=ax2, color=['#3498db', '#e74c3c'])
        ax2.set_title('Input vs Output Token Ratio by Architecture', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Architecture Type', fontsize=12)
        ax2.set_ylabel('Percentage (%)', fontsize=12)
        ax2.legend(['Input Tokens', 'Output Tokens'], loc='upper left')
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3, axis='y')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=0)
        
        plt.tight_layout()
        output_path = self.output_dir / "figure_15_input_vs_output_tokens.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
        
        # Print statistics
        print("\nToken Breakdown:")
        for arch in token_breakdown.index:
            inp = token_breakdown.loc[arch, input_col]
            out = token_breakdown.loc[arch, output_col]
            total = inp + out
            ratio = inp / out if out > 0 else 0
            print(f"\n{arch}:")
            print(f"  Input Tokens: {inp:.0f} ({inp/total*100:.1f}%)")
            print(f"  Output Tokens: {out:.0f} ({out/total*100:.1f}%)")
            print(f"  Input/Output Ratio: {ratio:.2f}")
    
    def figure_16_cost_efficiency_metrics(self):
        """
        Figure 16: Cost Efficiency Metrics
        Shows cost per token and identifies most cost-effective architecture
        """
        print("\n" + "=" * 80)
        print("FIGURE 16: Cost Efficiency Metrics")
        print("=" * 80)
        
        if self.analysis_sessions is None:
            print("✗ Cannot generate: analysis_sessions data not available")
            return
        
        # Check for cost column (handle both naming conventions)
        cost_col = 'total_cost' if 'total_cost' in self.analysis_sessions.columns else 'total_cost_usd'
        
        required_cols = ['total_token_usage', 'total_processing_time']
        missing_cols = [col for col in required_cols if col not in self.analysis_sessions.columns]
        
        if cost_col not in self.analysis_sessions.columns:
            print(f"✗ Cannot generate: Missing cost column ('total_cost' or 'total_cost_usd')")
            return
        
        if missing_cols:
            print(f"✗ Cannot generate: Missing columns {missing_cols}")
            return
        
        df = self.analysis_sessions[self.analysis_sessions['status'] == 'completed'].copy()
        
        if len(df) == 0:
            print("✗ Cannot generate: No completed sessions found")
            return
        
        # Calculate efficiency metrics
        df['cost_per_token'] = df[cost_col] / df['total_token_usage']
        df['cost_per_second'] = df[cost_col] / df['total_processing_time']
        
        print(f"✓ Analyzing {len(df)} sessions")
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Cost per Token
        efficiency1 = df.groupby('architecture')['cost_per_token'].mean().sort_values()
        bars1 = ax1.bar(efficiency1.index, efficiency1.values * 1000, 
                       color=['#2ecc71' if i == 0 else '#3498db' for i in range(len(efficiency1))],
                       alpha=0.8)
        
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:.3f}',
                   ha='center', va='bottom', fontweight='bold')
        
        ax1.set_title('Cost per 1000 Tokens by Architecture\n(Lower is Better)', 
                     fontsize=14, fontweight='bold')
        ax1.set_xlabel('Architecture Type', fontsize=12)
        ax1.set_ylabel('Cost per 1000 Tokens ($)', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Plot 2: Cost per Second
        efficiency2 = df.groupby('architecture')['cost_per_second'].mean().sort_values()
        bars2 = ax2.bar(efficiency2.index, efficiency2.values,
                       color=['#2ecc71' if i == 0 else '#3498db' for i in range(len(efficiency2))],
                       alpha=0.8)
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:.4f}',
                   ha='center', va='bottom', fontweight='bold')
        
        ax2.set_title('Cost per Second by Architecture\n(Lower is Better)', 
                     fontsize=14, fontweight='bold')
        ax2.set_xlabel('Architecture Type', fontsize=12)
        ax2.set_ylabel('Cost per Second ($)', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        output_path = self.output_dir / "figure_16_cost_efficiency_metrics.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
        
        # Print efficiency rankings
        print("\n💰 Cost Efficiency Rankings:")
        print("\nCost per 1000 Tokens (lower is better):")
        for i, (arch, cost) in enumerate(efficiency1.items(), 1):
            print(f"  {i}. {arch}: ${cost*1000:.3f}")
        
        print("\nCost per Second (lower is better):")
        for i, (arch, cost) in enumerate(efficiency2.items(), 1):
            print(f"  {i}. {arch}: ${cost:.4f}")
    
    def figure_17_cost_per_insight(self):
        """
        Figure 17: Cost per Insight Analysis
        Requires quality scores to calculate analytical value per dollar
        """
        print("\n" + "=" * 80)
        print("FIGURE 17: Cost per Insight (Value per Dollar)")
        print("=" * 80)
        
        if self.analysis_sessions is None:
            print("✗ Cannot generate: analysis_sessions data not available")
            return
        
        # Check for cost column
        cost_col = 'total_cost' if 'total_cost' in self.analysis_sessions.columns else 'total_cost_usd'
        
        if cost_col not in self.analysis_sessions.columns:
            print("⚠ Cannot generate: Missing cost column")
            return
        
        if 'quality_score' not in self.analysis_sessions.columns:
            print("⚠ Cannot generate: Missing 'quality_score' column")
            print("\n📝 TO ENABLE THIS FIGURE:")
            print("1. Add a 'quality_score' column to analysis_sessions.xlsx")
            print("2. Rate each session's output quality on a scale (e.g., 1-15)")
            print("   Consider: Coherence, Actionability, Depth, Relevance")
            print("3. Re-run the script")
            print("\nExample scoring rubric:")
            print("  - Coherence (1-5): How well-structured is the analysis?")
            print("  - Actionability (1-5): How useful are the recommendations?")
            print("  - Depth (1-5): How thorough is the insight?")
            print("  - Total: Sum of all criteria (1-15)")
            return
        
        df = self.analysis_sessions[self.analysis_sessions['status'] == 'completed'].copy()
        
        if len(df) == 0:
            print("✗ Cannot generate: No completed sessions found")
            return
        
        # Calculate cost per insight
        df['cost_per_insight'] = df[cost_col] / df['quality_score']
        df['insight_per_dollar'] = df['quality_score'] / df[cost_col]
        
        print(f"✓ Analyzing {len(df)} sessions with quality scores")
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Plot 1: Cost per Insight Point
        metric1 = df.groupby('architecture')['cost_per_insight'].mean().sort_values()
        bars1 = ax1.bar(metric1.index, metric1.values,
                       color=['#2ecc71' if i == 0 else '#3498db' for i in range(len(metric1))],
                       alpha=0.8)
        
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:.4f}',
                   ha='center', va='bottom', fontweight='bold')
        
        ax1.set_title('Cost per Insight Point by Architecture\n(Lower is Better)', 
                     fontsize=14, fontweight='bold')
        ax1.set_xlabel('Architecture Type', fontsize=12)
        ax1.set_ylabel('Cost per Quality Point ($)', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Plot 2: Insight per Dollar (inverse metric)
        metric2 = df.groupby('architecture')['insight_per_dollar'].mean().sort_values(ascending=False)
        bars2 = ax2.bar(metric2.index, metric2.values,
                       color=['#2ecc71' if i == 0 else '#3498db' for i in range(len(metric2))],
                       alpha=0.8)
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontweight='bold')
        
        ax2.set_title('Insight Quality per Dollar by Architecture\n(Higher is Better)', 
                     fontsize=14, fontweight='bold')
        ax2.set_xlabel('Architecture Type', fontsize=12)
        ax2.set_ylabel('Quality Points per Dollar', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        output_path = self.output_dir / "figure_17_cost_per_insight.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
        
        # Print value analysis
        print("\n💎 Value Analysis:")
        print("\nBest Value (Insight per Dollar):")
        for i, (arch, value) in enumerate(metric2.items(), 1):
            avg_cost = df[df['architecture'] == arch][cost_col].mean()
            avg_quality = df[df['architecture'] == arch]['quality_score'].mean()
            print(f"  {i}. {arch}:")
            print(f"     {value:.2f} quality points per dollar")
            print(f"     (Avg Quality: {avg_quality:.1f}, Avg Cost: ${avg_cost:.4f})")
    
    def figure_18_cost_vs_time_vs_quality(self):
        """
        Figure 18: 3D Cost-Time-Quality Trade-off
        Shows the relationship between all three key metrics
        """
        print("\n" + "=" * 80)
        print("FIGURE 18: Cost vs Time vs Quality Trade-off")
        print("=" * 80)
        
        if self.analysis_sessions is None:
            print("✗ Cannot generate: analysis_sessions data not available")
            return
        
        # Check for cost column
        cost_col = 'total_cost' if 'total_cost' in self.analysis_sessions.columns else 'total_cost_usd'
        
        if cost_col not in self.analysis_sessions.columns:
            print(f"✗ Cannot generate: Missing cost column")
            return
        
        if 'total_processing_time' not in self.analysis_sessions.columns:
            print(f"✗ Cannot generate: Missing 'total_processing_time' column")
            return
        
        df = self.analysis_sessions[self.analysis_sessions['status'] == 'completed'].copy()
        
        if len(df) == 0:
            print("✗ Cannot generate: No completed sessions found")
            return
        
        print(f"✓ Analyzing {len(df)} sessions")
        
        # Create scatter plot (Cost vs Time)
        fig, ax = plt.subplots(figsize=(12, 8))
        
        architectures = df['architecture'].unique()
        colors = sns.color_palette("husl", len(architectures))
        color_map = dict(zip(architectures, colors))
        
        for arch in architectures:
            arch_data = df[df['architecture'] == arch]
            
            # If quality score exists, size bubbles by it
            if 'quality_score' in df.columns:
                sizes = arch_data['quality_score'] * 50
                label_text = f"{arch} (size = quality)"
            else:
                sizes = 100
                label_text = arch
            
            ax.scatter(arch_data['total_processing_time'], 
                      arch_data[cost_col],
                      s=sizes,
                      alpha=0.6,
                      color=color_map[arch],
                      edgecolors='black',
                      linewidth=1,
                      label=label_text)
        
        ax.set_xlabel('Total Processing Time (seconds)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Cost ($)', fontsize=12, fontweight='bold')
        
        if 'quality_score' in df.columns:
            title = 'Cost vs. Time Trade-off by Architecture\n(Bubble Size = Quality Score)'
        else:
            title = 'Cost vs. Time Trade-off by Architecture'
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.legend(fontsize=10, loc='best')
        ax.grid(True, alpha=0.3)
        
        # Add ideal region annotation
        ax.text(0.02, 0.98, '← Faster, Cheaper (Ideal)', 
               transform=ax.transAxes, fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
        
        plt.tight_layout()
        output_path = self.output_dir / "figure_18_cost_vs_time_vs_quality.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
        plt.close()
        
        # Calculate and display efficiency score
        print("\n📊 Efficiency Score (lower is better):")
        print("   Formula: (Cost × Time) / Quality (if available)")
        for arch in architectures:
            arch_data = df[df['architecture'] == arch]
            avg_cost = arch_data[cost_col].mean()
            avg_time = arch_data['total_processing_time'].mean()
            
            if 'quality_score' in df.columns:
                avg_quality = arch_data['quality_score'].mean()
                efficiency = (avg_cost * avg_time) / avg_quality if avg_quality > 0 else float('inf')
                print(f"  {arch}: {efficiency:.4f} (Cost=${avg_cost:.4f}, Time={avg_time:.1f}s, Quality={avg_quality:.1f})")
            else:
                efficiency = avg_cost * avg_time
                print(f"  {arch}: {efficiency:.4f} (Cost=${avg_cost:.4f}, Time={avg_time:.1f}s)")
    
    def calculate_formulas(self):
        """
        Calculate the suggested formulas for thesis
        """
        print("\n" + "=" * 80)
        print("FORMULA CALCULATIONS")
        print("=" * 80)
        
        if self.analysis_sessions is None:
            print("✗ Cannot calculate: analysis_sessions data not available")
            return
        
        df = self.analysis_sessions[self.analysis_sessions['status'] == 'completed'].copy()
        
        if len(df) == 0:
            print("✗ Cannot calculate: No completed sessions found")
            return
        
        # 1. Performance Speedup
        print("\n1. PERFORMANCE SPEEDUP")
        print("-" * 80)
        # Check for Sequential (case-insensitive)
        archs_lower = [str(a).lower() for a in df['architecture'].unique()]
        if 'sequential' in archs_lower:
            sequential_mask = df['architecture'].str.lower() == 'sequential'
            t_sequential = df[sequential_mask]['total_processing_time'].mean()
            print(f"Baseline (Sequential): {t_sequential:.2f}s")
            
            for arch in df['architecture'].unique():
                if str(arch).lower() != 'sequential':
                    t_arch = df[df['architecture'] == arch]['total_processing_time'].mean()
                    speedup = t_sequential / t_arch if t_arch > 0 else 0
                    print(f"Speedup({arch}): {speedup:.2f}x (Avg Time: {t_arch:.2f}s)")
        else:
            print("⚠ Sequential architecture data not available for baseline")
        
        # 2. Cost Overhead of Orchestration
        print("\n2. COST OVERHEAD OF ORCHESTRATION")
        print("-" * 80)
        if self.agent_results is not None:
            # Merge to get architecture for each agent result
            merged = self.agent_results.merge(
                self.analysis_sessions[['id', 'architecture']], 
                left_on='session_id', 
                right_on='id',
                how='left'
            )
            
            for arch in df['architecture'].unique():
                # Total tokens from sessions
                c_total = df[df['architecture'] == arch]['total_token_usage'].mean()
                
                # Tokens from worker agents only
                arch_agents = merged[
                    (merged['architecture'] == arch) & 
                    (merged['status'] == 'completed')
                ]
                c_agents = arch_agents['token_usage'].sum() / len(df[df['architecture'] == arch])
                
                overhead = c_total - c_agents
                overhead_pct = (overhead / c_total * 100) if c_total > 0 else 0
                
                print(f"{arch}:")
                print(f"  Total Avg Tokens: {c_total:.0f}")
                print(f"  Worker Agent Avg Tokens: {c_agents:.0f}")
                print(f"  Overhead: {overhead:.0f} tokens ({overhead_pct:.1f}%)")
        else:
            print("⚠ Agent results not available")
        
        # 3. System Success Rate (SSR)
        print("\n3. SYSTEM SUCCESS RATE (SSR)")
        print("-" * 80)
        for arch in self.analysis_sessions['architecture'].unique():
            arch_data = self.analysis_sessions[self.analysis_sessions['architecture'] == arch]
            n_total = len(arch_data)
            n_completed = len(arch_data[arch_data['status'] == 'completed'])
            ssr = (n_completed / n_total * 100) if n_total > 0 else 0
            print(f"SSR({arch}): {ssr:.1f}% ({n_completed}/{n_total})")
        
        # 4. Composite "Value" Score
        print("\n4. COMPOSITE 'VALUE' SCORE")
        print("-" * 80)
        print("⚠ Requires qualitative scores from user evaluation (not in current data)")
        print("Formula: Value_Cost = Avg_Quality_Score / Avg_Total_Tokens")
        print("Formula: Value_Time = Avg_Quality_Score / Avg_Total_Time")
        print("\nTo calculate this, you need to:")
        print("1. Evaluate each session's output quality (score 1-15)")
        print("2. Add a 'quality_score' column to analysis_sessions.xlsx")
        print("3. Re-run this analysis")
    
    def generate_all(self):
        """Generate all figures and tables"""
        print("\n" + "=" * 80)
        print("GENERATING ALL VISUALIZATIONS AND TABLES")
        print("=" * 80)
        
        # Original 4 figures + 2 tables
        self.figure_1_performance_distribution_boxplot()
        self.figure_2_cost_vs_time_scatter()
        self.figure_3_granular_cost_breakdown()
        self.figure_4_system_reliability()
        self.table_1_detailed_failure_analysis()
        self.table_2_performance_summary_statistics()
        
        # Additional 9 figures (agent-level analysis)
        self.figure_5_agent_performance_comparison()
        self.figure_6_token_efficiency()
        self.figure_7_agent_contribution_pie()
        self.figure_8_processing_time_breakdown()
        self.figure_9_failure_rate_by_agent()
        self.figure_10_performance_variance()
        self.figure_11_parallel_efficiency()
        self.figure_12_time_cost_correlation()
        self.figure_13_agent_execution_heatmap()
        
        # NEW: Financial cost analysis (5 figures)
        self.figure_14_financial_cost_comparison()
        self.figure_15_input_vs_output_tokens()
        self.figure_16_cost_efficiency_metrics()
        self.figure_17_cost_per_insight()
        self.figure_18_cost_vs_time_vs_quality()
        
        # Formulas
        self.calculate_formulas()
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE!")
        print("=" * 80)
        print(f"\nAll outputs saved to: {self.output_dir.absolute()}")
        print("\n📊 GENERATED VISUALIZATIONS:")
        
        figures = [
            "Figures 1-4: Core Performance Metrics",
            "Figures 5-13: Agent-Level Deep Dive", 
            "Figures 14-18: Financial Cost Analysis (NEW!)"
        ]
        for fig_group in figures:
            print(f"  ✓ {fig_group}")
        
        print("\n📋 GENERATED TABLES:")
        print("  ✓ Table 1: Detailed Failure Analysis")
        print("  ✓ Table 2: Performance Summary Statistics")
        
        print("\n📁 Output Files:")
        for file in sorted(self.output_dir.glob("*")):
            print(f"  - {file.name}")


def main():
    """Main execution function"""
    print("\n" + "=" * 80)
    print("THESIS ANALYSIS SCRIPT")
    print("Strategic Intelligence Analysis Performance Evaluation")
    print("=" * 80)
    
    analyzer = ThesisAnalyzer()
    
    # Load data
    analyzer.load_data()
    
    # Inspect data structure
    analyzer.inspect_data()
    
    # Check for missing data
    missing_data = analyzer.check_missing_data()
    
    # Generate all visualizations and tables
    analyzer.generate_all()
    
    # Final recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS FOR DATA COLLECTION")
    print("=" * 80)
    print("""
To strengthen your thesis analysis, ensure you have:

1. MULTIPLE TEST RUNS (3-5 per architecture minimum)
   - Current recommendation: 5 different strategic questions
   - Each tested on all 3 architectures (Sequential, Parallel, Hierarchical)
   - Total: 15 analysis sessions minimum

2. COMPLETE METADATA for each session:
   - architecture (Sequential/Parallel/Hierarchical)
   - status (completed/failed/timeout)
   - total_processing_time (in seconds)
   - total_token_usage (integer)
   - input_tokens (prompt tokens)
   - output_tokens (completion tokens)
   - total_cost (actual dollar cost)
   - created_at, completed_at (timestamps)

3. AGENT-LEVEL DATA for each session:
   - session_id (links to analysis_sessions)
   - agent_name
   - status (completed/failed/timeout)
   - processing_time (seconds)
   - token_usage (integer)

4. QUALITATIVE EVALUATION (recommended):
   - Add 'quality_score' column to analysis_sessions
   - Score each output on criteria like:
     * Coherence (1-5)
     * Actionability (1-5)
     * Insight Depth (1-5)
     * Total: 1-15 scale

5. FAILURE TRACKING:
   - Record error_message for failed agents
   - Track timeout durations
   - Document failure patterns

6. FINANCIAL COST CALCULATION (NEW!):
   - Calculate actual dollar costs using LLM provider pricing
   - Input tokens typically cost less than output tokens
   - Example (Google Gemini): Input ~$0.075/1M tokens, Output ~$0.30/1M tokens
   - Formula: total_cost = (input_tokens × input_price) + (output_tokens × output_price)
   - This gives you TRUE cost efficiency, not just token counts!

Run your experiments, populate the Excel files with cost data, and re-run this script!
    """)


if __name__ == "__main__":
    main()

