# Day 2 – Getting Productive with **Promptfoo**

Welcome to Day 2 of **How to Test AI Apps**.  
Yesterday you explored common failure modes of LLMs; today you’ll learn how to **codify those checks in Promptfoo** so tests run automatically.


Here is the official [Promptfoo documentation](https://www.promptfoo.dev/docs/intro/). Always refer to it whenever you need details.

---

## 0  📦 Install Promptfoo

Here is the official [Promptfoo documentation](https://www.promptfoo.dev/docs/intro/). Always refer to it whenever you need details.

Pick **one** of the methods below (all give the same CLI):

| Package manager | Command |
|-----------------|---------|
| **npm** (global) | `npm install -g promptfoo` |
| **npx** (one-shot) | `npx promptfoo@latest` |
| **Homebrew** | `brew install promptfoo` |

Verify it works:

```bash
promptfoo --version
```

---


##  🛠️ Quick Project Setup

1. **Create a workspace folder** (anywhere you like) and move into it:

   ```bash
   # macOS / Linux
   mkdir promptfoo-demo && cd promptfoo-demo
   ```
   ```powershell
   # Windows (Command Prompt)
   mkdir promptfoo-demo && cd promptfoo-demo
   ```

2. **Initialize Promptfoo** in the empty folder:

   ```bash
   promptfoo init
   ```

   This scaffolds a minimal **`promptfooconfig.yaml`**.  
   If the file appears, Promptfoo is now configured for this directory. 🎉

3. **Run your first evaluation**:

   ```bash
   promptfoo eval
   ```

   > On the first run you’ll likely see errors about missing API keys.

4. **Set your OpenAI key**, then rerun the evaluation:

   ```bash
   # macOS / Linux
   export OPENAI_API_KEY="sk-••••••••••"
   ```
   ```powershell
   # Windows (Command Prompt)
   set OPENAI_API_KEY=sk-********
   ```

   ```bash
   promptfoo eval      # Errors should now be 0
   ```

5. **Open the results in a browser** :

   ```bash
   promptfoo view
   ```

   Press **`Ctrl + C`** in the terminal to shut down the local web server when you’re done.


---


## 1  🎯 Prompts

Learn how Promptfoo sources and expands prompts.

| Topic | Goal |
|-------|------|
| **Text prompts** | One-liner prompts in the config file |
| **Multiline prompts** | Use the `|` block syntax for long instructions |
| **Variable prompts** | Inject `${variable}` placeholders at runtime |
| **File-based prompts** | Keep large prompts in separate `.prompt` / `.md` files |

---

## 2  🔌 Providers

Connect Promptfoo to models.

| Topic | What you’ll practice |
|-------|----------------------|
| **Configuration** | Set `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc., via `providers:` block or env vars |
| **Local model** | Point a provider at an **LM Studio** endpoint running on your laptop |



---

## 3  📏 Assertions & Metrics

Automate pass/fail judgment.

### 3.1 Deterministic Assertions  
*Exact string rules.*

| Assertion | Purpose |
|-----------|---------|
| `contains` | Output must include a keyword/phrase |
| `regex` | Output must match a regular expression |

### 3.2 Model-graded Metrics  
*Let an LLM grade another LLM.*

| Metric | Checks |
|--------|--------|
| `answer-relevance` | Does the answer stay on topic? |
| `factuality` | Is the answer factually correct? |
| `llm-rubric` | Custom rubric you provide in prose |


---

Happy testing! 🚀
