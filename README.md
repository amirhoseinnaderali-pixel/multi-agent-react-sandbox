# ReAct Docker Sandbox

A multi-agent problem-solving system that uses the ReAct (Reasoning + Acting) methodology to solve programming problems. The system leverages multiple AI agents (24 agents by default) to generate and test solutions in isolated Docker containers or subprocess sandboxes.

## 🚀 Features

- **Multi-Agent Architecture**: Uses 24 different AI agents to solve problems
- **ReAct Methodology**: Implements Reasoning-Acting-Observation loops for iterative problem solving
- **Docker Sandbox**: Executes code in isolated Docker containers for security
- **Fallback Support**: Automatically falls back to subprocess sandbox if Docker is unavailable
- **Test Case Validation**: Validates solutions against test cases
- **Iterative Refinement**: Each agent can refine solutions up to 3 iterations based on error feedback

## 📋 Requirements

- Python 3.9+
- Docker (optional, for containerized execution)
- Google AI API key (for Gemini models)
- Required Python packages (see Installation)

## 🔧 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd red
```

2. Install dependencies:
```bash
pip install docker google-generativeai psutil
```

3. Set up configuration:
```bash
cp config.json.example config.json
```

4. Edit `config.json` and add your Google AI API keys:
```json
{
  "apis": [
    {
      "agent_id": "api_1",
      "type": "google",
      "key": "YOUR_API_KEY_HERE",
      "model": "gemini-2.5-pro"
    }
  ],
  "test_cases": [...]
}
```

## 📖 Usage

1. Create a problem file (`problem_example.txt`) with your problem description:
```
Problem: Calculate factorial of a number

Write a Python function that calculates the factorial of a non-negative integer n.
...
```

2. Run the main script:
```bash
python react_docker.py
```

The script will:
- Load agents from `config.json`
- Read the problem from `problem_example.txt`
- Each agent attempts to solve the problem using ReAct methodology
- Solutions are tested in Docker containers (or subprocess if Docker unavailable)
- Results are saved to `results2.json`

## 🏗️ Architecture

### Components

- **`react_docker.py`**: Main script that orchestrates the multi-agent system
- **`api_client.py`**: Google AI API client for calling Gemini models
- **`sandbox.py`**: Code execution sandbox (Docker or subprocess)
- **`config.json`**: Configuration file with API keys and test cases

### ReAct Loop

Each agent follows this iterative process:

1. **Reasoning**: Analyze the problem
2. **Action**: Generate Python code
3. **Observation**: Execute code in sandbox and observe results
4. **Refinement**: If errors occur, refine the solution (up to 3 iterations)

### Execution Modes

- **Docker Mode** (preferred): Executes code in isolated Docker containers with resource limits
- **Subprocess Mode** (fallback): Executes code in subprocess with memory/time limits

## 📊 Output

Results are saved to `results2.json` with the following structure:

```json
{
  "total_solutions": 24,
  "total_agents": 24,
  "solutions_per_agent": 1,
  "total_iterations": 48,
  "avg_iterations_per_solution": 2.0,
  "solutions": [
    {
      "agent_id": "api_1",
      "solution_number": 1,
      "iterations": 2,
      "code": "...",
      "sandbox_result": {
        "success": true,
        "output": "...",
        "error": "",
        "execution_time": 0.15
      }
    }
  ]
}
```

## 🔒 Security

- Code execution is isolated in Docker containers or subprocess sandboxes
- Resource limits: 512MB memory, 30 seconds timeout
- Network access disabled in Docker mode
- Temporary files are automatically cleaned up

## 🛠️ Configuration

### Adding More Agents

Edit `config.json` and add more agent configurations:

```json
{
  "agent_id": "api_N",
  "type": "google",
  "key": "YOUR_API_KEY",
  "model": "gemini-2.5-pro"
}
```

### Test Cases

Define test cases in `config.json`:

```json
{
  "test_cases": [
    {
      "input": "5\n",
      "expected_output": "120"
    }
  ]
}
```

## 📝 Notes

- The system automatically detects Docker availability
- If Docker is not available, it falls back to subprocess execution
- Each agent can make up to 3 attempts to solve a problem
- Solutions are validated against test cases

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## ⚠️ Disclaimer

This tool executes arbitrary code. Use with caution and only run code from trusted sources. The Docker sandbox provides isolation, but always review code before execution.

