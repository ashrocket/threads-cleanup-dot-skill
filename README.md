# Threads Cleanup for OpenAI dots, ChatGPT, and Codex

A reusable skill for clearing an account owner's Threads posts, replies, and saved items without deleting the account. It includes a checkpointed Playwright script that uses TypeSafe Jev for narrow menu-label decisions. The script uses the regular Threads website UI.

OpenAI dots are personal agents. This repository shares the workflow a dot can use; it does not transfer anyone's dot identity or signed-in browser session.

The canonical skill is in [`plugins/threads-cleanup/skills/threads-cleanup/`](plugins/threads-cleanup/skills/threads-cleanup/SKILL.md). This repository also packages it as an [OpenAI plugin](plugins/threads-cleanup/plugin.json), with a [repo marketplace](.agents/plugins/marketplace.json). The older `threads-cleanup/` path remains a symlink for existing Codex projects. A dot needs a connected local computer to run the included script; it may use its own browser to follow the skill's UI workflow when local execution is unavailable. The account owner signs in privately and authorizes the exact deletion scope. No browser profile, checkpoint, API key, or personal data is included here.

Install in Codex:

```bash
codex plugin marketplace add ashrocket/threads-cleanup-dot-skill --ref main
codex plugin add threads-cleanup@threads-cleanup-community
```

Start a new Codex chat after installation so its skill inventory refreshes. Alternatively, clone the repository and start Codex in its root to discover `.agents/skills/threads-cleanup`, or copy the canonical skill folder into another project's `.agents/skills`. The [skill ZIP](https://github.com/ashrocket/threads-cleanup-dot-skill/releases/latest/download/threads-cleanup-skill.zip) remains available for direct upload to ChatGPT Skills where supported.

See the skill's setup and recovery instructions before running it. The script requires Python, Chrome, Playwright, and a TypeSafe API key. It previews by default, verifies the signed-in username, records pending actions before clicking, and stops on uncertain results.

The example browser tests use simulated Threads pages and make no real account changes.

To give this to your dot, install and enable the plugin or skill in ChatGPT, connect your computer if you want the script to run locally, and send a request like:

> Use the Threads cleanup skill to clear my own @USERNAME posts, replies, and saved items. Keep my account. I authorize those deletions and unsaves. Verify each result, keep a resumable checkpoint, and tell me when every requested feed is empty. Ask me to sign in privately if needed.

The skill requires explicit invocation; merely mentioning Threads will not start a cleanup. Its default prompt previews first and requires the owner to name the deletion scope before execution. A new dot task needs the account, scope, and checkpoint context in its own message; it does not inherit an unrelated Codex conversation. Review progress in the dot's Activity view.

This is an independent community workflow, not an official Threads, TypeSafe, or OpenAI product.

References: [OpenAI dots](https://learn.chatgpt.com/docs/dots/tasks-and-memory), [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins), [OpenAI skill sharing](https://help.openai.com/en/articles/20001066-skills-in-chatgpt), [TypeSafe docs](https://docs.typesafe.ai/llms.txt).
