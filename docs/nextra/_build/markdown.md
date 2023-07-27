# Steamship

Steamship is the fastest way to add AI to your software.

Think of Steamship as both a package manager and package hosting for AI.
Each [Steamship package](https://www.steamship.com/packages) runs in the cloud on a managed stack.

## Steamship in 30 seconds

- [Build Agents](/markdown/agents/index.md#building-agents) which run in the cloud.
- [Use Plugins](/markdown/plugins/using/index.md#using-plugins) for common operations like generating text with GPT, converting a CSV to text, or generating an image from text. Steamship manages asynchronicity and retries.
- [Store data in Files, Blocks, and Tags](/markdown/data/index.md#data-model). This allows you to [query](/markdown/data/queries/index.md#queries) or [search](/markdown/embedding-search/index.md#embedding-search-index) it later.
- [Deploy as a Package](/markdown/packages/developing/index.md#developing-packages), creating a scalable API for your front end.
- [Create as many instances of the Package](/markdown/packages/developing/index.md#creating-package-instances) as you want, each with its own data.

The best way to start is to make a simple package:

## Start from a template

Clone one of our starter packages ([https://github.com/steamship-packages](https://github.com/steamship-packages)):

```bash
git clone https://github.com/steamship-packages/empty-package.git
```

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
pip install -r requirements.dev.txt
```

and start editing `src/api.py`.

## Start from scratch

First, install our SDK and CLI (ideally in a virtual environment):

```bash
python3 -m venv venv
source venv/bin/activate

pip install steamship
```

Now copy this into `api.py`:

```python
from steamship.invocable import post, PackageService

class MyPackage(PackageService):

    @post("hello_world")
    def hello_world(self, name: str = None) -> str:
        return f"Hello, {name}"
```

# Next Steps

Use full-stack language AI packages in your own code.

Build and deploy packages with our low-code framework.

Package examples for common scenarios.

# Contents

* [Configuration](/markdown/configuration/index.md)
  * [Authentication](/markdown/configuration/authentication.md)
    * [Steamship Configuration File](/markdown/configuration/authentication.md#steamship-configuration-file)
    * [Using Multiple Profiles](/markdown/configuration/authentication.md#using-multiple-profiles)
    * [Environment Variables](/markdown/configuration/authentication.md#environment-variables)
  * [Client Libraries](/markdown/configuration/clients.md)
    * [Python Client](/markdown/configuration/clients.md#python-client)
    * [Typescript Client](/markdown/configuration/clients.md#typescript-client)
  * [CLI](/markdown/configuration/cli.md)
  * [HTTP API](configuration/http.md)
    * [Requests](configuration/http.md#requests)
      * [Optional Headers](configuration/http.md#optional-headers)
      * [Engine Response Format](configuration/http.md#engine-response-format)
    * [Creating a Package Instance](configuration/http.md#creating-a-package-instance)
    * [Invoking a Package Method](configuration/http.md#invoking-a-package-method)
* [Agents](/markdown/agents/index.md)
  * [Agent](/markdown/agents/index.md#agent)
  * [AgentContext](/markdown/agents/index.md#agentcontext)
  * [Tool](/markdown/agents/index.md#tool)
  * [AgentService](/markdown/agents/index.md#agentservice)
* [Packages](/markdown/packages/index.md)
* [Plugins](/markdown/plugins/index.md)
  * [File Importers](/markdown/plugins/index.md#file-importers)
  * [Blockifiers](/markdown/plugins/index.md#blockifiers)
  * [Taggers](/markdown/plugins/index.md#taggers)
  * [Generators](/markdown/plugins/index.md#generators)
  * [Embedders](/markdown/plugins/index.md#embedders)
* [Data](/markdown/data/index.md)
  * [Workspaces](/markdown/data/workspaces.md)
    * [Creating Workspaces](/markdown/data/workspaces.md#creating-workspaces)
  * [Files](/markdown/data/files.md)
    * [Creating Files Directly](/markdown/data/files.md#creating-files-directly)
    * [Making File Data Public](/markdown/data/files.md#making-file-data-public)
  * [Blocks](/markdown/data/blocks.md)
    * [Creating Blocks](/markdown/data/blocks.md#creating-blocks)
    * [Making Block Data Public](/markdown/data/blocks.md#making-block-data-public)
  * [Tags](/markdown/data/tags.md)
    * [Ways to use Tags](/markdown/data/tags.md#ways-to-use-tags)
    * [Tag Schemas](/markdown/data/tags.md#tag-schemas)
    * [Block and File Tags](/markdown/data/tags.md#block-and-file-tags)
  * [Querying Data](/markdown/data/queries/index.md)
    * [Usage](/markdown/data/queries/index.md#usage)
    * [Language Description](/markdown/data/queries/index.md#language-description)
      * [Unary Predicates](/markdown/data/queries/index.md#unary-predicates)
      * [Binary Predicates](/markdown/data/queries/index.md#binary-predicates)
      * [Binary Relations](/markdown/data/queries/index.md#binary-relations)
      * [Conjunctions](/markdown/data/queries/index.md#conjunctions)
      * [Special Predicates](/markdown/data/queries/index.md#special-predicates)
* [Embedding Search Index](/markdown/embedding-search/index.md)
* [Inserting Data](/markdown/embedding-search/index.md#inserting-data)
* [Querying Data](/markdown/embedding-search/index.md#querying-data)
* [Developer Reference](/markdown/developing/index.md)
  * [Cloning a Starter Project](/markdown/developing/project-creation.md)
  * [The Steamship Manifest file](/markdown/developing/steamship-manifest.md)
    * [Plugin Configuration](/markdown/developing/steamship-manifest.md#plugin-configuration)
    * [Steamship Registry](/markdown/developing/steamship-manifest.md#steamship-registry)
  * [Python Environment Setup](/markdown/developing/environment-setup.md)
  * [Accepting Configuration](/markdown/developing/configuration.md)
    * [Defining and Accepting configuration in your code](/markdown/developing/configuration.md#defining-and-accepting-configuration-in-your-code)
  * [Storing Secrets](/markdown/developing/storing-secrets.md)
  * [Running on Localhost](/markdown/developing/running.md)
    * [Localhost caveats](/markdown/developing/running.md#localhost-caveats)
  * [Writing Tests](/markdown/developing/testing.md)
    * [Logging](/markdown/developing/testing.md#logging)
    * [Throwing Errors](/markdown/developing/testing.md#throwing-errors)
    * [Manual Testing](/markdown/developing/testing.md#manual-testing)
    * [Automated testing](/markdown/developing/testing.md#automated-testing)
      * [Automated testing setup](/markdown/developing/testing.md#automated-testing-setup)
      * [Modifying or removing automated testing](/markdown/developing/testing.md#modifying-or-removing-automated-testing)
  * [Deploying](/markdown/developing/deploying.md)
    * [Deploying with the Steamship CLI](/markdown/developing/deploying.md#deploying-with-the-steamship-cli)
    * [Deploying via GitHub Actions](/markdown/developing/deploying.md#deploying-via-github-actions)
      * [Automated Deployment Setup](/markdown/developing/deploying.md#automated-deployment-setup)
      * [Modifying or disabling automated deployments](/markdown/developing/deploying.md#modifying-or-disabling-automated-deployments)
    * [Troubleshooting Deployments](/markdown/developing/deploying.md#troubleshooting-deployments)
      * [The deployment fails because the version already exists](/markdown/developing/deploying.md#the-deployment-fails-because-the-version-already-exists)
      * [The deployment fails because the tag does not match the manifest file](/markdown/developing/deploying.md#the-deployment-fails-because-the-tag-does-not-match-the-manifest-file)
      * [The deployment fails with an authentication error](/markdown/developing/deploying.md#the-deployment-fails-with-an-authentication-error)
  * [Monitoring your Instances](/markdown/developing/monitoring.md)
    * [Monitoring via Web](/markdown/developing/monitoring.md#monitoring-via-web)
      * [Logs](/markdown/developing/monitoring.md#logs)
      * [Usage](/markdown/developing/monitoring.md#usage)
      * [Tasks](/markdown/developing/monitoring.md#tasks)
    * [Using Logging in Instances](/markdown/developing/monitoring.md#using-logging-in-instances)
    * [Logs Retrieval with `ship` CLI](/markdown/developing/monitoring.md#logs-retrieval-with-ship-cli)
* [Python Client Reference](/markdown/api/modules.md)
  * [steamship package](/markdown/api/steamship.md)
    * [Subpackages](/markdown/api/steamship.md#subpackages)
      * [steamship.agents package](/markdown/api/steamship.agents.md)
      * [steamship.base package](/markdown/api/steamship.base.md)
      * [steamship.cli package](/markdown/api/steamship.cli.md)
      * [steamship.client package](/markdown/api/steamship.client.md)
      * [steamship.data package](/markdown/api/steamship.data.md)
      * [steamship.experimental package](/markdown/api/steamship.experimental.md)
      * [steamship.invocable package](/markdown/api/steamship.invocable.md)
      * [steamship.plugin package](/markdown/api/steamship.plugin.md)
      * [steamship.utils package](/markdown/api/steamship.utils.md)
    * [Module contents](/markdown/api/steamship.md#module-steamship)
      * [`Block`](/markdown/api/steamship.md#steamship.Block)
      * [`Configuration`](/markdown/api/steamship.md#steamship.Configuration)
      * [`DocTag`](/markdown/api/steamship.md#steamship.DocTag)
      * [`EmbeddingIndex`](/markdown/api/steamship.md#steamship.EmbeddingIndex)
      * [`File`](/markdown/api/steamship.md#steamship.File)
      * [`MimeTypes`](/markdown/api/steamship.md#steamship.MimeTypes)
      * [`Package`](/markdown/api/steamship.md#steamship.Package)
      * [`PackageInstance`](/markdown/api/steamship.md#steamship.PackageInstance)
      * [`PackageVersion`](/markdown/api/steamship.md#steamship.PackageVersion)
      * [`PluginInstance`](/markdown/api/steamship.md#steamship.PluginInstance)
      * [`PluginVersion`](/markdown/api/steamship.md#steamship.PluginVersion)
      * [`RuntimeEnvironments`](/markdown/api/steamship.md#steamship.RuntimeEnvironments)
      * [`Steamship`](/markdown/api/steamship.md#steamship.Steamship)
      * [`SteamshipError`](/markdown/api/steamship.md#steamship.SteamshipError)
      * [`Tag`](/markdown/api/steamship.md#steamship.Tag)
      * [`Task`](/markdown/api/steamship.md#steamship.Task)
      * [`TaskState`](/markdown/api/steamship.md#steamship.TaskState)
      * [`Workspace`](/markdown/api/steamship.md#steamship.Workspace)
      * [`check_environment()`](/markdown/api/steamship.md#steamship.check_environment)
* [License](/markdown/license.md)
* [Authors](/markdown/authors.md)
