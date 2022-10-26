"""This class is a helper for plugins to use models hosted on Hugging Face.

It uses asyncio parallelism to make many http requests simultaneously.
"""

import asyncio
import logging
import time
from http import HTTPStatus
from typing import List, Optional

import aiohttp
from aiohttp import ClientTimeout

from steamship import Block, SteamshipError


async def _model_call(
    session, text: str, api_url, headers, additional_params: dict = None, use_gpu: bool = False
) -> Optional[list]:
    additional_params = additional_params or {}
    json_input = {
        "inputs": text or "",
        "parameters": additional_params,
        "options": {"use_gpu": use_gpu, "wait_for_model": False},
    }
    ok_response, nok_response = None, None

    max_error_retries = 3

    """
    Hugging Face returns an error that says that the model is currently loading
    if it believes you have 'too many' requests simultaneously, so the logic retries in this case, but fails on
    other errors.
    """
    tries = 0
    while tries <= max_error_retries:
        async with session.post(api_url, headers=headers, json=json_input) as response:
            if response.status == HTTPStatus.OK and response.content_type == "application/json":
                ok_response = await response.json()
                logging.info(ok_response)
                return ok_response
            else:
                nok_response = await response.text()
                if "is currently loading" not in nok_response:
                    logging.info(
                        f'Received text response "{nok_response}" for input text "{text}" [attempt {tries}/{max_error_retries}]'
                    )
                    tries += 1
                else:
                    await asyncio.sleep(1)
    if ok_response is None:
        raise SteamshipError(
            message="Unable to query Hugging Face model",
            internal_message=f"HF returned error: {nok_response} after {tries} attempts",
        )
    return ok_response


async def _model_calls(
    texts: List[str],
    api_url: str,
    headers,
    timeout_seconds: int,
    additional_params: dict = None,
    use_gpu: bool = False,
) -> List[list]:
    async with aiohttp.ClientSession(timeout=ClientTimeout(total=timeout_seconds)) as session:
        tasks = []
        for text in texts:
            tasks.append(
                asyncio.ensure_future(
                    _model_call(
                        session,
                        text,
                        api_url,
                        headers=headers,
                        additional_params=additional_params,
                        use_gpu=use_gpu,
                    )
                )
            )

        return await asyncio.gather(*tasks)


def get_huggingface_results(
    blocks: List[Block],
    hf_model_path: str,
    hf_bearer_token: str,
    additional_params: dict = None,
    timeout_seconds: int = 30,
    use_gpu: bool = False,
) -> List[list]:
    api_url = f"https://api-inference.huggingface.co/models/{hf_model_path}"
    headers = {"Authorization": f"Bearer {hf_bearer_token}"}
    start_time = time.perf_counter()
    results = asyncio.run(
        _model_calls(
            [block.text for block in blocks],
            api_url,
            headers,
            timeout_seconds=timeout_seconds,
            additional_params=additional_params,
            use_gpu=use_gpu,
        )
    )
    total_time = time.perf_counter() - start_time
    logging.info(
        f"Completed {len(blocks)} blocks in {total_time} seconds. ({float(len(blocks)) / total_time} bps)"
    )
    return results
