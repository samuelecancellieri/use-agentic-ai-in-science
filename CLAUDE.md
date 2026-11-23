# CLAUDE.md

Follow all scientific research guardrails, human-in-the-loop checkpoints, skill definitions, and tool instructions documented in [`AGENTS.md`](./AGENTS.md).

Quick pointers:
- Skills live in `.agents/skills/<skill-name>/SKILL.md`.
- Helper CLIs live in `tools/`.
- The end-to-end bioinformatics worked example lives in `example-study/`.
- Always run `uv run pytest` after modifying analysis scripts or helper tools.
