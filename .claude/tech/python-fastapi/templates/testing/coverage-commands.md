# Coverage Commands — python-fastapi (pytest-cov)

Universal workflow, module mapping, report format, and remediation: see `.claude/templates/testing/coverage-commands.md`.

## Run tests with coverage

For `usecase` or `domain`:
```bash
cd backend && pytest --cov={module}/src --cov-report=xml:coverage.xml --cov-report=html:htmlcov --cov-report=term-missing {module}/tests/
```

For adapter modules:
```bash
cd backend && pytest --cov=adapters/{adapter}/src --cov-report=xml:coverage.xml --cov-report=html:htmlcov --cov-report=term-missing adapters/{adapter}/tests/
```

## Report locations

- XML: `backend/coverage.xml`
- HTML: `backend/htmlcov/index.html`
- Data file: `backend/.coverage`

## Module summary

```bash
cd backend && python -m coverage report --format=total
```

## List classes with gaps

```bash
cd backend && python -m coverage report --show-missing | grep -v "100%" | grep -v "^-" | grep -v "^Name"
```

## Focus filter — touched files

```bash
git diff HEAD --name-only -- 'backend/*/src/' 'backend/adapters/*/src/' | grep -v 'tests/' | sed 's/.*\///' | sed 's/\.py//'
```

## Multi-module grouping

```bash
git diff HEAD --name-only -- 'backend/*/src/' 'backend/adapters/*/src/' | grep -v 'tests/' | sed -n 's|backend/adapters/\([^/]*\)/.*|\1|p; s|backend/\([^/]*\)/src/.*|\1|p' | sort -u
```

## Extract uncovered lines from XML

```bash
CLASS_FILTER="{class_filter}"
python -c "
import xml.etree.ElementTree as ET
filters = '$CLASS_FILTER'.split(',')
tree = ET.parse('backend/coverage.xml')
for pkg in tree.getroot().find('packages').findall('package'):
    for cls in pkg.findall('.//class'):
        name = cls.get('filename', '').rsplit('/', 1)[-1].replace('.py', '')
        if name not in filters:
            continue
        for line in cls.findall('.//line'):
            hits = int(line.get('hits', 0))
            nr = line.get('number')
            branch = line.get('branch') == 'true'
            cond = line.get('condition-coverage', '')
            missed_branch = 0
            if branch and cond:
                parts = cond.split('(')[1].rstrip(')').split('/')
                missed_branch = int(parts[1]) - int(parts[0])
            if hits == 0 or missed_branch > 0:
                print(f'  L{nr}: missed_hits={1 if hits==0 else 0} missed_branch={missed_branch}')
"
```

## Gap Classification (after GREEN)

- Map each uncovered line to: (a) missing test → add a red/green step, (b) unreachable/guard → justify or remove, (c) trivial (logging) → accept.
- Scan touched files across `backend/domain`, `backend/usecase`, `backend/adapters`; new branches must be covered before the work unit closes.

## Async note

- Ensure `pytest-asyncio` is installed and async tests actually execute — a silently-skipped async test shows as 0% coverage on the code it was meant to exercise.
