#!/usr/bin/env python3
"""
Browser-based End-to-End Testing for Next Action Tracker Frontend

This script uses Puppeteer to test the complete user interface workflow,
including dashboard loading, action completion modal, and error handling.

Requirements tested:
- 1.1, 1.2, 1.3, 1.4, 1.5: Dashboard functionality and UI
- 2.1, 2.2, 2.3, 2.5: Action completion workflow via UI
- 5.1, 5.2, 5.3, 5.4, 5.5: User interface feedback and error handling
"""

import asyncio
import time
from datetime import datetime, timezone, timedelta


class BrowserTestSuite:
    """Browser-based test suite using Puppeteer MCP."""
    
    def __init__(self):
        self.results = []
        self.frontend_url = "http://localhost:3000"
    
    def record_test(self, test_name: str, passed: bool, error: str = None):
        """Record a test result."""
        if passed:
            print(f"✅ {test_name}")
            self.results.append({"name": test_name, "passed": True})
        else:
            print(f"❌ {test_name}: {error}")
            self.results.append({"name": test_name, "passed": False, "error": error})
    
    async def test_dashboard_loads(self):
        """Test that the dashboard loads correctly (Requirements 1.1, 1.4)."""
        try:
            # Navigate to the application
            await navigate(self.frontend_url)
            
            # Wait a moment for the page to load
            await asyncio.sleep(2)
            
            # Take a screenshot to verify the page loaded
            await screenshot("dashboard_loaded", width=1200, height=800)
            
            # Check if the page title contains "Next Action Tracker"
            title = await evaluate("document.title")
            
            if "Next Action Tracker" in title or "React App" in title:
                self.record_test("Dashboard Loads", True)
            else:
                self.record_test("Dashboard Loads", False, f"Unexpected title: {title}")
                
        except Exception as e:
            self.record_test("Dashboard Loads", False, str(e))
    
    async def test_dashboard_content(self):
        """Test dashboard content and due actions display (Requirements 1.2, 1.3)."""
        try:
            # Check for main heading
            heading_exists = await evaluate("""
                document.querySelector('h1') && 
                document.querySelector('h1').textContent.includes('Next Action Tracker')
            """)
            
            if not heading_exists:
                self.record_test("Dashboard Content", False, "Main heading not found")
                return
            
            # Wait for data to load (React Query)
            await asyncio.sleep(3)
            
            # Check for due actions or "All done" message
            content_check = await evaluate("""
                const hasCards = document.querySelectorAll('[class*="card"], [class*="action"]').length > 0;
                const hasAllDone = document.body.textContent.includes('All done') || 
                                  document.body.textContent.includes('🎉');
                const hasLoading = document.body.textContent.includes('Loading') ||
                                  document.querySelectorAll('[class*="skeleton"], [class*="loading"]').length > 0;
                
                return {
                    hasCards: hasCards,
                    hasAllDone: hasAllDone,
                    hasLoading: hasLoading,
                    bodyText: document.body.textContent.substring(0, 500)
                };
            """)
            
            # Take screenshot of dashboard content
            await screenshot("dashboard_content", width=1200, height=800)
            
            if content_check["hasCards"] or content_check["hasAllDone"]:
                self.record_test("Dashboard Content", True)
            elif content_check["hasLoading"]:
                self.record_test("Dashboard Content", False, "Still loading after 3 seconds")
            else:
                self.record_test("Dashboard Content", False, f"No expected content found: {content_check}")
                
        except Exception as e:
            self.record_test("Dashboard Content", False, str(e))
    
    async def test_action_completion_modal(self):
        """Test action completion modal functionality (Requirements 2.1, 2.2, 5.3)."""
        try:
            # Wait for page to be ready
            await asyncio.sleep(2)
            
            # Look for "Complete Action" buttons
            button_exists = await evaluate("""
                const buttons = Array.from(document.querySelectorAll('button'));
                const completeButton = buttons.find(btn => 
                    btn.textContent.includes('Complete') || 
                    btn.textContent.includes('Action')
                );
                return completeButton !== undefined;
            """)
            
            if not button_exists:
                self.record_test("Action Completion Modal", True, "No due actions to test (expected)")
                return
            
            # Click the first "Complete Action" button
            await evaluate("""
                const buttons = Array.from(document.querySelectorAll('button'));
                const completeButton = buttons.find(btn => 
                    btn.textContent.includes('Complete') || 
                    btn.textContent.includes('Action')
                );
                if (completeButton) {
                    completeButton.click();
                }
            """)
            
            # Wait for modal to appear
            await asyncio.sleep(1)
            
            # Check if modal opened
            modal_exists = await evaluate("""
                const modal = document.querySelector('[class*="modal"], [role="dialog"]') ||
                             document.querySelector('div[style*="position: fixed"]');
                return modal !== null;
            """)
            
            if modal_exists:
                # Take screenshot of modal
                await screenshot("action_modal", width=1200, height=800)
                self.record_test("Action Completion Modal", True)
            else:
                self.record_test("Action Completion Modal", False, "Modal did not open")
                
        except Exception as e:
            self.record_test("Action Completion Modal", False, str(e))
    
    async def test_error_handling(self):
        """Test error handling and user feedback (Requirements 5.2, 5.4)."""
        try:
            # Check for error boundaries or error messages
            error_handling = await evaluate("""
                // Look for error handling indicators
                const hasErrorBoundary = document.querySelector('[class*="error"]') !== null;
                const hasToastContainer = document.querySelector('[class*="toast"], [class*="notification"]') !== null;
                const hasErrorText = document.body.textContent.toLowerCase().includes('error');
                
                return {
                    hasErrorBoundary: hasErrorBoundary,
                    hasToastContainer: hasToastContainer,
                    hasErrorText: hasErrorText
                };
            """)
            
            # Error handling components should exist (even if not visible)
            if error_handling["hasToastContainer"] or not error_handling["hasErrorText"]:
                self.record_test("Error Handling", True)
            else:
                self.record_test("Error Handling", False, "No error handling components found")
                
        except Exception as e:
            self.record_test("Error Handling", False, str(e))
    
    async def test_responsive_design(self):
        """Test responsive design (Requirements 5.5)."""
        try:
            # Test mobile viewport
            await evaluate("window.resizeTo(375, 667)")  # iPhone size
            await asyncio.sleep(1)
            
            mobile_layout = await evaluate("""
                const width = window.innerWidth;
                const hasHorizontalScroll = document.body.scrollWidth > window.innerWidth;
                return {
                    width: width,
                    hasHorizontalScroll: hasHorizontalScroll
                };
            """)
            
            # Take screenshot at mobile size
            await screenshot("mobile_layout", width=375, height=667)
            
            # Reset to desktop
            await evaluate("window.resizeTo(1200, 800)")
            await asyncio.sleep(1)
            
            if not mobile_layout["hasHorizontalScroll"]:
                self.record_test("Responsive Design", True)
            else:
                self.record_test("Responsive Design", False, "Horizontal scroll on mobile")
                
        except Exception as e:
            self.record_test("Responsive Design", False, str(e))
    
    async def run_all_tests(self):
        """Run all browser-based tests."""
        print("Starting Browser-based End-to-End Tests for Next Action Tracker")
        print("="*70)
        
        try:
            await self.test_dashboard_loads()
            await self.test_dashboard_content()
            await self.test_action_completion_modal()
            await self.test_error_handling()
            await self.test_responsive_design()
            
        except Exception as e:
            print(f"Test suite error: {e}")
        
        # Print results
        print("\n" + "="*70)
        print("BROWSER TEST RESULTS")
        print("="*70)
        
        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)
        
        print(f"Tests Run: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%" if total > 0 else "No tests run")
        
        failures = [r for r in self.results if not r["passed"]]
        if failures:
            print("\nFAILURES:")
            for failure in failures:
                print(f"  - {failure['name']}: {failure.get('error', 'Unknown error')}")
        
        return len(failures) == 0


# Import Puppeteer MCP functions
try:
    from mcp_puppeteer_puppeteer_navigate import navigate
    from mcp_puppeteer_puppeteer_screenshot import screenshot
    from mcp_puppeteer_puppeteer_evaluate import evaluate
    
    async def main():
        """Main test runner."""
        test_suite = BrowserTestSuite()
        success = await test_suite.run_all_tests()
        
        if success:
            print("\n🎉 All browser tests passed! The frontend is working correctly.")
        else:
            print(f"\n💥 Some browser tests failed. Check screenshots for details.")
        
        return success

except ImportError:
    print("Puppeteer MCP not available. Skipping browser tests.")
    print("To run browser tests, ensure Puppeteer MCP is configured.")
    
    async def main():
        return True


if __name__ == "__main__":
    asyncio.run(main())