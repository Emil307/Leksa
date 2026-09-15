# AGENTS.md

This repository uses one shared agent framework for Claude Code and Codex. The
canonical workflow library remains under `.claude/`; Codex-specific files are
adapters, not a second copy of the framework.

## Session bootstrap

Before doing repository work:

1. Read `CLAUDE.md` completely. It is the canonical repository instruction file.
2. Read every `.claude/rules/*.md` file completely. Claude Code loads these rules
   automatically; Codex must load them explicitly.
3. Read `ProductSpecification/technology.md` for the active technology bindings
   and commands.
4. Follow the on-demand guideline table in `CLAUDE.md` before performing the
   corresponding kind of work.

Instructions in this file adapt the framework to Codex. If an adapter conflicts
with the canonical workflow, preserve the workflow semantics and use the Codex
capability that implements them.

## Codex bindings

- Repository skills are exposed through `.agents/skills`. In Codex, invoke a
  skill as `$skill-name`; existing framework prose may still call the same skill
  `/skill-name` for Claude Code.
- Project custom agents live under `.codex/agents`. When a workflow requires a
  named agent, spawn that exact custom agent and pass it the requested context.
- Follow `.claude/guidelines/platform-capabilities.md` whenever framework prose
  names a capability. Tool names such as `TaskStop`, `TaskOutput`, `Skill tool`,
  or `AskUserQuestion` describe Claude bindings only; use the equivalent Codex
  process, skill, subagent, or user-input capability.
- Obey requested concurrency: start every independent named agent before waiting
  for results, then gather all results. Do not detach work that the workflow says
  to await.
- Some review custom agents run in a strict read-only sandbox. When one sends an
  `AGENT_MILESTONE` message because it cannot append
  `infrastructure/agent-progress.log`, append that exact milestone immediately on
  the agent's behalf. This is a transport adaptation only; never grant the review
  agent broader write access.
- Do not maintain a separate `.codex` copy of rules, skills, templates, or agent
  bodies. Update the canonical `.claude` source and regenerate only the thin
  Codex agent adapters with `.codex/scripts/sync_claude_agents.py`.

## Interaction

- Respond in Russian, as required by `CLAUDE.md`.
- Keep long-running commands pollable and surface progress at intervals of no
  more than 30 seconds.
