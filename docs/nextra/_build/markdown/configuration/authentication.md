<!-- _Auth -->

# Authentication

Steamship uses API Keys to authenticate our CLI and client libraries.
These keys can be stored in a configuration file, in environment variables, or passed manually to our client libraries.

## Steamship Configuration File

Logging in with the [Steamship CLI](cli.md#cli) creates a configuration file at `~/.steamship.json`.
This file contains your API Key, and our client libraries will auto-load information from this file when available.

It looks like this:

```json
{
  "apiKey": "mykey"
}
```

## Using Multiple Profiles

The Steamship configuration file supports multiple profiles.
To create multiple profiles, use the following structure:

```json
{
  "apiKey": "mykey",
  "profiles:" {
    "testing": {
      "apiKey": "test-key"
    },
    "work": {
      "apiKey": "work-key"
    }
  }
}
```

Use a profile from the command line by setting the  `STEAMSHIP_PROFILE` environment variable.

```bash
STEAMSHIP_PROFILE=work ship deploy
```

Use a profile from the Python Client by passing it into the `Steamship` constructor:

```python
client = Steamship(profile="work")
```

```typescript
const client = new Steamship({profile: "work"})
```

## Environment Variables

If the `STEAMSHIP_KEY` environment variable is set,
our client libraries will prioritize it over your `steamship.json` file.
