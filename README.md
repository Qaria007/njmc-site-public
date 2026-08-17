# njmcmedicsupp.com

The full site under `public_html/`, plus the Insights writing and publishing
pipeline under `.automation/`.

- Site source of truth: `public_html/` mirrors what is served at
  https://njmcmedicsupp.com
- How articles get written and checked: `.automation/README.md`
- Topic backlog: `.automation/topics.md`
- Pre-existing issues on older pages: `.automation/known-issues.md`

Check the whole site against the content rules at any time:

```bash
python3 .automation/gates.py
```
