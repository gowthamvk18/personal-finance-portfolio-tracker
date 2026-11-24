import os
import sys
import click
from app import create_app, db

# Determine environment
env = os.environ.get("FLASK_ENV", "development")
app = create_app(env)


@app.cli.command("init-db")
def init_db_command():
    """Create all database tables."""
    with app.app_context():
        db.create_all()
        click.echo("Initialized the database tables successfully.")


@app.cli.command("seed-data")
def seed_data_command():
    """Seed the database with rich demo data."""
    from seed_data import seed_demo_data
    seed_demo_data()
    click.echo("Seeded demo user financial data successfully.")


if __name__ == "__main__":
    # Ensure database exists before first request
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Personal Finance Portfolio Tracker on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
