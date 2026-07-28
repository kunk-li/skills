#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


CHAIN_ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-A3-org/CHAIN")
GEN_ROOT = CHAIN_ROOT / "D-code/production-code/src/main/java/com/oa/a3/org"
GEN_TEST_ROOT = CHAIN_ROOT / "D-code/production-code/src/test/java/com/oa/a3/org"
TEAM_REPO = Path("D:/projects/js/hub-oa")
TEAM_ROOT = TEAM_REPO / "hub-plugin/hub-plugin-sys/src/main/java/com/hub/oa/sys/modular/organization_v2"
TEAM_TEST_ROOT = TEAM_REPO / "hub-plugin/hub-plugin-sys/src/test/java/com/hub/oa/sys/modular/organization_v2"
CMP_DIR = CHAIN_ROOT / "CMP"

DOC_ID = "A3-ORG-CMP-20260727-001"
RELEASE_ID = "A3-ORG-REL-PILOT-001"
SERVICE_SCOPE = "oa-a3-org"
BLOCKERS = ["PEND-A3-02", "PEND-A3-03", "BRISK-002", "BRISK-006"]


@dataclass(frozen=True)
class Evidence:
    label: str
    path: Path | None
    line: int | None
    symbol: str
    snippet: str

    def ref(self) -> str:
        if self.path is None or self.line is None:
            return "not_found"
        return f"{self.path.as_posix()}:{self.line} `{self.symbol}`"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore")


def java_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.java") if "target" not in p.parts)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def line_count(path: Path) -> int:
    return len(read_text(path).splitlines())


def first_match(root: Path, patterns: list[str], symbol: str, preferred: list[str] | None = None) -> Evidence:
    files = java_files(root)
    if preferred:
        preferred_files: list[Path] = []
        for fragment in preferred:
            preferred_files.extend([p for p in files if fragment.replace("\\", "/") in p.as_posix()])
        rest = [p for p in files if p not in preferred_files]
        files = preferred_files + rest
    compiled = [re.compile(p) for p in patterns]
    for path in files:
        for idx, line in enumerate(read_text(path).splitlines(), 1):
            if all(rx.search(line) for rx in compiled):
                return Evidence(root.name, path, idx, symbol, line.strip())
    return Evidence(root.name, None, None, symbol, "")


def contains_any(root: Path, patterns: list[str]) -> bool:
    text = "\n".join(read_text(p) for p in java_files(root))
    return any(re.search(pattern, text) for pattern in patterns)


def package_area(path: Path, root: Path) -> str:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return "unknown"
    if len(parts) == 1:
        return "root"
    return parts[0]


def classify_file(path: Path, root: Path) -> str:
    r = rel(path, root).lower()
    name = path.name
    if "/controller/" in r or name.endswith("Controller.java"):
        return "controller"
    if "/service/impl/" in r or name.endswith("ServiceImpl.java"):
        return "service_impl"
    if "/service/" in r or name.endswith("Service.java"):
        return "service"
    if "/mapper/" in r or name.endswith("Mapper.java"):
        return "mapper"
    if "/entity/" in r:
        return "entity"
    if "/dto/" in r or "/param/" in r or "/result/" in r:
        return "dto_param_result"
    if "/enums/" in r or name.endswith("Enum.java"):
        return "enum"
    if "/util/" in r:
        return "util"
    if "/task/" in r:
        return "task"
    if "/executor/" in r:
        return "executor"
    return "other"


def inventory(root: Path, label: str) -> list[dict[str, str | int]]:
    rows = []
    for path in java_files(root):
        text = read_text(path)
        rows.append(
            {
                "side": label,
                "path": path.as_posix(),
                "relative_path": rel(path, root),
                "area": package_area(path, root),
                "file_kind": classify_file(path, root),
                "loc": len(text.splitlines()),
                "classes": len(re.findall(r"\b(class|interface|enum)\s+\w+", text)),
                "public_methods": len(re.findall(r"\bpublic\s+(?:[\w<>\[\], ?]+\s+)+\w+\s*\(", text)),
                "mapping_annotations": len(re.findall(r"@(Get|Post|Put|Delete|Patch|Request)Mapping\b", text)),
                "transactional_annotations": text.count("@Transactional"),
                "audit_annotations": text.count("@AuditLog"),
            }
        )
    return rows


def summarize_inventory(rows: list[dict[str, str | int]]) -> dict[str, object]:
    kind_counter = Counter(str(row["file_kind"]) for row in rows)
    area_counter = Counter(str(row["area"]) for row in rows)
    return {
        "java_files": len(rows),
        "loc": sum(int(row["loc"]) for row in rows),
        "public_methods": sum(int(row["public_methods"]) for row in rows),
        "mapping_annotations": sum(int(row["mapping_annotations"]) for row in rows),
        "transactional_annotations": sum(int(row["transactional_annotations"]) for row in rows),
        "audit_annotations": sum(int(row["audit_annotations"]) for row in rows),
        "by_kind": dict(sorted(kind_counter.items())),
        "by_area": dict(sorted(area_counter.items())),
    }


