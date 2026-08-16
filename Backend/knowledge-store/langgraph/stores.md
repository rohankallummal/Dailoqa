---
type: Documentation Page
title: Stores
description: LangGraph stores provide cross-thread long-term memory, complementing per-thread checkpointer persistence.
product: langgraph
resource: /docs/langgraph/stores
source: /oss/langgraph/stores
tags:
  - langgraph
  - stores
timestamp: 2026-08-13T12:51:01Z
code_examples:
  - ../code/langgraph/store-list-namespace-search.py
  - ../code/langgraph/store-list-namespace-search.ts
  - ../code/langgraph/store-list-namespace-paginate.py
  - ../code/langgraph/store-list-namespace-paginate.ts
  - ../code/langgraph/store-list-namespace-list.py
  - ../code/langgraph/store-list-namespace-list.ts
---

# Stores

Stores let agents persist information across threads, including user preferences, accumulated knowledge, and facts that should survive beyond a single conversation. Unlike [checkpointers](../langgraph/checkpoints.md), which save the full graph state scoped to one thread, stores hold arbitrary key-value data accessible from any thread.

_Figure: Model of shared state_

**Info**
**Agent Server handles stores automatically**
When using the Agent Server, you do not need to implement or configure stores manually. The API handles all storage infrastructure for you behind the scenes.

**Note**
`InMemoryStore` is suitable for development and testing. For production, use a persistent store like `PostgresStore`, `MongoDBStore`, `RedisStore`, or `UpstashStore`. All implementations extend `BaseStore`, which is the type annotation to use in node function signatures.

## Basic usage

The following code snippet shows the `InMemoryStore` in isolation without using LangGraph:

**Python**
```python
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()
```

**JavaScript / TypeScript**
```typescript
import { MemoryStore } from "@langchain/langgraph";

const memoryStore = new MemoryStore();
```

Memories are namespaced by a `tuple`, which is `(<user_id>, "memories")` in the following example. The namespace can be any length and represent anything, does not have to be user specific.

**Python**
```python
user_id = "1"
namespace_for_memory = (user_id, "memories")
```

**JavaScript / TypeScript**
```typescript
const userId = "1";
const namespaceForMemory = [userId, "memories"];
```

Use the `store.put` method to save memories to the namespace in the store. Specify the namespace, as defined above, and a key-value pair for the memory: the key is simply a unique identifier for the memory (`memory_id`) and the value (a dictionary) is the memory itself.

**Python**
```python
memory_id = str(uuid.uuid4())
memory = {"food_preference" : "I like pizza"}
store.put(namespace_for_memory, memory_id, memory)
```

**JavaScript / TypeScript**
```typescript
const memoryId = crypto.randomUUID();
const memory = { food_preference: "I like pizza" };
await memoryStore.put(namespaceForMemory, memoryId, memory);
```

