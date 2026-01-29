# Smoke Test Generator

Python-based tool that automatically generates smoke tests for Java enterprise applications using AST parsing and LLM-powered analysis.

## 🚀 How It Works (End-to-End Pipeline)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Java Repo     │────▶│   Phase 1:      │────▶│   Phase 2:      │────▶│   Phase 3:      │
│   (Any Type)    │     │   AST Parsing   │     │   Config Parse  │     │   LLM Prompt    │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                       │                       │
                               ▼                       ▼                       ▼
                        • REST endpoints        • application.yml       • Newman/Postman
                        • Kafka consumers       • pom.xml/build.gradle   collection JSON
                        • Scheduled tasks       • OCP/K8s configs       • Environment file
                        • Request schemas       • Existing tests        • CI/CD workflow
```

### Phase 1: AST Entry Point Discovery
- **Java AST Parsing** using `javalang` library
- Detects: REST endpoints, Kafka consumers, Scheduled tasks, Batch jobs, CLI commands
- Extracts: HTTP methods, paths, parameters, security annotations, request body schemas
- Output: `complete_analysis_{app}.json`

### Phase 2: Configuration Analysis
- **Application Config**: `application.yml`, `application.properties` (ports, context paths, DB URLs)
- **Build Config**: `pom.xml`, `build.gradle` (Java version, Spring Boot version, dependencies)
- **Deployment Config**: OpenShift/Kubernetes manifests (routes, replicas, health endpoints)
- **Existing Tests**: Detects existing smoke/integration tests to avoid duplication

### Phase 3: LLM Prompt Generation
- Selects appropriate prompt template (REST, Kafka, Batch, etc.)
- Injects application-specific data (endpoints, schemas, routes)
- Generates structured prompt ready for LLM consumption
- Output: `generated_prompt_{app}.txt`

## 📁 Project Structure

```
smoketest-generator/
├── src/
│   ├── ast_parser/              # Java AST parsing
│   │   ├── java_ast_parser.py   # Entry point discovery
│   │   └── model_schema_extractor.py  # DTO/Request body schemas
│   ├── config_analyzer/         # Configuration parsing
│   │   ├── application_config_parser.py
│   │   ├── build_config_parser.py
│   │   ├── deployment_config_parser.py
│   │   └── existing_test_detector.py
│   └── test_generator/          # LLM prompt building
│       ├── prompt_builder.py    # Dynamic prompt composition
│       └── prompts/             # Specialized prompt templates
├── examples-enterprise/         # Sample enterprise Java apps
│   ├── core-banking-api/        # Spring Boot REST + JPA
│   ├── ecommerce-order-service/ # REST + Kafka + Scheduled
│   ├── payment-gateway-secured/ # Spring Security + JWT
│   ├── inventory-reactive-service/  # Spring WebFlux
│   └── data-pipeline-batch/     # Spring Batch + Scheduled
├── tests/                       # Python tests
│   ├── test_ast_parser.py
│   ├── test_config_analyzers.py
│   ├── test_prompt_generation.py
│   └── test_end_to_end.py       # Full pipeline test
└── output/                      # Generated analysis & prompts
```

## 🛠️ Setup

### 1. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run End-to-End Pipeline

```bash
# Run on all example apps
python tests/test_end_to_end.py

# Run on specific apps
python tests/test_end_to_end.py payment-gateway-secured data-pipeline-batch
```

### 4. Generate LLM Prompts

```bash
python tests/test_prompt_generation.py
```

## 📊 Example Output

Running on `payment-gateway-secured`:

```
📍 PHASE 1: AST ENTRY POINT DISCOVERY
   Total Entry Points: 17
   REST Endpoints: 16
   Scheduled Tasks: 0
   Request Body Schemas: 6

⚙️  PHASE 2: CONFIGURATION ANALYSIS
   Server: localhost:8443/payment-api
   Spring Boot: 2.7.14
   Platform: OPENSHIFT
   Routes: https://payment-gateway-dev.apps.dev.example.com

📄 PHASE 3: PROMPT GENERATION
   Detected Types: ['REST_API', 'CLI']
   Primary Type: REST_API
   Prompt Length: 18,947 chars, 570 lines
```

### Sample Generated Prompt Content:

```
--- Endpoint 10: POST /api/v1/payments ---
Method Name: processPayment
Return Type: ResponseEntity<PaymentResponse>
Security: PROTECTED
  - Auth Type: PreAuthorize
  - Expression: hasAnyRole('USER', 'MERCHANT')
Parameters:
  - [body] request: PaymentRequest (REQUIRED)
    Request Body Schema (PaymentRequest):
      - cardNumber: String (optional)
      - amount: BigDecimal (optional)
      - currency: String (optional)
```

## ✅ Features

| Feature | Status | Description |
|---------|--------|-------------|
| REST Endpoint Discovery | ✅ | Spring MVC, JAX-RS annotations |
| Kafka Consumer Detection | ✅ | @KafkaListener, @JmsListener |
| Scheduled Task Detection | ✅ | @Scheduled with cron expressions |
| Security Annotation Parsing | ✅ | @PreAuthorize, @Secured, @RolesAllowed |
| Request Body Schema Extraction | ✅ | DTOs with validation annotations |
| Multi-Type App Support | ✅ | REST + Scheduled + Kafka in same app |
| Reactive Detection | ✅ | Mono<>/Flux<> return types |
| OpenShift/K8s Route Parsing | ✅ | Routes per environment |
| Existing Test Detection | ✅ | Avoid duplicate coverage |
| LLM Prompt Generation | ✅ | Newman/Postman collection format |

## 🧪 Test Coverage

```bash
# Test AST parser
python tests/test_ast_parser.py

# Test config analyzers
python tests/test_config_analyzers.py

# Test prompt generation
python tests/test_prompt_generation.py

# Full E2E pipeline
python tests/test_end_to_end.py
```

## 📈 Supported Application Types

| Type | Detection Method | Prompt Template |
|------|------------------|-----------------|
| REST API | @RestController, @GetMapping, etc. | Newman/Postman |
| Kafka Consumer | @KafkaListener | Kafka test guidance |
| Scheduled Jobs | @Scheduled | Actuator verification |
| Spring Batch | @EnableBatchProcessing | Job launcher tests |
| WebFlux Reactive | Mono<>/Flux<> returns | Reactive test patterns |
| CLI Tools | main() methods | CLI execution tests |

## 🔜 Next Steps

- [ ] LLM integration (Anthropic Claude)
- [ ] Actual test file generation
- [ ] CLI interface for running on any repo
- [ ] GitHub Actions workflow generation
- [ ] Test execution and reporting
