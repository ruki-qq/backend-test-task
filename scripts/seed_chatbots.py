import asyncio
import argparse
import secrets
import sys
from pathlib import Path
from typing import List


def _ensure_src_on_sys_path() -> None:
    project_root = Path(__file__).resolve().parents[1]
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


_ensure_src_on_sys_path()


from core.database.registry import initialize_database
from core.database.models import ChatBot


async def create_chatbots(names: List[str]) -> List[ChatBot]:
    created: List[ChatBot] = []

    for name in names:
        existing = await ChatBot.find_one(ChatBot.name == name)
        if existing:
            created.append(existing)
            continue

        bot = ChatBot(
            name=name,
            secret_token=secrets.token_urlsafe(24),
        )
        await bot.insert()
        created.append(bot)

    return created


async def clear_chatbots() -> int:
    result = await ChatBot.delete_all({})
    return int(result.deleted_count or 0)


async def async_main(args: argparse.Namespace) -> None:
    await initialize_database()

    if args.clear:
        deleted = await clear_chatbots()
        print(f"Deleted {deleted} existing chatbots")

    names: List[str]
    if args.names:
        names = [n.strip() for n in args.names.split(",") if n.strip()]
    else:
        count = max(1, args.count)
        prefix = args.prefix or "test-bot"
        names = [f"{prefix}-{i+1}" for i in range(count)]

    bots = await create_chatbots(names)

    print("Created/Found chatbots:")
    for b in bots:
        print(f"- name={b.name} id={b.id} secret_token={b.secret_token}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Seed test ChatBot documents into MongoDB",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=2,
        help="Number of chatbots to create when --names is not provided (default: 2)",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="test-bot",
        help="Name prefix for generated chatbots (default: test-bot)",
    )
    parser.add_argument(
        "--names",
        type=str,
        help="Comma-separated list of chatbot names to create (overrides --count/--prefix)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete all existing chatbots before seeding",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