Read out memories from your namespace using the `store.search` method, which returns memories for a given user as a list, up to the `limit` argument (default `10`). With `InMemoryStore`, items are returned in insertion order, so the most recent memory is last in the list; other backends may order memories differently (see [Listing items in a namespace](#listing-items-in-a-namespace)).

**Python**
```python
memories = store.search(namespace_for_memory)
memories[-1].dict()
{'value': {'food_preference': 'I like pizza'},
 'key': '07e0caf4-1631-47b7-b15f-65515d4c1843',
 'namespace': ['1', 'memories'],
 'created_at': '2024-10-02T17:22:31.590602+00:00',
 'updated_at': '2024-10-02T17:22:31.590605+00:00'}
```

Each memory type is a Python class (`Item`) with certain attributes. We can access it as a dictionary by converting with `.dict`.

The attributes it has are:

* `value`: The value (itself a dictionary) of this memory
* `key`: A unique key for this memory in this namespace
* `namespace`: A tuple of strings, the namespace of this memory type

**Note**
    While the type is `tuple[str, ...]`, it may be serialized as a list when converted to JSON (for example, `['1', 'memories']`).

* `created_at`: Timestamp for when this memory was created
* `updated_at`: Timestamp for when this memory was updated

**JavaScript / TypeScript**
```typescript
const memories = await memoryStore.search(namespaceForMemory);
memories[memories.length - 1];

// {
//   value: { food_preference: 'I like pizza' },
//   key: '07e0caf4-1631-47b7-b15f-65515d4c1843',
//   namespace: ['1', 'memories'],
//   createdAt: '2024-10-02T17:22:31.590602+00:00',
//   updatedAt: '2024-10-02T17:22:31.590605+00:00'
// }
```

The attributes it has are:

* `value`: The value of this memory
* `key`: A unique key for this memory in this namespace
* `namespace`: A tuple of strings, the namespace of this memory type

**Note**
    While the type is `tuple`, it may be serialized as a list when converted to JSON (for example, `['1', 'memories']`).

* `createdAt`: Timestamp for when this memory was created
* `updatedAt`: Timestamp for when this memory was updated

## Listing items in a namespace

**Python**
Calling `store.search` (or the async `store.asearch`) with no `query` and no `filter` returns the items stored under `namespace_prefix`, up to `limit`. Use this to enumerate everything in a namespace when you don't need semantic ranking.

**JavaScript / TypeScript**
Calling `store.search` with no `query` and no `filter` returns the items stored under the namespace prefix, up to `limit`. Use this to enumerate everything in a namespace when you don't need semantic ranking.

**Python**

Code example: [`code/langgraph/store-list-namespace-search.py`](../code/langgraph/store-list-namespace-search.py)

```python
# Return up to 100 items stored under ("alice", "memories").
items = store.search(("alice", "memories"), limit=100)
```

**JavaScript / TypeScript**

Code example: [`code/langgraph/store-list-namespace-search.ts`](../code/langgraph/store-list-namespace-search.ts)

```ts
// Return up to 100 items stored under ["alice", "memories"].
const items = await store.search(["alice", "memories"], { limit: 100 });
```

Three behaviors to keep in mind:

- **`namespace_prefix` matches by prefix, not exactly.** `("alice",)` also returns items under `("alice", "memories")`, `("alice", "preferences")`, and so on. To restrict to a single level, pass the full namespace or filter the returned items client-side on `item.namespace`.
- **Results past `limit` are silently truncated.** There is no overflow signal—set `limit` above your expected maximum, or paginate with `offset`.
- **Default ordering depends on the store backend.** `PostgresStore` and `AsyncPostgresStore` return results ordered by `updated_at` descending (most recently updated first). `InMemoryStore` returns results in insertion order (most recently inserted last). Do not rely on a specific order across implementations; sort client-side on `item.updated_at` if order matters.

**Python**
To page through a large namespace:

Code example: [`code/langgraph/store-list-namespace-paginate.py`](../code/langgraph/store-list-namespace-paginate.py)

```python
page_size = 50
offset = 0
while True:
    page = store.search(("alice", "memories"), limit=page_size, offset=offset)
    if not page:
        break
    for item in page:
        pass
    offset += page_size
```

**JavaScript / TypeScript**
To page through a large namespace:

Code example: [`code/langgraph/store-list-namespace-paginate.ts`](../code/langgraph/store-list-namespace-paginate.ts)

```ts
const pageSize = 50;
let offset = 0;
while (true) {
  const page = await store.search(["alice", "memories"], { limit: pageSize, offset });
  if (page.length === 0) break;
  for (const item of page) {
    // ...
  }
  offset += pageSize;
}
```

**Python**
To discover which namespaces exist (for example, to iterate over every user before listing their memories), use `store.list_namespaces` or `store.alist_namespaces`:

Code example: [`code/langgraph/store-list-namespace-list.py`](../code/langgraph/store-list-namespace-list.py)

```python
# All namespaces that start with ("alice",), truncated to two levels deep.
namespaces = store.list_namespaces(prefix=("alice",), max_depth=2)
```

**JavaScript / TypeScript**
To discover which namespaces exist (for example, to iterate over every user before listing their memories), use `store.listNamespaces`:

Code example: [`code/langgraph/store-list-namespace-list.ts`](../code/langgraph/store-list-namespace-list.ts)

```ts
// All namespaces that start with ["alice"], truncated to two levels deep.
const namespaces = await store.listNamespaces({ prefix: ["alice"], maxDepth: 2 });
```

## Semantic search

Beyond simple retrieval, the store also supports semantic search, allowing you to find memories based on meaning rather than exact matches. To enable this, configure the store with an embedding model:

**Python**
```python
from langchain.embeddings import init_embeddings

store = InMemoryStore(
    index={
        "embed": init_embeddings("openai:text-embedding-3-small"),  # Embedding provider
        "dims": 1536,                              # Embedding dimensions
        "fields": ["food_preference", "$"]              # Fields to embed
    }
)
```

**JavaScript / TypeScript**
```typescript
import { OpenAIEmbeddings } from "@langchain/openai";

const store = new InMemoryStore({
  index: {
    embeddings: new OpenAIEmbeddings({ model: "text-embedding-3-small" }),
    dims: 1536,
    fields: ["food_preference", "$"], // Fields to embed
  },
});
```

Now when searching, you can use natural language queries to find relevant memories:

**Python**
```python
# Find memories about food preferences
# (This can be done after putting memories into the store)
memories = store.search(
    namespace_for_memory,
    query="What does the user like to eat?",
    limit=3  # Return top 3 matches
)
```

**JavaScript / TypeScript**
```typescript
// Find memories about food preferences
// (This can be done after putting memories into the store)
const memories = await store.search(namespaceForMemory, {
  query: "What does the user like to eat?",
  limit: 3, // Return top 3 matches
});
```

You can control which parts of your memories get embedded by configuring the `fields` parameter or by specifying the `index` parameter when storing memories:

**Python**
```python
# Store with specific fields to embed
store.put(
    namespace_for_memory,
    str(uuid.uuid4()),
    {
        "food_preference": "I love Italian cuisine",
        "context": "Discussing dinner plans"
    },
    index=["food_preference"]  # Only embed "food_preferences" field
)

# Store without embedding (still retrievable, but not searchable)
store.put(
    namespace_for_memory,
    str(uuid.uuid4()),
    {"system_info": "Last updated: 2024-01-01"},
    index=False
)
```

**JavaScript / TypeScript**
```typescript
// Store with specific fields to embed
await store.put(
  namespaceForMemory,
  crypto.randomUUID(),
  {
    food_preference: "I love Italian cuisine",
    context: "Discussing dinner plans",
  },
  { index: ["food_preference"] } // Only embed "food_preferences" field
);

// Store without embedding (still retrievable, but not searchable)
await store.put(
  namespaceForMemory,
  crypto.randomUUID(),
  { system_info: "Last updated: 2024-01-01" },
  { index: false }
);
```

## Using in LangGraph

**Python**
The store works hand-in-hand with the checkpointer: the checkpointer saves state to threads, as discussed above, and the store allows you to store arbitrary information for access _across_ threads. Compile the graph with both the checkpointer and the store as follows.

```python
from dataclasses import dataclass
from langgraph.checkpoint.memory import InMemorySaver

@dataclass
class Context:
    user_id: str

# We need this because we want to enable threads (conversations)
checkpointer = InMemorySaver()

# ... Define the graph ...

# Compile the graph with the checkpointer and store
builder = StateGraph(MessagesState, context_schema=Context)
# ... add nodes and edges ...
graph = builder.compile(checkpointer=checkpointer, store=store)
```

**JavaScript / TypeScript**
The `memoryStore` works hand-in-hand with the checkpointer: the checkpointer saves state to threads, as discussed above, and the `memoryStore` allows you to store arbitrary information for access _across_ threads. Compile the graph with both the checkpointer and the `memoryStore` as follows.

```typescript
import { MemorySaver } from "@langchain/langgraph";

// We need this because we want to enable threads (conversations)
const checkpointer = new MemorySaver();

// ... Define the graph ...

// Compile the graph with the checkpointer and store
const graph = workflow.compile({ checkpointer, store: memoryStore });
```

Then invoke the graph with a `thread_id`, as before, and also with a `user_id`, which serves as the namespace for memories for this particular user as before.

**Python**
```python
# Invoke the graph
config = {"configurable": {"thread_id": "1"}}

# First let's just say hi to the AI
for update in graph.stream(
    {"messages": [{"role": "user", "content": "hi"}]},
    config,
    stream_mode="updates",
    context=Context(user_id="1"),
):
    print(update)
```

**JavaScript / TypeScript**
```typescript
// Invoke the graph
const userId = "1";
const config = { configurable: { thread_id: "1" }, context: { userId } };

// First let's just say hi to the AI
for await (const update of await graph.stream(
  { messages: [{ role: "user", content: "hi" }] },
  { ...config, streamMode: "updates" }
)) {
  console.log(update);
}
```

**Python**
You can access the store and the `user_id` from _any node_ by using the `Runtime` object. The `Runtime` is automatically injected by LangGraph when you add it as a parameter to your node function. You can use it to save memories:

```python
from langgraph.runtime import Runtime
from dataclasses import dataclass

@dataclass
class Context:
    user_id: str

async def update_memory(state: MessagesState, runtime: Runtime[Context]):

    # Get the user id from the runtime context
    user_id = runtime.context.user_id

    # Namespace the memory
    namespace = (user_id, "memories")

    # ... Analyze conversation and create a new memory

    # Create a new memory ID
    memory_id = str(uuid.uuid4())

    # We create a new memory
    await runtime.store.aput(namespace, memory_id, {"memory": memory})

```

**JavaScript / TypeScript**
You can access the store and the `userId` from _any node_ with the `runtime` argument. You can use it to save memories:

```typescript
import { StateSchema, MessagesValue, Runtime } from "@langchain/langgraph";

const MessagesState = new StateSchema({
  messages: MessagesValue,
});

const updateMemory: GraphNode<typeof MessagesState> = async (state, runtime) => {
  // Get the user id from the config
  const userId = runtime.context?.user_id;
  if (!userId) throw new Error("User ID is required");

  // Namespace the memory
  const namespace = [userId, "memories"];

  // ... Analyze conversation and create a new memory
  const memory = "Some memory content";

  // Create a new memory ID
  const memoryId = crypto.randomUUID();

  // We create a new memory
  await runtime.store?.put(namespace, memoryId, { memory });
};
```

You can also access the store from any node and use the `store.search` method to get memories. Memories are returned as a list of objects that can be converted to a dictionary.

**Python**
```python
memories[-1].dict()
{'value': {'food_preference': 'I like pizza'},
 'key': '07e0caf4-1631-47b7-b15f-65515d4c1843',
 'namespace': ['1', 'memories'],
 'created_at': '2024-10-02T17:22:31.590602+00:00',
 'updated_at': '2024-10-02T17:22:31.590605+00:00'}
```

**JavaScript / TypeScript**
```typescript
memories[memories.length - 1];
// {
//   value: { food_preference: 'I like pizza' },
//   key: '07e0caf4-1631-47b7-b15f-65515d4c1843',
//   namespace: ['1', 'memories'],
//   createdAt: '2024-10-02T17:22:31.590602+00:00',
//   updatedAt: '2024-10-02T17:22:31.590605+00:00'
// }
```

You access the memories and use them in model calls.

**Python**
```python
from dataclasses import dataclass
from langgraph.runtime import Runtime

@dataclass
class Context:
    user_id: str

async def call_model(state: MessagesState, runtime: Runtime[Context]):
    # Get the user id from the runtime context
    user_id = runtime.context.user_id

    # Namespace the memory
    namespace = (user_id, "memories")

    # Search based on the most recent message
    memories = await runtime.store.asearch(
        namespace,
        query=state["messages"][-1].content,
        limit=3
    )
    info = "\n".join([d.value["memory"] for d in memories])

    # ... Use memories in the model call
```

**JavaScript / TypeScript**
```typescript
const callModel: GraphNode<typeof MessagesState> = async (state, runtime) => {
  // Get the user id from the config
  const userId = runtime.context?.user_id;

  // Namespace the memory
  const namespace = [userId, "memories"];

  // Search based on the most recent message
  const memories = await runtime.store?.search(namespace, {
    query: state.messages[state.messages.length - 1].content,
    limit: 3,
  });
  const info = memories.map((d) => d.value.memory).join("\n");

  // ... Use memories in the model call
};
```

If you create a new thread, you can still access the same memories so long as the `user_id` is the same.

**Python**
```python
# Invoke the graph on a new thread
config = {"configurable": {"thread_id": "2"}}

# Let's say hi again
for update in graph.stream(
    {"messages": [{"role": "user", "content": "hi, tell me about my memories"}]},
    config,
    stream_mode="updates",
    context=Context(user_id="1"),
):
    print(update)
```

**JavaScript / TypeScript**
```typescript
// Invoke the graph
const config = { configurable: { thread_id: "2" }, context: { userId: "1" } };

// Let's say hi again
for await (const update of await graph.stream(
  { messages: [{ role: "user", content: "hi, tell me about my memories" }] },
  { ...config, streamMode: "updates" }
)) {
  console.log(update);
}
```

When you use LangSmith locally (e.g., in Studio) or hosted, the base store is available to use by default and you do not need to specify it during graph compilation. To enable semantic search, however, you **do** need to configure the indexing settings in your `langgraph.json` file. For example:

```json
{
    ...
    "store": {
        "index": {
            "embed": "openai:text-embeddings-3-small",
            "dims": 1536,
            "fields": ["$"]
        }
    }
}
```

See the deployment guide for more details and configuration options.

**Python**
## Build a custom store

To use a storage backend other than the built-in implementations, subclass `BaseStore` and implement its required methods. The built-in `InMemoryStore` is the simplest reference implementation.

### Base contract

All five async methods are required. Sync counterparts (`put`, `get`, `delete`, `search`, `list_namespaces`) are optional but recommended for compatibility with sync graph execution.

| Method | Description |
|--------|-------------|
| `aput(namespace, key, value, index=None)` | Store or overwrite a single item |
| `aget(namespace, key)` | Retrieve a single item by key; return `None` if missing |
| `adelete(namespace, key)` | Delete a single item |
| `asearch(namespace_prefix, *, query=None, filter=None, limit=10, offset=0)` | Search items under a namespace prefix; optionally by semantic query |
| `alist_namespaces(*, prefix=None, suffix=None, max_depth=None, limit=100, offset=0)` | List namespaces matching a prefix/suffix pattern |

Look up exact signatures before implementing:

```python
import inspect
from langgraph.store.base import BaseStore
print(inspect.getsource(BaseStore))
```

### Namespace design

Namespaces are tuples of strings, e.g. `("user_id", "memories")`. Store implementations must support:

- **Prefix matching**: `asearch(("alice",))` returns items under `("alice",)`, `("alice", "memories")`, and any other sub-namespace.
- **Exact key lookup**: `aget(("alice", "memories"), "some-key")` must be O(1) or close to it.

For SQL backends, a common schema:

```sql
CREATE TABLE store_items (
    namespace   TEXT[] NOT NULL,
    key         TEXT NOT NULL,
    value       JSONB NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (namespace, key)
);

CREATE INDEX ON store_items USING gin(namespace);
```

### Serialization

Store values are plain Python dicts — no special serializer is required. Serialize with `json.dumps` / `json.loads` or a JSONB column directly. Do not store raw Python objects that are not JSON-serializable.

### Semantic search support

If your backend supports vector search, implement the `query` parameter on `asearch`:

- Accept a `query: str | None` argument.
- When `query` is not `None`, embed it and rank results by cosine similarity.
- Results should include a `score` field on each `Item` when `query` is provided.

If your backend does not support vector search, raise `NotImplementedError` when `query` is passed.

### Testing

There is currently no conformance suite for custom stores. Test against `InMemoryStore` as the reference:

```python
import pytest
from langgraph.store.memory import InMemoryStore
from your_module import YourStore

@pytest.fixture
async def store():
    async with YourStore.create() as s:
        yield s

@pytest.fixture
def reference():
    return InMemoryStore()

async def test_put_and_get(store, reference):
    ns = ("test", "ns")
    for s in [store, reference]:
        await s.aput(ns, "k1", {"val": 1})
        item = await s.aget(ns, "k1")
        assert item is not None
        assert item.value == {"val": 1}

async def test_delete(store, reference):
    ns = ("test", "ns")
    for s in [store, reference]:
        await s.aput(ns, "k1", {"val": 1})
        await s.adelete(ns, "k1")
        assert await s.aget(ns, "k1") is None

async def test_search_prefix(store, reference):
    for s in [store, reference]:
        await s.aput(("user", "memories"), "m1", {"text": "likes pizza"})
        results = await s.asearch(("user",))
        assert any(r.key == "m1" for r in results)
```

### Next steps

- [Checkpointers](../langgraph/checkpoints.md) — thread-scoped state persistence
