# Expense Tracker

A command-line Python application for recording, viewing, summarizing, and deleting personal expenses.

## Features

- Add expenses with an amount, category, description, and date.
- List all saved expenses.
- Filter expenses by category.
- View total spending and totals grouped by category.
- Delete an expense by its ID.
- Save data permanently in a JSON file.
- Store money as cents to avoid common floating-point rounding problems.

## Requirements

- Python 3.6 or newer
- No external packages

## Data Storage

By default, expenses are saved in `skills/expenses.json`, next to the Python script. The file is created automatically when the first expense is added.

Each expense contains an ID, amount, category, description, and date:

```json
{
  "id": 1,
  "amount_cents": 1250,
  "category": "Food",
  "description": "Lunch",
  "date": "2026-09-20"
}
```

## Interactive Mode

Run the program without a command to open the menu:

```powershell
python skills/expense-tracker.py
```

The menu provides these options:

1. Add an expense
2. List expenses
3. Show a spending summary
4. Delete an expense
5. Exit

When adding an expense, the date defaults to today. An empty category is saved as `Other`, and an empty description is saved as `No description`.

## Command-Line Usage

### Add an expense

```powershell
python skills/expense-tracker.py add 12.50 Food Lunch
```

Use `--date` to provide a different date:

```powershell
python skills/expense-tracker.py add 45.00 Transport Train --date 2026-09-18
```

Amounts must be greater than zero.

### List expenses

```powershell
python skills/expense-tracker.py list
```

Filter by category:

```powershell
python skills/expense-tracker.py list --category Food
```

Category filtering is case-insensitive, so `Food`, `food`, and `FOOD` match the same expenses.

### Show a summary

```powershell
python skills/expense-tracker.py summary
```

The summary displays the total spent and a total for each category.

### Delete an expense

Use the ID shown by the `list` command:

```powershell
python skills/expense-tracker.py delete 1
```

## Use Another Data File

The `--file` option lets you use a different JSON file. Place it before the command:

```powershell
python skills/expense-tracker.py --file my-expenses.json list
python skills/expense-tracker.py --file my-expenses.json add 8.75 Coffee Breakfast
```

## Example

```text
$ python skills/expense-tracker.py add 12.50 Food Lunch
Added expense #1: $12.50

$ python skills/expense-tracker.py summary
Total spent: $12.50
By category:
  Food: $12.50
```
