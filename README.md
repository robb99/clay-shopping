# clay-shopping 🛒

A CLI tool to manage shopping lists via Apple Reminders. Perfect for adding items to a shared family grocery list from the command line.

## Features

- 📋 **List Management** - View all your reminder lists
- 🛒 **Shopping Lists** - Add, complete, and remove items from any list
- ✅ **Completion Tracking** - Mark items as done, see completed items
- 📄 **JSON Output** - Script-friendly output for automation
- 🔗 **Native Integration** - Uses Apple Reminders app directly

## Installation

```bash
# Link to tools for easy access
ln -s /path/to/projects/clay-shopping/clay_shopping.py tools/clay_shopping.py
```

## Usage

### List all reminder lists
```bash
python3 tools/clay_shopping.py lists
```

### Show items in Grocery list
```bash
python3 tools/clay_shopping.py list
python3 tools/clay_shopping.py list --list "Grocery"
python3 tools/clay_shopping.py list --all   # Include completed items
```

### Add items
```bash
python3 tools/clay_shopping.py add "Milk"
python3 tools/clay_shopping.py add "Eggs" --list "Grocery"
python3 tools/clay_shopping.py add "Bread" -l "Grocery"
```

### Mark items complete
```bash
python3 tools/clay_shopping.py complete 1    # By number
python3 tools/clay_shopping.py complete "x-apple-reminder://..."
```

### Remove items
```bash
python3 tools/clay_shopping.py remove 3
python3 tools/clay_shopping.py remove "x-apple-reminder://..."
```

### Clear completed items
```bash
python3 tools/clay_shopping.py clear
python3 tools/clay_shopping.py clear --list "Grocery"
```

### JSON output (for scripting)
```bash
python3 tools/clay_shopping.py --json list
python3 tools/clay_shopping.py --json add "Apples"
```

## Examples

**Add items while chatting:**
> "Add milk and eggs to the shopping list"
```
clay: Added 'Milk' to Grocery
clay: Added 'Eggs' to Grocery
```

**Check what's needed:**
```
🛒 Grocery:
  1. ⬜ Bread
  2. ⬜ Milk
  3. ⬜ Eggs

  (3 items)
```

**Mark items done:**
```
clay: ✅ Item marked as complete
```

## Requirements

- macOS (Apple Reminders app)
- Python 3.7+

## How It Works

Uses AppleScript via `osascript` to communicate with the Reminders app. This means:
- No API tokens needed
- Works with any Reminders lists you already have
- Items sync to all your Apple devices via iCloud

## Use Cases

1. **Quick add** - "Add [item] to shopping list" during conversations
2. **Meal planning** - Add ingredients while discussing dinner
3. **Household management** - Family shares one "Grocery" list
4. **Automation** - Add items from other scripts or workflows
