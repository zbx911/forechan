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
async for ch, item in await select(ch1, ch2, ch3, ...):
  if ch == ch1:
    # when receiving from `ch1`
    # do something with `item`
  elif ch == ch2:
    # when receiving from `ch2`
    # do something with `item`
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
from asyncio import create_task

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

Most Quality of Life functions that return a `Chan[T]` such as `select(*cs)` or `trans(xform, ch)` or `fan_in(*cs)` take a named param: `cascade_close`.

if `cascade_close = True`, which is the default. Closing the returned channel(s) will also close upstream channels.

### Fan In

```python
cs: Iterable[Chan[T]] = produce_bunch_of_chans()


ch: Chan[T] = await fan_in(*cs)
```

### Fan Out

```python
ch: Chan[T] = produce_some_channel()

# each entry of `ch` will get send to each channel in `cs`
# closing `ch` will close each of `cs`
cs: Sequence[Chan[T]] = await fan_out(ch)
```

### Stream Transform

```python
# regular old python generator
# can do `map` and `filter`, `flatmap`, whatever
async def xform(stream: AsyncIterator[int]) -> AsyncIterator[str]:
  for i in stream:
    if i > 100:
      break # `ch2` will be shut off
    elif is_prime(i):
      yield f"{i + 1} is a prime + 1"

# say one_to_inf() is a `Chan[int]` of ∞ integers
ch1: Chan[int] = one_to_inf()

# `ch2` is both a mapped and filtered stream
ch2: Chan[str] = await trans(xform, ch=ch1)
```


### Simple RPC
