# Forechan

[go](https://github.com/golang/go) style `asyncio` channels.

**Fully Typed with Generics**, `mypy` ready.

Inspired by [`core.async`](https://github.com/clojure/core.async) from [clojure](https://github.com/clojure/clojure).

## Examples

### Send & Recv

```python
ch = chan(int)         # Chan[int]
await (ch << 2)        # or use `await ch.send(x)`
two = await ([] << ch) # or use `await ch.recv()`
assert two == 2

# `ch.close()` is idempotent
await ch.close()
```

### Basic

```python
if ch:
  # if `Chan[T]` is open

len(ch) # How many items are in `ch`

async with ch:
  # close `ch` after exiting lexical-scope

async for item in ch:
  # use `ch` as AsyncIterator
```

### Select

```python
async for ch, item in select(ch1, ch2, ch3, ...):
  if ch == ch1:
    ...
  elif ch == ch2:
    ...
  elif ch == ch3:
    ...
```

### Wait Group

```python
wg = wait_group()

for _ in range(5):
  async def cont() -> None:
    with wg:
      # do some work

  create_task(cont())

# will wait for all work to be completed
await wg.wait()
```

### Synchronous

```python
head = ch.try_peek() # can throw `ChanEmpty`
(ch < 2)             # or use `ch.try_send(2)` , can throw `ChanFull`
two = ([] < ch)      # or use `ch.try_recv()`  , can throw `ChanEmpty`
assert two == 2
```

### Go -> Python

The following are roughly equivalent

```go
func fn() {
	// do things here
}
go fn()
```

When `GOMAXPROCS=1`

```python
async def fn() -> None:
  # do things here

create_task(fn())
```

## Common Concurrency Patterns

### Consumer

```python
async def consumer() -> None:
  async for item in ch:
    # do something with `item`, until `ch` is closed
```

### Producer

```python
def producer() -> Chan[int]:
  ch = chan(int)

  async def cont() -> None:
    # auto close `ch` when done
    async with ch:
      while ...:
        # send result `item` to downstream `ch`
        await (ch << item)

  create_task(cont())
  return ch
```

## Series of Tubes