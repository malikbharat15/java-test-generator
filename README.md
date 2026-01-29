# Smoke Test Generator

Python-based tool that automatically generates smoke tests for Java enterprise applications using AST parsing and LLM-powered analysis.

## Project Structure

```
smoketest-generator/
├── src/
│   ├── ast_parser/          # Java AST parsing
│   ├── entry_point_discovery/  # Find REST/CLI/Batch entry points
│   ├── test_generator/      # LLM-powered test generation
│   └── cli/                 # Command-line interface
├── examples/                # Sample Java applications
│   ├── spring-boot-rest/    # Spring Boot REST API
│   ├── jaxrs-service/       # JAX-RS REST service
│   ├── spring-batch/        # Spring Batch jobs
│   ├── kafka-consumer/      # Kafka message consumers
│   └── cli-tool/            # Command-line tools
├── tests/                   # Python tests
└── output/                  # Generated smoke tests
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test AST Parser

Run the AST parser on all example Java applications:

```bash
python tests/test_ast_parser.py
```

This will:
- Parse all example Java applications
- Identify entry points (REST endpoints, CLI commands, batch jobs, etc.)
- Generate detailed reports
- Save analysis results to `all_examples_analysis.json`

### 3. Test Individual Examples

```bash
python src/ast_parser/java_ast_parser.py examples/spring-boot-rest/
```

## Example Java Applications

The project includes 5 different types of enterprise Java applications:

1. **spring-boot-rest/** - Spring Boot REST API
   - UserController: CRUD operations for users
   - OrderController: Order management endpoints
   - Application: Main Spring Boot entry point

2. **jaxrs-service/** - JAX-RS REST Service
   - ProductResource: Product management API
   - HealthResource: Health check endpoint

3. **spring-batch/** - Spring Batch Jobs
   - DataProcessingJob: Batch job configuration
   - ScheduledTasks: @Scheduled tasks

4. **kafka-consumer/** - Message Consumers
   - OrderEventConsumer: Kafka listeners
   - NotificationListener: JMS listeners

5. **cli-tool/** - Command-Line Tools
   - DataTool: PicoCLI-based CLI tool
   - SimpleCLI: Basic main method CLI

## Current Status

- [x] Project structure created
- [x] Sample Java applications created (5 types)
- [x] AST parser implemented
- [ ] Entry point discovery tested
- [ ] LLM integration
- [ ] Test generation

## Next Steps

1. Test AST parser on examples
2. Validate entry point discovery accuracy
3. Implement LLM-powered test generation
4. Add repository cloning capability
5. Build CLI interface
