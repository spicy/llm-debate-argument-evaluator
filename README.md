# LLM Debate Argument Evaluator

This project implements a debate argument evaluation tool using Large Language Models (LLMs).

## Project Structure

``` bash
/llm_debate_argument_evaluator/
│
├── /main/
│   ├── main.py                             # Central orchestrator for user interactions, invoking services
│   ├── controller.py                       # Handles user requests, interacts with service layer
│   ├── dependency_injector.py              # Injects services and models into the system
│   └── user_interactions.py                # Encapsulates user commands like expand node or submit argument
│
├── /services/
│   ├── argument_generation_service.py      # Service layer for argument generation logic, ensuring argument variability across subcategories
│   ├── evaluation_service.py               # Coordinates evaluations across LLMs (e.g., ChatGPT, Claude)
│   ├── memoization_service.py              # Manages memoization and semantic caching
│   ├── priority_queue_service.py           # Manages BFS traversal and priority queue
│   ├── async_processing_service.py         # Handles asynchronous evaluations and processing
│   ├── score_aggregator_service.py         # Aggregates scores from multiple models (e.g., ChatGPT, Claude)
│   └── model_selection_service.py          # Dynamically selects and manages LLMs
│
├── /commands/
│   ├── expand_node_command.py              # Expands debate tree nodes
│   ├── submit_argument_command.py          # Handles user-submitted arguments
│   ├── generate_arguments_command.py       # Triggers argument generation with argument variability to capture diverse perspectives
│   └── evaluate_arguments_command.py       # Initiates argument evaluation
│
├── /config/
│   ├── logger_config.py              # Defines logging variables
│
├── /evaluation/
│   ├── model_factory.py                    # Initializes evaluation models and manages the instantiation and selection
│   ├── score_aggregator.py                 # Aggregates scores from multiple evaluation models
│   ├── /models/
│   │   ├── base_model.py                   # Abstract base class for LLM models
│   │   ├── chatgpt_model.py                # ChatGPT-specific implementation
│   │   ├── claude_model.py                 # Claude-specific implementation
│   │   └── model_injector.py               # Dynamically injects LLM models for evaluations
│   └── /api_clients/
│       ├── base_api_client.py              # Base API client for standardizing API interaction logic
│       ├── chatgpt_api_client.py           # API client handling ChatGPT API requests
│       └── claude_api_client.py            # API client handling Claude API requests
│
├── /memoization/
│   ├── semantic_similarity.py              # Calculates argument similarity using embeddings (e.g., Sentence-BERT)
│   └── cache_manager.py                    # Stores and retrieves cached evaluations
│
├── /debate_traversal/
│   ├── traversal_logic.py                  # Implements BFS traversal with priority queue
│   ├── priority_queue_manager.py           # Manages priority queue
│   └── traversal_injector.py               # Injects traversal services dynamically
│
├── /async_processing/
│   └── async_utils.py                      # Utility functions for async operations
│
├── /visualization/
│   ├── observer.py                         # Observer pattern for real-time updates
│   ├── tree_renderer.py                    # Renders debate tree with node structure representing arguments and branches for rebuttals
│   ├── node_expansion_handler.py           # Manages node expansion in the debate tree
│   ├── node_score_display.py               # Displays score breakdown for each node. Nodes are color-coded based on their evaluation scores
│   └── visualization_injector.py           # Injects visualization services dynamically
│
└── /utils/
    ├── constants.py                        # Stores constants, configuration values, thresholds
    ├── logger.py                          # Central logging mechanism
    └── dependency_registry.py              # Registers and manages dependency injection
```

## Features

- Argument generation with variability across subcategories
- Evaluation of arguments using multiple LLMs (e.g., ChatGPT, Claude)
- Memoization and semantic caching for efficient processing
- Asynchronous evaluation and processing
- Visualization of debate tree with color-coded nodes based on evaluation scores
- Dynamic model selection and injection
- Breadth-First Search (BFS) traversal with priority queue for debate exploration

## Getting Started

Run 'pip install -r requirements.txt' to install the dependencies.


## KEY
Setup env variables for CHATGPT_API_KEY and CHATGPT_API_ENDPOINT 

CHATGPT_API_KEY = {secret}
CHATGPT_API_ENDPOINT = https://api.openai.com/v1/chat/completions
DEBUG_MODE = 1 for true (for debugging)
MAX_TOKENS = 10 (Just seeing it functions)