#!/usr/bin/env python3
"""
clay-shopping - Apple Reminders CLI for shared shopping lists

A CLI tool to manage shopping lists via Apple Reminders. 
Uses native AppleScript to interact with the Reminders app.
"""

import argparse
import json
import subprocess
import sys
from typing import Optional


def run_applescript(script: str) -> str:
    """Execute AppleScript and return output."""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript error: {result.stderr}")
    return result.stdout.strip()


def get_lists() -> list[str]:
    """Get all reminder lists."""
    script = 'tell application "Reminders" to get name of every list'
    output = run_applescript(script)
    if not output:
        return []
    # Split by ", " but handle commas in list names
    return [s.strip() for s in output.split(", ")]


def get_list_id(list_name: str) -> Optional[str]:
    """Get the ID of a list by name."""
    script = f'''tell application "Reminders"
        set listName to "{list_name}"
        set allLists to every list
        repeat with aList in allLists
            if name of aList is equal to listName then
                return id of aList
            end if
        end repeat
        return ""
    end tell'''
    result = run_applescript(script)
    return result if result else None


def get_items(list_name: str, include_completed: bool = False) -> list[dict]:
    """Get all items in a list."""
    list_id = get_list_id(list_name)
    if not list_id:
        return []
    
    script = f'''tell application "Reminders"
        set theList to list id "{list_id}"
        set allReminders to every reminder in theList
        set itemList to {{}}
        repeat with i from 1 to count allReminders
            set aReminder to item i of allReminders
            set remName to name of aReminder
            set remCompleted to completed of aReminder
            set remId to id of aReminder
            set end of itemList to remId & "||" & remName & "||" & (remCompleted as text)
        end repeat
        set AppleScript's text item delimiters to "|||"
        return itemList as text
    end tell'''
    
    output = run_applescript(script)
    if not output:
        return []
    
    items = []
    for line in output.split("|||"):
        parts = line.strip().split("||")
        if len(parts) >= 3:
            item_id, name, completed = parts[0], parts[1], parts[2].lower() == "true"
            if include_completed or not completed:
                items.append({
                    "id": item_id,
                    "name": name,
                    "completed": completed
                })
    
    return items


def add_item(list_name: str, item_name: str) -> dict:
    """Add an item to a list."""
    list_id = get_list_id(list_name)
    if not list_id:
        raise ValueError(f"List '{list_name}' not found")
    
    # Escape quotes in item name
    escaped_name = item_name.replace('"', '\\"')
    
    script = f'''tell application "Reminders"
        set theList to list id "{list_id}"
        tell theList
            make new reminder with properties {{name:"{escaped_name}"}}
        end tell
    end tell'''
    
    run_applescript(script)
    return {"status": "added", "item": item_name, "list": list_name}


def complete_item(item_id: str) -> dict:
    """Mark an item as complete."""
    script = f'''tell application "Reminders"
        set theReminder to reminder id "{item_id}"
        set completed of theReminder to true
    end tell'''
    
    run_applescript(script)
    return {"status": "completed", "item_id": item_id}


def remove_item(item_id: str) -> dict:
    """Remove an item from a list."""
    script = f'''tell application "Reminders"
        set theReminder to reminder id "{item_id}"
        delete theReminder
    end tell'''
    
    run_applescript(script)
    return {"status": "removed", "item_id": item_id}


def clear_completed(list_name: str) -> dict:
    """Clear all completed items from a list."""
    list_id = get_list_id(list_name)
    if not list_id:
        raise ValueError(f"List '{list_name}' not found")
    
    script = f'''tell application "Reminders"
        set theList to list id "{list_id}"
        set allReminders to every reminder in theList
        repeat with aReminder in allReminders
            if completed of aReminder is true then
                delete aReminder
            end if
        end repeat
    end tell'''
    
    run_applescript(script)
    return {"status": "cleared", "list": list_name}


def print_lists(json_output: bool = False):
    """Print all reminder lists."""
    lists = get_lists()
    if json_output:
        print(json.dumps({"lists": lists}))
    else:
        if lists:
            print("📋 Reminder Lists:")
            for lst in lists:
                print(f"  • {lst}")
        else:
            print("No reminder lists found")


def print_items(list_name: str, json_output: bool = False, include_completed: bool = False):
    """Print items in a list."""
    items = get_items(list_name, include_completed)
    
    if json_output:
        print(json.dumps({
            "list": list_name,
            "items": items,
            "count": len(items)
        }))
    else:
        if not items:
            print(f"🛒 {list_name}: (empty)")
            return
        
        print(f"🛒 {list_name}:")
        for i, item in enumerate(items, 1):
            status = "✅" if item["completed"] else "⬜"
            print(f"  {i}. {status} {item['name']}")
        print(f"\n  ({len(items)} items)")


def main():
    parser = argparse.ArgumentParser(
        description="clay-shopping - Manage shopping lists via Apple Reminders"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # lists command
    subparsers.add_parser("lists", help="Show all reminder lists")
    
    # list command (show items)
    list_parser = subparsers.add_parser("list", help="Show items in a list")
    list_parser.add_argument("--list", "-l", default="Grocery", help="List name (default: Grocery)")
    list_parser.add_argument("--all", "-a", action="store_true", help="Include completed items")
    
    # add command
    add_parser = subparsers.add_parser("add", help="Add item to list")
    add_parser.add_argument("item", help="Item to add")
    add_parser.add_argument("--list", "-l", default="Grocery", help="List name (default: Grocery)")
    
    # complete command
    complete_parser = subparsers.add_parser("complete", help="Mark item as complete")
    complete_parser.add_argument("item", help="Item number or ID")
    
    # remove command
    remove_parser = subparsers.add_parser("remove", help="Remove item")
    remove_parser.add_argument("item", help="Item number or ID")
    
    # clear command
    clear_parser = subparsers.add_parser("clear", help="Clear completed items")
    clear_parser.add_argument("--list", "-l", default="Grocery", help="List name (default: Grocery)")
    
    args = parser.parse_args()
    
    try:
        if args.command == "lists" or args.command is None:
            print_lists(args.json)
            
        elif args.command == "list":
            print_items(args.list, args.json, args.all)
            
        elif args.command == "add":
            result = add_item(args.list, args.item)
            if args.json:
                print(json.dumps(result))
            else:
                print(f"✅ Added '{args.item}' to {args.list}")
                
        elif args.command == "complete":
            # Support both item number and item ID
            item_ref = args.item
            if item_ref.isdigit():
                # It's a number - get the item ID from the list
                items = get_items("Grocery", include_completed=True)
                idx = int(item_ref) - 1
                if 0 <= idx < len(items):
                    item_ref = items[idx]["id"]
                else:
                    print(f"Error: Invalid item number {args.item}", file=sys.stderr)
                    sys.exit(1)
            result = complete_item(item_ref)
            if args.json:
                print(json.dumps(result))
            else:
                print("✅ Item marked as complete")
                
        elif args.command == "remove":
            item_ref = args.item
            if item_ref.isdigit():
                items = get_items("Grocery", include_completed=True)
                idx = int(item_ref) - 1
                if 0 <= idx < len(items):
                    item_ref = items[idx]["id"]
                else:
                    print(f"Error: Invalid item number {args.item}", file=sys.stderr)
                    sys.exit(1)
            result = remove_item(item_ref)
            if args.json:
                print(json.dumps(result))
            else:
                print("🗑️ Item removed")
                
        elif args.command == "clear":
            result = clear_completed(args.list)
            if args.json:
                print(json.dumps(result))
            else:
                print(f"✅ Cleared completed items from {args.list}")
                
        else:
            parser.print_help()
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
