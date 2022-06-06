"""This class is a helper for plugins to use models hosted on Hugging Face.

It uses asyncio parallelism to make many http requests simultaneously.
"""

import asyncio
import json
import logging
import time
from http import HTTPStatus
from typing import List

import aiohttp
from aiohttp import ClientTimeout

from steamship import Block, SteamshipError


async def _model_call(session, text: str, api_url, headers, additional_params: dict = None) -> list:
    json_input = dict(inputs=text, wait_for_model=False, parameters=additional_params)
    data = json.dumps(json_input)

    max_error_retries = 3

    """
    Hugging Face returns an error that says that the model is currently loading
    if it believes you have 'too many' requests simultaneously, so the logic retries in this case, but fails on
    other errors.
    """
    while True:
        tries = 0
        async with session.post(api_url, headers=headers, data=data) as response:
            if response.status == HTTPStatus.OK and response.content_type == "application/json":
                json_response = await response.json()
                logging.info(json_response)
                return json_response
            else:
                text_response = await response.text()
                if "is currently loading" not in text_response:
                    logging.info(
                        f"received text response [{text_response}] for input text [{text}], attempt {tries}"
                    )
                    if tries >= max_error_retries:
                        raise SteamshipError(
                            message="Unable to query Hugging Face model",
                            internal_message=f"HF returned error: {text_response} after {tries} attempts",
                        )
                    else:
                        tries += 1
                else:
                    await asyncio.sleep(1)


async def _model_calls(
    texts: List[str], api_url: str, headers, additional_params: dict = None
) -> List[list]:
    async with aiohttp.ClientSession(timeout=ClientTimeout(total=30)) as session:
        tasks = []
        for text in texts:
            tasks.append(
                asyncio.ensure_future(
                    _model_call(
                        session, text, api_url, headers=headers, additional_params=additional_params
                    )
                )
            )

        results = await asyncio.gather(*tasks)
        return results


def get_huggingface_results(
    blocks: List[Block], hf_model_path: str, hf_bearer_token: str, additional_params: dict = None
) -> List[list]:
    api_url = f"https://api-inference.huggingface.co/models/{hf_model_path}"
    headers = {"Authorization": f"Bearer {hf_bearer_token}"}
    start_time = time.perf_counter()
    results = asyncio.run(
        _model_calls([block.text for block in blocks], api_url, headers, additional_params)
    )
    total_time = time.perf_counter() - start_time
    logging.info(
        f"Completed {len(blocks)} blocks in {total_time} seconds. ({float(len(blocks)) / total_time} bps)"
    )
    return results
