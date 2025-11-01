#!/usr/bin/env python3
"""
Interactive Benchmark Dashboard
Web-based dashboard for viewing and comparing framework benchmark results
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import os


def load_benchmark_data() -> List[Dict]:
    """Load the latest benchmark data"""
    # Find the most recent benchmark results file
    json_files = list(Path('.').glob('benchmark_results_*.json'))
    if not json_files:
        return []
    
    latest_file = max(json_files, key=os.path.getctime)
    
    with open(latest_file, 'r') as f:
        return json.load(f)


def load_summary_data() -> Dict:
    """Load benchmark summary statistics"""
    if Path('benchmark_summary.json').exists():
        with open('benchmark_summary.json', 'r') as f:
            return json.load(f)
    return {}


class BenchmarkDashboard:
    """Generate HTML dashboard for benchmark results"""
    
    def __init__(self):
        self.data = load_benchmark_data()
        self.summary = load_summary_data()
    
    def generate_html(self) -> str:
        """Generate complete HTML dashboard"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent Framework Benchmarks - Interactive Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .framework-card {{
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            transition: box-shadow 0.3s ease;
        }}
        .framework-card:hover {{
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 30px;
        }}
        .badge-success {{ background-color: #28a745; }}
        .badge-warning {{ background-color: #ffc107; color: #000; }}
        .badge-danger {{ background-color: #dc3545; }}
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <h1 class="text-center mt-4 mb-4">🧪 AI Agent Framework Benchmarks</h1>
                <p class="text-center text-muted">Real-time performance comparison of leading AI agent frameworks</p>
                
                {self.generate_overview_section()}
                {self.generate_performance_charts()}
                {self.generate_framework_comparison()}
                {self.generate_detailed_results()}
                {self.generate_methodology_section()}
                
                <div class="text-center mt-5 mb-4">
                    <p class="text-muted">
                        Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | 
                        <a href="https://www.agentically.sh/ai-agentic-frameworks/" target="_blank">
                            View More Framework Resources →
                        </a>
                    </p>
                </div>
            </div>
        </div>
    </div>

    <script>
        {self.generate_chart_scripts()}
    </script>
</body>
</html>
"""
    
    def generate_overview_section(self) -> str:
        """Generate overview metrics section"""
        if not self.summary:
            return ""
        
        return f"""
        <div class="row mb-5">
            <div class="col-md-3">
                <div class="metric-card text-center">
                    <h3>{self.summary.get('successful_tests', 0)}</h3>
                    <p>Successful Tests</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card text-center">
                    <h3>{len(self.summary.get('framework_stats', {}))}</h3>
                    <p>Frameworks Tested</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card text-center">
                    <h3>{self.summary.get('avg_response_time_ms', 0):.0f}ms</h3>
                    <p>Avg Response Time</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card text-center">
                    <h3>${self.summary.get('total_cost', 0):.4f}</h3>
                    <p>Total Test Cost</p>
                </div>
            </div>
        </div>
        
        <div class="row mb-5">
            <div class="col-12">
                <h2>🏆 Performance Leaders</h2>
                <div class="row">
                    {self.generate_leaders_cards()}
                </div>
            </div>
        </div>
        """
    
    def generate_leaders_cards(self) -> str:
        """Generate performance leaders cards"""
        if not self.summary.get('rankings'):
            return ""
        
        cards = []
        rankings = self.summary['rankings']
        
        categories = [
            ('fastest', 'Fastest Response', '⚡'),
            ('most_memory_efficient', 'Memory Efficient', '💾'),
            ('most_cost_effective', 'Cost Effective', '💰')
        ]
        
        for category, title, icon in categories:
            if category in rankings and rankings[category]:
                winner = rankings[category][0]
                framework = winner['framework']
                
                if 'time' in winner:
                    value = f"{winner['time']:.1f}ms"
                elif 'memory' in winner:
                    value = f"{winner['memory']:.1f}MB"
                elif 'cost' in winner:
                    value = f"${winner['cost']:.4f}"
                else:
                    value = "N/A"
                
                cards.append(f"""
                <div class="col-md-4">
                    <div class="framework-card text-center">
                        <h3>{icon} {title}</h3>
                        <h4 class="text-primary">{framework}</h4>
                        <p class="h5">{value}</p>
                    </div>
                </div>
                """)
        
        return "".join(cards)
    
    def generate_performance_charts(self) -> str:
        """Generate performance comparison charts"""
        return """
        <div class="row mb-5">
            <div class="col-12">
                <h2>📊 Performance Comparison</h2>
            </div>
            <div class="col-md-6">
                <div class="chart-container">
                    <canvas id="responseTimeChart"></canvas>
                </div>
            </div>
            <div class="col-md-6">
                <div class="chart-container">
                    <canvas id="memoryUsageChart"></canvas>
                </div>
            </div>
            <div class="col-md-6">
                <div class="chart-container">
                    <canvas id="costComparisonChart"></canvas>
                </div>
            </div>
            <div class="col-md-6">
                <div class="chart-container">
                    <canvas id="successRateChart"></canvas>
                </div>
            </div>
        </div>
        """
    
    def generate_framework_comparison(self) -> str:
        """Generate detailed framework comparison table"""
        if not self.summary.get('framework_stats'):
            return ""
        
        frameworks = self.summary['framework_stats']
        
        rows = []
        for framework, stats in frameworks.items():
            success_badge = "badge-success" if stats['success_rate'] > 0.9 else "badge-warning" if stats['success_rate'] > 0.8 else "badge-danger"
            
            rows.append(f"""
            <tr>
                <td><strong>{framework}</strong></td>
                <td>{stats['avg_response_time_ms']:.1f}ms</td>
                <td>{stats['avg_memory_usage_mb']:.1f}MB</td>
                <td>${stats['avg_cost_per_test']:.4f}</td>
                <td><span class="badge {success_badge}">{stats['success_rate']:.1%}</span></td>
                <td>{stats['tests_completed']}</td>
            </tr>
            """)
        
        return f"""
        <div class="row mb-5">
            <div class="col-12">
                <h2>📋 Detailed Framework Comparison</h2>
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>Framework</th>
                                <th>Avg Response Time</th>
                                <th>Avg Memory Usage</th>
                                <th>Avg Cost per Test</th>
                                <th>Success Rate</th>
                                <th>Tests Completed</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(rows)}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        """
    
    def generate_detailed_results(self) -> str:
        """Generate detailed test results section"""
        if not self.data:
            return ""
        
        # Show latest 20 results
        recent_results = sorted(self.data, key=lambda x: x['timestamp'], reverse=True)[:20]
        
        rows = []
        for result in recent_results:
            success_icon = "✅" if result['success'] else "❌"
            timestamp = datetime.fromisoformat(result['timestamp']).strftime("%m-%d %H:%M")
            
            rows.append(f"""
            <tr>
                <td>{success_icon}</td>
                <td>{result['framework']}</td>
                <td>{result['test_name']}</td>
                <td>{result['response_time_ms']:.1f}ms</td>
                <td>{result['memory_usage_mb']:.1f}MB</td>
                <td>{result['tokens_used']}</td>
                <td>${result['cost_estimate']:.4f}</td>
                <td>{timestamp}</td>
            </tr>
            """)
        
        return f"""
        <div class="row mb-5">
            <div class="col-12">
                <h2>📈 Recent Test Results</h2>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead class="table-light">
                            <tr>
                                <th>Status</th>
                                <th>Framework</th>
                                <th>Test</th>
                                <th>Response Time</th>
                                <th>Memory</th>
                                <th>Tokens</th>
                                <th>Cost</th>
                                <th>Time</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(rows)}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        """
    
    def generate_methodology_section(self) -> str:
        """Generate methodology and links section"""
        return """
        <div class="row mb-5">
            <div class="col-12">
                <h2>🔬 Benchmark Methodology</h2>
                <div class="card">
                    <div class="card-body">
                        <h5>Test Environment</h5>
                        <ul>
                            <li><strong>Hardware:</strong> AWS c5.4xlarge (16 vCPU, 32GB RAM)</li>
                            <li><strong>OS:</strong> Ubuntu 22.04 LTS</li>
                            <li><strong>Python:</strong> 3.9.18</li>
                            <li><strong>Models:</strong> GPT-4, GPT-3.5-turbo</li>
                        </ul>
                        
                        <h5>Test Scenarios</h5>
                        <ul>
                            <li><strong>Simple Task:</strong> Basic Q&A and text generation</li>
                            <li><strong>Multi-Agent Task:</strong> Agent collaboration and coordination</li>
                            <li><strong>Complex Task:</strong> Multi-step reasoning and problem solving</li>
                        </ul>
                        
                        <h5>Metrics Collected</h5>
                        <ul>
                            <li>Response times (average, p50, p95, p99)</li>
                            <li>Memory usage (base, peak, per-agent)</li>
                            <li>Token consumption (input, output, efficiency)</li>
                            <li>Success rates and error patterns</li>
                            <li>Cost estimates based on current API pricing</li>
                        </ul>
                        
                        <div class="mt-4">
                            <h5>🔗 Related Resources</h5>
                            <div class="row">
                                <div class="col-md-6">
                                    <ul>
                                        <li><a href="https://github.com/agenticallysh/ai-agentic-frameworks" target="_blank">Framework Guides</a></li>
                                        <li><a href="https://github.com/agenticallysh/agentic-framework-migration-guides" target="_blank">Migration Guides</a></li>
                                        <li><a href="https://github.com/agenticallysh/production-agent-templates" target="_blank">Production Templates</a></li>
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <ul>
                                        <li><a href="https://github.com/agenticallysh/framework-cost-calculator" target="_blank">Cost Calculator</a></li>
                                        <li><a href="https://www.agentically.sh/ai-agentic-frameworks/" target="_blank">Interactive Comparison</a></li>
                                        <li><a href="https://discord.gg/agentically" target="_blank">Community Discord</a></li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def generate_chart_scripts(self) -> str:
        """Generate JavaScript for interactive charts"""
        if not self.summary.get('framework_stats'):
            return ""
        
        frameworks = list(self.summary['framework_stats'].keys())
        response_times = [self.summary['framework_stats'][f]['avg_response_time_ms'] for f in frameworks]
        memory_usage = [self.summary['framework_stats'][f]['avg_memory_usage_mb'] for f in frameworks]
        costs = [self.summary['framework_stats'][f]['avg_cost_per_test'] for f in frameworks]
        success_rates = [self.summary['framework_stats'][f]['success_rate'] * 100 for f in frameworks]
        
        return f"""
        // Chart.js configuration
        const frameworks = {json.dumps(frameworks)};
        const responseTimes = {json.dumps(response_times)};
        const memoryUsage = {json.dumps(memory_usage)};
        const costs = {json.dumps(costs)};
        const successRates = {json.dumps(success_rates)};
        
        const chartColors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'];
        
        // Response Time Chart
        new Chart(document.getElementById('responseTimeChart'), {{
            type: 'bar',
            data: {{
                labels: frameworks,
                datasets: [{{
                    label: 'Response Time (ms)',
                    data: responseTimes,
                    backgroundColor: chartColors
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Average Response Time'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Memory Usage Chart
        new Chart(document.getElementById('memoryUsageChart'), {{
            type: 'bar',
            data: {{
                labels: frameworks,
                datasets: [{{
                    label: 'Memory Usage (MB)',
                    data: memoryUsage,
                    backgroundColor: chartColors
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Average Memory Usage'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Cost Comparison Chart
        new Chart(document.getElementById('costComparisonChart'), {{
            type: 'doughnut',
            data: {{
                labels: frameworks,
                datasets: [{{
                    label: 'Cost per Test ($)',
                    data: costs,
                    backgroundColor: chartColors
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Cost per Test Comparison'
                    }}
                }}
            }}
        }});
        
        // Success Rate Chart
        new Chart(document.getElementById('successRateChart'), {{
            type: 'radar',
            data: {{
                labels: frameworks,
                datasets: [{{
                    label: 'Success Rate (%)',
                    data: successRates,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Framework Success Rates'
                    }}
                }},
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});
        """
    
    def save_dashboard(self, filename: str = "benchmark_dashboard.html"):
        """Save the dashboard to an HTML file"""
        html_content = self.generate_html()
        with open(filename, 'w') as f:
            f.write(html_content)
        return filename


def main():
    """Generate and save the benchmark dashboard"""
    print("🖥️  Generating interactive benchmark dashboard...")
    
    dashboard = BenchmarkDashboard()
    filename = dashboard.save_dashboard()
    
    print(f"✅ Dashboard generated: {filename}")
    print(f"🌐 Open {filename} in your browser to view the interactive dashboard")
    print(f"🔗 Or view online at: https://www.agentically.sh/ai-agentic-frameworks/benchmarks/")


if __name__ == "__main__":
    main()