# Character Encoding Utils

[![Python](https://img.shields.io/badge/python-3.10-brightgreen)](https://www.python.org)
[![PyPI](https://img.shields.io/pypi/v/character-encoding-utils)](https://pypi.org/project/character-encoding-utils/)

Some [character encoding](https://en.wikipedia.org/wiki/Character_encoding) utils.

Now support:

- [GB2312](https://en.wikipedia.org/wiki/GB_2312)
- [Big5](https://en.wikipedia.org/wiki/Big5)
- [Shift-JIS](https://en.wikipedia.org/wiki/Shift_JIS)
- [KS-X-1001](https://en.wikipedia.org/wiki/KS_X_1001)

## Installation

```shell
pip install character-encoding-utils
```

## Usage

### GB2312

```python
from character_encoding_utils import gb2312

bs = gb2312.encode('abc中国')
assert gb2312.decode(bs) == 'abc中国'
```

### Big5

```python
from character_encoding_utils import big5

bs = big5.encode('abc中國')
assert big5.decode(bs) == 'abc中國'
```

### Shift-JIS

```python
from character_encoding_utils import shiftjis

bs = shiftjis.encode('abc日本')
assert shiftjis.decode(bs) == 'abc日本'
```

### KS-X-1001

```python
from character_encoding_utils import ksx1001

bs = ksx1001.encode('abc가쳰')
assert ksx1001.decode(bs) == 'abc가쳰'
```

## License

Under the [MIT license](LICENSE).
