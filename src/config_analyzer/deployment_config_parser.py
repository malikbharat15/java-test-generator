"""
Deployment Config Parser - Extract OCP/Kubernetes deployment configuration

Parses OpenShift (OCP) and Kubernetes manifests to extract:
- Application routes (base URLs for smoke tests hitting deployed apps)
- ConfigMaps (environment-specific configuration)
- Deployment topology (replicas, resources, health checks)
- Service definitions (ports, selectors)

Structure expected:
ocp/
  configs/
    base/
      config.yaml, deploy.yaml, kustomization.yaml, route.yaml, service.yaml
    overlays/
      dev-a/, qat-a/, uat-a/, prod-a/
        configmap.yaml, deploy.yaml, kustomization.yaml, overrides.yaml
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class DeploymentConfig:
    """Parsed deployment configuration"""
    deployment_platform: str = "none"  # "openshift", "kubernetes", "none"
    
    # Routes/Ingress (for smoke tests hitting deployed apps)
    routes: Dict[str, str] = field(default_factory=dict)  # {env: base_url}
    
    # Environments
    environments: List[str] = field(default_factory=list)  # ["dev-a", "qat-a", "uat-a", "prod-a"]
    
    # ConfigMaps per environment
    config_maps: Dict[str, Dict] = field(default_factory=dict)  # {env: {key: value}}
    
    # Health check endpoints
    health_endpoints: Dict[str, str] = field(default_factory=dict)  # {env: health_url}
    
    # Deployment config
    replicas: Dict[str, int] = field(default_factory=dict)  # {env: replica_count}
    
    # Config files found
    config_files: List[str] = field(default_factory=list)


class DeploymentConfigParser:
    """
    Parses OpenShift/Kubernetes deployment configurations.
    
    Use cases:
    1. Generate smoke tests that hit DEPLOYED applications (not @SpringBootTest)
    2. Extract base URLs from routes for each environment
    3. Understand deployment topology (how many instances, health checks)
    4. Get environment-specific config (DB URLs, Kafka brokers per env)
    """
    
    def __init__(self):
        self.config = DeploymentConfig()
    
    def parse(self, repo_path: str) -> DeploymentConfig:
        """
        Parse deployment configuration from repository.
        
        Args:
            repo_path: Path to Java repository
            
        Returns:
            DeploymentConfig with extracted deployment information
        """
        repo = Path(repo_path)
        
        print(f"\n☸️  Parsing deployment configuration from: {repo_path}")
        
        # Look for ocp/ or k8s/ directories
        ocp_dir = repo / "ocp"
        k8s_dir = repo / "k8s"
        deploy_dir = repo / "deploy"
        
        if ocp_dir.exists():
            print(f"   Found OpenShift configurations in: ocp/")
            self.config.deployment_platform = "openshift"
            self._parse_ocp_configs(ocp_dir)
        
        elif k8s_dir.exists():
            print(f"   Found Kubernetes configurations in: k8s/")
            self.config.deployment_platform = "kubernetes"
            self._parse_k8s_configs(k8s_dir)
        
        elif deploy_dir.exists():
            print(f"   Found deployment configurations in: deploy/")
            self.config.deployment_platform = "kubernetes"
            self._parse_k8s_configs(deploy_dir)
        
        else:
            print("   ℹ️  No deployment configurations found (ocp/ or k8s/)")
            print("      Smoke tests will use embedded mode (@SpringBootTest)")
        
        if self.config.routes:
            self._print_summary()
        
        return self.config
    
    def _parse_ocp_configs(self, ocp_dir: Path):
        """Parse OpenShift configuration structure"""
        configs_dir = ocp_dir / "configs"
        
        if not configs_dir.exists():
            return
        
        # Parse base configuration
        base_dir = configs_dir / "base"
        if base_dir.exists():
            self._parse_base_configs(base_dir)
        
        # Parse overlay configurations (environment-specific)
        overlays_dir = configs_dir / "overlays"
        if overlays_dir.exists():
            for env_dir in overlays_dir.iterdir():
                if env_dir.is_dir():
                    env_name = env_dir.name
                    self.config.environments.append(env_name)
                    self._parse_overlay_configs(env_dir, env_name)
    
    def _parse_k8s_configs(self, k8s_dir: Path):
        """Parse Kubernetes configuration structure"""
        # Look for YAML files
        yaml_files = list(k8s_dir.rglob("*.yaml")) + list(k8s_dir.rglob("*.yml"))
        
        for yaml_file in yaml_files:
            self._parse_k8s_manifest(yaml_file)
    
    def _parse_base_configs(self, base_dir: Path):
        """Parse base OCP configurations"""
        # Parse route.yaml for base URL
        route_file = base_dir / "route.yaml"
        if route_file.exists():
            self._parse_route_file(route_file, "base")
        
        # Parse deploy.yaml for health checks
        deploy_file = base_dir / "deploy.yaml"
        if deploy_file.exists():
            self._parse_deploy_file(deploy_file, "base")
        
        # Parse service.yaml
        service_file = base_dir / "service.yaml"
        if service_file.exists():
            self._parse_service_file(service_file, "base")
    
    def _parse_overlay_configs(self, overlay_dir: Path, env_name: str):
        """Parse environment-specific overlay configurations"""
        # Parse route overrides
        route_file = overlay_dir / "route.yaml"
        if route_file.exists():
            self._parse_route_file(route_file, env_name)
        
        # Parse configmap for environment variables
        configmap_file = overlay_dir / "configmap.yaml"
        if configmap_file.exists():
            self._parse_configmap_file(configmap_file, env_name)
        
        # Parse deployment overrides
        deploy_file = overlay_dir / "deploy.yaml"
        if deploy_file.exists():
            self._parse_deploy_file(deploy_file, env_name)
    
    def _parse_route_file(self, route_file: Path, env: str):
        """Extract route URL from OpenShift route.yaml"""
        try:
            self.config.config_files.append(str(route_file))
            
            with open(route_file, 'r', encoding='utf-8') as f:
                docs = yaml.safe_load_all(f)
                
                for doc in docs:
                    if not doc:
                        continue
                    
                    if doc.get('kind') == 'Route':
                        spec = doc.get('spec', {})
                        host = spec.get('host')
                        
                        if host:
                            # Determine protocol
                            tls = spec.get('tls')
                            protocol = 'https' if tls else 'http'
                            
                            base_url = f"{protocol}://{host}"
                            
                            # Add path if specified
                            path = spec.get('path', '')
                            if path:
                                base_url += path
                            
                            self.config.routes[env] = base_url
                            
                            # Set health endpoint
                            self.config.health_endpoints[env] = f"{base_url}/actuator/health"
        
        except Exception as e:
            print(f"   ⚠️  Could not parse {route_file.name}: {e}")
    
    def _parse_configmap_file(self, configmap_file: Path, env: str):
        """Extract ConfigMap data"""
        try:
            self.config.config_files.append(str(configmap_file))
            
            with open(configmap_file, 'r', encoding='utf-8') as f:
                docs = yaml.safe_load_all(f)
                
                for doc in docs:
                    if not doc:
                        continue
                    
                    if doc.get('kind') == 'ConfigMap':
                        data = doc.get('data', {})
                        self.config.config_maps[env] = data
        
        except Exception as e:
            print(f"   ⚠️  Could not parse {configmap_file.name}: {e}")
    
    def _parse_deploy_file(self, deploy_file: Path, env: str):
        """Extract deployment information"""
        try:
            self.config.config_files.append(str(deploy_file))
            
            with open(deploy_file, 'r', encoding='utf-8') as f:
                docs = yaml.safe_load_all(f)
                
                for doc in docs:
                    if not doc:
                        continue
                    
                    kind = doc.get('kind')
                    
                    if kind in ['Deployment', 'DeploymentConfig']:
                        spec = doc.get('spec', {})
                        
                        # Extract replica count
                        replicas = spec.get('replicas', 1)
                        self.config.replicas[env] = replicas
                        
                        # Extract health check paths
                        template = spec.get('template', {})
                        containers = template.get('spec', {}).get('containers', [])
                        
                        for container in containers:
                            liveness_probe = container.get('livenessProbe', {})
                            http_get = liveness_probe.get('httpGet', {})
                            
                            if http_get:
                                health_path = http_get.get('path', '/actuator/health')
                                if env in self.config.routes:
                                    base_url = self.config.routes[env]
                                    self.config.health_endpoints[env] = f"{base_url}{health_path}"
        
        except Exception as e:
            print(f"   ⚠️  Could not parse {deploy_file.name}: {e}")
    
    def _parse_service_file(self, service_file: Path, env: str):
        """Extract service information"""
        try:
            self.config.config_files.append(str(service_file))
            
            with open(service_file, 'r', encoding='utf-8') as f:
                docs = yaml.safe_load_all(f)
                
                for doc in docs:
                    if not doc:
                        continue
                    
                    if doc.get('kind') == 'Service':
                        # Service config extracted if needed
                        pass
        
        except Exception as e:
            print(f"   ⚠️  Could not parse {service_file.name}: {e}")
    
    def _parse_k8s_manifest(self, manifest_file: Path):
        """Parse generic Kubernetes manifest"""
        try:
            self.config.config_files.append(str(manifest_file))
            
            with open(manifest_file, 'r', encoding='utf-8') as f:
                docs = yaml.safe_load_all(f)
                
                for doc in docs:
                    if not doc:
                        continue
                    
                    kind = doc.get('kind')
                    
                    # Detect environment from namespace or labels
                    metadata = doc.get('metadata', {})
                    namespace = metadata.get('namespace', 'default')
                    env = namespace if namespace != 'default' else 'prod'
                    
                    if env not in self.config.environments:
                        self.config.environments.append(env)
                    
                    # Parse Ingress for routes
                    if kind == 'Ingress':
                        spec = doc.get('spec', {})
                        rules = spec.get('rules', [])
                        
                        for rule in rules:
                            host = rule.get('host')
                            if host:
                                tls = spec.get('tls')
                                protocol = 'https' if tls else 'http'
                                self.config.routes[env] = f"{protocol}://{host}"
                    
                    # Parse Deployment
                    elif kind == 'Deployment':
                        spec = doc.get('spec', {})
                        replicas = spec.get('replicas', 1)
                        self.config.replicas[env] = replicas
        
        except Exception as e:
            print(f"   ⚠️  Could not parse {manifest_file.name}: {e}")
    
    def _print_summary(self):
        """Print parsed deployment configuration summary"""
        print(f"\n   ✅ Deployment Configuration:")
        print(f"      Platform: {self.config.deployment_platform.upper()}")
        
        if self.config.environments:
            print(f"      Environments: {', '.join(self.config.environments)}")
        
        if self.config.routes:
            print(f"      Routes:")
            for env, url in self.config.routes.items():
                replicas = self.config.replicas.get(env, 1)
                print(f"         {env}: {url} ({replicas} replicas)")
    
    def to_dict(self) -> Dict:
        """Export deployment config as dictionary"""
        return {
            'platform': self.config.deployment_platform,
            'environments': self.config.environments,
            'routes': self.config.routes,
            'health_endpoints': self.config.health_endpoints,
            'replicas': self.config.replicas,
            'config_maps': {env: dict(list(cm.items())[:10]) for env, cm in self.config.config_maps.items()},  # Top 10 per env
            'config_files': self.config.config_files
        }
    
    def export_json(self, output_path: str):
        """Export deployment config to JSON file"""
        Path(output_path).write_text(json.dumps(self.to_dict(), indent=2))
        print(f"💾 Exported deployment config to: {output_path}")
