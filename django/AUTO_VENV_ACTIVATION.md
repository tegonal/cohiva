# Auto Virtual Environment Activation

This guide shows how to automatically activate the Python virtual environment when entering the project directory.

> **TL;DR:** Install `direnv`, add one line to your shell config, reload, and run `direnv allow .` in the project directory. Done!

---

## Quick Reference

| Platform | Shell | Config File | Install Command |
|----------|-------|-------------|-----------------|
| **macOS** | Zsh | `~/.zshrc` | `brew install direnv` |
| **macOS** | Bash | `~/.bash_profile` | `brew install direnv` |
| **Linux (Ubuntu/Debian)** | Bash | `~/.bashrc` | `sudo apt install direnv` |
| **Linux (Fedora/RHEL)** | Bash | `~/.bashrc` | `sudo dnf install direnv` |
| **Linux (Arch)** | Bash | `~/.bashrc` | `sudo pacman -S direnv` |

**Shell hook command:**
- **Zsh:** `eval "$(direnv hook zsh)"`
- **Bash:** `eval "$(direnv hook bash)"`
- **Fish:** `direnv hook fish | source`

---

## Quick Start

### macOS

```bash
# 1. Install direnv
brew install direnv

# 2. Add to your shell (Zsh is default on macOS)
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc

# 3. Reload shell
source ~/.zshrc

# 4. Allow the project
cd /path/to/cohiva/django
direnv allow .

# Done! Test it:
cd ~
cd /path/to/cohiva/django  # venv should auto-activate
```

### Linux (Ubuntu/Debian)

```bash
# 1. Install direnv
sudo apt update
sudo apt install direnv

# 2. Add to your shell (usually bash)
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc

# 3. Reload shell
source ~/.bashrc

# 4. Allow the project
cd /path/to/cohiva/django
direnv allow .

# Done! Test it:
cd ~
cd /path/to/cohiva/django  # venv should auto-activate
```

---

## Option 1: direnv (Recommended)

`direnv` is a shell extension that loads/unloads environment variables based on the current directory.

### Installation

#### macOS
```bash
# Using Homebrew (recommended)
brew install direnv

# Alternative: Download binary
curl -sfL https://direnv.net/install.sh | bash
```

#### Linux

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install direnv
```

**Fedora/RHEL:**
```bash
sudo dnf install direnv
```

**Arch Linux:**
```bash
sudo pacman -S direnv
```

**From source (any Linux):**
```bash
curl -sfL https://direnv.net/install.sh | bash
```

### Shell Integration

Add the appropriate hook to your shell configuration file:

#### Zsh (default on macOS Catalina+)
```bash
# Add to ~/.zshrc
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc

# Reload
source ~/.zshrc
```

#### Bash
```bash
# macOS: Add to ~/.bash_profile
echo 'eval "$(direnv hook bash)"' >> ~/.bash_profile
source ~/.bash_profile

# Linux: Add to ~/.bashrc
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
source ~/.bashrc
```

#### Fish
```bash
# Add to ~/.config/fish/config.fish
echo 'direnv hook fish | source' >> ~/.config/fish/config.fish

# Reload
source ~/.config/fish/config.fish
```

### Enable for This Project

```bash
cd /path/to/cohiva/django
direnv allow .
```

You should see:
```
direnv: loading ~/path/to/cohiva/django/.envrc
```

### How It Works

- The `.envrc` file is automatically loaded by direnv when you enter the directory
- It searches for the venv in common locations and activates it
- It also loads `.env` file if present
- When you leave the directory, the venv is automatically deactivated

### Example Usage

```bash
# Outside project - no venv active
~ $ python --version
Python 3.9.6

# Enter project - venv auto-activates
~ $ cd projects/cohiva/django
direnv: loading ~/projects/cohiva/django/.envrc
(cohiva-dev) ~/projects/cohiva/django $ python --version
Python 3.11.7

