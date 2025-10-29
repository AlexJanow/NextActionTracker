#!/usr/bin/env python3
"""
Database seeding CLI for Next Action Tracker.

Usage:
    python seed_db.py          # Seed the database with demo data
    python seed_db.py cleanup  # Clean up all data
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.database.seed import seed_database, cleanup_database


async def main():
    """Main CLI function."""
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        print("🧹 Cleaning up database...")
        await cleanup_database()
        print("✅ Database cleanup completed!")
    else:
        print("🌱 Seeding database with demo data...")
        await seed_database()
        print("✅ Database seeding completed!")


if __name__ == "__main__":
    asyncio.run(main())