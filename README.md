# VishAI Next

VishAI Next is a production-grade, capability-based AI Operating System.

## Architecture
The system uses a strictly layered architecture:
- `kernel`: Core lifecycle management and configuration.
- `interface`: Input/Output channels (CLI, API, Voice, GUI).
- `learning`: Adaptive capabilities (Observation, Workflow, Skills).
- `planner`, `executor`, `memory`: Cognitive sub-systems.
- `plugins`: Extensible support for external applications.
- `capabilities`: Core reusable features.

## Booting
To start the operating system:
```bash
python main.py
```

To verify the boot sequence without running the event loop:
```bash
python main.py --verify
```
