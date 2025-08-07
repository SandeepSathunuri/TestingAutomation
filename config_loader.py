#!/usr/bin/env python3
"""
Configuration Loader
====================
Utility to load and manage YAML configuration files
"""

import os
import yaml
from typing import Dict, Any, Optional
import logging

class ConfigLoader:
    """Load and manage YAML configuration files"""
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize the configuration loader
        
        Args:
            config_dir: Directory containing YAML configuration files
        """
        self.config_dir = config_dir
        self.configs = {}
        self.logger = logging.getLogger(__name__)
        
        # Ensure config directory exists
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            self.logger.info(f"Created config directory: {config_dir}")
    
    def load_config(self, config_name: str, reload: bool = False) -> Dict[str, Any]:
        """
        Load a specific configuration file
        
        Args:
            config_name: Name of the config file (without .yaml extension)
            reload: Force reload even if already cached
            
        Returns:
            Dictionary containing the configuration data
        """
        if config_name in self.configs and not reload:
            return self.configs[config_name]
        
        config_path = os.path.join(self.config_dir, f"{config_name}.yaml")
        
        if not os.path.exists(config_path):
            self.logger.error(f"Configuration file not found: {config_path}")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
                self.configs[config_name] = config_data
                self.logger.info(f"Loaded configuration: {config_name}")
                return config_data
        
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML file {config_path}: {str(e)}")
            return {}
        
        except Exception as e:
            self.logger.error(f"Error loading configuration {config_path}: {str(e)}")
            return {}
    
    def get_stored_procedures(self) -> Dict[str, Any]:
        """Get stored procedures configuration"""
        return self.load_config("stored_procedures")
    
    def get_drillthrough_filters(self) -> Dict[str, Any]:
        """Get drillthrough filters configuration"""
        return self.load_config("drillthrough_filters")
    
    def get_widget_mappings(self) -> Dict[str, Any]:
        """Get widget mappings configuration"""
        return self.load_config("widget_mappings")
    
    def get_dynamic_engine_config(self) -> Dict[str, Any]:
        """Get dynamic engine configuration"""
        return self.load_config("dynamic_engine_config")
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return self.load_config("database_config")
    
    def get_landing_page_widgets(self) -> Dict[str, str]:
        """Get landing page widget to SP mappings"""
        sp_config = self.get_stored_procedures()
        return sp_config.get("landing_page_widgets", {})
    
    def get_landing_page_kpis(self) -> Dict[str, str]:
        """Get landing page KPI to SP mappings"""
        sp_config = self.get_stored_procedures()
        return sp_config.get("landing_page_kpis", {})
    
    def get_drillthrough_kpis(self) -> Dict[str, str]:
        """Get drillthrough KPI to SP mappings"""
        sp_config = self.get_stored_procedures()
        return sp_config.get("drillthrough_kpis", {})
    
    def get_drillthrough_procedures(self, target: str) -> Dict[str, str]:
        """
        Get drillthrough procedures for a specific target
        
        Args:
            target: Target name (e.g., 'love_library', 'routledge_publications')
            
        Returns:
            Dictionary of procedure mappings for the target
        """
        sp_config = self.get_stored_procedures()
        drillthrough_procs = sp_config.get("drillthrough_procedures", {})
        return drillthrough_procs.get(target, {})
    
    def get_drillthrough_parameters(self, submenu: str) -> tuple:
        """
        Get drillthrough parameters for a specific submenu
        
        Args:
            submenu: Submenu name (e.g., 'Love Library', 'Routledge Publications')
            
        Returns:
            Tuple containing the parameters (year, month, store, state, channel, fromdate, todate)
        """
        filter_config = self.get_drillthrough_filters()
        params = filter_config.get("drillthrough_parameters", {}).get(submenu, {})
        
        # Convert to tuple format expected by the application
        if params:
            return (
                params.get("year", 2024),
                params.get("month"),
                params.get("store"),
                params.get("state"),
                params.get("channel"),
                params.get("fromdate"),
                params.get("todate")
            )
        
        # Return default parameters
        default_params = filter_config.get("default_parameters", {})
        return (
            default_params.get("year", 2024),
            default_params.get("month"),
            default_params.get("store"),
            default_params.get("state"),
            default_params.get("channel"),
            default_params.get("fromdate"),
            default_params.get("todate")
        )
    
    def get_kpi_parameters(self, kpi_type: str = "default") -> Dict[str, Any]:
        """
        Get KPI parameters in dictionary format
        
        Args:
            kpi_type: Type of KPI ('landing', 'drillthrough', or 'default')
            
        Returns:
            Dictionary containing KPI parameters
        """
        filter_config = self.get_drillthrough_filters()
        default_params = filter_config.get("default_parameters", {})
        
        return {
            "Year": default_params.get("year", 2024),
            "Month": default_params.get("month"),
            "Store": default_params.get("store"),
            "State": default_params.get("state"),
            "Channel": default_params.get("channel"),
            "FromDate": default_params.get("fromdate"),
            "ToDate": default_params.get("todate")
        }
    
    def get_store_mapping(self, store_name: str) -> Optional[str]:
        """
        Get store ID for a store name
        
        Args:
            store_name: Name of the store
            
        Returns:
            Store ID or None if not found
        """
        filter_config = self.get_drillthrough_filters()
        store_mappings = filter_config.get("store_mappings", {})
        return store_mappings.get(store_name)
    
    def get_widget_sp_map(self) -> Dict[str, str]:
        """Get the complete widget to stored procedure mapping"""
        return self.get_landing_page_widgets()
    
    def get_dynamic_engine_sps(self) -> list:
        """Get list of available stored procedures for dynamic engine"""
        sp_config = self.get_stored_procedures()
        return sp_config.get("dynamic_engine_sps", [])
    
    def get_pattern_mappings(self) -> Dict[str, Any]:
        """Get pattern recognition mappings for dynamic engine"""
        engine_config = self.get_dynamic_engine_config()
        return engine_config.get("pattern_recognition", {})
    
    def get_scoring_system(self) -> Dict[str, float]:
        """Get scoring system configuration for dynamic engine"""
        engine_config = self.get_dynamic_engine_config()
        return engine_config.get("scoring_system", {})
    
    def is_filter_supported(self, submenu: str) -> str:
        """
        Check if a submenu filter is supported
        
        Args:
            submenu: Submenu name
            
        Returns:
            Filter type ('store', 'brand', 'category', 'none', etc.)
        """
        filter_config = self.get_drillthrough_filters()
        supported_filters = filter_config.get("supported_filters", {})
        return supported_filters.get(submenu, "none")
    
    def validate_parameters(self, params: tuple) -> bool:
        """
        Validate parameters against configuration rules
        
        Args:
            params: Parameter tuple (year, month, store, state, channel, fromdate, todate)
            
        Returns:
            True if parameters are valid, False otherwise
        """
        filter_config = self.get_drillthrough_filters()
        validation_rules = filter_config.get("parameter_validation", {})
        
        if not params or len(params) != 7:
            return False
        
        year, month, store, state, channel, fromdate, todate = params
        
        # Validate year
        year_rules = validation_rules.get("year", {})
        if year is not None:
            if not isinstance(year, int):
                return False
            if year < year_rules.get("min", 2020) or year > year_rules.get("max", 2030):
                return False
        
        # Validate month
        month_rules = validation_rules.get("month", {})
        if month is not None:
            if not isinstance(month, int):
                return False
            if month < month_rules.get("min", 1) or month > month_rules.get("max", 12):
                return False
        
        # Validate store
        store_rules = validation_rules.get("store", {})
        if store is not None:
            if not isinstance(store, str):
                return False
            if len(store) > store_rules.get("max_length", 10):
                return False
        
        return True
    
    def reload_all_configs(self):
        """Reload all cached configurations"""
        self.logger.info("Reloading all configurations...")
        config_files = [
            "stored_procedures",
            "drillthrough_filters", 
            "widget_mappings",
            "dynamic_engine_config",
            "database_config"
        ]
        
        for config_name in config_files:
            self.load_config(config_name, reload=True)
        
        self.logger.info("All configurations reloaded")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of all loaded configurations"""
        summary = {
            "loaded_configs": list(self.configs.keys()),
            "config_files": [],
            "total_stored_procedures": 0,
            "total_drillthrough_targets": 0,
            "total_widget_mappings": 0
        }
        
        # Check for config files
        if os.path.exists(self.config_dir):
            config_files = [f for f in os.listdir(self.config_dir) if f.endswith('.yaml')]
            summary["config_files"] = config_files
        
        # Count stored procedures
        sp_config = self.get_stored_procedures()
        if sp_config:
            landing_widgets = len(sp_config.get("landing_page_widgets", {}))
            drillthrough_procs = sp_config.get("drillthrough_procedures", {})
            drillthrough_count = sum(len(procs) for procs in drillthrough_procs.values())
            summary["total_stored_procedures"] = landing_widgets + drillthrough_count
        
        # Count drillthrough targets
        filter_config = self.get_drillthrough_filters()
        if filter_config:
            summary["total_drillthrough_targets"] = len(filter_config.get("drillthrough_parameters", {}))
        
        # Count widget mappings
        widget_config = self.get_widget_mappings()
        if widget_config:
            widget_mappings = widget_config.get("widget_sheet_mappings", {})
            landing_count = len(widget_mappings.get("landing_page", {}))
            drillthrough_count = len(widget_mappings.get("drillthrough", {}))
            summary["total_widget_mappings"] = landing_count + drillthrough_count
        
        return summary

