# Security Policy

## Supported versions

Security fixes are provided for the latest published release.

| Version | Supported |
|---|---|
| 1.0.x | Yes |
| Earlier versions | No |

## Reporting a vulnerability

Do not report vulnerabilities, credentials, private documents, or working exploit details through a public GitHub Issue.

Use GitHub's private vulnerability reporting feature on this repository when available:

```text
Security -> Advisories -> Report a vulnerability
```

If private vulnerability reporting is not enabled, contact the maintainer through the GitHub profile before sharing sensitive details:

<https://github.com/chengzi2333>

Include:

- A concise description of the issue.
- Affected version and platform.
- Reproduction steps using non-sensitive sample data.
- Expected security impact.
- A suggested mitigation, if available.

Remove API keys, passwords, personal documents, private URLs, and organization data from all attachments.

## Security boundaries

The skill can invoke local Python and shell scripts, open local browser previews, and optionally use third-party deployment or PDF tools. Review commands and platform permission prompts before approving them.

Playwright, Vercel CLI, and other optional runtime dependencies are supplied by the user's environment or installed on demand. Keep these tools updated and follow their security guidance.

