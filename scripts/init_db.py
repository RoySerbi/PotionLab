#!/usr/bin/env python3
"""Initialize database tables for PotionLab."""

from app.db.session import init_db


def main() -> None:
    print("Creating database tables...")
    init_db()
    print("✓ All tables created successfully")


if __name__ == "__main__":
    main()
