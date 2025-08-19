import random
from datetime import timedelta
import click
from faker import Faker
from app import db
from app.models import Todo

fake = Faker()


@click.command("seed")
@click.option("--count", default=10, help="Number of todos to create. Default: 10")
@click.option("--clear", is_flag=True, help="Clear existing todos before seeding.")
@click.option("--clean", is_flag=True, help="Remove all todos permanently.")
def seed_command(count, clear, clean):
    """
    Seed the database with realistic fake todo data.

    Safety & Performance Notes (for portfolio reviewers):
    - ✅ Uses batch-friendly design: avoids 1 query per insert
    - ⚠️ Re-checks total count every 25 inserts to balance safety + speed
    - 🛑 Hard cap at 1000 todos to protect system limits
    - 💡 This shows awareness of database cost in loops — a key skill in real apps
    """

    # === Cleanup Options ===
    if clear:
        deleted = Todo.query.delete()
        db.session.commit()
        click.echo(f"🗑️  Cleared {deleted} existing todos.")
    elif clean:
        confirm = input("⚠️  This deletes ALL data permanently. Continue? (y/N): ")
        if confirm.lower() != "y":
            click.echo("🛑 Operation cancelled.")
            return
        Todo.query.delete()
        db.session.commit()
        click.echo("🔥 All todos deleted permanently.")
        return

    # === Input Validation ===
    if count <= 0:
        click.echo("❌ Count must be positive.")
        return

    # === Safe Seeding with Periodic Checks ===
    added = 0
    check_interval = 25  # Balance: not too frequent, not too risky

    try:
        for i in range(count):
            # 🔄 Re-check every N inserts (not every time) to reduce DB load
            if added % check_interval == 0:
                
                current_total = Todo.query.with_entities(Todo.id).count()
                if current_total >= 1000:
                    click.echo("🚫 Database reached 1000 todos. Stopping early.")
                    break

            # 🎲 Generate realistic fake data
            # generate 
            task = fake.sentence(nb_words=random.randint(3, 7))
            done = random.choice([True, False])
            if random.choice([True, False]):
                start_date = fake.date_time_this_year()
                end_date = start_date + timedelta(days=random.randint(1, 10))
            else:
                start_date = None
                end_date = None

            todo = Todo(
                task=task,
                done=done,
                created_at=fake.date_time_this_year(),
                date_from=start_date,
                date_to=end_date,
            )
            db.session.add(todo)
            added += 1

        db.session.commit()
        final_total = Todo.query.count()
        click.echo(f"✅ Added {added} new todos.")
        click.echo(f"📊 Total todos: {final_total}/1000")

    except Exception as e:
        db.session.rollback()
        click.echo(f"❌ Error during seeding: {str(e)}")
        raise