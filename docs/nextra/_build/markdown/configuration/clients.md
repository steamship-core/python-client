<a id="clients"></a>

# Steamship Client Libraries

<a id="python-client"></a>

## Python Client

To install the Steamship Python Client, run:

```bash
pip install steamship
```

Then, import and use Steamship with:

```python
from steamship import Steamship

ai_package = Steamship.use("package-name")
```

Most of this documentation site is Python-centric and will assume operation via that client.

<a id="typescript-client"></a>

## Typescript Client

#### WARNING
The Typescript client is alpha quality.

To install the Steamship Typescript Client, run:

```bash
npm install --save @steamship/client
```

Then, import and use Steamship with:

```python
import {Steamship, Workspace} from '@steamship/client'

const client = new Steamship()
const instance = await client.use("package")
```

Most of this documentation site is Python-centric and will assume operation via that client.