# Leave project - venv auto-deactivates
(cohiva-dev) ~/projects/cohiva/django $ cd ~
direnv: unloading
~ $ python --version
Python 3.9.6
```

## Option 2: Shell Function (Manual)

Add this to your `~/.bashrc` or `~/.zshrc`:

```bash
# Auto-activate Python venv based on .venv-path file
auto_activate_venv() {
    if [ -f ".venv-path" ]; then
        local venv_path=$(head -n 1 .venv-path | sed 's/#.*//' | xargs)
        # Expand tilde to home directory
        venv_path="${venv_path/#\~/$HOME}"

        if [ -f "$venv_path/bin/activate" ]; then
            # Only activate if not already in this venv
            if [ -z "$VIRTUAL_ENV" ] || [ "$VIRTUAL_ENV" != "$venv_path" ]; then
                source "$venv_path/bin/activate"
                echo "✓ Activated venv: $venv_path"
            fi
        fi
    fi
}

# Run on every directory change
chpwd_functions=(${chpwd_functions[@]} "auto_activate_venv")  # Zsh
PROMPT_COMMAND="auto_activate_venv; $PROMPT_COMMAND"          # Bash
```

After adding, reload your shell:
```bash
source ~/.bashrc  # or ~/.zshrc
```

## Option 3: VS Code

VS Code can automatically detect and activate virtual environments.

1. Open project in VS Code
2. Press `Cmd/Ctrl + Shift + P`
3. Type "Python: Select Interpreter"
4. Choose the venv at `~/.venv/cohiva-dev` (or your custom path)

VS Code will automatically activate this venv in its integrated terminal.

## Option 4: PyCharm

PyCharm can automatically activate the project's virtual environment.

1. Open project in PyCharm
2. Go to: Settings/Preferences → Project → Python Interpreter
3. Click the gear icon → Add → Existing Environment
4. Browse to `~/.venv/cohiva-dev/bin/python` (or your custom path)
5. Check "Make available to all projects" if desired

PyCharm will automatically activate this venv in its terminal.

## Verification

To verify automatic activation is working:

1. Exit the project directory:
   ```bash
   cd ~
   echo $VIRTUAL_ENV  # Should be empty or different venv
   ```

2. Enter the project directory:
   ```bash
   cd /path/to/cohiva/django
   echo $VIRTUAL_ENV  # Should show: /Users/you/.venv/cohiva-dev
   ```

3. Check Python version:
   ```bash
   python --version  # Should show the venv's Python version
   which python      # Should show path inside venv
   ```

## Troubleshooting

### direnv: Error "direnv is blocked"

**Problem:** When entering the directory, you see:
```
direnv: error /path/to/cohiva/django/.envrc is blocked. Run `direnv allow` to approve its content
```

**Solution:**
```bash
cd /path/to/cohiva/django
direnv allow .
```

This is a security feature - direnv requires explicit approval before loading `.envrc` files.

---

### direnv not loading automatically

**Problem:** No message when entering the directory.

**Check 1:** Is direnv installed?
```bash
direnv --version
# Should show: 2.32.1 (or similar)
```

**macOS:** Install with `brew install direnv`
**Linux:** Install with `sudo apt install direnv`

**Check 2:** Is the hook configured?
```bash
# For Zsh (macOS default)
grep direnv ~/.zshrc

# For Bash (Linux default)
grep direnv ~/.bashrc
```

Should show: `eval "$(direnv hook zsh)"` or similar

**Check 3:** Did you reload your shell?
```bash
# For Zsh
source ~/.zshrc

# For Bash (macOS)
source ~/.bash_profile

# For Bash (Linux)
source ~/.bashrc

# OR: Just open a new terminal window
```

---

### Wrong shell configuration file

**macOS users:** The default shell changed to Zsh in macOS Catalina (10.15).

**Check your shell:**
```bash
echo $SHELL
# /bin/zsh  → Use ~/.zshrc
# /bin/bash → Use ~/.bash_profile (macOS) or ~/.bashrc (Linux)
```

**If you see `/bin/zsh`**, add direnv hook to `~/.zshrc`:
```bash
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
source ~/.zshrc
```

**If you see `/bin/bash`**, add direnv hook to:
- **macOS:** `~/.bash_profile`
- **Linux:** `~/.bashrc`

```bash
# macOS
echo 'eval "$(direnv hook bash)"' >> ~/.bash_profile
source ~/.bash_profile

