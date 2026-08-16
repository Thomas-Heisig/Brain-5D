# Security Policy

## Project status

Brain-5D is an experimental research and engineering project. The current
development line is `0.5.x`; it is not presented as a hardened internet-facing
service.

Security fixes are prioritized for the current development line. Historical
pre-0.5 versions are not actively maintained.

| Version line | Status |
| --- | --- |
| 0.5.x | Current development line |
| < 0.5 | Not actively supported |

## Reporting a vulnerability

Please do **not** publish exploit details in a normal public issue.

Preferred reporting path:

1. Open the repository's **Security** section on GitHub.
2. Use private vulnerability reporting / a private security advisory if the
   repository has it enabled.
3. If private reporting is unavailable, contact the maintainer privately using
   an established project contact channel before public disclosure.

Repository security page:

https://github.com/Thomas-Heisig/Brain-5D/security

Please include:

- affected version or commit;
- clear description;
- reproduction steps or proof of concept where safe;
- likely impact;
- suggested mitigation if known.

No fixed response-time SLA is promised in this experimental development phase.

## Current security assumptions

- The dashboard is designed primarily for local operation.
- Do not expose it directly to an untrusted network without an authentication
  and authorization layer.
- Configuration files are trusted operator inputs; parsing code should still
  validate types and bounds.
- Dashboard write endpoints must use explicit typed commands and must not expose
  arbitrary shell execution.
- Structural auto-approval is off by default.
- Neuron pruning is off by default.
- Structural mutations should pass through the coordinator/plasticity/manipulator
  boundaries.
- Dependencies should be installed in an isolated virtual environment.

## Dependency updates

For editable development installs:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Review dependency changes before merging them.
