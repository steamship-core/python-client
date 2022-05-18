import logging
import asyncio
import aiohttp
from typing import List
from steamship import Block, SteamshipError
import time
import json


"""
This class is a helper for plugins to use models hosted on Hugging Face.
It uses asyncio parallelism to make many http requests simultaneously.
"""


async def _model_call(session, text: str, api_url, headers) -> list:
    json_input = dict(inputs=text, wait_for_model=True)
    data = json.dumps(json_input)

    """
    Hugging Face returns an error that says that the model is currently loading
    if it believes you have 'too many' requests simultaneously, so the logic retries in this case, but fails on
    other errors.
    """
    while True:
        async with session.post(api_url, headers=headers, data=data) as response:
            json_response = await response.json()
            logging.info(json_response)
            if 'error' in json_response:
                if 'is currently loading' not in json_response['error']:
                    raise SteamshipError(message='Unable to query Hugging Face model',
                                         internal_message=f'HF returned error: {json_response["error"]}')
                else:
                    await asyncio.sleep(1)
            else:
                return json_response


async def _model_calls(texts: List[str], api_url: str, headers) -> List[list]:
    async with aiohttp.ClientSession() as session:
        tasks = []
        for text in texts:
            tasks.append(asyncio.ensure_future(_model_call(session, text, api_url, headers=headers)))

        results = await asyncio.gather(*tasks)
        return results


def get_huggingface_results(blocks: List[Block], hf_model_path: str, hf_bearer_token: str) -> List[list]:
    api_url = f"https://api-inference.huggingface.co/models/{hf_model_path}"
    headers = {"Authorization": f"Bearer {hf_bearer_token}"}
    start_time = time.perf_counter()
    results = asyncio.run(_model_calls([block.text for block in blocks], api_url, headers))
    total_time = time.perf_counter() - start_time
    logging.info(
        f'Completed {len(blocks)} blocks in {total_time} seconds. ({float(len(blocks)) / total_time} bps)')
    return results
