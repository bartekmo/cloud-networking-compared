# Contributing

Thanks for your interest in improving Cloud Networking Compared! This is a community resource and corrections are welcome.

## Reporting Issues

The most helpful contributions are **factual corrections**:

- Incorrect service names, limits, or pricing
- Outdated information (services renamed, retired, or significantly changed)
- Missing important capabilities that make a cloud look unfairly limited
- Broken documentation links

Please [open an issue](https://github.com/adstuart/cloud-networking-compared/issues) with:
1. Which feature and cloud is affected
2. What the current text says
3. What it should say
4. A link to the source documentation

## Pull Requests

PRs are welcome for:

- **Data corrections** in `data/combined.json` — fix a description, update a limit, correct pricing
- **New features** — add a networking feature that's missing from the comparison
- **UI improvements** — better mobile layout, accessibility, etc.

### Data Format

Each feature in `data/combined.json` follows this structure:

```json
{
  "id": "feature-id",
  "category": "category-id",
  "conceptName": "Human-Readable Feature Name",
  "azure": {
    "name": "Azure Service Name",
    "description": "What it does",
    "keyDetail": "Limits, pricing, important notes",
    "diagram": "graph TD\n  A --> B",
    "url": "https://learn.microsoft.com/..."
  },
  "aws": { ... },
  "gcp": { ... },
  "differences": "Key differences between the three clouds",
  "practitionerNote": "Real-world context for practitioners"
}
```

### Guidelines

- All claims must be sourced from **publicly available documentation**
- Include a documentation URL for any new facts
- Keep language **neutral** — no cloud is "better", just different
- Practitioner notes should be factual observations, not opinions
- Test locally before submitting (`python3 -m http.server 8080`)

## Code of Conduct

Be respectful. Focus on facts. This is a technical resource — keep discussions constructive and evidence-based.
