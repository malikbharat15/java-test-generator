# Smoke Test Generator - Project Setup

## Project Overview
Python-based tool that generates smoke tests for Java enterprise applications using AST parsing and LLM-powered analysis.

## Tech Stack
- Python 3.10+
- LangChain + Anthropic Claude
- AST Parsing (javalang/tree-sitter)
- GitPython for repository management

## Project Structure
```
smoketest-generator/
├── src/
│   ├── ast_parser/          # Java AST parsing
│   ├── entry_point_discovery/  # Find REST/CLI/Batch entry points
│   ├── test_generator/      # LLM-powered test generation
│   └── cli/                 # Command-line interface
├── examples/                # Sample Java applications
│   ├── spring-boot-rest/
│   ├── jaxrs-service/
│   ├── spring-batch/
│   ├── kafka-consumer/
│   └── cli-tool/
├── tests/                   # Python tests
└── output/                  # Generated smoke tests
```

## Setup Steps
- [x] Create copilot instructions
- [ ] Scaffold project structure
- [ ] Create sample Java applications
- [ ] Implement AST parser
- [ ] Test against samples
- [ ] Setup dependencies
