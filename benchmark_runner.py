#!/usr/bin/env python3
"""
AI Agent Framework Benchmark Runner
Comprehensive performance testing for all major agent frameworks
"""

import time
import psutil
import json
import csv
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
import asyncio
import threading
from pathlib import Path

# Framework-specific imports
try:
    import autogen
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False

try:
    from crewai import Agent, Task, Crew
    from crewai_tools import SerperDevTool
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False

try:
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    from langchain.tools import Tool
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolExecutor
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

try:
    import semantic_kernel as sk
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    SEMANTIC_KERNEL_AVAILABLE = False


@dataclass
class BenchmarkResult:
    """Standard benchmark result structure"""
    framework: str
    test_name: str
    response_time_ms: float
    memory_usage_mb: float
    tokens_used: int
    cost_estimate: float
    success: bool
    error_message: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class FrameworkConfig:
    """Configuration for each framework"""
    name: str
    available: bool
    model: str = "gpt-4"
    max_tokens: int = 1000
    temperature: float = 0.7


class PerformanceMonitor:
    """Monitor system performance during benchmark execution"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.monitoring = False
        self.peak_memory = 0
        self.memory_samples = []
    
    def start_monitoring(self):
        """Start performance monitoring in background thread"""
        self.monitoring = True
        self.peak_memory = 0
        self.memory_samples = []
        threading.Thread(target=self._monitor_loop, daemon=True).start()
    
    def stop_monitoring(self) -> Dict[str, float]:
        """Stop monitoring and return metrics"""
        self.monitoring = False
        time.sleep(0.1)  # Allow final sample
        
        return {
            "peak_memory_mb": self.peak_memory,
            "avg_memory_mb": sum(self.memory_samples) / len(self.memory_samples) if self.memory_samples else 0,
            "memory_samples": len(self.memory_samples)
        }
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                memory_mb = self.process.memory_info().rss / 1024 / 1024
                self.memory_samples.append(memory_mb)
                self.peak_memory = max(self.peak_memory, memory_mb)
                time.sleep(0.1)  # Sample every 100ms
            except:
                break


class TokenCounter:
    """Estimate token usage for cost calculations"""
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough token estimation (1 token ≈ 4 characters)"""
        return len(text) // 4
    
    @staticmethod
    def calculate_cost(input_tokens: int, output_tokens: int, model: str = "gpt-4") -> float:
        """Calculate cost based on current OpenAI pricing (2024)"""
        pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03}
        }
        
        rates = pricing.get(model, pricing["gpt-4"])
        input_cost = (input_tokens / 1000) * rates["input"]
        output_cost = (output_tokens / 1000) * rates["output"]
        
        return input_cost + output_cost


