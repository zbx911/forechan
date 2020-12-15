# Forechan

Go style `asyncio` channels with convinence methods & syntax.

**Fully Typed with Generics**, `mypy` ready.

Inspired by [`core.async`](https://github.com/clojure/core.async) from [clojure](https://github.com/clojure/clojure).

## Example

### Basic

```python
ch = chan(int)         # Chan[int]
await (ch << 2)        # send
two = await ([] << ch) # recv
assert two == 2

# or use `await ch.send(x)` & `await ch.recv()`
# up to you
```

### Select

```python
async for ch, item in await select(ch1, ch2):
  if ch == ch1:
    # when receiving from `ch1`
    # do something with `item`
  elif ch == ch2:
    # when receiving from `ch2`
    # do something with `item`
```

### Consumer

```python
async def consumer() -> None:
  async for item in ch: # `Chan[T]` is also AsyncIterator
    pass
    # do something with `item`, until `ch` is closed
    # or call `await ch.close()` to shutdown producer
```

### Producer

```python
def producer() -> Chan[int]:
  ch = chan(int)

  async def cont() -> None:
    async with ch: # `Chan[T]` is AsyncContextManager, auto close `ch` when done
      for i in range(100):
        await (ch << i)

  create_task(cont())
  return ch

# or call `await ch.close()` any time
# up to you
```

### Synchronous

```python
head = ch.try_peek() # Throws `ChanEmpty`
(ch < 2)             # or use `ch.try_send(2)` throws `ChanFull`
two = ([] < ch)      # or use `ch.try_recv()`  throws `ChanEmpty`
assert two == 2
```

## Doc

Most QOL (Quality of Life) functions that return a `Chan[T]` such as `select(*chs)` or `trans(xform, ch)` or `fan_in(*chs)` take a named param: `cascade_close`.

if `cascade_close = True`, which is the default. Closing the returned channel will also close upstream channels.

### Basic

```python
if ch:
  # if `Chan[T]` is open

len(ch) # How many items are in `ch`

async with ch:
  # close `ch` after exiting lexical-scope

async for item in ch:
  # use `ch` as Iterator
```

### Go -> Python

The following are roughly equivalent

```go
func fn() {
	// do things here
}
go fn()
```

Only that the `Python` version is single threaded

```python
from asyncio import create_task

async def fn() -> None:
  # do things here

create_task(fn())
```

### Fan in

```python
cs: Sequence[Chan[T]] = produce_bunch_of_chans()

# `ch` take items from each channel in `cs` until they are all closed
#  after which `ch` will also close
ch: Chan[T] = await fan_in(*cs)
```

### Fan out

```python
ch: Chan[T] = produce_some_channel()

# each entry of `ch` will get send to each channel in `cs`
# closing `ch` will close each of `cs`
cs: Sequence[Chan[T]] = await fan_out(ch)
```

### Generator Based Transform

```python
# regular old python generator
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
