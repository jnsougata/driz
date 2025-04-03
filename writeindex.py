import driz

classes = [i for i in dir(driz) if i[0].isupper()]

with open("./docs/index.rst", "w") as f:
    block = (f".. automodule:: driz"
             f"\n"
             f"\n"
             f"\n")
    templ = ("\n.. autoclass:: discohook.{0}"
             "\n    :members:"
             "\n    :undoc-members:"
             "\n    :show-inheritance:"
             "\n")
    f.write(block)
    f.write("\n".join([templ.format(i) for i in classes]))
    block = (f"\nIndices and tables"
             f"\n=================="
             f"\n"
             f"\n* :ref:`genindex`"
             f"\n* :ref:`modindex`"
             f"\n* :ref:`search`"
             f"\n")
    f.write(block)