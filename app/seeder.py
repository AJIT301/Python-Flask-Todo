import random
from datetime import timedelta, datetime
import click
from faker import Faker
from app import db
from app.models import Todo, User, UserGroup, Deadline
from app.security.hsh import hash_password

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
        # Also clear deadlines
        Deadline.query.delete()
        db.session.commit()
        click.echo(f"🗑️  Cleared {deleted} existing todos and all deadlines.")
    elif clean:
        confirm = input("⚠️  This deletes ALL data permanently. Continue? (y/N): ")
        if confirm.lower() != "y":
            click.echo("🛑 Operation cancelled.")
            return
        Todo.query.delete()
        Deadline.query.delete()
        db.session.commit()
        click.echo("🔥 All todos and deadlines deleted permanently.")
        return

    if count <= 0:
        click.echo("❌ Count must be positive.")
        return

    # === Ensure groups exist ===
    groups = UserGroup.query.all()
    if not groups:
        # Create demo groups
        group_names = ["qa", "frontend", "backend", "fullstack", "devops", "vibecoders"]
        group_descriptions = [
            "Quality Assurance Team",
            "Front-end Developers",
            "Back-end Developers",
            "Full-stack Developers",
            "DevOps Engineers",
            "Vibe Coders Group",
        ]

        groups = []
        for name, desc in zip(group_names, group_descriptions):
            group = UserGroup(name=name, description=desc, is_active=True)
            db.session.add(group)
            groups.append(group)

        db.session.commit()
        click.echo("👥 Created 6 demo groups.")

    # === Ensure users exist - one per department + admin ===
    users = User.query.all()
    if not users:
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password=hash_password("admin123"),
            is_admin=True,
        )
        db.session.add(admin_user)

        # Create one user per department
        department_users = []
        department_usernames = [
            "alice_qa",
            "frank_frontend",
            "brian_backend",
            "felix_fullstack",
            "david_devops",
            "victor_vibecoders",
        ]
        department_emails = [
            "alice@qa.com",
            "frank@frontend.com",
            "brian@backend.com",
            "felix@fullstack.com",
            "david@devops.com",
            "victor@vibecoders.com",
        ]

        for i, (username, email) in enumerate(
            zip(department_usernames, department_emails)
        ):
            user = User(
                username=username,
                email=email,
                password=hash_password("password123"),
                is_admin=False,
            )
            # Assign to corresponding group
            user.groups.append(groups[i])
            db.session.add(user)
            department_users.append(user)

        # Also add admin to vibecoders group
        admin_user.groups.append(groups[-1])

        db.session.commit()
        users = [admin_user] + department_users
        click.echo("👤 Created admin user and one user for each department.")
    else:
        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            admin_user = users[0]  # fallback

    # === Create sample deadlines ===
    deadlines = Deadline.query.all()
    if not deadlines:
        deadline_titles = [
            "Q1 Project Delivery",
            "Security Audit Completion",
            "Database Migration",
            "API Documentation",
            "User Testing Phase",
            "Deployment to Production",
        ]

        deadline_descriptions = [
            "Complete all features for Q1 release",
            "Perform comprehensive security review",
            "Migrate legacy database to new system",
            "Document all API endpoints and usage",
            "Conduct user acceptance testing",
            "Final deployment to production servers",
        ]

        deadlines_to_create = []
        for i in range(min(6, len(deadline_titles))):
            # Create deadlines for next 30-90 days
            deadline_date = fake.date_time_between(start_date="+30d", end_date="+90d")

            deadline = Deadline(
                title=deadline_titles[i],
                description=deadline_descriptions[i],
                deadline_date=deadline_date,
                is_active=random.choice([True, False]),  # Mix of active/inactive
                created_by=admin_user,
            )
            deadlines_to_create.append(deadline)

        # Add a few more random deadlines
        for i in range(3):
            deadline = Deadline(
                title=fake.sentence(nb_words=4),
                description=fake.paragraph(nb_sentences=2),
                deadline_date=fake.date_time_between(
                    start_date="+15d", end_date="+120d"
                ),
                is_active=random.choice([True, False]),
                created_by=admin_user,
            )
            deadlines_to_create.append(deadline)

        db.session.add_all(deadlines_to_create)
        db.session.commit()
        click.echo(f"📅 Created {len(deadlines_to_create)} sample deadlines.")

    # === Ensure each user has at least one task ===
    users_with_tasks = set()
    existing_todos = Todo.query.all()
    for todo in existing_todos:
        if todo.assigned_user:
            users_with_tasks.add(todo.assigned_user.id)
        elif todo.assigned_group:
            # Add all users in this group to users_with_tasks
            for user in todo.assigned_group.members:
                users_with_tasks.add(user.id)

    # Create tasks for users who don't have any
    all_users = User.query.all()
    todos_to_create = []

    for user in all_users:
        if user.id not in users_with_tasks:
            # Create a task for this user
            task = fake.sentence(nb_words=random.randint(3, 7))
            if random.choice([True, False]):
                start_date = fake.date_time_this_year()
                end_date = start_date + timedelta(days=random.randint(1, 10))
            else:
                start_date, end_date = None, None

            todo = Todo(
                task=f"[ASSIGNED] {task}",
                done=False,
                created_at=fake.date_time_this_year(),
                date_from=start_date,
                date_to=end_date,
                assigned_user=user,
                created_by=admin_user,
            )
            todos_to_create.append(todo)
            users_with_tasks.add(user.id)
            click.echo(f"📝 Created initial task for user: {user.username}")

    # Add user todos to session first to avoid relationship warnings
    if todos_to_create:
        db.session.add_all(todos_to_create)
        db.session.flush()  # Flush to make them available for relationship queries

    # Also ensure each group has at least one task
    groups_with_tasks = set()
    for todo in existing_todos:
        if todo.assigned_group:
            groups_with_tasks.add(todo.assigned_group.id)

    group_todos_to_create = []
    
    # Use no_autoflush to prevent warnings during group.members access
    with db.session.no_autoflush:
        for group in groups:
            if group.id not in groups_with_tasks and group.members:
                # Create a task for this group
                task = fake.sentence(nb_words=random.randint(3, 7))
                if random.choice([True, False]):
                    start_date = fake.date_time_this_year()
                    end_date = start_date + timedelta(days=random.randint(1, 10))
                else:
                    start_date, end_date = None, None

                todo = Todo(
                    task=f"[GROUP] {task}",
                    done=False,
                    created_at=fake.date_time_this_year(),
                    date_from=start_date,
                    date_to=end_date,
                    assigned_group=group,
                    created_by=admin_user
                )
                group_todos_to_create.append(todo)
                groups_with_tasks.add(group.id)
                click.echo(f"📝 Created initial task for group: {group.name}")

    # Add group todos to session
    if group_todos_to_create:
        db.session.add_all(group_todos_to_create)

    # Commit all initial assignment tasks
    total_initial_todos = len(todos_to_create) + len(group_todos_to_create)
    if total_initial_todos > 0:
        db.session.commit()
        click.echo(f"✅ Created {total_initial_todos} initial assignment tasks.")

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
                created_by=admin_user,
            )

            # === Random assignment logic ===
            roll = random.choice(["user", "group", "none"])
            if roll == "user" and all_users:
                todo.assigned_user = random.choice(all_users)
            elif roll == "group" and groups:
                todo.assigned_group = random.choice(groups)

            db.session.add(todo)
            added += 1

        db.session.commit()
        final_total = Todo.query.count()
        click.echo(f"✅ Added {added} new todos.")
        click.echo(f"📊 Total todos: {final_total}/1000")

        # Show final stats
        total_deadlines = Deadline.query.count()
        active_deadlines = Deadline.query.filter_by(is_active=True).count()
        click.echo(
            f"📅 Total deadlines: {total_deadlines} (Active: {active_deadlines})"
        )

    except Exception as e:
        db.session.rollback()
        click.echo(f"❌ Error during seeding: {str(e)}")
        raise