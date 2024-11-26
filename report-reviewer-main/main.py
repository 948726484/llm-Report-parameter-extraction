import json
import re

text = '''
Some text before
```json
{
  "key": "value",
  "array": [1, 2, 3]
}```
Some text after '''

pattern = r'```json([\s\S]*?)```'

matches = re.findall(pattern, text)[0]
matches=json.loads(matches)
print(matches)

