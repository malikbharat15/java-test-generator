"""
Existing Test Detector - Find and analyze existing test infrastructure

Detects existing tests to:
1. Identify test folder structure (src/test/java, __tests__, test/)
2. Distinguish smoke tests vs unit tests
3. Extract test patterns and conventions
4. Determine what's already covered (avoid duplication)
5. Learn coding style for generated tests

Smoke test indicators:
- Folder names: smoke/, smoketest/, integration/, e2e/, __tests__/
- File patterns: *SmokeTest.java, *IT.java, *E2E.java, *IntegrationTest.java
- Annotations: @SpringBootTest, @Testcontainers, @IntegrationTest
- Framework usage: RestAssured, Testcontainers, embedded servers
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field


@dataclass
class TestInfo:
    """Information about a single test file"""
    file_path: str
    file_name: str
    test_type: str  # "smoke", "integration", "unit", "e2e"
    test_framework: str  # "junit5", "junit4", "testng", "spock"
    
    # Test characteristics
    has_spring_boot_test: bool = False
    has_testcontainers: bool = False
    has_rest_assured: bool = False
    has_web_client: bool = False
    has_mock_mvc: bool = False
    
    # Coverage indicators
    tests_rest_endpoints: bool = False
    tests_database: bool = False
    tests_messaging: bool = False
    
    # Test methods
    test_method_count: int = 0
    test_method_names: List[str] = field(default_factory=list)


@dataclass
class ExistingTests:
    """Summary of existing test infrastructure"""
    has_tests: bool = False
    has_smoke_tests: bool = False
    
    # Test structure
    test_folders: List[str] = field(default_factory=list)
    test_file_count: int = 0
    
    # Test types
    smoke_tests: List[TestInfo] = field(default_factory=list)
    integration_tests: List[TestInfo] = field(default_factory=list)
    unit_tests: List[TestInfo] = field(default_factory=list)
    
    # Test patterns detected
    naming_patterns: Set[str] = field(default_factory=set)  # {"*Test.java", "*IT.java"}
    test_frameworks: Set[str] = field(default_factory=set)  # {"junit5", "testng"}
    test_libraries: Set[str] = field(default_factory=set)  # {"spring-boot-test", "rest-assured"}
    
    # Coverage analysis
    endpoints_covered: List[str] = field(default_factory=list)  # REST endpoints being tested
    coverage_percentage: float = 0.0  # Estimated coverage


class ExistingTestDetector:
    """
    Analyzes existing test code in repository.
    
    Key goals:
    1. Avoid duplicating existing smoke test coverage
    2. Match existing test patterns and style
    3. Identify gaps in test coverage
    4. Determine best test strategy based on what exists
    """
    
    # Smoke test indicators
    SMOKE_TEST_PATTERNS = {
        'folder': ['smoke', 'smoketest', 'integration', 'e2e', '__tests__'],
        'file': ['SmokeTest', 'IT.java', 'E2E', 'IntegrationTest'],
        'annotation': ['@SpringBootTest', '@Testcontainers', '@IntegrationTest', '@WebMvcTest']
    }
    
    # Test framework indicators
    TEST_FRAMEWORK_IMPORTS = {
        'junit5': ['org.junit.jupiter', 'jupiter.api.Test'],
        'junit4': ['org.junit.Test', 'junit.framework'],
        'testng': ['org.testng', 'testng.annotations.Test'],
        'spock': ['spock.lang.Specification']
    }
    
    def __init__(self):
        self.existing = ExistingTests()
    
    def analyze(self, repo_path: str) -> ExistingTests:
        """
        Analyze existing tests in repository.
        
        Args:
            repo_path: Path to Java repository
            
        Returns:
            ExistingTests with analysis results
        """
        repo = Path(repo_path)
        
        print(f"\n🧪 Analyzing existing tests in: {repo_path}")
        
        # Find test directories
        test_dirs = self._find_test_directories(repo)
        self.existing.test_folders = [str(d) for d in test_dirs]
        
        if not test_dirs:
            print("   ℹ️  No test directories found")
            return self.existing
        
        print(f"   Found {len(test_dirs)} test directories")
        
        # Analyze test files
        for test_dir in test_dirs:
            java_files = list(test_dir.rglob("*.java"))
            
            for java_file in java_files:
                if self._is_test_file(java_file):
                    test_info = self._analyze_test_file(java_file)
                    self.existing.test_file_count += 1
                    
                    # Categorize test
                    if test_info.test_type == 'smoke':
                        self.existing.smoke_tests.append(test_info)
                        self.existing.has_smoke_tests = True
                    elif test_info.test_type == 'integration':
                        self.existing.integration_tests.append(test_info)
                    else:
                        self.existing.unit_tests.append(test_info)
                    
                    # Track patterns
                    self.existing.test_frameworks.add(test_info.test_framework)
                    
                    # Track libraries
                    if test_info.has_spring_boot_test:
                        self.existing.test_libraries.add('spring-boot-test')
                    if test_info.has_testcontainers:
                        self.existing.test_libraries.add('testcontainers')
                    if test_info.has_rest_assured:
                        self.existing.test_libraries.add('rest-assured')
        
        self.existing.has_tests = self.existing.test_file_count > 0
        
        # Detect naming patterns
        self._detect_naming_patterns()
        
        self._print_summary()
        
        return self.existing
    
    def _find_test_directories(self, repo: Path) -> List[Path]:
        """Find all test directories in repository"""
        test_dirs = []
        
        # Standard Maven/Gradle structure
        test_dirs.extend(repo.rglob("src/test/java"))
        test_dirs.extend(repo.rglob("src/test/groovy"))
        
        # Common alternative structures
        test_dirs.extend(repo.rglob("__tests__"))
        test_dirs.extend(repo.rglob("test"))
        test_dirs.extend(repo.rglob("tests"))
        
        # Smoke test specific folders
        for pattern in self.SMOKE_TEST_PATTERNS['folder']:
            test_dirs.extend(repo.rglob(pattern))
        
        # Deduplicate and filter
        unique_dirs = []
        seen = set()
        
        for d in test_dirs:
            if d.is_dir() and str(d) not in seen:
                seen.add(str(d))
                unique_dirs.append(d)
        
        return unique_dirs
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file"""
        filename = file_path.name
        
        # Common test file patterns
        return (
            filename.endswith('Test.java') or
            filename.endswith('Tests.java') or
            filename.endswith('IT.java') or
            filename.endswith('ITCase.java') or
            filename.endswith('TestCase.java') or
            filename.startswith('Test') or
            'Test' in filename
        )
    
    def _analyze_test_file(self, file_path: Path) -> TestInfo:
        """Analyze a single test file"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            test_info = TestInfo(
                file_path=str(file_path),
                file_name=file_path.name,
                test_type=self._determine_test_type(file_path, content),
                test_framework=self._detect_test_framework(content)
            )
            
            # Detect test libraries
            test_info.has_spring_boot_test = '@SpringBootTest' in content or 'SpringBootTest' in content
            test_info.has_testcontainers = '@Testcontainers' in content or 'Testcontainers' in content
            test_info.has_rest_assured = 'RestAssured' in content or 'rest-assured' in content
            test_info.has_web_client = 'WebTestClient' in content or 'MockMvc' in content
            test_info.has_mock_mvc = 'MockMvc' in content
            
            # Detect what's being tested
            test_info.tests_rest_endpoints = any(keyword in content for keyword in ['GET', 'POST', 'endpoint', 'rest', 'api', '@GetMapping', '@PostMapping'])
            test_info.tests_database = any(keyword in content for keyword in ['repository', 'jdbc', 'jpa', 'database', 'sql'])
            test_info.tests_messaging = any(keyword in content for keyword in ['kafka', 'jms', 'message', 'queue'])
            
            # Count test methods
            test_info.test_method_count = len(re.findall(r'@Test\s+(?:public|private|protected)?\s+void', content))
            
            # Extract test method names
            test_methods = re.findall(r'@Test.*?\s+(?:public|private|protected)?\s+void\s+(\w+)\s*\(', content, re.DOTALL)
            test_info.test_method_names = test_methods[:10]  # First 10 only
            
            # Extract covered endpoints from test
            if test_info.tests_rest_endpoints:
                endpoints = re.findall(r'["\']/([\w/\-{}]+)["\']', content)
                self.existing.endpoints_covered.extend(endpoints[:5])  # Sample
            
            return test_info
            
        except Exception as e:
            print(f"   ⚠️  Could not analyze {file_path.name}: {e}")
            return TestInfo(
                file_path=str(file_path),
                file_name=file_path.name,
                test_type="unknown",
                test_framework="unknown"
            )
    
    def _determine_test_type(self, file_path: Path, content: str) -> str:
        """Determine if test is smoke/integration/unit test"""
        path_str = str(file_path).lower()
        filename = file_path.name
        
        # Check folder name
        for smoke_folder in self.SMOKE_TEST_PATTERNS['folder']:
            if smoke_folder in path_str:
                return 'smoke'
        
        # Check file name
        for smoke_pattern in self.SMOKE_TEST_PATTERNS['file']:
            if smoke_pattern in filename:
                return 'smoke' if 'Smoke' in smoke_pattern or 'E2E' in smoke_pattern else 'integration'
        
        # Check annotations
        for smoke_annotation in self.SMOKE_TEST_PATTERNS['annotation']:
            if smoke_annotation in content:
                return 'smoke'
        
        # Check for integration test indicators
        if any(keyword in content for keyword in ['@SpringBootTest', '@DataJpaTest', '@WebMvcTest', 'Testcontainers']):
            return 'integration'
        
        # Default to unit test
        return 'unit'
    
    def _detect_test_framework(self, content: str) -> str:
        """Detect test framework used"""
        for framework, imports in self.TEST_FRAMEWORK_IMPORTS.items():
            if any(imp in content for imp in imports):
                return framework
        
        return 'unknown'
    
    def _detect_naming_patterns(self):
        """Detect test file naming patterns"""
        all_tests = self.existing.smoke_tests + self.existing.integration_tests + self.existing.unit_tests
        
        for test in all_tests:
            filename = test.file_name
            
            if filename.endswith('Test.java'):
                self.existing.naming_patterns.add('*Test.java')
            elif filename.endswith('Tests.java'):
                self.existing.naming_patterns.add('*Tests.java')
            elif filename.endswith('IT.java'):
                self.existing.naming_patterns.add('*IT.java')
            elif 'SmokeTest' in filename:
                self.existing.naming_patterns.add('*SmokeTest.java')
            elif 'IntegrationTest' in filename:
                self.existing.naming_patterns.add('*IntegrationTest.java')
    
    def _print_summary(self):
        """Print existing test analysis summary"""
        print(f"\n   ✅ Existing Test Analysis:")
        print(f"      Total Test Files: {self.existing.test_file_count}")
        print(f"      Smoke Tests: {len(self.existing.smoke_tests)}")
        print(f"      Integration Tests: {len(self.existing.integration_tests)}")
        print(f"      Unit Tests: {len(self.existing.unit_tests)}")
        
        if self.existing.test_frameworks:
            print(f"      Test Frameworks: {', '.join(self.existing.test_frameworks)}")
        
        if self.existing.test_libraries:
            print(f"      Test Libraries: {', '.join(sorted(self.existing.test_libraries))}")
        
        if self.existing.naming_patterns:
            print(f"      Naming Patterns: {', '.join(self.existing.naming_patterns)}")
        
        if self.existing.has_smoke_tests:
            print(f"      ⚠️  SMOKE TESTS ALREADY EXIST - Will generate incremental coverage only")
    
    def to_dict(self) -> Dict:
        """Export test analysis as dictionary"""
        return {
            'has_tests': self.existing.has_tests,
            'has_smoke_tests': self.existing.has_smoke_tests,
            'test_folders': self.existing.test_folders,
            'test_file_count': self.existing.test_file_count,
            'summary': {
                'smoke_tests': len(self.existing.smoke_tests),
                'integration_tests': len(self.existing.integration_tests),
                'unit_tests': len(self.existing.unit_tests)
            },
            'test_frameworks': list(self.existing.test_frameworks),
            'test_libraries': list(self.existing.test_libraries),
            'naming_patterns': list(self.existing.naming_patterns),
            'endpoints_covered': list(set(self.existing.endpoints_covered))[:20],  # Top 20 unique
            'smoke_test_samples': [
                {
                    'file': test.file_name,
                    'framework': test.test_framework,
                    'method_count': test.test_method_count,
                    'has_spring_boot_test': test.has_spring_boot_test,
                    'has_testcontainers': test.has_testcontainers,
                    'has_rest_assured': test.has_rest_assured
                }
                for test in self.existing.smoke_tests[:5]  # First 5 smoke tests
            ]
        }
    
    def export_json(self, output_path: str):
        """Export test analysis to JSON file"""
        Path(output_path).write_text(json.dumps(self.to_dict(), indent=2))
        print(f"💾 Exported test analysis to: {output_path}")
