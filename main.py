"""Main entry point for the job application agent."""

import sys


def main() -> None:
    # Load config — exits with clear error if .env is missing or incomplete
    try:
        from core.config import settings  # noqa: F401
    except Exception as exc:
        print(f"❌ Config error: {exc}")
        print("   Copy .env.example → .env and fill in the required keys.")
        sys.exit(1)

    print("✅ Config loaded")

    # Initialize database and create tables
    from core.database import init_db

    init_db()
    print("✅ Database ready — tables: observations, companies, jobs")
    print("Run with a flag: --health --load-seeds --poll --score --run --bot")


if __name__ == "__main__":
    main()
