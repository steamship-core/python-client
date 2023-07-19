<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/blockifier/transcriber.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.plugin.blockifier.transcriber`




**Global Variables**
---------------
- **TRANSCRIPT_ID**


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/blockifier/transcriber.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Transcriber`







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/blockifier/transcriber.py#L20"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_transcript`

```python
get_transcript(transcript_id: str) → (Optional[str], Optional[List[Tag]])
```

Method to retrieve the transcript and optional Tags. If the transcription is not ready, return None 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/blockifier/transcriber.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    request: PluginRequest[RawDataPluginInput]
) → InvocableResponse[BlockAndTagPluginOutput]
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/blockifier/transcriber.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `start_transcription`

```python
start_transcription(audio_file: PluginRequest[RawDataPluginInput]) → str
```

Start a transcription job and return an id to identify the transcription. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
