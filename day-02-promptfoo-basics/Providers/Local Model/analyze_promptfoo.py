import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
import sys
import os
from datetime import datetime

@dataclass
class ModelPerformance:
    success_rate: float
    total_tests: int
    total_cost: float
    avg_latency: float

class PromptfooAnalyzer:
    def __init__(self, json_file: str):
        self.data = self._load_json_file(json_file)
        self.results = self.data['results']['results']
        self.stats = self.data['results']['stats']
    
    def _load_json_file(self, file_path: str) -> Dict:
        """
        Attempt to load JSON file with different encodings and error handlers
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
        errors = ['strict', 'ignore', 'replace']
        
        for encoding in encodings:
            for error_handler in errors:
                try:
                    print(f"Attempting to read with {encoding} encoding and {error_handler} error handler...")
                    with open(file_path, 'r', encoding=encoding, errors=error_handler) as f:
                        content = f.read()
                        return json.loads(content)
                except (UnicodeDecodeError, UnicodeError):
                    continue
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON with {encoding} encoding: {str(e)}")
                    continue
                except Exception as e:
                    print(f"Unexpected error: {str(e)}")
                    continue
        
        raise ValueError(f"Could not read file {file_path} with any of the attempted encodings")

    def analyze_model_performance(self) -> Dict[str, ModelPerformance]:
        """Analyze performance metrics for each model/provider."""
        model_stats = defaultdict(lambda: {'successes': 0, 'total': 0, 'cost': 0.0, 'latency': []})
        
        for result in self.results:
            provider = result['provider']['id']
            model_stats[provider]['total'] += 1
            model_stats[provider]['successes'] += 1 if result['success'] else 0
            model_stats[provider]['cost'] += result.get('cost', 0)
            model_stats[provider]['latency'].append(result['latencyMs'])
            
        return {
            model: ModelPerformance(
                success_rate=stats['successes'] / stats['total'] * 100,
                total_tests=stats['total'],
                total_cost=stats['cost'],
                avg_latency=sum(stats['latency']) / len(stats['latency'])
            )
            for model, stats in model_stats.items()
        }

    def identify_problematic_patterns(self) -> List[Dict[str, Any]]:
        """Identify patterns in test failures and issues."""
        patterns = []
        
        # Group failures by error type
        error_patterns = defaultdict(list)
        for result in self.results:
            if not result['success']:
                error_patterns[result.get('error', 'Unknown error')].append(result)
        
        # Identify significant patterns
        for error, instances in error_patterns.items():
            if len(instances) >= 3:  # Consider it a pattern if it occurs 3 or more times
                patterns.append({
                    'type': 'error_pattern',
                    'error': error,
                    'frequency': len(instances),
                    'affected_tests': [i['testIdx'] for i in instances]
                })
                
        return patterns

    def analyze_cost_efficiency(self) -> List[Dict[str, Any]]:
        """Analyze cost efficiency and identify potential cost optimizations."""
        insights = []
        
        # Analyze cost per successful test by model
        cost_per_success = defaultdict(lambda: {'cost': 0.0, 'successes': 0})
        for result in self.results:
            provider = result['provider']['id']
            if result['success']:
                cost_per_success[provider]['cost'] += result.get('cost', 0)
                cost_per_success[provider]['successes'] += 1
        
        # Calculate and compare efficiency
        efficiencies = []
        for provider, stats in cost_per_success.items():
            if stats['successes'] > 0:
                efficiency = stats['cost'] / stats['successes']
                efficiencies.append((provider, efficiency))
        
        # Sort by efficiency
        efficiencies.sort(key=lambda x: x[1])
        
        if efficiencies:
            insights.append({
                'type': 'cost_efficiency',
                'most_efficient': efficiencies[0],
                'least_efficient': efficiencies[-1],
                'efficiency_range': efficiencies[-1][1] - efficiencies[0][1]
            })
            
        return insights

    def analyze_error_patterns(self) -> List[Dict[str, Any]]:
        """Analyze error patterns and provide detailed insights."""
        error_patterns = defaultdict(list)
        for result in self.results:
            if not result['success']:
                error = result.get('error', 'Unknown error')
                error_patterns[error].append({
                    'test_idx': result['testIdx'],
                    'provider': result['provider']['id'],
                    'vars': result.get('vars', {}),
                    'prompt': result.get('prompt', {}).get('raw', '')
                })
        
        insights = []
        for error, instances in error_patterns.items():
            if len(instances) >= 3:
                affected_models = set(i['provider'] for i in instances)
                affected_prompts = set(i['prompt'] for i in instances)
                insights.append({
                    'error': error,
                    'frequency': len(instances),
                    'affected_models': list(affected_models),
                    'affected_prompts': list(affected_prompts),
                    'example_vars': instances[0]['vars']
                })
        
        return insights

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate specific recommendations based on the analysis."""
        recommendations = []
        
        # Analyze success rates
        if self.stats['successes'] / (self.stats['successes'] + self.stats['failures']) < 0.5:
            recommendations.append({
                'category': 'Success Rate',
                'severity': 'High',
                'finding': 'Overall success rate is below 50%',
                'impact': 'Low reliability of prompt responses across all models',
                'actions': [
                    'Review and refine test assertions for potential over-strictness',
                    'Analyze successful cases to identify patterns that work',
                    'Consider implementing prompt templates for consistent output formatting'
                ]
            })

        # Analyze cost efficiency
        model_costs = defaultdict(float)
        model_successes = defaultdict(int)
        for result in self.results:
            provider = result['provider']['id']
            model_costs[provider] += result.get('cost', 0)
            if result['success']:
                model_successes[provider] += 1
        
        # Cost efficiency recommendations
        cost_per_success = {
            model: (cost / model_successes[model] if model_successes[model] > 0 else float('inf'))
            for model, cost in model_costs.items()
        }
        if len(cost_per_success) > 1:
            most_efficient = min(cost_per_success.items(), key=lambda x: x[1])
            least_efficient = max(cost_per_success.items(), key=lambda x: x[1])
            if least_efficient[1] > most_efficient[1] * 2:
                recommendations.append({
                    'category': 'Cost Optimization',
                    'severity': 'Medium',
                    'finding': f'{least_efficient[0]} is significantly more expensive per successful test',
                    'impact': 'Higher operational costs without proportional quality improvement',
                    'actions': [
                        f'Consider reducing usage of {least_efficient[0]} for cost optimization',
                        f'Investigate what makes {most_efficient[0]} more cost-effective',
                        'Implement cost monitoring and alerting'
                    ]
                })

        # Analyze error patterns
        error_patterns = self.analyze_error_patterns()
        for pattern in error_patterns:
            if len(pattern['affected_models']) == len(model_costs):  # All models affected
                recommendations.append({
                    'category': 'Error Pattern',
                    'severity': 'High',
                    'finding': f'Systematic error across all models: {pattern["error"]}',
                    'impact': 'Consistent failure pattern affecting all providers',
                    'actions': [
                        'Review and revise prompt structure for affected test cases',
                        'Verify test assertions match expected model capabilities',
                        'Consider implementing pre-processing for consistent input formatting'
                    ]
                })

        return recommendations

    def generate_detailed_report(self) -> str:
        """Generate a detailed report with analysis and recommendations."""
        report = []
        model_performance = self.analyze_model_performance()
        recommendations = self.generate_recommendations()
        
        # Header
        report.append("=== Promptfoo Analysis Report ===")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Executive Summary
        report.append("📊 EXECUTIVE SUMMARY")
        report.append("-----------------")
        success_rate = (self.stats['successes'] / (self.stats['successes'] + self.stats['failures']) * 100)
        report.append(f"Overall Success Rate: {success_rate:.1f}%")
        report.append(f"Total Tests Run: {self.stats['successes'] + self.stats['failures']}")
        report.append(f"Total Cost: ${sum(result.get('cost', 0) for result in self.results):.4f}\n")
        
        # Key Findings and Recommendations
        report.append("🔍 KEY FINDINGS & RECOMMENDATIONS")
        report.append("-------------------------------")
        for rec in recommendations:
            report.append(f"\n[{rec['severity']} Priority] {rec['category']}")
            report.append(f"Finding: {rec['finding']}")
            report.append(f"Impact: {rec['impact']}")
            report.append("Recommended Actions:")
            for action in rec['actions']:
                report.append(f"  • {action}")
        
        # Model Performance Comparison
        report.append("\n📈 MODEL PERFORMANCE COMPARISON")
        report.append("-----------------------------")
        for model, perf in model_performance.items():
            report.append(f"\n{model}:")
            report.append(f"  • Success Rate: {perf.success_rate:.1f}%")
            report.append(f"  • Tests Run: {perf.total_tests}")
            report.append(f"  • Total Cost: ${perf.total_cost:.4f}")
            report.append(f"  • Avg Latency: {perf.avg_latency:.1f}ms")
        
        # Error Analysis
        error_patterns = self.analyze_error_patterns()
        if error_patterns:
            report.append("\n❌ ERROR ANALYSIS")
            report.append("---------------")
            for pattern in error_patterns:
                report.append(f"\nError: {pattern['error']}")
                report.append(f"Frequency: {pattern['frequency']} occurrences")
                report.append(f"Affected Models: {', '.join(pattern['affected_models'])}")
                report.append("Example Test Variables:")
                for var, value in pattern['example_vars'].items():
                    report.append(f"  • {var}: {value}")
        
        return "\n".join(report)

def main():
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = 'results.json'
    
    try:
        analyzer = PromptfooAnalyzer(json_file)
        detailed_report = analyzer.generate_detailed_report()
        print(detailed_report)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 