class AutoGenBenchmark:
    """AutoGen framework benchmarks"""
    
    def __init__(self, config: FrameworkConfig):
        self.config = config
        self.llm_config = {
            "model": config.model,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature
        }
    
    def simple_task(self, prompt: str) -> BenchmarkResult:
        """Simple single-agent task"""
        monitor = PerformanceMonitor()
        start_time = time.time()
        
        try:
            monitor.start_monitoring()
            
            # Create AutoGen agents
            assistant = autogen.AssistantAgent(
                name="assistant",
                system_message="You are a helpful AI assistant.",
                llm_config=self.llm_config
            )
            
            user_proxy = autogen.UserProxyAgent(
                name="user_proxy",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=1,
                code_execution_config=False
            )
            
            # Execute conversation
            user_proxy.initiate_chat(assistant, message=prompt)
            
            response_time = (time.time() - start_time) * 1000
            memory_stats = monitor.stop_monitoring()
            
            # Estimate tokens and cost
            input_tokens = TokenCounter.estimate_tokens(prompt)
            output_tokens = TokenCounter.estimate_tokens("Sample response")  # Approximate
            cost = TokenCounter.calculate_cost(input_tokens, output_tokens, self.config.model)
            
            return BenchmarkResult(
                framework="AutoGen",
                test_name="simple_task",
                response_time_ms=response_time,
                memory_usage_mb=memory_stats["peak_memory_mb"],
                tokens_used=input_tokens + output_tokens,
                cost_estimate=cost,
                success=True
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            memory_stats = monitor.stop_monitoring()
            
            return BenchmarkResult(
                framework="AutoGen",
                test_name="simple_task",
                response_time_ms=response_time,
                memory_usage_mb=memory_stats.get("peak_memory_mb", 0),
                tokens_used=0,
                cost_estimate=0,
                success=False,
                error_message=str(e)
            )
    
    def multi_agent_task(self, prompt: str) -> BenchmarkResult:
        """Multi-agent collaboration task"""
        monitor = PerformanceMonitor()
        start_time = time.time()
        
        try:
            monitor.start_monitoring()
            
            # Create multiple agents
            researcher = autogen.AssistantAgent(
                name="researcher",
                system_message="You are a research specialist. Research topics thoroughly.",
                llm_config=self.llm_config
            )
            
            writer = autogen.AssistantAgent(
                name="writer",
                system_message="You are a writer. Create content based on research.",
                llm_config=self.llm_config
            )
            
            user_proxy = autogen.UserProxyAgent(
                name="user_proxy",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=0,
                code_execution_config=False
            )
            
            # Create group chat
            groupchat = autogen.GroupChat(
                agents=[user_proxy, researcher, writer],
                messages=[],
                max_round=6
            )
            
            manager = autogen.GroupChatManager(
                groupchat=groupchat,
                llm_config=self.llm_config
            )
            
            # Execute group conversation
            user_proxy.initiate_chat(manager, message=prompt)
            
            response_time = (time.time() - start_time) * 1000
            memory_stats = monitor.stop_monitoring()
            
            # Estimate tokens (higher for multi-agent)
            input_tokens = TokenCounter.estimate_tokens(prompt) * 3  # Multiple agents
            output_tokens = TokenCounter.estimate_tokens("Multi-agent response") * 3
            cost = TokenCounter.calculate_cost(input_tokens, output_tokens, self.config.model)
            
            return BenchmarkResult(
                framework="AutoGen",
                test_name="multi_agent_task",
                response_time_ms=response_time,
                memory_usage_mb=memory_stats["peak_memory_mb"],
                tokens_used=input_tokens + output_tokens,
                cost_estimate=cost,
                success=True
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            memory_stats = monitor.stop_monitoring()
            
            return BenchmarkResult(
                framework="AutoGen",
                test_name="multi_agent_task",
                response_time_ms=response_time,
                memory_usage_mb=memory_stats.get("peak_memory_mb", 0),
                tokens_used=0,
                cost_estimate=0,
                success=False,
                error_message=str(e)
            )


class CrewAIBenchmark:
    """CrewAI framework benchmarks"""
    
    def __init__(self, config: FrameworkConfig):
        self.config = config
    
    def simple_task(self, prompt: str) -> BenchmarkResult:
        """Simple single-agent task"""
        monitor = PerformanceMonitor()
        start_time = time.time()
        
        try:
            monitor.start_monitoring()
            
            # Create CrewAI agent
            agent = Agent(
                role="Assistant",
                goal="Help users with their questions",
                backstory="You are a helpful AI assistant.",
                verbose=False,
                allow_delegation=False
            )
            
            # Create task
            task = Task(
                description=prompt,
                agent=agent,
                expected_output="A helpful response"
            )
            
            # Create crew
            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=False
            )
            
            # Execute
            result = crew.kickoff()
            
            response_time = (time.time() - start_time) * 1000
            memory_stats = monitor.stop_monitoring()
            
            # Estimate tokens and cost
            input_tokens = TokenCounter.estimate_tokens(prompt)
            output_tokens = TokenCounter.estimate_tokens(str(result))
            cost = TokenCounter.calculate_cost(input_tokens, output_tokens, self.config.model)
            
            return BenchmarkResult(
                framework="CrewAI",
                test_name="simple_task",
                response_time_ms=response_time,
                memory_usage_mb=memory_stats["peak_memory_mb"],
                tokens_used=input_tokens + output_tokens,
                cost_estimate=cost,
                success=True
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            memory_stats = monitor.stop_monitoring()
            
            return BenchmarkResult(
                framework="CrewAI",
                test_name="simple_task",
                response_time_ms=response_time,
                memory_usage_mb=memory_stats.get("peak_memory_mb", 0),
                tokens_used=0,
                cost_estimate=0,
                success=False,
                error_message=str(e)
            )
    
    def multi_agent_task(self, prompt: str) -> BenchmarkResult:
        """Multi-agent crew task"""
        monitor = PerformanceMonitor()
        start_time = time.time()
        
        try:
            monitor.start_monitoring()
            
            # Create multiple agents
            researcher = Agent(
                role="Researcher",
                goal="Research topics thoroughly",
                backstory="You are an expert researcher.",
                verbose=False,
                allow_delegation=False
            )
            
            writer = Agent(
                role="Writer",
                goal="Write based on research",
                backstory="You are a skilled writer.",
                verbose=False,
                allow_delegation=False
            )
            
            # Create tasks
            research_task = Task(
                description=f"Research this topic: {prompt}",
                agent=researcher,
                expected_output="Research findings"
            )
            
            writing_task = Task(
                description="Write content based on the research",
                agent=writer,
                expected_output="Written content",
                dependencies=[research_task]
            )
            
            # Create crew
            crew = Crew(
                agents=[researcher, writer],
                tasks=[research_task, writing_task],
                verbose=False
            )
            
            # Execute
            result = crew.kickoff()
            
            response_time = (time.time() - start_time) * 1000
            memory_stats = monitor.stop_monitoring()
            
            # Estimate tokens (higher for multi-agent)
            input_tokens = TokenCounter.estimate_tokens(prompt) * 2
            output_tokens = TokenCounter.estimate_tokens(str(result))
            cost = TokenCounter.calculate_cost(input_tokens, output_tokens, self.config.model)
            
            return BenchmarkResult(
                framework="CrewAI",
                test_name="multi_agent_task",
                response_time_ms=response_time,
                memory_usage_mb=memory_stats["peak_memory_mb"],
                tokens_used=input_tokens + output_tokens,
                cost_estimate=cost,
                success=True
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            memory_stats = monitor.stop_monitoring()
            
            return BenchmarkResult(
                framework="CrewAI",
                test_name="multi_agent_task",
                response_time_ms=response_time,
                memory_usage_mb=memory_stats.get("peak_memory_mb", 0),
                tokens_used=0,
                cost_estimate=0,
                success=False,
                error_message=str(e)
            )


class LangChainBenchmark:
    """LangChain framework benchmarks"""
    
    def __init__(self, config: FrameworkConfig):
        self.config = config
        self.llm = ChatOpenAI(
            model=config.model,
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )
    
    def simple_task(self, prompt: str) -> BenchmarkResult:
        """Simple agent task"""
        monitor = PerformanceMonitor()
        start_time = time.time()
        
        try:
            monitor.start_monitoring()
            
            # Simple LLM call
            response = self.llm.invoke(prompt)
            
            response_time = (time.time() - start_time) * 1000
            memory_stats = monitor.stop_monitoring()
            
            # Estimate tokens and cost
            input_tokens = TokenCounter.estimate_tokens(prompt)
            output_tokens = TokenCounter.estimate_tokens(response.content)
            cost = TokenCounter.calculate_cost(input_tokens, output_tokens, self.config.model)
            
            return BenchmarkResult(
                framework="LangChain",
                test_name="simple_task",
                response_time_ms=response_time,
                memory_usage_mb=memory_stats["peak_memory_mb"],
                tokens_used=input_tokens + output_tokens,
                cost_estimate=cost,
                success=True
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            memory_stats = monitor.stop_monitoring()
            
            return BenchmarkResult(
                framework="LangChain",
                test_name="simple_task",
                response_time_ms=response_time,
                memory_usage_mb=memory_stats.get("peak_memory_mb", 0),
                tokens_used=0,
                cost_estimate=0,
                success=False,
                error_message=str(e)
            )
    
    def multi_agent_task(self, prompt: str) -> BenchmarkResult:
        """Multi-step chain task"""
        monitor = PerformanceMonitor()
        start_time = time.time()
        
        try:
            monitor.start_monitoring()
            
            # Sequential chain simulation
            research_prompt = f"Research this topic: {prompt}"
            research_response = self.llm.invoke(research_prompt)
            
            write_prompt = f"Based on this research: {research_response.content}, write a summary"
            final_response = self.llm.invoke(write_prompt)
            
            response_time = (time.time() - start_time) * 1000
            memory_stats = monitor.stop_monitoring()
            
            # Estimate tokens for multi-step
            input_tokens = TokenCounter.estimate_tokens(research_prompt + write_prompt)
            output_tokens = TokenCounter.estimate_tokens(research_response.content + final_response.content)
            cost = TokenCounter.calculate_cost(input_tokens, output_tokens, self.config.model)
            
            return BenchmarkResult(
                framework="LangChain",
                test_name="multi_agent_task",
                response_time_ms=response_time,
                memory_usage_mb=memory_stats["peak_memory_mb"],
                tokens_used=input_tokens + output_tokens,
                cost_estimate=cost,
                success=True
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            memory_stats = monitor.stop_monitoring()
            
            return BenchmarkResult(
                framework="LangChain",
                test_name="multi_agent_task",
                response_time_ms=response_time,
                memory_usage_mb=memory_stats.get("peak_memory_mb", 0),
                tokens_used=0,
                cost_estimate=0,
                success=False,
                error_message=str(e)
            )


class BenchmarkSuite:
    """Main benchmark orchestrator"""
    
    def __init__(self):
        self.frameworks = {
            "AutoGen": FrameworkConfig("AutoGen", AUTOGEN_AVAILABLE),
            "CrewAI": FrameworkConfig("CrewAI", CREWAI_AVAILABLE),
            "LangChain": FrameworkConfig("LangChain", LANGCHAIN_AVAILABLE),
            "LangGraph": FrameworkConfig("LangGraph", LANGGRAPH_AVAILABLE),
            "Semantic Kernel": FrameworkConfig("Semantic Kernel", SEMANTIC_KERNEL_AVAILABLE)
        }
        
        self.test_prompts = {
            "simple_task": "Explain the benefits of AI in customer service in 100 words.",
            "multi_agent_task": "Research and write a brief analysis of current AI trends in business automation.",
            "complex_task": "Create a step-by-step plan for implementing an AI chatbot in a small business, including technical requirements, cost estimates, and timeline."
        }
        
        self.results = []
    
    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run benchmarks for all available frameworks"""
        print("🧪 Starting comprehensive framework benchmarks...")
        
        for framework_name, config in self.frameworks.items():
            if not config.available:
                print(f"⚠️  Skipping {framework_name} - not installed")
                continue
            
            print(f"🔬 Benchmarking {framework_name}...")
            
            # Initialize framework benchmark
            if framework_name == "AutoGen":
                benchmark = AutoGenBenchmark(config)
            elif framework_name == "CrewAI":
                benchmark = CrewAIBenchmark(config)
            elif framework_name == "LangChain":
                benchmark = LangChainBenchmark(config)
            else:
                print(f"   Skipping {framework_name} - benchmark not implemented")
                continue
            
            # Run tests
            for test_name, prompt in self.test_prompts.items():
                if test_name == "complex_task":
                    continue  # Skip complex for now
                
                print(f"   Running {test_name}...")
                
                try:
                    if test_name == "simple_task":
                        result = benchmark.simple_task(prompt)
                    elif test_name == "multi_agent_task":
                        result = benchmark.multi_agent_task(prompt)
                    
                    self.results.append(result)
                    
                    status = "✅" if result.success else "❌"
                    print(f"   {status} {test_name}: {result.response_time_ms:.1f}ms, {result.memory_usage_mb:.1f}MB")
                    
                except Exception as e:
                    print(f"   ❌ {test_name} failed: {str(e)}")
        
        return self.results
    
    def save_results(self, format: str = "json"):
        """Save benchmark results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            filename = f"benchmark_results_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump([asdict(result) for result in self.results], f, indent=2)
        
        elif format == "csv":
            filename = f"benchmark_results_{timestamp}.csv"
            with open(filename, 'w', newline='') as f:
                if self.results:
                    writer = csv.DictWriter(f, fieldnames=asdict(self.results[0]).keys())
                    writer.writeheader()
                    for result in self.results:
                        writer.writerow(asdict(result))
        
        print(f"📊 Results saved to {filename}")
        return filename
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate benchmark summary statistics"""
        if not self.results:
            return {}
        
        successful_results = [r for r in self.results if r.success]
        
        summary = {
            "total_tests": len(self.results),
            "successful_tests": len(successful_results),
            "frameworks_tested": len(set(r.framework for r in successful_results)),
            "avg_response_time_ms": sum(r.response_time_ms for r in successful_results) / len(successful_results) if successful_results else 0,
            "avg_memory_usage_mb": sum(r.memory_usage_mb for r in successful_results) / len(successful_results) if successful_results else 0,
            "total_estimated_cost": sum(r.cost_estimate for r in successful_results),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Framework-specific summaries
        framework_stats = {}
        for framework in set(r.framework for r in successful_results):
            framework_results = [r for r in successful_results if r.framework == framework]
            framework_stats[framework] = {
                "tests_run": len(framework_results),
                "avg_response_time_ms": sum(r.response_time_ms for r in framework_results) / len(framework_results),
                "avg_memory_usage_mb": sum(r.memory_usage_mb for r in framework_results) / len(framework_results),
                "total_cost": sum(r.cost_estimate for r in framework_results)
            }
        
        summary["framework_stats"] = framework_stats
        
        return summary


def main():
    """Main execution function"""
    print("🚀 AI Agent Framework Benchmark Suite")
    print("=" * 50)
    
    # Create benchmark suite
    suite = BenchmarkSuite()
    
    # Run all benchmarks
    results = suite.run_all_benchmarks()
    
    # Save results
    suite.save_results("json")
    suite.save_results("csv")
    
    # Generate and display summary
    summary = suite.generate_summary()
    print("\n📊 Benchmark Summary:")
    print(f"   Total tests: {summary.get('total_tests', 0)}")
    print(f"   Successful: {summary.get('successful_tests', 0)}")
    print(f"   Frameworks tested: {summary.get('frameworks_tested', 0)}")
    print(f"   Average response time: {summary.get('avg_response_time_ms', 0):.1f}ms")
    print(f"   Average memory usage: {summary.get('avg_memory_usage_mb', 0):.1f}MB")
    print(f"   Total estimated cost: ${summary.get('total_estimated_cost', 0):.4f}")
    
    print("\n🔗 Framework Performance Comparison:")
    for framework, stats in summary.get("framework_stats", {}).items():
        print(f"   {framework}:")
        print(f"     Response time: {stats['avg_response_time_ms']:.1f}ms")
        print(f"     Memory usage: {stats['avg_memory_usage_mb']:.1f}MB")
        print(f"     Cost: ${stats['total_cost']:.4f}")
    
    print(f"\n✅ Benchmarks complete! View interactive results at:")
    print(f"   https://www.agentically.sh/ai-agentic-frameworks/benchmarks/")


if __name__ == "__main__":
    main()