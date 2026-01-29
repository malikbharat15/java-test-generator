"""
Build Config Parser - Extract build and dependency information

Parses pom.xml (Maven) and build.gradle (Gradle) to extract:
- Java version
- Test frameworks (JUnit, TestNG, Spock)
- Testing libraries (Spring Boot Test, RestAssured, Testcontainers, Mockito)
- Dependencies (Spring Boot starters, database drivers, messaging)
- Build plugins (test runners, code coverage)

This tells us what testing infrastructure is already available.
"""

import xml.etree.ElementTree as ET
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field


@dataclass
class BuildConfig:
    """Parsed build configuration"""
    build_tool: str = "unknown"  # "maven" or "gradle"
    java_version: Optional[str] = None
    
    # Test frameworks
    test_frameworks: List[str] = field(default_factory=list)  # ["junit5", "testng"]
    
    # Testing libraries
    testing_libraries: Set[str] = field(default_factory=set)  # {"spring-boot-test", "rest-assured"}
    
    # Dependencies
    dependencies: List[Dict] = field(default_factory=list)  # [{groupId, artifactId, version}]
    
    # Spring Boot version
    spring_boot_version: Optional[str] = None
    
    # Build files found
    build_files: List[str] = field(default_factory=list)


class BuildConfigParser:
    """
    Parses Maven pom.xml and Gradle build.gradle files.
    
    Detects:
    - Existing test infrastructure (what's already available?)
    - Java version (compatibility)
    - Spring Boot version (test strategies differ by version)
    - Dependencies (tells us app capabilities)
    """
    
    # Known test framework artifacts
    TEST_FRAMEWORKS = {
        'junit-jupiter': 'junit5',
        'junit-jupiter-api': 'junit5',
        'junit-jupiter-engine': 'junit5',
        'junit': 'junit4',
        'testng': 'testng',
        'spock-core': 'spock'
    }
    
    # Known testing libraries
    TESTING_LIBRARIES = {
        'spring-boot-starter-test': 'spring-boot-test',
        'rest-assured': 'rest-assured',
        'testcontainers': 'testcontainers',
        'mockito-core': 'mockito',
        'mockito-junit-jupiter': 'mockito',
        'wiremock': 'wiremock',
        'cucumber-java': 'cucumber'
    }
    
    def __init__(self):
        self.config = BuildConfig()
    
    def parse(self, repo_path: str) -> BuildConfig:
        """
        Parse build configuration from repository.
        
        Args:
            repo_path: Path to Java repository
            
        Returns:
            BuildConfig with extracted build information
        """
        repo = Path(repo_path)
        
        print(f"\n🔧 Parsing build configuration from: {repo_path}")
        
        # Find build files
        pom_files = list(repo.rglob("pom.xml"))
        gradle_files = list(repo.rglob("build.gradle")) + list(repo.rglob("build.gradle.kts"))
        
        if pom_files:
            print(f"   Found {len(pom_files)} pom.xml files (Maven)")
            self.config.build_tool = "maven"
            # Parse root pom.xml
            for pom in pom_files:
                if pom.parent == repo or 'src' not in str(pom):  # Root pom
                    self._parse_pom(pom)
                    break
        
        elif gradle_files:
            print(f"   Found {len(gradle_files)} build.gradle files (Gradle)")
            self.config.build_tool = "gradle"
            # Parse root build.gradle
            for gradle in gradle_files:
                if gradle.parent == repo:  # Root build.gradle
                    self._parse_gradle(gradle)
                    break
        
        else:
            print("   ⚠️  No build files found (pom.xml or build.gradle)")
        
        self._print_summary()
        
        return self.config
    
    def _parse_pom(self, pom_path: Path):
        """Parse Maven pom.xml file"""
        try:
            self.config.build_files.append(str(pom_path))
            
            tree = ET.parse(pom_path)
            root = tree.getroot()
            
            # Handle XML namespace
            ns = {'maven': 'http://maven.apache.org/POM/4.0.0'}
            if root.tag.startswith('{'):
                ns_url = root.tag.split('}')[0][1:]
                ns = {'maven': ns_url}
            
            # Extract Java version
            java_version = root.find('.//maven:properties/maven:java.version', ns)
            if java_version is not None:
                self.config.java_version = java_version.text
            else:
                # Try maven.compiler.source
                source = root.find('.//maven:properties/maven:maven.compiler.source', ns)
                if source is not None:
                    self.config.java_version = source.text
            
            # Extract Spring Boot version
            parent_version = root.find('.//maven:parent/maven:version', ns)
            if parent_version is not None and 'spring-boot' in str(ET.tostring(root.find('.//maven:parent', ns))):
                self.config.spring_boot_version = parent_version.text
            
            # Extract dependencies
            dependencies = root.findall('.//maven:dependency', ns)
            for dep in dependencies:
                group_id = dep.find('maven:groupId', ns)
                artifact_id = dep.find('maven:artifactId', ns)
                version = dep.find('maven:version', ns)
                scope = dep.find('maven:scope', ns)
                
                if artifact_id is not None:
                    artifact = artifact_id.text
                    
                    # Check for test frameworks
                    for test_artifact, framework in self.TEST_FRAMEWORKS.items():
                        if test_artifact in artifact:
                            if framework not in self.config.test_frameworks:
                                self.config.test_frameworks.append(framework)
                    
                    # Check for testing libraries
                    for lib_artifact, lib_name in self.TESTING_LIBRARIES.items():
                        if lib_artifact in artifact:
                            self.config.testing_libraries.add(lib_name)
                    
                    # Store all dependencies
                    self.config.dependencies.append({
                        'groupId': group_id.text if group_id is not None else '',
                        'artifactId': artifact,
                        'version': version.text if version is not None else '',
                        'scope': scope.text if scope is not None else 'compile'
                    })
            
        except Exception as e:
            print(f"   ⚠️  Could not parse {pom_path.name}: {e}")
    
    def _parse_gradle(self, gradle_path: Path):
        """Parse Gradle build.gradle file"""
        try:
            self.config.build_files.append(str(gradle_path))
            
            content = gradle_path.read_text(encoding='utf-8')
            
            # Extract Java version
            java_match = re.search(r'sourceCompatibility\s*=\s*[\'"]?(\d+\.?\d*)[\'"]?', content)
            if java_match:
                self.config.java_version = java_match.group(1)
            
            # Extract Spring Boot version
            spring_boot_match = re.search(r'org\.springframework\.boot[\'"]?\s+version\s+[\'"]([^\'\"]+)', content)
            if spring_boot_match:
                self.config.spring_boot_version = spring_boot_match.group(1)
            
            # Extract dependencies
            dep_pattern = r'(?:testImplementation|implementation|api|compileOnly|runtimeOnly|testRuntimeOnly)\s*[\'"]([^:\'\"]+):([^:\'\"]+)(?::([^\'\"]+))?[\'"]'
            
            for match in re.finditer(dep_pattern, content):
                group_id = match.group(1)
                artifact_id = match.group(2)
                version = match.group(3) if match.group(3) else ''
                
                # Check for test frameworks
                for test_artifact, framework in self.TEST_FRAMEWORKS.items():
                    if test_artifact in artifact_id:
                        if framework not in self.config.test_frameworks:
                            self.config.test_frameworks.append(framework)
                
                # Check for testing libraries
                for lib_artifact, lib_name in self.TESTING_LIBRARIES.items():
                    if lib_artifact in artifact_id:
                        self.config.testing_libraries.add(lib_name)
                
                # Store dependency
                self.config.dependencies.append({
                    'groupId': group_id,
                    'artifactId': artifact_id,
                    'version': version,
                    'scope': 'test' if 'test' in content[max(0, match.start()-50):match.start()] else 'compile'
                })
            
        except Exception as e:
            print(f"   ⚠️  Could not parse {gradle_path.name}: {e}")
    
    def _print_summary(self):
        """Print parsed build configuration summary"""
        print(f"\n   ✅ Build Configuration:")
        print(f"      Build Tool: {self.config.build_tool}")
        
        if self.config.java_version:
            print(f"      Java Version: {self.config.java_version}")
        
        if self.config.spring_boot_version:
            print(f"      Spring Boot: {self.config.spring_boot_version}")
        
        if self.config.test_frameworks:
            print(f"      Test Frameworks: {', '.join(self.config.test_frameworks)}")
        
        if self.config.testing_libraries:
            print(f"      Testing Libraries: {', '.join(sorted(self.config.testing_libraries))}")
        
        print(f"      Total Dependencies: {len(self.config.dependencies)}")
    
    def to_dict(self) -> Dict:
        """Export build config as dictionary"""
        return {
            'build_tool': self.config.build_tool,
            'java_version': self.config.java_version,
            'spring_boot_version': self.config.spring_boot_version,
            'test_frameworks': self.config.test_frameworks,
            'testing_libraries': list(self.config.testing_libraries),
            'dependencies': self.config.dependencies[:50],  # Top 50 only
            'build_files': self.config.build_files
        }
    
    def export_json(self, output_path: str):
        """Export build config to JSON file"""
        Path(output_path).write_text(json.dumps(self.to_dict(), indent=2))
        print(f"💾 Exported build config to: {output_path}")
