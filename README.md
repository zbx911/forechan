# Forechan

Go style `asyncio` channels with convinence methods & syntax.

Fully Typed with Generics, `mypy` ready.

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
async for ch, item in select(ch1, ch2):
  if ch == ch1:
    # when receiving from `ch1`
    # do something with item
  elif ch == ch2:
    # when receiving from `ch2`
    # do something with item
```

### Consumer

```python
async for item in ch: # `Chan[T]` is AsyncIterator
  # do something with item
  # until `ch` is closed
```

### Producer

```python
def producer() -> Chan[int]:
  ch = chan(int)

  async def cont() -> None:
    async with ch: # auto close `ch` when done
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
ch < 2               # Throws `ChanFull`
two = [] < ch        # Throws `ChanEmpty`
assert two == 2

# or use `ch.try_send(2)` and `ch.try_recv()`
# up to you
```

## Doc
