#!/usr/bin/env python3
"""
Performance Monitoring Script for Next Action Tracker

This script monitors the application performance and provides metrics
for database queries, API response times, and system resources.
"""

import asyncio
import time
import json
from datetime import datetime, timezone
from typing import Dict, List, Any
import aiohttp
import asyncpg


class PerformanceMonitor:
    """Monitor application performance metrics."""
    
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.db_url = "postgresql://nat_user:nat_password@localhost:5432/nat_dev"
        self.metrics = []
    
    async def test_api_performance(self) -> Dict[str, Any]:
        """Test API endpoint performance."""
        headers = {"X-Tenant-ID": "550e8400-e29b-41d4-a716-446655440000"}
        
        async with aiohttp.ClientSession() as session:
            # Test multiple requests to get average
            response_times = []
            
            for i in range(10):
                start_time = time.time()
                
                try:
                    async with session.get(f"{self.api_url}/api/v1/opportunities/due", headers=headers) as response:
                        if response.status == 200:
                            await response.json()
                            response_times.append(time.time() - start_time)
                        else:
                            print(f"API request failed with status {response.status}")
                except Exception as e:
                    print(f"API request failed: {e}")
            
            if response_times:
                return {
                    "avg_response_time": sum(response_times) / len(response_times),
                    "min_response_time": min(response_times),
                    "max_response_time": max(response_times),
                    "total_requests": len(response_times),
                    "success_rate": len(response_times) / 10 * 100
                }
            else:
                return {"error": "No successful API requests"}
    
    async def test_database_performance(self) -> Dict[str, Any]:
        """Test database query performance."""
        try:
            connection = await asyncpg.connect(self.db_url)
            
            # Test the critical due opportunities query
            tenant_id = "550e8400-e29b-41d4-a716-446655440000"
            query = """
                SELECT id, name, value, stage, next_action_at, next_action_details
                FROM opportunities
                WHERE tenant_id = $1
                  AND next_action_at IS NOT NULL
                  AND next_action_at <= NOW()
                ORDER BY next_action_at ASC
            """
            
            query_times = []
            
            for i in range(10):
                start_time = time.time()
                result = await connection.fetch(query, tenant_id)
                query_times.append(time.time() - start_time)
            
            # Test connection pool performance
            pool_start = time.time()
            pool = await asyncpg.create_pool(self.db_url, min_size=1, max_size=5)
            pool_creation_time = time.time() - pool_start
            
            await pool.close()
            await connection.close()
            
            return {
                "avg_query_time": sum(query_times) / len(query_times),
                "min_query_time": min(query_times),
                "max_query_time": max(query_times),
                "pool_creation_time": pool_creation_time,
                "result_count": len(result) if 'result' in locals() else 0
            }
            
        except Exception as e:
            return {"error": f"Database test failed: {e}"}
    
    async def test_concurrent_load(self) -> Dict[str, Any]:
        """Test performance under concurrent load."""
        headers = {"X-Tenant-ID": "550e8400-e29b-41d4-a716-446655440000"}
        
        async def make_request(session):
            start_time = time.time()
            try:
                async with session.get(f"{self.api_url}/api/v1/opportunities/due", headers=headers) as response:
                    if response.status == 200:
                        await response.json()
                        return time.time() - start_time
            except:
                pass
            return None
        
        async with aiohttp.ClientSession() as session:
            # Run 20 concurrent requests
            tasks = [make_request(session) for _ in range(20)]
            results = await asyncio.gather(*tasks)
            
            successful_requests = [r for r in results if r is not None]
            
            if successful_requests:
                return {
                    "concurrent_requests": 20,
                    "successful_requests": len(successful_requests),
                    "avg_response_time": sum(successful_requests) / len(successful_requests),
                    "max_response_time": max(successful_requests),
                    "success_rate": len(successful_requests) / 20 * 100
                }
            else:
                return {"error": "No successful concurrent requests"}
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics from the API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/metrics") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"Metrics endpoint returned {response.status}"}
        except Exception as e:
            return {"error": f"Failed to get system metrics: {e}"}
    
    async def run_performance_test(self) -> Dict[str, Any]:
        """Run complete performance test suite."""
        print("🚀 Starting Performance Test Suite")
        print("=" * 50)
        
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tests": {}
        }
        
        # API Performance Test
        print("Testing API Performance...")
        api_results = await self.test_api_performance()
        results["tests"]["api_performance"] = api_results
        
        if "error" not in api_results:
            print(f"✅ API Average Response Time: {api_results['avg_response_time']:.3f}s")
            print(f"✅ API Success Rate: {api_results['success_rate']:.1f}%")
        else:
            print(f"❌ API Test Failed: {api_results['error']}")
        
        # Database Performance Test
        print("\nTesting Database Performance...")
        db_results = await self.test_database_performance()
        results["tests"]["database_performance"] = db_results
        
        if "error" not in db_results:
            print(f"✅ DB Average Query Time: {db_results['avg_query_time']:.3f}s")
            print(f"✅ DB Pool Creation Time: {db_results['pool_creation_time']:.3f}s")
        else:
            print(f"❌ Database Test Failed: {db_results['error']}")
        
        # Concurrent Load Test
        print("\nTesting Concurrent Load...")
        load_results = await self.test_concurrent_load()
        results["tests"]["concurrent_load"] = load_results
        
        if "error" not in load_results:
            print(f"✅ Concurrent Success Rate: {load_results['success_rate']:.1f}%")
            print(f"✅ Concurrent Avg Response: {load_results['avg_response_time']:.3f}s")
        else:
            print(f"❌ Concurrent Load Test Failed: {load_results['error']}")
        
        # System Metrics
        print("\nGetting System Metrics...")
        system_results = await self.get_system_metrics()
        results["tests"]["system_metrics"] = system_results
        
        if "error" not in system_results:
            print(f"✅ System Status: {system_results.get('status', 'unknown')}")
            if "database" in system_results:
                db_info = system_results["database"]
                print(f"✅ DB Pool Size: {db_info.get('pool_size', 'unknown')}")
        else:
            print(f"❌ System Metrics Failed: {system_results['error']}")
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a performance report."""
        report = []
        report.append("NEXT ACTION TRACKER - PERFORMANCE REPORT")
        report.append("=" * 50)
        report.append(f"Test Date: {results['timestamp']}")
        report.append("")
        
        # Performance Summary
        api_perf = results["tests"].get("api_performance", {})
        db_perf = results["tests"].get("database_performance", {})
        load_perf = results["tests"].get("concurrent_load", {})
        
        if "avg_response_time" in api_perf:
            report.append("📊 PERFORMANCE SUMMARY")
            report.append("-" * 30)
            report.append(f"API Response Time: {api_perf['avg_response_time']:.3f}s (avg)")
            report.append(f"Database Query Time: {db_perf.get('avg_query_time', 'N/A'):.3f}s (avg)")
            report.append(f"Concurrent Load Success: {load_perf.get('success_rate', 'N/A'):.1f}%")
            report.append("")
        
        # Performance Thresholds
        report.append("🎯 PERFORMANCE ANALYSIS")
        report.append("-" * 30)
        
        if "avg_response_time" in api_perf:
            api_time = api_perf["avg_response_time"]
            if api_time < 0.1:
                report.append("✅ API Response Time: Excellent (<100ms)")
            elif api_time < 0.5:
                report.append("✅ API Response Time: Good (<500ms)")
            else:
                report.append("⚠️  API Response Time: Needs optimization (>500ms)")
        
        if "avg_query_time" in db_perf:
            db_time = db_perf["avg_query_time"]
            if db_time < 0.01:
                report.append("✅ Database Performance: Excellent (<10ms)")
            elif db_time < 0.05:
                report.append("✅ Database Performance: Good (<50ms)")
            else:
                report.append("⚠️  Database Performance: Needs optimization (>50ms)")
        
        if "success_rate" in load_perf:
            success_rate = load_perf["success_rate"]
            if success_rate >= 95:
                report.append("✅ Concurrent Load Handling: Excellent (>95%)")
            elif success_rate >= 90:
                report.append("✅ Concurrent Load Handling: Good (>90%)")
            else:
                report.append("⚠️  Concurrent Load Handling: Needs optimization (<90%)")
        
        report.append("")
        report.append("📋 DETAILED RESULTS")
        report.append("-" * 30)
        report.append(json.dumps(results, indent=2))
        
        return "\n".join(report)


async def main():
    """Main performance monitoring function."""
    monitor = PerformanceMonitor()
    
    try:
        results = await monitor.run_performance_test()
        
        # Generate and save report
        report = monitor.generate_report(results)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_report_{timestamp}.txt"
        
        with open(filename, "w") as f:
            f.write(report)
        
        print(f"\n📄 Performance report saved to: {filename}")
        
        # Print summary
        print("\n" + "=" * 50)
        print("PERFORMANCE TEST COMPLETE")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Performance monitoring failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())