# LLM Debate Argument Evaluator

This project implements a tree argument evaluation tool using Large Language Models (LLMs).

## Project Structure

``` bash
/llm_debate_argument_evaluator/
│
├── /main/
│   ├── core.py                             # Central orchestrator for user interactions, invoking services
```

## Features

- Argument generation with variability across subcategories
- Evaluation of arguments using multiple LLMs (e.g., ChatGPT, Claude)
- Memoization and semantic caching for efficient processing
- Asynchronous evaluation and processing
- Visualization of tree with color-coded nodes based on evaluation scores
- Dynamic model selection and injection

## Getting Started

Run 'pip install -r requirements.txt' to install the dependencies.
