<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/signed_urls.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.utils.signed_urls`





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/signed_urls.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `url_to_json`

```python
url_to_json(url: str) → <built-in function any>
```

Downloads the Signed URL and returns the contents as JSON. 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/signed_urls.py#L21"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `url_to_bytes`

```python
url_to_bytes(url: str) → bytes
```

Downloads the Signed URL and returns the contents as bytes. 

This is a helper function to consolidate Steamship Client URL fetching to ensure a single point of handling for:  * Error messages  * Any required manipulations for URL signed URLs  * Any required manipulations for localstack-based environments 

Note that the base API Client does not use this method on purpose: in the event of error code, it inspects the contents of the response for a SteamshipError. 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/signed_urls.py#L55"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `download_from_signed_url`

```python
download_from_signed_url(url: str, to_file: Path = None) → Path
```

Downloads the Signed URL to the filename `desired_filename` in a temporary directory on disk. 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/signed_urls.py#L71"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `upload_to_signed_url`

```python
upload_to_signed_url(
    url: str,
    _bytes: Optional[bytes] = None,
    filepath: Optional[Path] = None
)
```

Uploads either the bytes or filepath contents to the provided Signed URL. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
