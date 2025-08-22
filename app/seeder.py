import random
from datetime import timedelta
import click
from faker import Faker
from app import db
from app.models import Todo, User, UserGroup
from app.hsh import hash_password
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

    # === Ensure groups exist ===
    groups = UserGroup.query.all()
    if not groups:
        # Create demo groups
        demo_groups = [
            UserGroup(name="qa", description="Quality Assurance Team"),
            UserGroup(name="frontend", description="Front-end Developers"),
            UserGroup(name="backend", description="Back-end Developers"),
            UserGroup(name="fullstack", description="Full-stack Developers"),
            UserGroup(name="devops", description="DevOps Engineers"),
            UserGroup(name="vibecoders", description="Vibe Coders Group"),
        ]
        db.session.add_all(demo_groups)
        db.session.commit()
        groups = demo_groups
        click.echo("👥 Created 6 demo groups.")

    # === Ensure users exist ===
    users = User.query.all()
    if not users:
        # Create 3 demo users with emails
        demo_users = [
            User(username="admin", email="admin@example.com", password=hash_password("admin123"), is_admin=True),
            User(username="alice", email="alice@example.com", password=hash_password("alice123")),
            User(username="bob", email="bob@example.com", password=hash_password("bob12345")),
        ]
        # Assign users to groups
        for i, user in enumerate(demo_users):
            user.groups.append(groups[i % len(groups)])  # Distribute among groups
            if user.username == "admin":
                user.groups.append(groups[-1])  # Admin in vibecoders too

        db.session.add_all(demo_users)
        db.session.commit()
        users = demo_users
        click.echo("👤 Created 3 demo users with emails and group assignments.")

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