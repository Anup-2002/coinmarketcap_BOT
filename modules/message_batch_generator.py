import json
import os
import shutil
import time

from modules.message_generator import generate_messages

BATCH_SIZE = 50

LAST_TRENDING_FILE = "output/last_trending.json"
PROGRESS_FILE = "output/progress.json"
GENERATED_MESSAGES_FILE = "output/generated_messages.json"
BATCH_FOLDER = "output/message_batches"

MAX_RETRIES = 3


def ensure_directories():

    os.makedirs(
        BATCH_FOLDER,
        exist_ok=True
    )


def cleanup_previous_run():

    if os.path.exists(
        GENERATED_MESSAGES_FILE
    ):
        os.remove(
            GENERATED_MESSAGES_FILE
        )

    if os.path.exists(
        PROGRESS_FILE
    ):
        os.remove(
            PROGRESS_FILE
        )

    if os.path.exists(
        BATCH_FOLDER
    ):
        shutil.rmtree(
            BATCH_FOLDER
        )

    os.makedirs(
        BATCH_FOLDER,
        exist_ok=True
    )


def load_json(path, default):

    if not os.path.exists(path):
        return default

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return default


def save_json(path, data):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


def save_progress(next_index):

    save_json(
        PROGRESS_FILE,
        {
            "next_index": next_index
        }
    )


def generate_batch(batch):

    for attempt in range(
        MAX_RETRIES
    ):

        try:

            return generate_messages(
                batch
            )

        except Exception as e:

            print(
                f"Retry {attempt+1}/{MAX_RETRIES}:",
                e
            )

            time.sleep(
                3 * (attempt + 1)
            )

    raise Exception(
        "Batch failed after retries."
    )


def generate_all_messages():

    ensure_directories()

    cleanup_previous_run()

    coins = load_json(
        LAST_TRENDING_FILE,
        []
    )

    if not coins:

        raise Exception(
            "last_trending.json is empty."
        )

    generated_messages = []

    total_coins = len(
        coins
    )

    batch_number = 1

    for start in range(
        0,
        total_coins,
        BATCH_SIZE
    ):

        end = min(
            start + BATCH_SIZE,
            total_coins
        )

        batch = coins[
            start:end
        ]

        print(
            f"Processing batch {batch_number} "
            f"({start}-{end})"
        )

        try:

            messages = generate_batch(
                batch
            )

            batch_result = []

            for coin, msg in zip(
                batch,
                messages
            ):

                batch_result.append(
                    {
                        "name": coin.get(
                            "name"
                        ),

                        "symbol": coin.get(
                            "symbol"
                        ),

                        "url": coin.get(
                            "url"
                        ),

                        "message": msg.get(
                            "message"
                        )
                    }
                )

            batch_file = os.path.join(
                BATCH_FOLDER,
                f"batch_{batch_number}.json"
            )

            save_json(
                batch_file,
                batch_result
            )

            generated_messages.extend(
                batch_result
            )

            save_json(
                GENERATED_MESSAGES_FILE,
                generated_messages
            )

            save_progress(
                end
            )

            print(
                f"Batch {batch_number} completed "
                f"({len(batch_result)} messages)"
            )

        except Exception as e:

            print(
                f"Batch {batch_number} failed:",
                e
            )

        batch_number += 1

    print(
        f"Generated {len(generated_messages)} total messages."
    )

    return generated_messages


if __name__ == "__main__":

    generate_all_messages()