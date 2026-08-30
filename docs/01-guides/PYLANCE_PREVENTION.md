# Pylance/Pyright prevention rules

The prior error log shows recurring classes: unknown container element types, mutable Protocol invariance, unvalidated YAML/JSON values, broad `dict[str, object]` forwarding into typed APIs, and dynamic attributes.

For alpha.4 and later:

1. Public boundaries use `Protocol` methods and read-only `@property` accessors rather than mutable container attributes.
2. Every empty container has an explicit element type.
3. YAML/JSON is `object` only before validation; application code receives a dataclass or TypedDict.
4. Never pass `dict[str, object]` with `**kwargs` to `subprocess.Popen`, HTTP, storage or network APIs.
5. Runtime state is stored in controllers/engines, not added dynamically to neuron objects.
6. Test fakes implement the same read-only Protocol surfaces as production types.
7. `pyright src scripts tests` is a release gate, not an editor-only diagnostic.
