# Setup Guide

## Quick Start

Get up and running with AI Agent Framework Benchmarks in under 10 minutes.

### Prerequisites

- Python 3.8+ 
- 4GB+ RAM
- OpenAI API key (or alternative LLM provider)
- Git

### 1. Clone Repository

```bash
git clone https://github.com/agenticallysh/agent-framework-benchmarks.git
cd agent-framework-benchmarks
```

### 2. Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install core dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

Required environment variables:
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Optional: Alternative providers
ANTHROPIC_API_KEY=your_claude_api_key
COHERE_API_KEY=your_cohere_api_key

# Benchmark Configuration
BENCHMARK_RUNS=10
TIMEOUT_SECONDS=30
OUTPUT_FORMAT=json
```

### 4. Run Benchmarks

```bash
# Generate sample data (for demo)
python generate_simple_data.py

# Create interactive dashboard
python dashboard.py

# Open dashboard in browser
open benchmark_dashboard.html
```

## Framework Installation

Install only the frameworks you want to benchmark:

### AutoGen
```bash
pip install pyautogen>=0.2.0
```

### CrewAI
```bash
pip install crewai>=0.12.0 crewai-tools>=0.12.0
```

### LangChain
```bash
pip install langchain>=0.1.0 langchain-openai>=0.1.0
```

### LangGraph
```bash
pip install langgraph>=0.0.40
```

### Semantic Kernel
```bash
pip install semantic-kernel>=0.9.0
```

## Running Real Benchmarks

### Basic Benchmark Run

```bash
# Run benchmarks for installed frameworks
python benchmark_runner.py

# Run specific framework
python benchmark_runner.py --framework AutoGen

# Run with custom parameters
python benchmark_runner.py --runs 5 --timeout 60
```

### Advanced Configuration

Create `benchmark_config.yaml`:

```yaml
# Benchmark Configuration
runs_per_test: 10
timeout_seconds: 30
output_formats: [json, csv, html]

# Framework Selection
frameworks:
  - AutoGen
  - CrewAI
  - LangChain

# Test Selection
tests:
  - simple_task
  - multi_agent_task

# Model Configuration
models:
  primary: gpt-4
  fallback: gpt-3.5-turbo
  temperature: 0.7
  max_tokens: 1000
```

Run with config:
```bash
python benchmark_runner.py --config benchmark_config.yaml
```

## Docker Setup

### Using Docker Compose

```bash
# Clone repository
git clone https://github.com/agenticallysh/agent-framework-benchmarks.git
cd agent-framework-benchmarks

# Start benchmark environment
docker-compose up -d

# Run benchmarks
docker-compose exec benchmarks python benchmark_runner.py

# View dashboard
open http://localhost:8080
```

### Manual Docker Setup

```bash
# Build image
docker build -t framework-benchmarks .

# Run container
docker run -it \
  -e OPENAI_API_KEY=your_key_here \
  -v $(pwd)/results:/app/results \
  framework-benchmarks python benchmark_runner.py
```

## Cloud Deployment

### AWS Setup

```bash
# Launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0c7217cdde317cfec \
  --instance-type c5.4xlarge \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxx

# Connect and setup
ssh -i your-key.pem ubuntu@your-instance-ip
git clone https://github.com/agenticallysh/agent-framework-benchmarks.git
cd agent-framework-benchmarks
./scripts/setup.sh
```

### Automated AWS Deployment

```bash
# Using CloudFormation
aws cloudformation create-stack \
  --stack-name framework-benchmarks \
  --template-body file://aws/cloudformation.yaml \
  --parameters ParameterKey=KeyName,ParameterValue=your-key
```

## Continuous Integration

### GitHub Actions

Add `.github/workflows/benchmarks.yml`:

```yaml
name: Framework Benchmarks

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run benchmarks
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        python benchmark_runner.py --output results/
    
    - name: Generate dashboard
      run: |
        python dashboard.py
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./
        publish_branch: gh-pages
```

## Monitoring Setup

### Prometheus Integration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'framework-benchmarks'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

### Grafana Dashboard

```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Import dashboard
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @grafana/benchmark-dashboard.json
```

## Custom Framework Integration

### 1. Create Framework Adapter

```python
# frameworks/my_framework.py
from benchmark_runner import FrameworkBenchmark

class MyFrameworkBenchmark(FrameworkBenchmark):
    def __init__(self, config):
        super().__init__(config)
        self.framework_name = "MyFramework"
    
    def simple_task(self, prompt: str) -> BenchmarkResult:
        # Implement simple task benchmark
        pass
    
    def multi_agent_task(self, prompt: str) -> BenchmarkResult:
        # Implement multi-agent benchmark
        pass
```

### 2. Register Framework

```python
# benchmark_runner.py
from frameworks.my_framework import MyFrameworkBenchmark

# Add to framework registry
FRAMEWORKS = {
    "AutoGen": AutoGenBenchmark,
    "CrewAI": CrewAIBenchmark,
    "MyFramework": MyFrameworkBenchmark,  # Add here
    # ...
}
```

### 3. Test Integration

```bash
# Test your framework integration
python benchmark_runner.py --framework MyFramework --runs 1
```

## Troubleshooting

### Common Issues

#### "Module not found" errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

#### API timeout errors
```bash
# Increase timeout in config
export TIMEOUT_SECONDS=60

# Check API key
python -c "import openai; print(openai.api_key)"
```

#### Memory errors
```bash
# Reduce concurrent runs
python benchmark_runner.py --runs 3

# Use lighter frameworks
python benchmark_runner.py --framework LangGraph
```

#### Permission errors (Docker)
```bash
# Fix Docker permissions
sudo chmod 666 /var/run/docker.sock

# Or run with sudo
sudo docker-compose up
```

### Performance Optimization

#### Faster Benchmarks
```bash
# Use lighter model
export OPENAI_MODEL=gpt-3.5-turbo

# Reduce test runs
python benchmark_runner.py --runs 3

# Parallel execution
python benchmark_runner.py --parallel 4
```

#### Resource Limits
```bash
# Set memory limits
export MEMORY_LIMIT=2GB

# CPU limits
export CPU_LIMIT=2

# Disk space monitoring
df -h
```

### Getting Help

- **GitHub Issues**: [Report bugs](https://github.com/agenticallysh/agent-framework-benchmarks/issues)
- **Discord**: [Community support](https://discord.gg/agentically)
- **Documentation**: [Full docs](https://docs.agentically.sh)

## Production Deployment

### Load Balancer Setup

```nginx
# nginx.conf
upstream benchmark_servers {
    server benchmark1:8080;
    server benchmark2:8080;
    server benchmark3:8080;
}

server {
    listen 80;
    location / {
        proxy_pass http://benchmark_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Auto-scaling Configuration

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: framework-benchmarks
spec:
  replicas: 3
  selector:
    matchLabels:
      app: framework-benchmarks
  template:
    metadata:
      labels:
        app: framework-benchmarks
    spec:
      containers:
      - name: benchmarks
        image: agentically/framework-benchmarks:latest
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi" 
            cpu: "2000m"
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-key
```

### Monitoring Production

```yaml
# monitoring/alerts.yaml
groups:
- name: benchmark.rules
  rules:
  - alert: BenchmarkFailureRate
    expr: benchmark_failure_rate > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Benchmark failure rate is high"
      
  - alert: BenchmarkLatency
    expr: benchmark_response_time_p95 > 5000
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Benchmark response time is too high"
```

---

You're now ready to run comprehensive AI agent framework benchmarks! Start with the quick start guide and gradually explore advanced features as needed.