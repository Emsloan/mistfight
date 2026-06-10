"""Execute the experiment notebooks in place, embedding their outputs.

Run from the mistfight folder:  python notebooks/execute_notebooks.py
"""

import pathlib

import nbformat
from nbclient import NotebookClient

notebooks_folder = pathlib.Path(__file__).parent

for notebook_path in sorted(notebooks_folder.glob("[0-9]*.ipynb")):
    print(f"executing {notebook_path.name} ...")
    notebook = nbformat.read(notebook_path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=300,
        kernel_name="python3",
        resources={"metadata": {"path": str(notebooks_folder)}},
    )
    client.execute()
    nbformat.write(notebook, notebook_path)
    print(f"  done: {notebook_path.name}")

print("all notebooks executed")
