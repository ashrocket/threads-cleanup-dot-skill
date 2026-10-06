# Threads Cleanup for OpenAI dots and Codex

A reusable skill for clearing an account owner's Threads posts, replies, and saved items without deleting the account. It includes a checkpointed Playwright script that uses TypeSafe Jev for narrow menu-label decisions. The script uses the regular Threads website UI.

The skill is in [`threads-cleanup/`](threads-cleanup/SKILL.md). Give that folder to a dot or Codex as a local skill, or [download the skill ZIP](https://github.com/ashrocket/threads-cleanup-dot-skill/releases/latest/download/threads-cleanup-skill.zip) for upload through ChatGPT Skills where supported. A dot needs a connected local computer to run the included script; it may use its own browser to follow the skill's UI workflow when local execution is unavailable. The account owner signs in privately and authorizes the exact deletion scope. No browser profile, checkpoint, API key, or personal data is included here.

See the skill's setup and recovery instructions before running it. The script requires Python, Chrome, Playwright, and a TypeSafe API key. It previews by default, verifies the signed-in username, records pending actions before clicking, and stops on uncertain results.

The example browser tests use simulated Threads pages and make no real account changes.

To give this to your dot, install the `threads-cleanup` skill from the ZIP in ChatGPT Skills, connect your computer if you want the script to run locally, and send a request like:

> Use the Threads cleanup skill to clear my own @USERNAME posts, replies, and saved items. Keep my account. I authorize those deletions and unsaves. Verify each result, keep a resumable checkpoint, and tell me when every requested feed is empty. Ask me to sign in privately if needed.

This is an independent community workflow, not an official Threads, TypeSafe, or OpenAI product.

References: [OpenAI dots guide](https://learn.chatgpt.com/docs/dots), [OpenAI skill sharing](https://help.openai.com/en/articles/20001066-skills-in-chatgpt), [TypeSafe docs](https://docs.typesafe.ai/llms.txt).
