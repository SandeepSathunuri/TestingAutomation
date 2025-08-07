#!/usr/bin/env python3
"""
Background processor for all data comparisons
Handles KPI, landing page widgets, and drillthrough widget comparisons in parallel
"""

import threading
import queue
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from kpistoreprocedures import Data, compare_kpi_data, read_kpi_from_excel
from widgetstoreprocedures import read_widget_values, fetch_db_widget_values, compare_widget_data, widget_sp_map
from drillthrough_db_handler import DrillthroughDBHandler
from dynamic_comparison_engine import DynamicComparisonEngine

class BackgroundProcessor:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=4)  # Increased to 4 threads
        
        # Initialize dynamic comparison engine
        self.dynamic_engine = DynamicComparisonEngine()
        print("🧠 Background processor initialized with dynamic comparison engine")
        self.active_tasks = {}
        self.completed_tasks = {}
        self.running = True
        
        # Enhanced features
        self.db_cache = {}  # Cache DB results
        self.sp_performance = {}  # Track SP performance
        self.batch_queue = queue.Queue()  # For batch processing
        self.cache_lock = threading.Lock()
        
        # Start background worker
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        
        # Start batch processor
        self.batch_thread = threading.Thread(target=self._batch_processor, daemon=True)
        self.batch_thread.start()
        
        print("🔄 Enhanced background processor started with 4 worker threads + batch processing")

    def _batch_processor(self):
        """Batch processor for handling multiple similar tasks efficiently"""
        print("🔄 Batch processor thread started")
        
        while self.running:
            try:
                # Simple batch processing - can be enhanced later
                time.sleep(1)  # Check every second
                
                # For now, just ensure the thread runs without errors
                # Actual batch processing logic can be added later
                
            except Exception as e:
                print(f"❌ Batch processor error: {e}")
                time.sleep(1)  # Prevent tight error loop

    def _worker(self):
        """Background worker that processes tasks from the queue"""
        while self.running:
            try:
                if not self.task_queue.empty():
                    task = self.task_queue.get(timeout=1)
                    task_id = task['id']
                    task_type = task['type']
                    
                    print(f"🔄 Background: Starting {task_type} (ID: {task_id})")
                    self.active_tasks[task_id] = task
                    
                    # Submit task to thread pool
                    future = self.executor.submit(self._execute_task, task)
                    
                    # Handle completion
                    def on_complete(fut):
                        try:
                            result = fut.result()
                            self.completed_tasks[task_id] = result
                            self.active_tasks.pop(task_id, None)
                            self.results_queue.put({
                                'id': task_id,
                                'type': task_type,
                                'result': result,
                                'status': 'completed'
                            })
                            print(f"✅ Background: Completed {task_type} (ID: {task_id})")
                        except Exception as e:
                            self.completed_tasks[task_id] = {'error': str(e)}
                            self.active_tasks.pop(task_id, None)
                            self.results_queue.put({
                                'id': task_id,
                                'type': task_type,
                                'error': str(e),
                                'status': 'failed'
                            })
                            print(f"❌ Background: Failed {task_type} (ID: {task_id}): {e}")
                    
                    future.add_done_callback(on_complete)
                else:
                    time.sleep(0.1)  # Brief pause when queue is empty
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Background worker error: {e}")

    def _execute_task(self, task):
        """Execute a specific task based on its type"""
        task_type = task['type']
        
        if task_type == 'kpi_comparison':
            return self._compare_kpi(task)
        elif task_type == 'landing_widget_comparison':
            return self._compare_landing_widgets(task)
        elif task_type == 'drillthrough_widget_comparison':
            return self._compare_drillthrough_widgets(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    def _compare_kpi(self, task):
        """Background KPI comparison"""
        try:
            excel_path = task['excel_path']
            output_path = task['output_path']
            is_drillthrough = task.get('is_drillthrough', False)
            extra_params = task.get('extra_params', {})
            
            # Read KPI from Excel
            excel_data = read_kpi_from_excel(excel_path)
            
            # Fetch DB data
            data = Data(is_drillthrough=is_drillthrough, extra_params=extra_params)
            db_kpis = data.fetch_db_kpi_values()
            
            # Compare and save
            compare_kpi_data(excel_data, db_kpis, output_path)
            
            return {
                'success': True,
                'output_path': output_path,
                'excel_count': len(excel_data),
                'db_count': len(db_kpis)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _compare_landing_widgets(self, task):
        """Enhanced background landing page widget comparison with dynamic engine"""
        try:
            excel_path = task['excel_path']
            output_path = task['output_path']
            
            print(f"🧠 Background landing widget comparison using dynamic engine...")
            
            # Try dynamic comparison first
            params = (2024, None, None, None, None, None, None)
            success = self.dynamic_engine.dynamic_compare_data(
                excel_path=excel_path,
                params=params,
                output_path=output_path
            )
            
            if success:
                file_size = os.path.getsize(output_path)
                return {
                    'success': True,
                    'output_path': output_path,
                    'method': 'dynamic_engine',
                    'file_size': file_size
                }
            else:
                # Fallback to legacy method
                print(f"🔄 Dynamic comparison failed, using legacy method...")
                return self._legacy_compare_landing_widgets(task)
            
        except Exception as e:
            print(f"❌ Dynamic landing widget comparison error: {str(e)}")
            # Fallback to legacy method
            return self._legacy_compare_landing_widgets(task)
    
    def _legacy_compare_landing_widgets(self, task):
        """Legacy background landing page widget comparison (fallback)"""
        try:
            excel_path = task['excel_path']
            output_path = task['output_path']
            
            print(f"🔄 Using legacy landing widget comparison method...")
            
            # Read widget values from Excel
            normalized_widget_map = {self._normalize(v): v for v in widget_sp_map.values()}
            excel_data = read_widget_values(excel_path, normalized_widget_map)
            
            # Fetch DB data
            params = (2024, None, None, None, None, None, None)
            db_data = fetch_db_widget_values(widget_sp_map, params)
            
            # Compare and save
            compare_widget_data(excel_path, db_data, output_path, widget_sp_map)
            
            return {
                'success': True,
                'output_path': output_path,
                'method': 'legacy',
                'excel_count': len(excel_data),
                'db_count': len(db_data)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'method': 'legacy'}

    def _compare_drillthrough_widgets(self, task):
        """Background drillthrough widget comparison"""
        try:
            excel_path = task['excel_path']
            widget_title = task['widget_title']
            submenu_selection = task['submenu_selection']
            output_path = task['output_path']
            
            # Use drillthrough handler
            db_handler = DrillthroughDBHandler()
            success = db_handler.compare_drillthrough_widgets(
                excel_path, widget_title, submenu_selection, output_path
            )
            
            return {
                'success': success,
                'output_path': output_path if success else None
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _normalize(self, name: str) -> str:
        """Normalize names for comparison"""
        return ''.join(name.lower().strip().replace('_', '').replace(' ', ''))

    # Public methods for submitting tasks
    
    def submit_kpi_comparison(self, excel_path, output_path, is_drillthrough=False, extra_params=None):
        """Submit KPI comparison task to background queue"""
        task_id = f"kpi_{int(time.time() * 1000)}"
        task = {
            'id': task_id,
            'type': 'kpi_comparison',
            'excel_path': excel_path,
            'output_path': output_path,
            'is_drillthrough': is_drillthrough,
            'extra_params': extra_params or {}
        }
        self.task_queue.put(task)
        print(f"📤 Queued KPI comparison: {os.path.basename(excel_path)} (ID: {task_id})")
        return task_id

    def submit_landing_widget_comparison(self, excel_path, output_path):
        """Submit landing page widget comparison task to background queue"""
        task_id = f"landing_{int(time.time() * 1000)}"
        task = {
            'id': task_id,
            'type': 'landing_widget_comparison',
            'excel_path': excel_path,
            'output_path': output_path
        }
        self.task_queue.put(task)
        print(f"📤 Queued landing widget comparison: {os.path.basename(excel_path)} (ID: {task_id})")
        return task_id

    def submit_drillthrough_widget_comparison(self, excel_path, widget_title, submenu_selection, output_path):
        """Submit drillthrough widget comparison task to background queue"""
        task_id = f"drill_{int(time.time() * 1000)}"
        task = {
            'id': task_id,
            'type': 'drillthrough_widget_comparison',
            'excel_path': excel_path,
            'widget_title': widget_title,
            'submenu_selection': submenu_selection,
            'output_path': output_path
        }
        self.task_queue.put(task)
        print(f"📤 Queued drillthrough comparison: {widget_title} -> {submenu_selection} (ID: {task_id})")
        return task_id

    # Status and result methods
    
    def get_status(self):
        """Get current processing status"""
        return {
            'queued': self.task_queue.qsize(),
            'active': len(self.active_tasks),
            'completed': len(self.completed_tasks)
        }

    def get_completed_results(self):
        """Get all completed results and clear the results queue"""
        results = []
        while not self.results_queue.empty():
            try:
                result = self.results_queue.get_nowait()
                results.append(result)
            except queue.Empty:
                break
        return results

    def wait_for_completion(self, timeout=300):
        """Wait for all tasks to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_status()
            if status['queued'] == 0 and status['active'] == 0:
                print("✅ All background tasks completed")
                return True
            
            print(f"🔄 Background status: {status['queued']} queued, {status['active']} active, {status['completed']} completed")
            time.sleep(2)
        
        print(f"⚠️ Timeout waiting for background tasks after {timeout}s")
        return False

    def shutdown(self):
        """Shutdown the background processor"""
        print("🔄 Shutting down background processor...")
        self.running = False
        self.executor.shutdown(wait=True)
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        print("✅ Background processor shutdown complete")

# Global instance
background_processor = BackgroundProcessor()

# Convenience functions
def submit_kpi_comparison_bg(excel_path, output_path, is_drillthrough=False, extra_params=None):
    """Submit KPI comparison to background processing"""
    return background_processor.submit_kpi_comparison(excel_path, output_path, is_drillthrough, extra_params)

def submit_landing_widget_comparison_bg(excel_path, output_path):
    """Submit landing widget comparison to background processing"""
    return background_processor.submit_landing_widget_comparison(excel_path, output_path)

def submit_drillthrough_widget_comparison_bg(excel_path, widget_title, submenu_selection, output_path):
    """Submit drillthrough widget comparison to background processing"""
    return background_processor.submit_drillthrough_widget_comparison(excel_path, widget_title, submenu_selection, output_path)

def get_background_status():
    """Get background processing status"""
    return background_processor.get_status()

def wait_for_all_comparisons(timeout=300):
    """Wait for all background comparisons to complete"""
    return background_processor.wait_for_completion(timeout)

def shutdown_background_processor():
    """Shutdown background processor"""
    background_processor.shutdown()