from pathlib import Path

# Path to app/prompts/
PROMPT_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(filename: str) -> str:
    file_path = PROMPT_DIR / filename

    # Debug
    print("\n" + "=" * 80)
    print("LOADING PROMPT FILE")
    print(file_path.resolve())
    print("=" * 80)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Prompt file not found:\n{file_path.resolve()}"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        prompt = file.read()

    print("\n" + "=" * 80)
    print("PROMPT LOADED SUCCESSFULLY")
    print(prompt[:500])  # Print first 500 characters
    print("=" * 80)

    return prompt