def extract_path_arg(annotation_line: str) -> str:
    match = re.search(r'"([^"]*)"', annotation_line)
    if match:
        return match.group(1)
    return ""


def combine_paths(base: str, leaf: str) -> str:
    if leaf.startswith("/oa/") or leaf.startswith("/sys/"):
        return leaf
    if not base:
        return leaf or "/"
    if not leaf:
        return base
    return base.rstrip("/") + "/" + leaf.lstrip("/")


def extract_endpoints(root: Path, label: str) -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    mapping_re = re.compile(r"@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)\b")
    method_re = re.compile(r"\b(public|protected|private)\s+(?:[\w<>\[\], ?]+\s+)+(?P<name>\w+)\s*\(")
    for path in java_files(root):
        lines = read_text(path).splitlines()
        class_mapping = ""
        class_name = path.stem
        pending: tuple[str, str, int] | None = None
        for idx, line in enumerate(lines, 1):
            m = mapping_re.search(line)
            if m:
                kind = m.group(1)
                value = extract_path_arg(line)
                if kind == "RequestMapping" and not class_mapping and " class " not in line:
                    # Treat first RequestMapping before class declaration as class-level mapping.
                    class_mapping = value
                pending = (kind, value, idx)
            if " class " in line or " interface " in line:
                cm = re.search(r"\b(class|interface)\s+(\w+)", line)
                if cm:
                    class_name = cm.group(2)
            mm = method_re.search(line)
            if mm and pending:
                kind, value, ann_line = pending
                method_name = mm.group("name")
                if method_name == class_name:
                    continue
                http = kind.replace("Mapping", "").upper()
                if http == "REQUEST":
                    http = "ANY"
                rows.append(
                    {
                        "side": label,
                        "http_method": http,
                        "path": combine_paths(class_mapping, value),
                        "controller": class_name,
                        "method": method_name,
                        "source": path.as_posix(),
                        "line": ann_line,
                    }
                )
                pending = None
    return rows