# Linux
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
source ~/.bashrc
```

---

### Virtual environment path incorrect

**Problem:** direnv loads but venv doesn't activate.

**Check the venv path:**
```bash
cat .venv-path
# Should show something like: ~/.venv/cohiva-dev
```

**Verify the venv exists:**
```bash
ls -la ~/.venv/cohiva-dev/bin/activate
# Should show the activate script
```

**If path is wrong:**
```bash
# Edit .envrc and update the path
nano .envrc  # or vim, code, etc.

# Then reload
direnv allow .
```

---

### Shell function not working

**Problem:** Custom shell function doesn't activate venv.

**Check 1:** Verify the function is loaded
```bash
# For Zsh
type auto_activate_venv

# For Bash
declare -f auto_activate_venv
```

**Check 2:** Verify .venv-path file exists
```bash
cat .venv-path
```

**Check 3:** Test the function manually
```bash
auto_activate_venv
echo $VIRTUAL_ENV
```

---

### VS Code not detecting venv

**Problem:** Integrated terminal doesn't activate venv.

**Solution 1:** Select interpreter manually
1. Press `Cmd/Ctrl + Shift + P`
2. Type "Python: Select Interpreter"
3. Choose the venv path (e.g., `~/.venv/cohiva-dev/bin/python`)

**Solution 2:** Check Python extension
1. Verify Python extension is installed
2. Reload window: `Cmd/Ctrl + Shift + P` → "Developer: Reload Window"

**Solution 3:** Check settings.json
```json
{
  "python.defaultInterpreterPath": "~/.venv/cohiva-dev/bin/python",
  "python.terminal.activateEnvironment": true
}
```

---

### PyCharm not activating venv

**Problem:** PyCharm terminal doesn't use the venv.

**Solution:**
1. Go to: `Settings/Preferences` → `Project` → `Python Interpreter`
2. Click the gear icon → `Add...` → `Existing Environment`
3. Browse to: `~/.venv/cohiva-dev/bin/python`
4. Apply and restart PyCharm

---

### Permission denied on .envrc

**Problem:**
```bash
bash: ./.envrc: Permission denied
```

**Solution:**
```bash
chmod +x .envrc
direnv allow .
```

---

### Verification Commands

Use these to verify everything is working:

```bash
# 1. Check direnv is installed
direnv --version

# 2. Check shell hook is loaded
echo $SHELL
grep direnv ~/.zshrc  # or ~/.bashrc

# 3. Check .envrc exists
ls -la .envrc

# 4. Check .venv-path points to correct location
cat .venv-path

# 5. Check venv exists
ls -la ~/.venv/cohiva-dev/bin/activate

# 6. Test activation manually
cd ~
cd /path/to/cohiva/django
echo $VIRTUAL_ENV  # Should show venv path
python --version   # Should show venv Python version
which python       # Should show path inside venv
```

---

## Platform-Specific Notes

### macOS

- **Default shell:** Zsh (since macOS Catalina 10.15)
- **Config file:** `~/.zshrc`
- **Homebrew paths:**
  - Apple Silicon: `/opt/homebrew/`
  - Intel: `/usr/local/`

### Linux (Ubuntu/Debian)

- **Default shell:** Bash
- **Config file:** `~/.bashrc`
- **Common issue:** Make sure to use `~/.bashrc` not `~/.bash_profile`

### Linux (Fedora/RHEL)

- **Default shell:** Bash
- **Config file:** `~/.bashrc`
- **Install:** `sudo dnf install direnv`

---

## Custom Virtual Environment Path

If you created your venv in a different location:

### For direnv
Edit `.envrc` and update the path:
```bash
nano .envrc
# Change the venv path to your custom location
# Then:
direnv allow .
```

### For shell function
Edit `.venv-path`:
```bash
echo "/your/custom/path/to/venv" > .venv-path
```

### For VS Code/PyCharm
Select the new interpreter path in settings (see troubleshooting sections above).
