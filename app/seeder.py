import random
from datetime import timedelta
import click
from faker import Faker
from app import db
from app.models import Todo, User, UserGroup

fake = Faker()


@click.command("seed")
@click.option("--count", default=10, help="Number of todos to create. Default: 10")
@click.option("--clear", is_flag=True, help="Clear existing todo tasks before seeding.")
@click.option("--clean", is_flag=True, help="Remove all todo tasks permanently.")
def seed_command(count, clear, clean):
    """Seed the database with realistic fake todo data."""

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

    if count <= 0:
        click.echo("❌ Count must be positive.")
        return

    # === Ensure users exist ===
    users = User.query.all()
    if not users:
        # Create 3 demo users
        demo_users = [
            User(username="demo1", password="demo1", is_admin=True),
            User(username="demo2", password="demo2"),
            User(username="demo3", password="demo3"),
        ]
        db.session.add_all(demo_users)
        db.session.commit()
        users = demo_users
        click.echo("👤 Created 3 demo users (including 1 admin).")

    groups = UserGroup.query.all()
    admin_user = User.query.filter_by(is_admin=True).first()
    if not admin_user:
        admin_user = users[0]  # fallback

    added = 0
    check_interval = 25

    try:
        for i in range(count):
            if added % check_interval == 0:
                current_total = Todo.query.with_entities(Todo.id).count()
                if current_total >= 1000:
                    click.echo("🚫 Database reached 1000 todos. Stopping early.")
                    break

            # === Generate fake todo ===
            task = fake.sentence(nb_words=random.randint(3, 7))
            done = random.choice([True, False])
            if random.choice([True, False]):
                start_date = fake.date_time_this_year()
                end_date = start_date + timedelta(days=random.randint(1, 10))
            else:
                start_date, end_date = None, None

            todo = Todo(
                task=task,
                done=done,
                created_at=fake.date_time_this_year(),
                date_from=start_date,
                date_to=end_date,
                created_by=admin_user
            )

            # === Random assignment logic ===
            roll = random.choice(["user", "group", "none"])
            if roll == "user":
                todo.assigned_user = random.choice(users)
            elif roll == "group" and groups:
                todo.assigned_group = random.choice(groups)

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