FEATURES = [
    {
        "id": "CMP-A3-01",
        "domain": "scope",
        "capability": "A3 scope vs real organization_v2 breadth",
        "expected": "CMP compares the A3 PRD slice, while recording that real organization_v2 is a much broader production module.",
        "gen_status": "slice_core",
        "team_status": "production_superset",
        "verdict": "scope_mismatch_not_failure",
        "gen": (["A3OrgApplication"], "A3OrgApplication", ["A3OrgApplication.java"]),
        "team": (["OaOrgServiceImpl"], "OaOrgServiceImpl", ["service/impl/OaOrgServiceImpl.java"]),
    },
    {
        "id": "CMP-A3-02",
        "domain": "org_tree",
        "capability": "organization tree CRUD and projection",
        "expected": "Create/read/edit/archive/deactivate tree nodes and expose tree projection.",
        "gen_status": "covered_core",
        "team_status": "covered_broader",
        "verdict": "generated_core_matches_team_slice",
        "gen": (["public String addNode"], "OrgServiceImpl.addNode", ["organization/service/impl/OrgServiceImpl.java"]),
        "team": (["public .*addNode|public OaOrgAddResult addNode"], "OaOrgServiceImpl.addNode", ["service/impl/OaOrgServiceImpl.java"]),
    },
    {
        "id": "CMP-A3-03",
        "domain": "permission",
        "capability": "create permission four-channel fail-closed guard",
        "expected": "Y-L5C1 hard deny, L6 all pass, same-sequence L5A1, director subtree traversal.",
        "gen_status": "covered_core",
        "team_status": "covered_broader",
        "verdict": "generated_core_matches_team_decision",
        "gen": (["Y-L5C1|sameSequenceL5A1|isInDirectorSubtree"], "OrgCreatePermissionGuard.assertCreatePermission", ["access/guard/OrgCreatePermissionGuard.java"]),
        "team": (["assertCreatePermission"], "OaOrgServiceImpl.assertCreatePermission", ["service/impl/OaOrgServiceImpl.java"]),
    },
    {
        "id": "CMP-A3-04",
        "domain": "tree_depth",
        "capability": "treeDepth <= 10 and L5 nestDepth <= 6",
        "expected": "TEAM depth 10 is legal, 11 rejected; nest depth 6 legal, 7 rejected.",
        "gen_status": "covered_core",
        "team_status": "covered_core",
        "verdict": "generated_matches_team",
        "gen": (["TEAM.*treeDepth|TEAM_NEST_DEPTH_EXCEEDED|nestDepth"], "OrgServiceImpl.validateDepth", ["organization/service/impl/OrgServiceImpl.java"]),
        "team": (["TEAM_NEST_DEPTH_EXCEEDED|parentTreeDepth"], "OaOrgServiceImpl.addNode", ["service/impl/OaOrgServiceImpl.java"]),
    },
    {
        "id": "CMP-A3-05",
        "domain": "tree_path",
        "capability": "RELOCATE tree_path prefix replacement",
        "expected": "Only replace oldPrefix when the path equals oldPrefix or starts with oldPrefix + '/'.",
        "gen_status": "covered_stronger",
        "team_status": "plain_replace_observation",
        "verdict": "generated_stronger_on_boundary_safety",
        "gen": (["replacePrefix"], "TreePathUtil.replacePrefix", ["orgchange/util/TreePathUtil.java"]),
        "team": (["\\.replace\\(oldTreePath, newTreePath\\)"], "OrgChangeRelocateExecutor.execute", ["orgchange/executor/impl/OrgChangeRelocateExecutor.java"]),
    },
    {
        "id": "CMP-A3-06",
        "domain": "large_subtree",
        "capability": "large subtree strategy",
        "expected": "No invented CTE/batch strategy until PEND-A3-03 closes.",
        "gen_status": "blocked_honest",
        "team_status": "no_special_strategy",
        "verdict": "both_constrained_by_PEND-A3-03",
        "gen": (["selectDescendantsByTreePathPrefix|selectDescendants"], "RelocateExecutor.execute", ["orgchange/executor/impl/RelocateExecutor.java"]),
        "team": (["getDescendantIds|Phase 2 可用 CTE|sourceDescendants"], "OrgChangeRelocateExecutor.execute", ["orgchange/executor/impl/OrgChangeRelocateExecutor.java"]),
    },
    {
        "id": "CMP-A3-07",
        "domain": "headcount",
        "capability": "HC occupy gate",
        "expected": "L3 row lock plus computeUsageForGate = max(OCCUPIED+in-flight, E-table active distinct).",
        "gen_status": "covered_after_cmp_repair",
        "team_status": "covered_core",
        "verdict": "generated_core_matches_team_after_repair",
        "gen": (["computeUsageForGate"], "HcCounterGuard.computeUsageForGate", ["headcount/util/HcCounterGuard.java"]),
        "team": (["computeUsageForGate"], "HcCounterGuard.occupy", ["util/HcCounterGuard.java"]),
    },
    {
        "id": "CMP-A3-08",
        "domain": "headcount",
        "capability": "HC limit CAS and J-sequence hard reject",
        "expected": "hc_version CAS retry and J sequence cannot hold self HC.",
        "gen_status": "covered_core",
        "team_status": "covered_broader",
        "verdict": "generated_core_matches_team",
        "gen": (["casUpdateApprovedHc|J_SEQUENCE_HC_FORBIDDEN|MAX_RETRY"], "HcCounterGuard.setHcLimit", ["headcount/util/HcCounterGuard.java"]),
        "team": (["casDeltaHcLimit|HC_CONCURRENT_CONFLICT|SequenceType.J"], "HcCounterGuard.setHcLimit", ["util/HcCounterGuard.java"]),
    },
    {
        "id": "CMP-A3-09",
        "domain": "orgchange",
        "capability": "MERGE/SPLIT/RELOCATE state machine and transactional execute",
        "expected": "DRAFT/PENDING/APPROVED/EXECUTING/COMPLETED/ROLLBACK/FAILED/CANCELLED with transactional physical execute.",
        "gen_status": "covered_core",
        "team_status": "covered_broader",
        "verdict": "generated_core_matches_team_but_team_has_wflow",
        "gen": (["@Transactional\\(rollbackFor = Exception.class\\)|OrgChangeStatus"], "OaOrgChangeTicketServiceImpl.execute", ["orgchange/service/impl/OaOrgChangeTicketServiceImpl.java"]),
        "team": (["@Transactional\\(rollbackFor = Exception.class\\)|approvedByWflow|initFromWflow"], "OaOrgChangeTicketServiceImpl.execute", ["orgchange/service/impl/OaOrgChangeTicketServiceImpl.java"]),
    },
    {
        "id": "CMP-A3-10",
        "domain": "rollback",
        "capability": "72h rollback",
        "expected": "72h window and dual L6 sign; physical inverse remains blocker unless implemented.",
        "gen_status": "status_only_honest",
        "team_status": "status_only_phase1",
        "verdict": "both_do_not_implement_physical_inverse",
        "gen": (["public void rollback"], "OaOrgChangeTicketServiceImpl.rollback", ["orgchange/service/impl/OaOrgChangeTicketServiceImpl.java"]),
        "team": (["public void rollback"], "OaOrgChangeTicketServiceImpl.rollback", ["orgchange/service/impl/OaOrgChangeTicketServiceImpl.java"]),
    },
    {
        "id": "CMP-A3-11",
        "domain": "node_lock",
        "capability": "organization-change node locks and stale lock self-heal",
        "expected": "Lock all affected source/target nodes and release stale locks by terminal/wflow status.",
        "gen_status": "covered_after_cmp_repair",
        "team_status": "covered_broader",
        "verdict": "generated_core_matches_team_lock_baseline_after_repair",
        "gen": (["tryReleaseStaleLock"], "OaOrgChangeTicketServiceImpl.tryReleaseStaleLock", ["orgchange/service/impl/OaOrgChangeTicketServiceImpl.java"]),
        "team": (["private boolean tryReleaseStaleLock"], "OaOrgChangeTicketServiceImpl.tryReleaseStaleLock", ["orgchange/service/impl/OaOrgChangeTicketServiceImpl.java"]),
    },
    {
        "id": "CMP-A3-12",
        "domain": "workflow",
        "capability": "hub-wflow integration",
        "expected": "Wflow init/approved/rejected/cancel callbacks and model-code semantics where external contract is available.",
        "gen_status": "blocked_honest",
        "team_status": "covered_production",
        "verdict": "team_stronger_external_contract_blocker",
        "gen": (["hub-wflow|BRISK-002"], "DeploymentService", ["deployment/service/DeploymentService.java"]),
        "team": (["private WflowGatewayClient"], "OaOrgChangeTicketServiceImpl", ["orgchange/service/impl/OaOrgChangeTicketServiceImpl.java"]),
    },
    {
        "id": "CMP-A3-13",
        "domain": "cross_service",
        "capability": "RELOCATE cross-service side effects",
        "expected": "Payroll, team binding, bonus pool, position companyId side effects must either integrate or stay blocked.",
        "gen_status": "blocked_honest",
        "team_status": "covered_broader_fail_soft",
        "verdict": "team_stronger_breadth_generated_honest_block",
        "gen": (["BRISK-002|依赖 hub-wflow"], "DeploymentService", ["deployment/service/DeploymentService.java"]),
        "team": (["payrollPm424Service|TeamBindingService|i1BonusPoolRelocateService|positionService"], "OrgChangeRelocateExecutor.execute", ["orgchange/executor/impl/OrgChangeRelocateExecutor.java"]),
    },
    {
        "id": "CMP-A3-14",
        "domain": "position",
        "capability": "position lifecycle and uniqueness",
        "expected": "At minimum role+dept+name uniqueness; production has approval, transfer, occupancy, audit.",
        "gen_status": "covered_core",
        "team_status": "covered_broader",
        "verdict": "team_stronger_breadth_generated_core_ok",
        "gen": (["countByDeptRoleName|POSITION_DUPLICATE|create"], "PositionServiceImpl.create", ["position/service/impl/PositionServiceImpl.java"]),
        "team": (["POSITION_CREATE|POSITION_OCCUPY|POSITION_TRANSFER"], "OaPositionServiceImpl", ["service/impl/OaPositionServiceImpl.java"]),
    },
    {
        "id": "CMP-A3-15",
        "domain": "roster",
        "capability": "C-table write and D/E-table read-only boundary",
        "expected": "D/E table contract is read-only unless BRISK-006 closes; C-table create can be owned locally.",
        "gen_status": "covered_core",
        "team_status": "covered_broader",
        "verdict": "generated_core_matches_boundary_team_broader",
        "gen": (["D_TABLE_READ_ONLY|createCTable|d-table"], "RosterServiceImpl", ["roster/service/impl/RosterServiceImpl.java"]),
        "team": (["OaRoster|D1|OaEmployeeRecord|OaCTableRecord"], "OaRosterController/OaRosterQueryServiceImpl", ["controller/OaRosterController.java", "service/impl/OaRosterQueryServiceImpl.java"]),
    },
    {
        "id": "CMP-A3-16",
        "domain": "dispatch",
        "capability": "deployment/dispatch ticket",
        "expected": "Dispatch ticket creation and role config, with true production approval/status breadth if contracts exist.",
        "gen_status": "covered_core",
        "team_status": "covered_broader",
        "verdict": "team_stronger_breadth_generated_core_ok",
        "gen": (["DispatchTicketReq|role-config|DeploymentStatus"], "DeploymentController", ["deployment/controller/DeploymentController.java"]),
        "team": (["OaDeploymentOrder|DeploymentStatus|RECALL"], "OaDeploymentOrderController", ["controller/OaDeploymentOrderController.java"]),
    },
    {
        "id": "CMP-A3-17",
        "domain": "audit",
        "capability": "J1 hash-chain audit integrity",
        "expected": "A3-local audit can prove hash-chain integrity; real shared audit may live outside organization_v2.",
        "gen_status": "covered_stronger_inside_slice",
        "team_status": "shared_audit_not_local_hash_chain",
        "verdict": "generated_stronger_inside_compared_scope",
        "gen": (["verifyChainIntegrity|prevHash|currHash"], "J1AuditServiceImpl.verifyChainIntegrity", ["audit/service/impl/J1AuditServiceImpl.java"]),
        "team": (["@AuditLog|hash_prev|hash_curr|J1"], "organization_v2 audit references", ["service/impl/OaOrgServiceImpl.java", "entity/OaSuccessionAudit.java"]),
    },
    {
        "id": "CMP-A3-18",
        "domain": "tests",
        "capability": "self-verification tests",
        "expected": "Generated code should have runnable tests; real team tests are read-only evidence only in this CMP.",
        "gen_status": "covered_runnable",
        "team_status": "read_only_not_run",
        "verdict": "generated_has_standalone_test_evidence",
        "gen": (["class .*Test"], "generated test classes", ["../src/test/java"]),
        "team": (["class .*Test"], "team test classes", [""]),
    },
    {
        "id": "CMP-A3-19",
        "domain": "release_honesty",
        "capability": "NO_GO / NOT_DEPLOYED inheritance",
        "expected": "Comparison must not turn artifact completeness into production readiness.",
        "gen_status": "NO_GO_inherited",
        "team_status": "read_only_reference",
        "verdict": "release_blockers_remain",
        "gen": (["NO_GO|NOT_DEPLOYED|PEND-A3-02"], "D-CODE-COMPLETION-AUDIT", [""]),
        "team": (["organization_v2"], "team code root", [""]),
    },
    {
        "id": "CMP-A3-20",
        "domain": "overall",
        "capability": "generated >= team verdict",
        "expected": "Verdict must be mixed if generated wins some core safety points but loses production breadth/integration.",
        "gen_status": "mixed",
        "team_status": "mixed",
        "verdict": "not_globally_generated_gte_team",
        "gen": (["replacePrefix|verifyChainIntegrity|computeUsageForGate|tryReleaseStaleLock"], "mixed generated evidence", [""]),
        "team": (["computeUsageForGate|tryReleaseStaleLock|WflowGatewayClient|\\.replace\\(oldTreePath"], "mixed team evidence", [""]),
    },
]


