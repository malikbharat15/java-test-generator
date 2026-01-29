"""
Application Config Parser - Extract runtime configuration

Parses application.yml, application.properties, and application-{profile}.yml
to extract runtime settings needed for smoke test generation.

Key extractions:
- Server port and context path (for REST endpoint base URLs)
- Database configuration (connection details, JPA settings)
- Kafka broker settings (bootstrap servers, topics)
- Spring profiles (dev, test, prod)
- Actuator endpoints (health check URLs)
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ApplicationConfig:
    """Parsed application configuration"""
    server_port: int = 8080
    context_path: str = ""
    profiles: List[str] = field(default_factory=list)
    
    # Database
    datasource_url: Optional[str] = None
    datasource_driver: Optional[str] = None
    jpa_dialect: Optional[str] = None
    
    # Kafka
    kafka_bootstrap_servers: Optional[str] = None
    kafka_consumer_group: Optional[str] = None
    
    # Actuator
    actuator_base_path: str = "/actuator"
    actuator_enabled: bool = False
    
    # Custom properties
    custom_properties: Dict = field(default_factory=dict)
    
    # Source files
    config_files: List[str] = field(default_factory=list)


class ApplicationConfigParser:
    """
    Parses Spring Boot application.yml and application.properties files.
    
    Handles:
    - YAML and properties format
    - Multiple profiles (application-dev.yml, application-prod.yml)
    - Property placeholders (${VAR:default})
    - Nested properties (spring.datasource.url)
    """
    
    def __init__(self):
        self.config = ApplicationConfig()
    
    def parse(self, repo_path: str) -> ApplicationConfig:
        """
        Parse application configuration from repository.
        
        Args:
            repo_path: Path to Java repository
            
        Returns:
            ApplicationConfig with extracted settings
        """
        repo = Path(repo_path)
        
        print(f"\n📄 Parsing application configuration from: {repo_path}")
        
        # Find all application config files
        config_files = []
        
        # Search in src/main/resources
        resources_dirs = list(repo.rglob("src/main/resources"))
        
        for resources_dir in resources_dirs:
            # YAML files
            config_files.extend(resources_dir.glob("application*.yml"))
            config_files.extend(resources_dir.glob("application*.yaml"))
            
            # Properties files
            config_files.extend(resources_dir.glob("application*.properties"))
        
        print(f"   Found {len(config_files)} config files")
        
        # Parse each config file
        for config_file in config_files:
            self.config.config_files.append(str(config_file))
            
            if config_file.suffix in ['.yml', '.yaml']:
                self._parse_yaml_file(config_file)
            elif config_file.suffix == '.properties':
                self._parse_properties_file(config_file)
        
        self._print_summary()
        
        return self.config
    
    def _parse_yaml_file(self, file_path: Path):
        """Parse YAML configuration file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                return
            
            # Extract profile from filename
            filename = file_path.stem  # application-dev.yml -> application-dev
            if '-' in filename:
                profile = filename.split('-', 1)[1]
                if profile not in self.config.profiles:
                    self.config.profiles.append(profile)
            
            # Parse server config
            if 'server' in data:
                server = data['server']
                if 'port' in server:
                    self.config.server_port = int(server['port'])
                if 'servlet' in server and 'context-path' in server['servlet']:
                    self.config.context_path = server['servlet']['context-path']
                elif 'context-path' in server:
                    self.config.context_path = server['context-path']
            
            # Parse Spring config
            if 'spring' in data:
                spring = data['spring']
                
                # Datasource
                if 'datasource' in spring:
                    ds = spring['datasource']
                    self.config.datasource_url = ds.get('url')
                    self.config.datasource_driver = ds.get('driver-class-name')
                
                # JPA
                if 'jpa' in spring:
                    jpa = spring['jpa']
                    if 'properties' in jpa and 'hibernate' in jpa['properties']:
                        self.config.jpa_dialect = jpa['properties']['hibernate'].get('dialect')
                    elif 'database-platform' in jpa:
                        self.config.jpa_dialect = jpa['database-platform']
                
                # Kafka
                if 'kafka' in spring:
                    kafka = spring['kafka']
                    self.config.kafka_bootstrap_servers = kafka.get('bootstrap-servers')
                    if 'consumer' in kafka:
                        self.config.kafka_consumer_group = kafka['consumer'].get('group-id')
            
            # Parse management/actuator config
            if 'management' in data:
                mgmt = data['management']
                self.config.actuator_enabled = True
                
                if 'endpoints' in mgmt and 'web' in mgmt['endpoints']:
                    web = mgmt['endpoints']['web']
                    if 'base-path' in web:
                        self.config.actuator_base_path = web['base-path']
            
            # Store all other properties as custom
            self.config.custom_properties.update(self._flatten_dict(data))
            
        except Exception as e:
            print(f"   ⚠️  Could not parse {file_path.name}: {e}")
    
    def _parse_properties_file(self, file_path: Path):
        """Parse properties configuration file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#') or line.startswith('!'):
                    continue
                
                # Parse key=value
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Server port
                    if key == 'server.port':
                        self.config.server_port = int(value)
                    
                    # Context path
                    elif key in ['server.servlet.context-path', 'server.context-path']:
                        self.config.context_path = value
                    
                    # Datasource
                    elif key == 'spring.datasource.url':
                        self.config.datasource_url = value
                    elif key == 'spring.datasource.driver-class-name':
                        self.config.datasource_driver = value
                    
                    # Kafka
                    elif key == 'spring.kafka.bootstrap-servers':
                        self.config.kafka_bootstrap_servers = value
                    elif key == 'spring.kafka.consumer.group-id':
                        self.config.kafka_consumer_group = value
                    
                    # Actuator
                    elif key.startswith('management.endpoints'):
                        self.config.actuator_enabled = True
                        if key == 'management.endpoints.web.base-path':
                            self.config.actuator_base_path = value
                    
                    # Store all properties
                    self.config.custom_properties[key] = value
                    
        except Exception as e:
            print(f"   ⚠️  Could not parse {file_path.name}: {e}")
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """Flatten nested dictionary to dot notation"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _print_summary(self):
        """Print parsed configuration summary"""
        print(f"\n   ✅ Application Configuration:")
        print(f"      Server: localhost:{self.config.server_port}{self.config.context_path}")
        
        if self.config.profiles:
            print(f"      Profiles: {', '.join(self.config.profiles)}")
        
        if self.config.datasource_url:
            print(f"      Database: {self.config.datasource_url}")
        
        if self.config.kafka_bootstrap_servers:
            print(f"      Kafka: {self.config.kafka_bootstrap_servers}")
        
        if self.config.actuator_enabled:
            print(f"      Actuator: {self.config.actuator_base_path}")
    
    def to_dict(self) -> Dict:
        """Export configuration as dictionary"""
        return {
            'server': {
                'port': self.config.server_port,
                'context_path': self.config.context_path
            },
            'profiles': self.config.profiles,
            'datasource': {
                'url': self.config.datasource_url,
                'driver': self.config.datasource_driver,
                'jpa_dialect': self.config.jpa_dialect
            },
            'kafka': {
                'bootstrap_servers': self.config.kafka_bootstrap_servers,
                'consumer_group': self.config.kafka_consumer_group
            },
            'actuator': {
                'enabled': self.config.actuator_enabled,
                'base_path': self.config.actuator_base_path
            },
            'config_files': self.config.config_files,
            'custom_properties': dict(list(self.config.custom_properties.items())[:20])  # Top 20 only
        }
    
    def export_json(self, output_path: str):
        """Export configuration to JSON file"""
        Path(output_path).write_text(json.dumps(self.to_dict(), indent=2))
        print(f"💾 Exported application config to: {output_path}")
