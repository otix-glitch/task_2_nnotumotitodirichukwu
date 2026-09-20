import os
import sys


script_directory = os.path.dirname(os.path.abspath(__file__))
if sys.path and os.path.abspath(sys.path[0]) == script_directory:
	sys.path.pop(0)

import argparse
import json
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


DEFAULT_FILE = Path(__file__).with_name("expenses.json")


def load_expenses(file_path):
	if not file_path.exists():
		return []

	try:
		with file_path.open("r", encoding="utf-8") as file:
			expenses = json.load(file)
	except (json.JSONDecodeError, OSError) as error:
		raise SystemExit(f"Could not read {file_path}: {error}")

	if not isinstance(expenses, list):
		raise SystemExit(f"{file_path} must contain a list of expenses.")
	return expenses


def save_expenses(file_path, expenses):
	try:
		with file_path.open("w", encoding="utf-8") as file:
			json.dump(expenses, file, indent=2)
	except OSError as error:
		raise SystemExit(f"Could not save {file_path}: {error}")


def amount_to_cents(amount):
	try:
		value = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
	except InvalidOperation:
		raise argparse.ArgumentTypeError("amount must be a number, for example 12.50")

	if value <= 0:
		raise argparse.ArgumentTypeError("amount must be greater than zero")
	return int(value * 100)


def format_money(cents):
	return f"${cents / 100:.2f}"


def add_expense(args, file_path):
	expenses = load_expenses(file_path)
	next_id = max((expense["id"] for expense in expenses), default=0) + 1
	expense = {
		"id": next_id,
		"amount_cents": args.amount,
		"category": args.category,
		"description": args.description,
		"date": args.date,
	}
	expenses.append(expense)
	save_expenses(file_path, expenses)
	print(f"Added expense #{next_id}: {format_money(args.amount)}")


def list_expenses(args, file_path):
	expenses = load_expenses(file_path)
	if args.category:
		expenses = [expense for expense in expenses if expense["category"].lower() == args.category.lower()]

	if not expenses:
		print("No expenses found.")
		return

	print(f"{'ID':>3}  {'Date':<10}  {'Category':<15}  {'Amount':>10}  Description")
	print("-" * 65)
	for expense in expenses:
		print(
			f"{expense['id']:>3}  {expense['date']:<10}  "
			f"{expense['category']:<15}  {format_money(expense['amount_cents']):>10}  "
			f"{expense['description']}"
		)


def show_summary(args, file_path):
	expenses = load_expenses(file_path)
	if not expenses:
		print("No expenses found.")
		return

	totals = {}
	for expense in expenses:
		category = expense["category"]
		totals[category] = totals.get(category, 0) + expense["amount_cents"]

	total = sum(totals.values())
	print(f"Total spent: {format_money(total)}")
	print("By category:")
	for category, amount in sorted(totals.items()):
		print(f"  {category}: {format_money(amount)}")


def delete_expense(args, file_path):
	expenses = load_expenses(file_path)
	remaining = [expense for expense in expenses if expense["id"] != args.id]
	if len(remaining) == len(expenses):
		raise SystemExit(f"No expense with ID {args.id} was found.")

	save_expenses(file_path, remaining)
	print(f"Deleted expense #{args.id}.")


def run_interactive(file_path):
	while True:
		print("\n--- EXPENSE TRACKER ---")
		print("1. Add expense")
		print("2. List expenses")
		print("3. Show summary")
		print("4. Delete expense")
		print("5. Exit")
		choice = input("Choose an option: ").strip()

		if choice == "1":
			try:
				amount = amount_to_cents(input("Amount: ").strip())
			except argparse.ArgumentTypeError as error:
				print(f"Error: {error}")
				continue
			category = input("Category: ").strip() or "Other"
			description = input("Description: ").strip() or "No description"
			expense = argparse.Namespace(
				amount=amount,
				category=category,
				description=description,
				date=input(f"Date [{date.today()}]: ").strip() or str(date.today()),
			)
			add_expense(expense, file_path)
		elif choice == "2":
			list_expenses(argparse.Namespace(category=None), file_path)
		elif choice == "3":
			show_summary(argparse.Namespace(), file_path)
		elif choice == "4":
			try:
				expense_id = int(input("Expense ID to delete: ").strip())
				delete_expense(argparse.Namespace(id=expense_id), file_path)
			except ValueError:
				print("Error: ID must be a whole number.")
		elif choice == "5":
			print("Goodbye!")
			return
		else:
			print("Please choose a number from 1 to 5.")


def build_parser():
	parser = argparse.ArgumentParser(description="Track personal expenses.")
	parser.add_argument("--file", type=Path, default=DEFAULT_FILE, help="JSON data file")
	subparsers = parser.add_subparsers(dest="command")

	add_parser = subparsers.add_parser("add", help="add an expense")
	add_parser.add_argument("amount", type=amount_to_cents, help="amount, for example 12.50")
	add_parser.add_argument("category", help="expense category")
	add_parser.add_argument("description", help="what the expense was for")
	add_parser.add_argument("--date", default=str(date.today()), help="date in YYYY-MM-DD format")

	list_parser = subparsers.add_parser("list", help="list expenses")
	list_parser.add_argument("--category", help="only show one category")
	subparsers.add_parser("summary", help="show spending totals")

	delete_parser = subparsers.add_parser("delete", help="delete an expense")
	delete_parser.add_argument("id", type=int, help="expense ID")
	return parser


def main():
	parser = build_parser()
	args = parser.parse_args()
	if not args.command:
		run_interactive(args.file)
	elif args.command == "add":
		add_expense(args, args.file)
	elif args.command == "list":
		list_expenses(args, args.file)
	elif args.command == "summary":
		show_summary(args, args.file)
	elif args.command == "delete":
		delete_expense(args, args.file)


if __name__ == "__main__":
	main()