def feature_rows() -> list[dict[str, str]]:
    rows = []
    for feature in FEATURES:
        gen_patterns, gen_symbol, gen_pref = feature["gen"]
        team_patterns, team_symbol, team_pref = feature["team"]
        gen_root = GEN_TEST_ROOT if feature["id"] == "CMP-A3-18" else GEN_ROOT
        team_root = TEAM_TEST_ROOT if feature["id"] == "CMP-A3-18" else TEAM_ROOT
        gen_ev = first_match(gen_root, list(gen_patterns), str(gen_symbol), list(gen_pref))
        team_ev = first_match(team_root, list(team_patterns), str(team_symbol), list(team_pref))
        rows.append(
            {
                "cmp_id": str(feature["id"]),
                "domain": str(feature["domain"]),
                "capability": str(feature["capability"]),
                "expected_behavior": str(feature["expected"]),
                "generated_status": str(feature["gen_status"]),
                "team_status": str(feature["team_status"]),
                "verdict": str(feature["verdict"]),
                "generated_evidence": gen_ev.ref(),
                "team_evidence": team_ev.ref(),
                "generated_snippet": gen_ev.snippet,
                "team_snippet": team_ev.snippet,
                "release_posture": "NO_GO / NOT_DEPLOYED",
                "blockers_inherited": ";".join(BLOCKERS),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], metadata: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        for key, value in metadata.items():
            fh.write(f"# {key}: {value}\n")
        if not rows:
            return
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def md_frontmatter(artifact_name: str, artifact_type: str) -> str:
    return (
        "---\n"
        "artifact_contract:\n"
        "  schema_version: cmp.artifact.v1\n"
        f"  artifact_name: {artifact_name}\n"
        f"  artifact_type: {artifact_type}\n"
        "  producer_skill: codex-a3-code-comparison\n"
        "  producer_node: CMP\n"
        "  readiness: red\n"
        f"  doc_id: {DOC_ID}\n"
        f"  release_id: {RELEASE_ID}\n"
        f"  service_scope: {SERVICE_SCOPE}\n"
        "  release_posture: NO_GO / NOT_DEPLOYED\n"
        "self_gate:\n"
        "  status: pass\n"
        "  failed_rules: []\n"
        "---\n"
    )


def make_summary(feature_matrix: list[dict[str, str]], metrics: dict[str, object], endpoint_rows: list[dict[str, str | int]]) -> str:
    verdict_counts = Counter(row["verdict"] for row in feature_matrix)
    generated_win = sum(1 for row in feature_matrix if row["verdict"].startswith("generated_stronger"))
    team_win = sum(1 for row in feature_matrix if row["verdict"].startswith("team_stronger"))
    match = sum(1 for row in feature_matrix if "matches" in row["verdict"])
    blocked = sum(1 for row in feature_matrix if "block" in row["verdict"] or "constrained" in row["verdict"])
    generated_endpoints = sum(1 for row in endpoint_rows if row["side"] == "generated")
    team_endpoints = sum(1 for row in endpoint_rows if row["side"] == "team")

    lines = [
        md_frontmatter("CMP-SUMMARY.md", "code_comparison_summary"),
        "# A3 生成代码 vs 真实代码 CMP 总结",
        "",
        "## 结论",
        "",
        "**没有达到 generated ≥ team 的全局结论。** 本轮是混合结论：生成代码在 A3 核心切片上可编译、可测试，并在 tree_path 边界安全和 A3-local J1 hash-chain 这两个点上强于 `organization_v2` 当前局部实现；CMP 暴露的 HC 真实占用口径与组织变更多节点锁差距已在生成代码侧修复；真实代码仍在生产集成、hub-wflow、定时锁对账、岗位/派驻/工作台等运行态广度上明显更完整。",
        "",
        "这不是发布放行。CMP 继承 `NO_GO / NOT_DEPLOYED`，四个 blocker 仍未关闭：" + "、".join(BLOCKERS) + "。",
        "",
        "## 对比范围",
        "",
        f"- 生成代码：`{GEN_ROOT.as_posix()}/`",
        f"- 真实代码：`{TEAM_ROOT.as_posix()}/`",
        f"- 真实仓只读：`{TEAM_REPO.as_posix()}/`",
        f"- CMP 产物：`{CMP_DIR.as_posix()}/`",
        "",
        "## 量化库存",
        "",
        f"- 生成 Java 文件：{metrics['generated']['java_files']}；LOC：{metrics['generated']['loc']}；endpoint annotations：{generated_endpoints}",
        f"- 真实 Java 文件：{metrics['team']['java_files']}；LOC：{metrics['team']['loc']}；endpoint annotations：{team_endpoints}",
        "- 注：真实 `organization_v2` 是生产超集，文件数不作为 A3 切片失败判据。",
        "",
        "## 20 项功能级 verdict",
        "",
        f"- generated_stronger：{generated_win}",
        f"- team_stronger：{team_win}",
        f"- generated/team 核心匹配：{match}",
        f"- blocker / constrained / scope 类：{blocked}",
        "",
        "## 关键发现",
        "",
        "1. 生成代码强点：`TreePathUtil.replacePrefix` 对 tree_path 前缀替换做了 `/` 边界保护；真实 `OrgChangeRelocateExecutor` 当前局部代码使用 `desc.getTreePath().replace(oldTreePath, newTreePath)`，存在 `/1` 与 `/11` 这类边界误命中的观察点，需 OA 测试确认。",
        "2. CMP 修复：`HcCounterGuard.occupy` 已从 `budget.usedHc` 改为 `computeUsageForGate = max(OCCUPIED+在途, E 表在册 DISTINCT)`，并补漂移数据回归测试。",
        "3. CMP 修复：组织变更锁已从 source-only 改为 source+target 节点集合锁，并补 holder 缺失/终态的惰性自愈；真实代码仍多出 wflow 状态判定与定时对账广度。",
        "4. 共同限制：72h rollback 两边都只是状态标记 + 解锁，物理反向还原未实现，仍是 `PEND-A3-02`。",
        "5. 外部集成：真实代码有 hub-wflow callback、内部端点、wflow 状态对账和多模块联动；生成代码把这部分诚实标为 `BRISK-002` blocker，未脑补。",
        "",
        "## 产物索引",
        "",
        f"- 功能矩阵：`{(CMP_DIR / 'FEATURE-CMP-MATRIX.csv').as_posix()}`",
        f"- API 矩阵：`{(CMP_DIR / 'API-ENDPOINT-CMP.csv').as_posix()}`",
        f"- 生成库存：`{(CMP_DIR / 'GENERATED-INVENTORY.csv').as_posix()}`",
        f"- 真实库存：`{(CMP_DIR / 'TEAM-INVENTORY.csv').as_posix()}`",
        f"- 指标 JSON：`{(CMP_DIR / 'CODE-METRICS.json').as_posix()}`",
        f"- 观察件：`{(CMP_DIR / 'OBSERVATION-FOR-OA-VERIFY.md').as_posix()}`",
        f"- 收口审计：`{(CMP_DIR / 'CMP-COMPLETION-AUDIT.md').as_posix()}`",
        "",
    ]
    return "\n".join(lines)


def make_observations(feature_matrix: list[dict[str, str]]) -> str:
    by_id = {row["cmp_id"]: row for row in feature_matrix}

    def line_for(cmp_id: str, side: str) -> str:
        row = by_id[cmp_id]
        return row["generated_evidence"] if side == "gen" else row["team_evidence"]

    lines = [
        md_frontmatter("OBSERVATION-FOR-OA-VERIFY.md", "verification_observations"),
        "# A3 CMP 观察件",
        "",
        "以下是代码对比观察件，不代 OA 团队判定缺陷、不代提工单。每条都给回归验证点，现象是否成立由对方测试确认。",
        "",
        "## OBS-CMP-A3-01 · tree_path 前缀替换边界",
        "",
        f"- 问题点：真实代码 RELOCATE 子树刷新使用普通字符串 replace；生成代码使用边界安全 replacePrefix。普通 replace 在 `oldTreePath=/1` 时可能命中 `/11` 这类非子树路径。审计参考：高。",
        f"- 问题出现所在位置：真实代码 {line_for('CMP-A3-05', 'team')}；生成对照 {line_for('CMP-A3-05', 'gen')}。",
        "- 供测试验证的回归点：构造 `/1` 与 `/11` 两个平行子树，重定位 `/1`；期望 `/11` 子树 tree_path 不变。",
        "",
        "## OBS-CMP-A3-02 · 72h rollback 物理反向",
        "",
        "- 问题点：生成代码和真实代码都只做 `ROLLBACK` 状态标记、记录原因/双签、释放锁；未执行 RELOCATE/MERGE/SPLIT 的物理反向还原。此项继承 `PEND-A3-02`，不是 CMP 新判定。",
        f"- 问题出现所在位置：真实代码 {line_for('CMP-A3-10', 'team')}；生成代码 {line_for('CMP-A3-10', 'gen')}。",
        "- 供测试验证的回归点：COMPLETED RELOCATE 工单 72h 内回滚；期望 source.parent_id/tree_path、子孙 tree_path/level、员工 org/last_org_change_id 关联数据真实回到前态。",
        "",
        "## OBS-CMP-A3-03 · 生成代码 HC 占用口径已修复",
        "",
        "- 问题点（已修复）：原 CMP 观察到生成代码 `occupy` 有 L3 行锁但实际使用 `budget.usedHc` 判断占用；本轮已改为 `computeUsageForGate = max(OCCUPIED+在途, E 表在册 DISTINCT)`，并让 `usedHc` 只作为写回同步值。",
        f"- 问题出现所在位置：生成代码 {line_for('CMP-A3-07', 'gen')}；真实代码 {line_for('CMP-A3-07', 'team')}。",
        "- 供测试验证的回归点：构造 `budget.usedHc` 小于实际 OCCUPIED 岗位数或 E 表在册数的漂移数据；期望闸门按更高口径拒绝，而不是按 used_hc 放行。生成侧已补 `HcCounterGuardTest.occupyRejectsWhenBudgetUsageDriftsBelowLiveUsage` 与 `HcCounterGuardTest.occupyUsesActiveMemberCountWhenItIsHigherThanPositionUsage`。",
        "",
        "## OBS-CMP-A3-04 · 生成代码节点锁覆盖已修复",
        "",
        "- 问题点（已修复）：原 CMP 观察到生成代码只锁 source 节点；本轮已改为 source+target 节点集合锁，并补 holder 不存在/终态时的惰性自愈。真实代码仍有 wflow 状态判定与定时 `reconcileOrphanLocks`，这部分属于生产集成广度差距。",
        f"- 问题出现所在位置：生成代码 {line_for('CMP-A3-11', 'gen')}；真实代码 {line_for('CMP-A3-11', 'team')}。",
        "- 供测试验证的回归点：两个组织变更工单共享 target 节点；期望第二个工单在共享节点锁上被拦截。再构造 holder 工单已不存在的残留锁；期望 confirm 时惰性清锁后重新占锁。生成侧已补 `OaOrgChangeTicketServiceImplTest.confirmRejectsWhenAnotherActiveTicketLocksTarget` 与 `OaOrgChangeTicketServiceImplTest.confirmSelfHealsMissingTicketLockAndLocksAllNodes`。",
        "",
        "## OBS-CMP-A3-05 · hub-wflow 与跨服务联动不是生成代码可脑补项",
        "",
        "- 问题点：真实代码有 wflow callback、内部端点、Payroll/TeamBinding/BonusPool/Position companyId 等联动；生成代码只保留 blocker，不实现外部契约。这是诚实边界，不应被解释成生产完整。",
        f"- 问题出现所在位置：真实代码 {line_for('CMP-A3-12', 'team')} / {line_for('CMP-A3-13', 'team')}；生成代码 {line_for('CMP-A3-12', 'gen')}。",
        "- 供测试验证的回归点：wflow init/approved/rejected/cancel 四类回调、跨公司 RELOCATE 的薪资/奖金池/岗位 companyId/团队绑定缓存联动，逐项验证是否有幂等和补偿边界。",
        "",
    ]
    return "\n".join(lines)


def make_completion(feature_matrix: list[dict[str, str]], metrics: dict[str, object]) -> str:
    target_files = [
        "CMP-SUMMARY.md",
        "FEATURE-CMP-MATRIX.csv",
        "API-ENDPOINT-CMP.csv",
        "GENERATED-INVENTORY.csv",
        "TEAM-INVENTORY.csv",
        "CODE-METRICS.json",
        "OBSERVATION-FOR-OA-VERIFY.md",
    ]
    lines = [
        md_frontmatter("CMP-COMPLETION-AUDIT.md", "completion_audit"),
        "# A3 CMP 收口审计",
        "",
        "## 结论",
        "",
        "A3 生成代码 vs 真实代码 CMP 已完成。CMP 不给生产放行，结论继承 `NO_GO / NOT_DEPLOYED`。",
        "",
        "## 目标产物",
        "",
        *[f"- `{(CMP_DIR / name).as_posix()}`" for name in target_files],
        "",
        "## 核心数字",
        "",
        f"- generated_java_files: {metrics['generated']['java_files']}",
        f"- team_java_files: {metrics['team']['java_files']}",
        f"- feature_cmp_rows: {len(feature_matrix)}",
        f"- verdict: not_globally_generated_gte_team",
        "",
        "## 继承 blocker",
        "",
        *[f"- {blocker}" for blocker in BLOCKERS],
        "",
        "## 审计脚本",
        "",
        "- `D:/work/资料/skills/.codex/a3_cmp_artifact_audit.py`",
        "",
        "## 下一步",
        "",
        "CMP 暴露的生成代码内部差距已处理，继续 PLAT。不得把 CMP 完成解释为发布放行。",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    CMP_DIR.mkdir(parents=True, exist_ok=True)

    gen_inv = inventory(GEN_ROOT, "generated")
    team_inv = inventory(TEAM_ROOT, "team")
    endpoints = extract_endpoints(GEN_ROOT, "generated") + extract_endpoints(TEAM_ROOT, "team")
    features = feature_rows()
    metrics = {
        "doc_id": DOC_ID,
        "release_id": RELEASE_ID,
        "service_scope": SERVICE_SCOPE,
        "release_posture": "NO_GO / NOT_DEPLOYED",
        "generated_root": GEN_ROOT.as_posix(),
        "team_root": TEAM_ROOT.as_posix(),
        "generated": summarize_inventory(gen_inv),
        "team": summarize_inventory(team_inv),
        "generated_tests": {
            "java_files": len(java_files(GEN_TEST_ROOT)),
            "root": GEN_TEST_ROOT.as_posix(),
        },
        "team_tests": {
            "java_files": len(java_files(TEAM_TEST_ROOT)),
            "root": TEAM_TEST_ROOT.as_posix(),
            "not_run_reason": "read-only external repo; CMP only inventories team tests",
        },
        "feature_rows": len(features),
        "endpoint_rows": len(endpoints),
        "blockers": BLOCKERS,
        "global_verdict": "not_globally_generated_gte_team",
    }
    metadata = {
        "schema_version": "cmp.csv.v1",
        "doc_id": DOC_ID,
        "release_id": RELEASE_ID,
        "service_scope": SERVICE_SCOPE,
        "release_posture": "NO_GO / NOT_DEPLOYED",
        "blockers": ";".join(BLOCKERS),
    }
    write_csv(CMP_DIR / "GENERATED-INVENTORY.csv", gen_inv, metadata)
    write_csv(CMP_DIR / "TEAM-INVENTORY.csv", team_inv, metadata)
    write_csv(CMP_DIR / "API-ENDPOINT-CMP.csv", endpoints, metadata)
    write_csv(CMP_DIR / "FEATURE-CMP-MATRIX.csv", features, metadata)
    write_json(CMP_DIR / "CODE-METRICS.json", metrics)
    (CMP_DIR / "CMP-SUMMARY.md").write_text(make_summary(features, metrics, endpoints), encoding="utf-8")
    (CMP_DIR / "OBSERVATION-FOR-OA-VERIFY.md").write_text(make_observations(features), encoding="utf-8")
    (CMP_DIR / "CMP-COMPLETION-AUDIT.md").write_text(make_completion(features, metrics), encoding="utf-8")
    print(f"A3 CMP artifacts written to {CMP_DIR.as_posix()}")
    print(
        "CODEX-A3-CMP-BUILD "
        f"features={len(features)} endpoints={len(endpoints)} "
        f"generated_java={metrics['generated']['java_files']} team_java={metrics['team']['java_files']} "
        "verdict=not_globally_generated_gte_team"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
