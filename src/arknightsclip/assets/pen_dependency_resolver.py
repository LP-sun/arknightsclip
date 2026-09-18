"""
Pen Asset Dependency Resolver and Auditor.

Provides explicit, portable dependency mapping and fallback resolution for external
image references inside Pen (.pen) vector design project files (e.g. psd2pen templates).
Guarantees read-only inspection of .pen files and safe downstream consumption.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


REMOTE_ARTWORK_BASE = (
    "https://raw.githubusercontent.com/ArknightsAssets/ArknightsAssets2/cn/assets/dyn/arts/characters"
)


@dataclass
class PenAssetDependency:
    raw_url: str
    is_present_on_disk: bool
    resolved_local_path: Optional[str] = None
    char_id: Optional[str] = None
    operator_name: Optional[str] = None
    resolution_type: str = "unknown"  # "present_local" | "hero_art" | "card_fallback" | "unresolved"
    remote_source_url: Optional[str] = None
    occurrences: int = 0


@dataclass
class PenFileAuditResult:
    pen_path: str
    total_references: int
    unique_urls: int
    present_count: int
    missing_count: int
    dependencies: Dict[str, PenAssetDependency] = field(default_factory=dict)


class PenDependencyResolver:
    """
    Audits and resolves external asset references within Pen design files.
    Ensures that legacy references (such as assets/raw_batch/char_*_1.png)
    map explicitly to canonical repository assets or defined fallbacks.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = (repo_root or Path(__file__).resolve().parents[3]).resolve()
        self.manifests_dir = self.repo_root / "data" / "manifests"
        self.hero_art_dir = self.repo_root / "assets" / "operators"
        self.cards_raw_dir = self.repo_root / "cards_raw"

    def extract_urls(self, data: Any) -> List[str]:
        """Recursively extracts all 'url' string fields from Pen JSON structure."""
        urls: List[str] = []

        def _traverse(node: Any) -> None:
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == "url" and isinstance(v, str):
                        urls.append(v)
                    else:
                        _traverse(v)
            elif isinstance(node, list):
                for item in node:
                    _traverse(item)

        _traverse(data)
        return urls

    def audit_pen_file(self, pen_path: Path) -> PenFileAuditResult:
        """Reads a .pen file in read-only mode and computes full dependency status."""
        pen_path = Path(pen_path).resolve()
        if not pen_path.is_file():
            raise FileNotFoundError(f"Pen file not found: {pen_path}")

        pen_dir = pen_path.parent
        content = json.loads(pen_path.read_text(encoding="utf-8"))
        extracted_urls = self.extract_urls(content)

        counts: Dict[str, int] = {}
        for u in extracted_urls:
            counts[u] = counts.get(u, 0) + 1

        dependencies: Dict[str, PenAssetDependency] = {}
        present_count = 0
        missing_count = 0

        for url, count in counts.items():
            # Check relative to pen_dir, then relative to repo_root
            local_direct = (pen_dir / url).resolve()
            local_repo = (self.repo_root / url).resolve()

            if local_direct.is_file():
                rel_path = str(local_direct.relative_to(self.repo_root)).replace("\\", "/")
                dep = PenAssetDependency(
                    raw_url=url,
                    is_present_on_disk=True,
                    resolved_local_path=rel_path,
                    resolution_type="present_local",
                    occurrences=count,
                )
                present_count += 1
            elif local_repo.is_file():
                rel_path = str(local_repo.relative_to(self.repo_root)).replace("\\", "/")
                dep = PenAssetDependency(
                    raw_url=url,
                    is_present_on_disk=True,
                    resolved_local_path=rel_path,
                    resolution_type="present_local",
                    occurrences=count,
                )
                present_count += 1
            else:
                # File is missing locally - inspect if it's an operator raw_batch reference
                dep = self._resolve_missing_reference(url, count)
                if dep.is_present_on_disk:
                    present_count += 1
                else:
                    missing_count += 1
            dependencies[url] = dep

        rel_pen_path = str(pen_path.relative_to(self.repo_root)).replace("\\", "/")
        return PenFileAuditResult(
            pen_path=rel_pen_path,
            total_references=len(extracted_urls),
            unique_urls=len(counts),
            present_count=present_count,
            missing_count=missing_count,
            dependencies=dependencies,
        )

    def _resolve_missing_reference(self, url: str, occurrences: int) -> PenAssetDependency:
        """Attempts to resolve a missing URL (e.g. assets/raw_batch/char_xxx_1.png)."""
        filename = Path(url).name
        char_id = None
        if filename.startswith("char_") and "_1.png" in filename:
            char_id = filename.replace("_1.png", "")

        operator_name = None
        remote_url = None
        if char_id:
            remote_url = f"{REMOTE_ARTWORK_BASE}/{char_id}/{char_id}_1.png"
            manifest_file = self.manifests_dir / f"{char_id}.json"
            if manifest_file.is_file():
                try:
                    mdata = json.loads(manifest_file.read_text(encoding="utf-8"))
                    operator_name = mdata.get("name_zh") or mdata.get("name")
                except Exception:
                    pass

            # Check if repo has canonical hero art
            canonical_hero = self.hero_art_dir / char_id / "full.png"
            if canonical_hero.is_file():
                rel_hero = str(canonical_hero.relative_to(self.repo_root)).replace("\\", "/")
                return PenAssetDependency(
                    raw_url=url,
                    is_present_on_disk=True,
                    resolved_local_path=rel_hero,
                    char_id=char_id,
                    operator_name=operator_name,
                    resolution_type="hero_art",
                    remote_source_url=remote_url,
                    occurrences=occurrences,
                )

            # Check if repo has normalized card cache or raw card
            card_cache = self.repo_root / "generated" / "cache" / "cards" / f"{char_id}.png"
            if card_cache.is_file():
                rel_card = str(card_cache.relative_to(self.repo_root)).replace("\\", "/")
                return PenAssetDependency(
                    raw_url=url,
                    is_present_on_disk=True,
                    resolved_local_path=rel_card,
                    char_id=char_id,
                    operator_name=operator_name,
                    resolution_type="card_fallback",
                    remote_source_url=remote_url,
                    occurrences=occurrences,
                )

        return PenAssetDependency(
            raw_url=url,
            is_present_on_disk=False,
            resolved_local_path=None,
            char_id=char_id,
            operator_name=operator_name,
            resolution_type="unresolved",
            remote_source_url=remote_url,
            occurrences=occurrences,
        )

    def generate_manifest(
        self, pen_paths: List[Path], output_json: Path, output_md: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Audits multiple Pen files and generates portable dependency manifest and markdown report."""
        audit_results = [self.audit_pen_file(p) for p in pen_paths]

        manifest_data: Dict[str, Any] = {
            "version": "1.0",
            "repo_root": ".",
            "pen_files": {},
            "raw_batch_operator_mapping": {},
        }

        all_raw_batch_mappings: Dict[str, Dict[str, Any]] = {}

        for res in audit_results:
            file_record: Dict[str, Any] = {
                "total_references": res.total_references,
                "unique_urls": res.unique_urls,
                "present_count": res.present_count,
                "missing_count": res.missing_count,
                "dependencies": {},
            }
            for url, dep in res.dependencies.items():
                file_record["dependencies"][url] = {
                    "is_present_on_disk": dep.is_present_on_disk,
                    "resolved_local_path": dep.resolved_local_path,
                    "resolution_type": dep.resolution_type,
                    "char_id": dep.char_id,
                    "operator_name": dep.operator_name,
                    "remote_source_url": dep.remote_source_url,
                    "occurrences": dep.occurrences,
                }
                if dep.char_id:
                    all_raw_batch_mappings[dep.char_id] = {
                        "raw_url": dep.raw_url,
                        "char_id": dep.char_id,
                        "operator_name": dep.operator_name,
                        "resolved_local_path": dep.resolved_local_path,
                        "resolution_type": dep.resolution_type,
                        "remote_source_url": dep.remote_source_url,
                    }
            manifest_data["pen_files"][res.pen_path] = file_record

        manifest_data["raw_batch_operator_mapping"] = all_raw_batch_mappings

        output_json = Path(output_json).resolve()
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")

        if output_md:
            output_md = Path(output_md).resolve()
            output_md.parent.mkdir(parents=True, exist_ok=True)
            self._write_markdown_report(output_md, audit_results, all_raw_batch_mappings)

        return manifest_data

    def _write_markdown_report(
        self,
        output_md: Path,
        results: List[PenFileAuditResult],
        raw_batch_mappings: Dict[str, Dict[str, Any]],
    ) -> None:
        lines = [
            "# Pen Asset Dependency & Portability Report",
            "",
            "## 1. Overview",
            "This report documents external image asset dependencies in all `.pen` design templates,",
            "identifies legacy `assets/raw_batch/` paths, and provides portable fallbacks to canonical assets.",
            "",
            "| Pen Template | Total Refs | Unique URLs | Direct Local | Resolved via Repo / Fallback | Unresolved |",
            "|---|---|---|---|---|---|",
        ]
        for r in results:
            direct_local = sum(1 for d in r.dependencies.values() if d.resolution_type == "present_local")
            resolved_fallback = sum(
                1 for d in r.dependencies.values() if d.resolution_type in ("hero_art", "card_fallback")
            )
            lines.append(
                f"| `{r.pen_path}` | {r.total_references} | {r.unique_urls} | {direct_local} | {resolved_fallback} | {r.missing_count} |"
            )

        lines.extend([
            "",
            "## 2. Raw Batch (`assets/raw_batch/char_*_1.png`) Mapping",
            f"Total unique operators referenced via legacy raw_batch paths: **{len(raw_batch_mappings)}**.",
            "",
            "| Operator ID | Name | Resolution Type | Resolved Local Path | Upstream Remote URL |",
            "|---|---|---|---|---|",
        ])

        for cid, info in sorted(raw_batch_mappings.items()):
            resolved = f"`{info['resolved_local_path']}`" if info['resolved_local_path'] else "*None (Fallback Mode)*"
            lines.append(
                f"| `{cid}` | {info['operator_name'] or 'Unknown'} | `{info['resolution_type']}` | {resolved} | [Source]({info['remote_source_url']}) |"
            )

        lines.extend([
            "",
            "## 3. Downstream Consumption & Portability Policy",
            "1. **Never mutate .pen binary/JSON files directly** without Pencil MCP / editor verification.",
            "2. **Downstream consumers** should read `reports/pen_asset_dependencies.json` to map any `assets/raw_batch/` URL to `resolved_local_path`.",
            "3. If a hero art is missing in `assets/operators/`, consumers gracefully fall back to Rhine's card art specimen or metadata-only render mode.",
            "",
        ])
        output_md.write_text("\n".join(lines), encoding="utf-8")
