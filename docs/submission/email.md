# Submission email

Ready to send, as a reply to the Adaptyv Hiring Team's original email.

---

**To:** Adaptyv Hiring Team
**Subject:** Re: AI Engineer take-home — Laurent ROSA-ARSENE

Hi,

Thanks for the open-ended brief — I enjoyed it. Rather than build one feature, I
read through what Adaptyv does and builds, then turned the frictions you document
yourselves (a binding data package with no reader, a published expression workflow
nobody implemented, a quarter of your delivery window spent on manual review) into
a suite of thirteen small, finished tools on one shared foundation.

- **Live site (novice & expert depth):** https://baloozeone972.github.io/adaptyv-suite/
- **Repository:** https://github.com/baloozeone972/adaptyv-suite
- **Loom walkthrough:** https://www.loom.com/share/laurent-rosa-arsene-adaptyv

Quick path in if you only have a few minutes:
```bash
git clone https://github.com/baloozeone972/adaptyv-suite.git && cd adaptyv-suite
make install && make demo    # synth a binding package, QC it, render an HTML report
```

Everything is genuinely finished: 286 tests, 100% coverage, `mypy --strict` and
`ruff` clean, and every claim carries a confidence interval (all demo data is
synthetic and declared, since I don't have your real data). I also checked my
work against `adaptyv-sdk`'s actual source rather than assuming — matched its
conventions where I could (env vars, tooling), and wrote down precisely where a
real adapter would still be needed, in each package's `docs/limitations.md`.

Happy to walk through any of it live, and to talk about which piece would be
most useful to build out further.

Best,
Laurent

---

### Shorter version (if preferred)

Hi,

Thanks for the brief. I read up on Adaptyv and built a suite of thirteen finished
tools targeting frictions you document yourselves — flagship reads and
independently re-verifies your binding data package in one command, the rest
covers submission validation, expression risk, plate selection, budget planning
and guardrails, an autonomous DBTL loop, and more.

- Live site: https://baloozeone972.github.io/adaptyv-suite/
- Repo: https://github.com/baloozeone972/adaptyv-suite
- Loom: https://www.loom.com/share/laurent-rosa-arsene-adaptyv

`make install && make demo` gets you a working report in under a minute. 286
tests, 100% coverage, everything honestly labelled (synthetic data declared,
limitations written down per tool).

Happy to talk through it whenever works.

Best,
Laurent
