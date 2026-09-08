# MHRN: naming and publication identity

## Multi-Scale Homeostatic Recurrence Network

### Mehrskaliges homöostatisches Rekurrenznetzwerk

Effective 8 September 2026. `project_identity.json` is the source for names, titles and intended platform identifiers. English is the main title language; German translations appear underneath. The body language of existing German research is not automatically translated.

## Scientific treatise

**Recursive Epistemics in Embodied Spiking Neural Architectures: A Framework for Delegated Agency and Multi-Scale Recurrence**

*Rekursive Epistemik in verkörperten spikenden neuronalen Architekturen: Ein Framework für delegierte Handlungsmacht und mehrskalige Rekurrenz*

Short citation title: **Recursive Epistemics / Rekursive Epistemik**. The current chapter-based edition is [1.3](research/publications/2026-09-08_recursive-epistemics_v1.3/README.md). New publications, title pages, exports, citations, dashboard headings and repository cards use this identity. This is a scientific treatise; naming does not confer a doctoral degree, peer review, a novelty verdict or validated cognition.

## What changes, what must remain traceable

MHRN replaces the public project name. New package metadata uses `mhrn-core`; the Python import namespace remains `src`. The preferred launcher is `scripts/mhrn_launcher.py`; existing `scripts/brain5d_launcher.py` commands continue working. New environment names use `MHRN_`; at process import they map to the existing `BRAIN5D_` keys with the new value taking precedence. Do not change settings in the middle of a running experiment. Existing process/PID files, browser storage keys, import symbols, checkpoint magic, `.b5d` files and old release tags remain compatible. Versions are not bumped merely to suggest new scientific results.

Published editions 1.0–1.2, supplied original manuscripts, source quotations, bibliographic identities, frozen preregistrations, experiment data, evidence IDs and checksums are historical records. They retain their original bytes and titles. The current edition supersedes them in the navigation, without forging a revised past. A name search will therefore still find documented historical names and compatibility identifiers. See the [migration inventory](docs/05-quality/mhrn-naming-audit.json).

A five-coordinate neuron address is not the complete dynamical state space and is not silently renamed into a state-space projection or a tensor implementation. Dimensionality, recurrence, temporal scales and plasticity retain their actual mathematical and implementation meaning. Renaming provides no evidence of their utility. Likewise, epistemic dependence is not identical to deliberate delegation: genealogical dependence on training data may exist without an act of delegation. The former metaphor is explained historically, not treated as a scientific mistake or as a synonym of every new term.

## Platform completion is separately verified

Requested repository slug: **MHRN** on GitHub and for both existing Hugging Face repositories (model mirror and Space, in separate namespaces by type). [Platform migration status](docs/05-quality/mhrn-platform-migration.json) records the actual API outcomes. Requested IDs are not proof of a completed rename. An occupied destination is never overwritten or replaced by a duplicate. No owner, visibility, access policy or paid hardware is changed.

GitHub repository renaming requires administrative rights. When the API operation is denied, the owner must use repository Settings → General → Repository name → MHRN. A later identity check can confirm the new URL. Existing historical links are retained; do not reuse the old repository name, as that would interrupt GitHub's redirects. Local clones outside the executing environment are not silently renamed.

After the GitHub rename, update an existing local clone with:

```bash
git remote set-url origin https://github.com/Thomas-Heisig/MHRN.git
git fetch origin --prune
```

The directory on Windows may be renamed to `MHRN` after processes and editors using the old directory are closed. Existing editable installations should be refreshed from the renamed checkout; old distribution metadata can be removed with `python -m pip uninstall brain5d-core`, followed by `python -m pip install -e ".[dev,docs]"`. Do not delete scientific artifacts or checkpoint files during that maintenance.

## Sources for platform behavior

GitHub, “Renaming a repository”: https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository . Hugging Face, “Create and manage a repository”, `move_repo`: https://huggingface.co/docs/huggingface_hub/guides/repository . Consulted 2026-09-08; the actual operation is documented separately from the intended configuration.

The migration inventory is a dated byte-preservation record, not a ban on future canonical research updates. Persistent checks protect the historical publication editions; legitimate future registry and run changes remain possible.

Preferred configuration import: `from src.core.network import MHRNConfig`. The historical `Brain5DConfig` name refers to the identical class. The current publication package includes a CFF record with a report-type preferred citation and a matching BibTeX citation. Audit inventories are split into bounded files; they preserve the full migration record.
