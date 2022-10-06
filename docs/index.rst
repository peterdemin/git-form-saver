Git form saver
==============

.. contents::
   :local:

What is Git form saver
----------------------

Git form saver is an HTTP API that pushes HTML forms to git repositories.

In a nutshell, API does the following:

- Accept HTTP POST request.
- Clone git repository passed in ``repo`` parameter.
- Format the passed form fields using chosen ``formatter``.
- Append formatted data to a file passed in ``file`` parameter.
- Push changes back to git repository.


When to use Git form saver
--------------------------

Git form saver is useful when you want to allow appending data to specific file in a git repo through HTML form submission.

Possible use-cases
~~~~~~~~~~~~~~~~~~

- In public environment:

    - Collect anonymous comments.
    - Publish comments on statically-generated websites.
    - A replacement for a database for simple data models.

- In protected environment:

    - Collect usage statistics from internal commandline tools.
    - Simple plain-text file journaling without git access (mobile).


Security features
-----------------

Git form saver supports limiting user actions in 3 ways:

1. Git form saver uses SSH with **private key authentication**
   for all interactions with git repositories.
   It can only access repositories that allowed its public key.
2. **Mandatory token** --- Git form saver appends form submissions
   only to the files, that contain a cryptographically secure
   Java Web Token (JWT) at the beginning of the file.
3. For protected environments, form owner can optionally set up **secret** value,
   required for the token verification.

Git SSH authentication
~~~~~~~~~~~~~~~~~~~~~~

Each git form saver instance can have a unique private key used for all
git interactions. The same private key is used for generating the JWT.
Private key never leaves the server and is hidden from target
git repository and form owners.

.. note::

   On GitHub, you can either add Git form saver's public SSH key to your account,
   or create a separate GitHub account and add as a collaborator to your repo.

Mandatory token
~~~~~~~~~~~~~~~

To enable Git form saver to append forms to a file, you need to generate
a security token, and save it in the target file.
Security token encodes repository URL and file path (with optional secret)
using Git form saver's private key.
Long unique token ensures, that Git form saver can access only
specific files inside the repository.

The token is different for each repository and for each file inside the repository.

Secret
~~~~~~

For protected environments, as internal networks, or mobile applications,
security token can include additional ``secret`` value.
Only form submissions, that include this ``secret`` value will be permitted.

Demo server
-----------

Security token generation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

    <form action="https://gitformsaver.demin.dev/token" method="POST">
      <div>
        <label for="repo">Enter repository URL:</label>
        <input name="repo" value="git@github.com:user/repo.git" />
      </div>
      <div>
        <label for="file">File path:</label>
        <input name="file" value="file.txt" />
      </div>
      <div>
        <label for="secret">Secret (optional):</label>
        <input name="secret" value="" />
      </div>
      <div>
        <button>Generate token</button>
      </div>
    </form>

Save text to any file
~~~~~~~~~~~~~~~~~~~~~

.. raw:: html

    <form action="https://gitformsaver.demin.dev/" method="POST">
      <div>
        <label for="repo">Repository URL</label>
        <input name="repo" value="git@github.com:user/repo.git" />
      </div>
      <div>
        <label for="file">File path inside of the repository</label>
        <input name="file" value="README.md" />
      </div>
      <div>
        <label for="text">Text</label>
        <input name="text" id="text" value="Text" />
      </div>
      <div>
        <label for="redirect">Redirect target after submission</label>
        <input name="redirect" value="https://gitformsaver.github.io" />
      </div>
      <div>
        <button>Send</button>
      </div>
    </form>