# Global configuration loader instance
config_loader = ConfigLoader()

# Convenience functions for easy access
def get_stored_procedures():
    """Get stored procedures configuration"""
    return config_loader.get_stored_procedures()

def get_drillthrough_filters():
    """Get drillthrough filters configuration"""
    return config_loader.get_drillthrough_filters()

def get_widget_mappings():
    """Get widget mappings configuration"""
    return config_loader.get_widget_mappings()

def get_dynamic_engine_config():
    """Get dynamic engine configuration"""
    return config_loader.get_dynamic_engine_config()

def get_database_config():
    """Get database configuration"""
    return config_loader.get_database_config()

def get_landing_page_kpis():
    """Get landing page KPI mappings"""
    return config_loader.get_landing_page_kpis()

def get_drillthrough_kpis():
    """Get drillthrough KPI mappings"""
    return config_loader.get_drillthrough_kpis()

if __name__ == "__main__":
    # Test the configuration loader
    loader = ConfigLoader()
    
    print("🔧 Configuration Loader Test")
    print("=" * 50)
    
    # Load and display summary
    summary = loader.get_config_summary()
    print(f"📁 Config files found: {len(summary['config_files'])}")
    print(f"📊 Loaded configs: {len(summary['loaded_configs'])}")
    print(f"🔧 Total stored procedures: {summary['total_stored_procedures']}")
    print(f"🎯 Total drillthrough targets: {summary['total_drillthrough_targets']}")
    print(f"🧩 Total widget mappings: {summary['total_widget_mappings']}")
    
    # Test specific configurations
    print(f"\n📋 Landing page widgets: {len(loader.get_landing_page_widgets())}")
    print(f"🔍 Love Library procedures: {len(loader.get_drillthrough_procedures('love_library'))}")
    print(f"🏪 Store mappings: {len(loader.get_drillthrough_filters().get('store_mappings', {}))}")
    
    print(f"\n✅ Configuration loader test completed!")