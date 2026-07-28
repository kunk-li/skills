from pathlib import Path
import textwrap

ROOT = Path("D:/projects/skills-pilot/oa-skill-gen/_oa-validation/oaval-Z1-watchdog/CHAIN/D-code/production-code-full")
MAIN = ROOT / "src/main/java/com/skills/pilot/oa/watchdog/full"
TEST = ROOT / "src/test/java/com/skills/pilot/oa/watchdog/full"


def write(rel: str, body: str, test: bool = False) -> None:
    base = TEST if test else MAIN
    path = base / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(body).strip() + "\n", encoding="utf-8")


def simple_class(pkg: str, name: str, fields: list[str]) -> str:
    lines = [f"package com.skills.pilot.oa.watchdog.full.{pkg};", "", "import java.time.Instant;", "import java.util.*;", "", f"public final class {name} {{"]
    for field in fields:
        lines.append(f"    public {field};")
    lines.append("}")
    return "\n".join(lines)


def generate_api() -> None:
    write("api/ErrorCode.java", """
        package com.skills.pilot.oa.watchdog.full.api;

        public enum ErrorCode {
            COMMON_VALIDATION_ERROR(400), UNAUTHORIZED(401), FORBIDDEN_ROLE(403),
            ALERT_NOT_FOUND(404), ALERT_ALREADY_ACKED(409), BLACKSWAN_ALERT_CLOSED(409),
            BLACKSWAN_DIM_NOT_FOUND(404), BLACKSWAN_DIM_PARAM_INVALID(400),
            BLACKSWAN_DIM_PARAM_MISSING(404), BLACKSWAN_CONFIG_NEED_APPROVAL(409),
            COMPLAINT_TARGET_NOT_FOUND(404), COMPLAINT_SCREEN_ROLE_DENIED(403),
            COMPLAINT_TICKET_NOT_FOUND(404), COMPLAINT_SCREEN_STATUS_INVALID(409),
            COMPLAINT_SCREENING_FAILED(409), COMPLAINT_NOT_DUAL_SIGN_STATUS(409),
            COMPLAINT_DUAL_SIGN_NOT_L6(403), COMPLAINT_L6_SELF_SIGN_FORBIDDEN(403),
            COMPLAINT_SAME_L6_DUAL_SIGN_FORBIDDEN(409), COMPLAINT_DUAL_SIGN_TIMEOUT(409),
            REVIEW_HOLD_ACTION_CONFLICT(409), REVIEW_HOLD_NOT_FOUND(404),
            WHISTLEBLOWER_PROTECTION_HOLD(403), WHISTLEBLOWER_RETALIATION_BLOCKED(403),
            WATCHDOG_CHAIR_CONFLICT(403), IMPERIAL_TAKEOVER_L6_ONLY(403),
            IMPERIAL_TAKEOVER_NOT_FOUND(404), IMPERIAL_TAKEOVER_ALREADY_REVOKED(409),
            COMPLIANCE_INQUIRY_FORBIDDEN(403), COMPLIANCE_INQUIRY_TICKET_REQUIRED(403),
            TICKET_STATUS_NOT_APPROVABLE(409), IDEMPOTENCY_CONFLICT(409),
            MONTHLY_REPORT_TAIL_TRUNCATED(409);

            private final int httpStatus;
            ErrorCode(int httpStatus) { this.httpStatus = httpStatus; }
            public int httpStatus() { return httpStatus; }
            public ApiException toException(Object... details) {
                String msg = details == null || details.length == 0 ? name() : name() + " " + java.util.Arrays.toString(details);
                return new ApiException(this, msg);
            }
        }
    """)
    write("api/ApiException.java", """
        package com.skills.pilot.oa.watchdog.full.api;

        public final class ApiException extends RuntimeException {
            private final ErrorCode code;
            public ApiException(ErrorCode code, String message) { super(message); this.code = code; }
            public ErrorCode code() { return code; }
            public int httpStatus() { return code.httpStatus(); }
        }
    """)
    write("api/RequestContext.java", """
        package com.skills.pilot.oa.watchdog.full.api;

        import java.time.Instant;

        public final class RequestContext {
            public final String userId;
            public final String eid;
            public final String roleCode;
            public final String orgId;
            public final String totp;
            public final Instant now;
            public RequestContext(String userId, String eid, String roleCode, String orgId, String totp, Instant now) {
                this.userId = userId;
                this.eid = eid;
                this.roleCode = roleCode == null ? "" : roleCode;
                this.orgId = orgId;
                this.totp = totp;
                this.now = now == null ? Instant.now() : now;
            }
            public boolean role(String expected) { return expected.equals(roleCode); }
            public boolean roleStartsWith(String prefix) { return roleCode != null && roleCode.startsWith(prefix); }
        }
    """)
    write("api/EndpointCatalog.java", """
        package com.skills.pilot.oa.watchdog.full.api;

        import java.util.*;

        public final class EndpointCatalog {
            public static final class Route {
                public final String method;
                public final String path;
                public final String owner;
                Route(String method, String path, String owner) { this.method = method; this.path = path; this.owner = owner; }
            }
            private final List<Route> routes = new ArrayList<>();
            public EndpointCatalog() {
                add("GET","/oa/blackswan/dashboard","blackswan");
                add("GET","/oa/blackswan/alerts","blackswan");
                add("GET","/oa/blackswan/alerts/{alertUuid}","blackswan");
                add("POST","/oa/blackswan/alerts/{alertUuid}/ack","blackswan");
                add("POST","/oa/blackswan/alerts/{alertUuid}/close","blackswan");
                add("POST","/oa/blackswan/complaints","complaint");
                add("GET","/oa/blackswan/complaints","complaint");
                add("GET","/oa/blackswan/complaints/{complaintUuid}","complaint");
                add("POST","/oa/blackswan/complaints/{complaintUuid}/screen","complaint");
                add("POST","/oa/blackswan/complaints/{complaintUuid}/dual-l6-first-sign","complaint");
                add("POST","/oa/blackswan/complaints/{complaintUuid}/dual-l6-second-sign","complaint");
                add("GET","/oa/blackswan/config","config");
                add("POST","/oa/blackswan/config","config");
                add("POST","/oa/blackswan/config/approve","config");
                add("POST","/oa/internal/blackswan/scan","internal");
                add("POST","/oa/internal/blackswan/deadlock/fingerprint","internal");
                add("GET","/oa/blackswan/deadlock/fingerprints","deadlock");
                add("POST","/oa/blackswan/review-hold","review-hold");
                add("GET","/oa/blackswan/review-hold","review-hold");
                add("POST","/oa/blackswan/review-hold/{id}/release","review-hold");
                add("POST","/oa/blackswan/peak-month","peak-month");
                add("GET","/oa/blackswan/peak-month/list","peak-month");
                add("POST","/oa/governance/imperial/assign","imperial");
                add("POST","/oa/governance/imperial/revoke","imperial");
                add("GET","/oa/governance/imperial/page","imperial");
                add("POST","/oa/compliance/inquiry/apply","compliance-inquiry");
                add("POST","/oa/compliance/inquiry/{id}/handle","compliance-inquiry");
                add("GET","/oa/compliance/inquiry/real-name","compliance-inquiry");
                add("GET","/oa/compliance/inquiry/pending","compliance-inquiry");
            }
            private void add(String method, String path, String owner) { routes.add(new Route(method, path, owner)); }
            public List<Route> routes() { return Collections.unmodifiableList(routes); }
            public boolean contains(String method, String path) { return routes.stream().anyMatch(r -> r.method.equals(method) && r.path.equals(path)); }
        }
    """)


def generate_model() -> None:
    write("model/DimCode.java", """
        package com.skills.pilot.oa.watchdog.full.model;
        public enum DimCode {
            D1, D2, D3, D4, D5, D6, D7, D8, D9, F7_PIP;
            public String getCode() { return this == F7_PIP ? "F7-PIP" : name(); }
            public static DimCode of(String code) {
                if (code == null) return null;
                if ("F7-PIP".equals(code)) return F7_PIP;
                try { return DimCode.valueOf(code); } catch (IllegalArgumentException ex) { return null; }
            }
        }
    """)
    write("model/BlackswanAlertStatus.java", """
        package com.skills.pilot.oa.watchdog.full.model;
        public enum BlackswanAlertStatus {
            TRIGGERED, ACKED, IN_HANDLING, CLOSED, ESCALATED_L6, EXTERNAL_TAKEOVER;
            public String getCode() { return name(); }
            public boolean isTerminal() { return this == CLOSED || this == EXTERNAL_TAKEOVER; }
        }
    """)
    write("model/BlackswanSeverity.java", """
        package com.skills.pilot.oa.watchdog.full.model;
        public enum BlackswanSeverity {
            RED, ORANGE, YELLOW;
            public String getCode() { return name(); }
            public int slaHours() { return this == RED ? 24 : this == ORANGE ? 48 : 72; }
        }
    """)
    write("model/ComplaintStatus.java", """
        package com.skills.pilot.oa.watchdog.full.model;
        public enum ComplaintStatus {
            SUBMITTED, SCREENING_PASSED, SCREENING_FAILED, FILED,
            PENDING_DUAL_L6_SIGN, L6_SIGNED_FIRST, L6_DUAL_SIGNED,
            CLOSED_REJECTED, EXTERNAL_COMMITTEE_TAKEOVER, CLOSED;
            public String getCode() { return name(); }
            public boolean isTerminal() {
                return this == CLOSED || this == CLOSED_REJECTED || this == L6_DUAL_SIGNED
                        || this == SCREENING_FAILED || this == EXTERNAL_COMMITTEE_TAKEOVER;
            }
        }
    """)
    write("model/ComplaintScreeningResult.java", """
        package com.skills.pilot.oa.watchdog.full.model;
        public enum ComplaintScreeningResult { PENDING, PASSED, FAILED, QUALITY_REVIEW, MALICIOUS; public String getCode() { return name(); } }
    """)
    write("model/ReviewHoldAction.java", """
        package com.skills.pilot.oa.watchdog.full.model;
        public enum ReviewHoldAction {
            PAYROLL_ADJUST("PAYROLL_ADJUST","SUSPEND_PAY"), TRANSFER("TRANSFER","TRANSFER"),
            TERMINATION("TERMINATION",null), PERF_DOWN("PERF_DOWN","PERF_DOWN"), DEMOTE("DEMOTE","DEMOTE");
            private final String code; private final String whistleblowerCode;
            ReviewHoldAction(String code, String whistleblowerCode) { this.code = code; this.whistleblowerCode = whistleblowerCode; }
            public String getCode() { return code; }
            public String getWhistleblowerCode() { return whistleblowerCode; }
        }
    """)
    write("model/ImperialTakeoverStatus.java", """
        package com.skills.pilot.oa.watchdog.full.model;
        public enum ImperialTakeoverStatus { ACTIVE, REVOKED, EXPIRED; public String getCode() { return name(); } }
    """)
    write("model/ComplianceInquiryAction.java", """
        package com.skills.pilot.oa.watchdog.full.model;
        public enum ComplianceInquiryAction { COMPLETE, REJECT; public String getCode() { return name(); } }
    """)
    write("model/TicketStatus.java", """
        package com.skills.pilot.oa.watchdog.full.model;
        public enum TicketStatus { PENDING, COMPLETED, REJECTED; public String getCode() { return name(); } }
    """)


def generate_data_classes() -> None:
    entities = {
        "Alert": ["long id", "String alertUuid", "String dimCode", "String severity", "String orgId", "String targetEid", "int problemSourceIsL6", "String payloadJson", "String payloadHash", "String status", "String ackUserId", "Instant ackTime", "String closedUserId", "Instant closedTime", "String resolution", "Instant escalatedL6Time", "Instant createTime"],
        "Complaint": ["long id", "String complaintUuid", "String reporterEidHash", "String targetEid", "String targetRoleCode", "String contentRefId", "String contentText", "String targetAliasName", "int isAnonymousTemplate", "int hasConcreteFacts", "String screeningResult", "String chairpersonEid", "int chairReassigned", "String status", "Instant filedAt", "Instant reviewDeadline", "Instant escalatedL6At", "Instant closedAt", "Instant externalTakeoverAt", "String l6FirstSignUserId", "Instant l6FirstSignAt", "String l6SecondSignUserId", "Instant l6SecondSignAt", "int reporterRecentCount30d", "Instant createTime"],
        "ComplaintTarget": ["long id", "long complaintId", "String targetEid", "String targetRoleCode", "String targetAliasName", "int sequence"],
        "DimConfig": ["long id", "String dimCode", "String paramKey", "String paramValue", "String paramUnit", "String lastUpdatedBy", "String lastApprovedBy", "Instant lastApprovedAt", "String approvalTicketId", "String pendingValue", "String changeReason"],
        "DeadlockFingerprint": ["long id", "String topicHash", "List<String> nodeSet = new ArrayList<>()", "int cumulativeCount", "Instant lastTriggeredAt", "String triggeredAlertUuid"],
        "ReviewHold": ["long id", "String targetEid", "String complaintUuid", "Instant holdStart", "Instant holdUntil", "String blockedActions", "String status", "Instant releasedAt", "String releasedBy", "String originalChairpersonEid", "int chairpersonForceSwitched"],
        "PeakMonth": ["long id", "String orgId", "int peakYear", "int peakMonth", "String declaredBy", "Instant declaredAt"],
        "ImperialTakeover": ["long id", "String ticketNo", "String agentEid", "String scopeJson", "String status", "String orgId", "String reason", "String createdBy", "Instant approvedAt", "Instant revokedAt", "String revokeReason", "Instant createTime"],
        "ComplianceInquiryTicket": ["long id", "String ticketNo", "String type", "String status", "String subjectEid", "String fieldsCsv", "String reason", "String purpose", "String applicantId", "String applicantRole", "String currentApproverId", "Instant completedAt", "String handlerId", "String comment", "Instant createTime"],
        "AuditEvent": ["String eventType", "String targetType", "String targetId", "String operatorUid", "String result", "Instant at"],
        "RedAlertPush": ["String alertUuid", "String status", "Instant at"],
    }
    for name, fields in entities.items():
        write(f"entity/{name}.java", simple_class("entity", name, fields))
    dtos = {
        "AlertPageQuery": ["String dimCode", "String severity", "String status", "String orgId", "int current = 1", "int size = 20"],
        "AckRequest": ["String remark"],
        "CloseRequest": ["String resolution", "String remark"],
        "ComplaintSubmitRequest": ["String targetAliasName", "List<ComplaintTargetRequest> targets = new ArrayList<>()", "String contentText", "Integer isAnonymousTemplate", "Integer hasConcreteFacts"],
        "ComplaintScreenRequest": ["Integer hasConcreteFacts", "Integer isAnonymousTemplate", "String remark"],
        "DualSignRequest": ["Boolean accept", "String remark"],
        "ConfigSaveRequest": ["String dimCode", "String paramKey", "String pendingValue", "String changeReason"],
        "ConfigApproveRequest": ["String dimCode", "String paramKey", "String totp"],
        "DeadlockReportRequest": ["String topicHash", "List<String> nodeSet = new ArrayList<>()"],
        "ReviewHoldCreateRequest": ["String targetEid", "String complaintUuid", "String blockedActions", "Integer holdWorkdays", "String originalChairpersonEid", "Integer chairpersonForceSwitched"],
        "PeakMonthRequest": ["String orgId", "int peakYear", "int peakMonth"],
        "ImperialAssignRequest": ["String agentEid", "String scopeJson", "String orgId", "String reason"],
        "ImperialRevokeRequest": ["String id", "String reason"],
        "ComplianceInquiryApplyRequest": ["String subjectEid", "String reason", "String purpose"],
    }
    for name, fields in dtos.items():
        write(f"dto/{name}.java", simple_class("dto", name, fields))
    write("dto/ComplaintTargetRequest.java", simple_class("dto", "ComplaintTargetRequest", ["String aliasName", "Integer sequence"]))
    write("dto/ComplianceInquiryHandleRequest.java", """
        package com.skills.pilot.oa.watchdog.full.dto;
        import com.skills.pilot.oa.watchdog.full.model.ComplianceInquiryAction;
        public final class ComplianceInquiryHandleRequest { public ComplianceInquiryAction action; public String comment; }
    """)


def generate_core_module() -> None:
    write("WatchdogFullModule.java", r'''
        package com.skills.pilot.oa.watchdog.full;

        import com.skills.pilot.oa.watchdog.full.api.*;
        import com.skills.pilot.oa.watchdog.full.dto.*;
        import com.skills.pilot.oa.watchdog.full.entity.*;
        import com.skills.pilot.oa.watchdog.full.model.*;
        import java.nio.charset.StandardCharsets;
        import java.security.MessageDigest;
        import java.time.*;
        import java.time.format.DateTimeFormatter;
        import java.util.*;
        import java.util.concurrent.atomic.AtomicInteger;
        import java.util.function.Predicate;
        import java.util.stream.Collectors;

        public final class WatchdogFullModule {
            public final Store store = new Store();
            public final EndpointCatalog endpoints = new EndpointCatalog();
            public final UserDirectory users = new UserDirectory();
            public final Workdays workdays = new Workdays();
            public final Idempotency idempotency = new Idempotency();
            public final Alerts alerts = new Alerts();
            public final Configs configs = new Configs();
            public final Complaints complaints = new Complaints();
            public final ReviewHolds reviewHolds = new ReviewHolds();
            public final Deadlocks deadlocks = new Deadlocks();
            public final Scans scans = new Scans();
            public final MetaDeadlock metaDeadlock = new MetaDeadlock();
            public final PeakMonths peakMonths = new PeakMonths();
            public final Imperial imperial = new Imperial();
            public final Compliance compliance = new Compliance();
            public final MonthlyReports monthlyReports = new MonthlyReports();
            public final Controllers controllers = new Controllers();

            public WatchdogFullModule seedDefaultUsers() {
                users.add("u-reporter", "E-REPORTER", "reporter", "Y-L3", "Reporter One");
                users.add("u-target", "E-TARGET", "target", "Y-L5B", "Target One");
                users.add("u-l6a", "E-L6-A", "l6a", "L6", "L6 Alpha");
                users.add("u-l6b", "E-L6-B", "l6b", "L6", "L6 Beta");
                users.add("u-l6c", "E-L6-C", "l6c", "L6", "L6 Gamma");
                users.add("u-zl5", "E-ZL5", "zl5", "Z-L5A1", "ZL5 Chair");
                users.add("u-zl4", "E-ZL4", "zl4", "Z-L4C1", "ZL4 Compliance");
                users.add("u-yl5b", "E-YL5B", "yl5b", "Y-L5B", "YL5B Chair");
                users.add("u-agent", "E-AGENT", "agent", "Y-L4", "Agent One");
                return this;
            }

            public static String sha256(String value) {
                try {
                    MessageDigest digest = MessageDigest.getInstance("SHA-256");
                    byte[] hashed = digest.digest((value == null ? "" : value).getBytes(StandardCharsets.UTF_8));
                    StringBuilder out = new StringBuilder();
                    for (byte b : hashed) out.append(String.format("%02x", b));
                    return out.toString();
                } catch (Exception ex) {
                    throw new IllegalStateException(ex);
                }
            }

            public final class Store {
                long seq = 1;
                public final List<Alert> alerts = new ArrayList<>();
                public final List<Complaint> complaints = new ArrayList<>();
                public final List<ComplaintTarget> complaintTargets = new ArrayList<>();
                public final List<DimConfig> configs = new ArrayList<>();
                public final List<DeadlockFingerprint> deadlocks = new ArrayList<>();
                public final List<ReviewHold> reviewHolds = new ArrayList<>();
                public final List<PeakMonth> peakMonths = new ArrayList<>();
                public final List<ImperialTakeover> imperialTakeovers = new ArrayList<>();
                public final List<ComplianceInquiryTicket> complianceTickets = new ArrayList<>();
                public final List<AuditEvent> auditEvents = new ArrayList<>();
                public final List<RedAlertPush> redAlertPushes = new ArrayList<>();
                synchronized long nextId() { return seq++; }
                void audit(RequestContext ctx, String event, String type, String target, String result) {
                    AuditEvent a = new AuditEvent();
                    a.eventType = event; a.targetType = type; a.targetId = target; a.operatorUid = ctx == null ? null : ctx.userId; a.result = result; a.at = ctx == null ? Instant.now() : ctx.now;
                    auditEvents.add(a);
                }
            }

            public final class UserDirectory {
                public final class User { public String userId, eid, alias, role, realName; }
                private final Map<String, User> byAlias = new HashMap<>();
                private final Map<String, User> byUserId = new HashMap<>();
                private final Map<String, User> byEid = new HashMap<>();
                public UserDirectory add(String userId, String eid, String alias, String role, String realName) {
                    User u = new User(); u.userId = userId; u.eid = eid; u.alias = alias; u.role = role; u.realName = realName;
                    byAlias.put(alias, u); byUserId.put(userId, u); byEid.put(eid, u); return this;
                }
                public User byAlias(String alias) { return byAlias.get(alias); }
                public String resolveEid(String idOrEid) { User u = byUserId.get(idOrEid); return u == null ? idOrEid : u.eid; }
                public String resolveUserId(String idOrEid) { User u = byUserId.get(idOrEid); if (u != null) return u.userId; u = byEid.get(idOrEid); return u == null ? null : u.userId; }
                public String realName(String eid) { User u = byEid.get(eid); return u == null ? null : u.realName; }
            }

            public final class Workdays {
                public Instant plus(Instant base, int workdays) {
                    LocalDate d = base.atZone(ZoneOffset.UTC).toLocalDate(); int added = 0;
                    while (added < workdays) { d = d.plusDays(1); DayOfWeek w = d.getDayOfWeek(); if (w != DayOfWeek.SATURDAY && w != DayOfWeek.SUNDAY) added++; }
                    return d.atTime(base.atZone(ZoneOffset.UTC).toLocalTime()).toInstant(ZoneOffset.UTC);
                }
                public int remaining(Instant from, Instant until) {
                    LocalDate c = from.atZone(ZoneOffset.UTC).toLocalDate(); LocalDate e = until.atZone(ZoneOffset.UTC).toLocalDate(); int n = 0;
                    while (c.isBefore(e)) { c = c.plusDays(1); DayOfWeek w = c.getDayOfWeek(); if (w != DayOfWeek.SATURDAY && w != DayOfWeek.SUNDAY) n++; }
                    return n;
                }
            }

            public final class Idempotency {
                private final Map<String, String> seen = new HashMap<>();
                public synchronized void remember(String key, String payloadHash) {
                    if (key == null || key.isBlank()) return;
                    String old = seen.get(key);
                    if (old != null && !old.equals(payloadHash)) throw ErrorCode.IDEMPOTENCY_CONFLICT.toException(key);
                    seen.put(key, payloadHash);
                }
            }

            public final class Alerts {
                public Alert create(DimCode dim, BlackswanSeverity severity, String orgId, String targetEid, String payload, int isL6, Instant now) {
                    Alert a = new Alert(); a.id = store.nextId(); a.alertUuid = UUID.randomUUID().toString(); a.dimCode = dim.getCode(); a.severity = severity.getCode();
                    a.orgId = orgId; a.targetEid = targetEid; a.problemSourceIsL6 = isL6; a.payloadJson = payload; a.payloadHash = sha256(payload); a.status = BlackswanAlertStatus.TRIGGERED.getCode(); a.createTime = now;
                    store.alerts.add(a);
                    if (severity == BlackswanSeverity.RED) { RedAlertPush p = new RedAlertPush(); p.alertUuid = a.alertUuid; p.status = "QUEUED"; p.at = now; store.redAlertPushes.add(p); }
                    return a;
                }
                public List<Alert> list(AlertPageQuery q) { return store.alerts.stream().filter(a -> match(q.dimCode, a.dimCode) && match(q.severity, a.severity) && match(q.status, a.status) && match(q.orgId, a.orgId)).collect(Collectors.toList()); }
                public Alert get(String uuid) { return store.alerts.stream().filter(a -> uuid.equals(a.alertUuid)).findFirst().orElseThrow(() -> ErrorCode.ALERT_NOT_FOUND.toException(uuid)); }
                public Alert ack(RequestContext ctx, String uuid, AckRequest req) {
                    Alert a = get(uuid);
                    if (BlackswanAlertStatus.CLOSED.getCode().equals(a.status)) throw ErrorCode.BLACKSWAN_ALERT_CLOSED.toException(uuid);
                    if (BlackswanAlertStatus.ACKED.getCode().equals(a.status) || BlackswanAlertStatus.IN_HANDLING.getCode().equals(a.status)) throw ErrorCode.ALERT_ALREADY_ACKED.toException(uuid);
                    a.status = BlackswanAlertStatus.ACKED.getCode(); a.ackUserId = ctx.userId; a.ackTime = ctx.now; store.audit(ctx, "BLACKSWAN_ALERT_ACK", "OA_BLACKSWAN_ALERT", uuid, "OK"); return a;
                }
                public Alert close(RequestContext ctx, String uuid, CloseRequest req) {
                    Alert a = get(uuid); if (BlackswanAlertStatus.CLOSED.getCode().equals(a.status)) throw ErrorCode.BLACKSWAN_ALERT_CLOSED.toException(uuid);
                    a.status = BlackswanAlertStatus.CLOSED.getCode(); a.closedUserId = ctx.userId; a.closedTime = ctx.now; a.resolution = req.resolution; store.audit(ctx, "BLACKSWAN_ALERT_CLOSE", "OA_BLACKSWAN_ALERT", uuid, "OK"); return a;
                }
                public Map<String,Object> dashboard(Instant now) {
                    Map<String,Object> m = new LinkedHashMap<>(); long active = store.alerts.stream().filter(a -> !BlackswanAlertStatus.CLOSED.getCode().equals(a.status)).count();
                    m.put("totalAlertsThisMonth", (long) store.alerts.size()); m.put("activeAlerts", active);
                    m.put("redCount", countOpen(BlackswanSeverity.RED)); m.put("orangeCount", countOpen(BlackswanSeverity.ORANGE)); m.put("yellowCount", countOpen(BlackswanSeverity.YELLOW));
                    m.put("resolveRate", store.alerts.isEmpty() ? 0.0 : (store.alerts.size() - active) * 1.0 / store.alerts.size());
                    m.put("ackRate", store.alerts.isEmpty() ? 0.0 : store.alerts.stream().filter(a -> a.ackTime != null).count() * 1.0 / store.alerts.size());
                    m.put("byDim", store.alerts.stream().collect(Collectors.groupingBy(a -> a.dimCode, Collectors.counting())));
                    m.put("overdueCount", store.alerts.stream().filter(a -> !BlackswanAlertStatus.CLOSED.getCode().equals(a.status) && a.createTime != null && a.createTime.plusSeconds(sla(a.severity) * 3600L).isBefore(now)).count());
                    return m;
                }
                private long countOpen(BlackswanSeverity s) { return store.alerts.stream().filter(a -> s.getCode().equals(a.severity) && !BlackswanAlertStatus.CLOSED.getCode().equals(a.status)).count(); }
                private int sla(String s) { return "RED".equals(s) ? 24 : "ORANGE".equals(s) ? 48 : "YELLOW".equals(s) ? 72 : 0; }
                private boolean match(String expected, String actual) { return expected == null || expected.isBlank() || expected.equals(actual); }
            }

            public final class Configs {
                public List<DimConfig> list(String dimCode) { return store.configs.stream().filter(c -> dimCode == null || dimCode.isBlank() || dimCode.equals(c.dimCode)).collect(Collectors.toList()); }
                public DimConfig save(RequestContext ctx, ConfigSaveRequest r) {
                    if (DimCode.of(r.dimCode) == null) throw ErrorCode.BLACKSWAN_DIM_NOT_FOUND.toException(r.dimCode);
                    if (r.pendingValue == null || r.pendingValue.isBlank()) throw ErrorCode.BLACKSWAN_DIM_PARAM_INVALID.toException(r.paramKey, "<empty>");
                    DimConfig c = find(r.dimCode, r.paramKey); if (c == null) { c = new DimConfig(); c.id = store.nextId(); c.dimCode = r.dimCode; c.paramKey = r.paramKey; store.configs.add(c); }
                    c.lastUpdatedBy = ctx.userId; c.changeReason = r.changeReason;
                    if ("L6".equals(ctx.roleCode)) { c.paramValue = r.pendingValue; c.pendingValue = null; c.lastApprovedBy = ctx.userId; c.lastApprovedAt = ctx.now; } else { c.pendingValue = r.pendingValue; }
                    store.audit(ctx, "BLACKSWAN_CONFIG_PROPOSE", "OA_BLACKSWAN_DIM_CONFIG", r.dimCode + ":" + r.paramKey, "OK"); return c;
                }
                public DimConfig approve(RequestContext ctx, ConfigApproveRequest r) {
                    DimConfig c = find(r.dimCode, r.paramKey); if (c == null) throw ErrorCode.BLACKSWAN_DIM_PARAM_MISSING.toException(r.dimCode, r.paramKey);
                    if (c.pendingValue == null || c.pendingValue.isBlank()) throw ErrorCode.BLACKSWAN_CONFIG_NEED_APPROVAL.toException();
                    c.paramValue = c.pendingValue; c.pendingValue = null; c.lastApprovedBy = ctx.userId; c.lastApprovedAt = ctx.now; store.audit(ctx, "BLACKSWAN_CONFIG_APPROVE", "OA_BLACKSWAN_DIM_CONFIG", r.dimCode + ":" + r.paramKey, "OK"); return c;
                }
                public String value(String dim, String key) { DimConfig c = find(dim, key); return c == null ? null : c.paramValue; }
                private DimConfig find(String dim, String key) { return store.configs.stream().filter(c -> dim.equals(c.dimCode) && key.equals(c.paramKey)).findFirst().orElse(null); }
            }

            public final class Complaints {
                public Complaint submit(RequestContext ctx, ComplaintSubmitRequest r) {
                    if (ctx.userId == null || ctx.userId.isBlank()) throw ErrorCode.UNAUTHORIZED.toException();
                    if (r.contentText == null || r.contentText.length() < 10 || r.contentText.length() > 5000) throw ErrorCode.COMMON_VALIDATION_ERROR.toException("contentText");
                    List<ComplaintTargetRequest> targets = r.targets == null || r.targets.isEmpty() ? Collections.singletonList(target(r.targetAliasName, 1)) : r.targets;
                    List<UserDirectory.User> resolved = new ArrayList<>(); for (ComplaintTargetRequest tr : targets) { UserDirectory.User u = users.byAlias(tr.aliasName); if (u == null) throw ErrorCode.COMPLAINT_TARGET_NOT_FOUND.toException(tr.aliasName); resolved.add(u); }
                    UserDirectory.User primary = resolved.get(0); String hash = sha256(ctx.userId); long recent = countRecent(hash, ctx.now.minusSeconds(30L * 24L * 3600L));
                    Complaint c = new Complaint(); c.id = store.nextId(); c.complaintUuid = UUID.randomUUID().toString(); c.reporterEidHash = hash; c.targetEid = primary.eid; c.targetRoleCode = primary.role; c.contentRefId = null; c.contentText = r.contentText; c.targetAliasName = primary.alias; c.isAnonymousTemplate = r.isAnonymousTemplate == null ? 0 : r.isAnonymousTemplate; c.hasConcreteFacts = r.hasConcreteFacts == null ? 1 : r.hasConcreteFacts; c.screeningResult = recent >= 3 ? ComplaintScreeningResult.QUALITY_REVIEW.getCode() : ComplaintScreeningResult.PENDING.getCode(); c.reporterRecentCount30d = (int) recent + 1; c.createTime = ctx.now;
                    if (resolved.stream().allMatch(u -> "L6".equals(u.role)) && distinctOpenL6With(resolved) >= 3) { c.status = ComplaintStatus.EXTERNAL_COMMITTEE_TAKEOVER.getCode(); c.externalTakeoverAt = ctx.now; }
                    else if ("L6".equals(primary.role)) c.status = ComplaintStatus.PENDING_DUAL_L6_SIGN.getCode(); else c.status = ComplaintStatus.SUBMITTED.getCode();
                    store.complaints.add(c);
                    for (int i = 0; i < resolved.size(); i++) { UserDirectory.User u = resolved.get(i); ComplaintTarget ct = new ComplaintTarget(); ct.id = store.nextId(); ct.complaintId = c.id; ct.targetEid = u.eid; ct.targetRoleCode = u.role; ct.targetAliasName = u.alias; ct.sequence = targets.get(i).sequence == null ? i + 1 : targets.get(i).sequence; store.complaintTargets.add(ct); }
                    store.audit(ctx, "WATCHDOG_COMPLAINT_SUBMITTED", "OA_BLACKSWAN_COMPLAINT", c.complaintUuid, "OK"); return c;
                }
                public List<Complaint> list(String status) { return store.complaints.stream().filter(c -> status == null || status.isBlank() || status.equals(c.status)).collect(Collectors.toList()); }
                public Complaint detail(String uuid) { return store.complaints.stream().filter(c -> uuid.equals(c.complaintUuid)).findFirst().orElseThrow(() -> ErrorCode.COMPLAINT_TICKET_NOT_FOUND.toException(uuid)); }
                public Complaint screen(RequestContext ctx, String uuid, ComplaintScreenRequest r) {
                    if (!"Z-L5A1".equals(ctx.roleCode)) throw ErrorCode.COMPLAINT_SCREEN_ROLE_DENIED.toException();
                    Complaint c = detail(uuid); if (!ComplaintStatus.SUBMITTED.getCode().equals(c.status)) throw ErrorCode.COMPLAINT_SCREEN_STATUS_INVALID.toException(c.status);
                    boolean pass = Integer.valueOf(1).equals(r.hasConcreteFacts) && Integer.valueOf(0).equals(r.isAnonymousTemplate); c.chairpersonEid = ctx.eid; c.hasConcreteFacts = r.hasConcreteFacts == null ? 0 : r.hasConcreteFacts; c.isAnonymousTemplate = r.isAnonymousTemplate == null ? 0 : r.isAnonymousTemplate;
                    if (!pass) { c.screeningResult = ComplaintScreeningResult.FAILED.getCode(); c.status = ComplaintStatus.SCREENING_FAILED.getCode(); c.closedAt = ctx.now; store.audit(ctx, "WATCHDOG_COMPLAINT_SCREENED", "OA_BLACKSWAN_COMPLAINT", uuid, "FAILED"); throw ErrorCode.COMPLAINT_SCREENING_FAILED.toException(); }
                    c.screeningResult = ComplaintScreeningResult.PASSED.getCode(); c.status = ComplaintStatus.FILED.getCode(); c.filedAt = ctx.now; c.reviewDeadline = workdays.plus(ctx.now, 30);
                    ReviewHold h = new ReviewHold(); h.id = store.nextId(); h.targetEid = c.targetEid; h.complaintUuid = c.complaintUuid; h.holdStart = ctx.now; h.holdUntil = workdays.plus(ctx.now, 30); h.blockedActions = "PAYROLL_ADJUST,TRANSFER,TERMINATION,PERF_DOWN,DEMOTE"; h.status = "ACTIVE";
                    if (ctx.roleStartsWith("Y-L5B") && c.targetRoleCode != null && c.targetRoleCode.startsWith("Y-L5B")) { h.originalChairpersonEid = ctx.eid; h.chairpersonForceSwitched = 1; c.chairReassigned = 1; }
                    store.reviewHolds.add(h); store.audit(ctx, "WATCHDOG_COMPLAINT_SCREENED", "OA_BLACKSWAN_COMPLAINT", uuid, "PASSED"); return c;
                }
                public Complaint firstSign(RequestContext ctx, String uuid, DualSignRequest r) {
                    Complaint c = detail(uuid); if (!ComplaintStatus.PENDING_DUAL_L6_SIGN.getCode().equals(c.status)) throw ErrorCode.COMPLAINT_NOT_DUAL_SIGN_STATUS.toException(c.status);
                    assertL6(ctx); assertNotSelf(ctx, c.targetEid); c.l6FirstSignUserId = ctx.userId; c.l6FirstSignAt = ctx.now; c.status = ComplaintStatus.L6_SIGNED_FIRST.getCode(); store.audit(ctx, "WATCHDOG_COMPLAINT_DUAL_L6_FIRST_SIGN", "OA_BLACKSWAN_COMPLAINT", uuid, "OK"); return c;
                }
                public Complaint secondSign(RequestContext ctx, String uuid, DualSignRequest r) {
                    Complaint c = detail(uuid); if (!ComplaintStatus.L6_SIGNED_FIRST.getCode().equals(c.status)) throw ErrorCode.COMPLAINT_NOT_DUAL_SIGN_STATUS.toException(c.status);
                    if (c.l6FirstSignAt != null && c.l6FirstSignAt.plusSeconds(72L * 3600L).isBefore(ctx.now)) { c.status = ComplaintStatus.EXTERNAL_COMMITTEE_TAKEOVER.getCode(); c.externalTakeoverAt = ctx.now; throw ErrorCode.COMPLAINT_DUAL_SIGN_TIMEOUT.toException(); }
                    assertL6(ctx); assertNotSelf(ctx, c.targetEid); if (ctx.userId.equals(c.l6FirstSignUserId)) throw ErrorCode.COMPLAINT_SAME_L6_DUAL_SIGN_FORBIDDEN.toException();
                    c.l6SecondSignUserId = ctx.userId; c.l6SecondSignAt = ctx.now; c.closedAt = ctx.now; c.status = Boolean.TRUE.equals(r.accept) ? ComplaintStatus.L6_DUAL_SIGNED.getCode() : ComplaintStatus.CLOSED_REJECTED.getCode(); store.audit(ctx, "WATCHDOG_COMPLAINT_DUAL_L6_SECOND_SIGN", "OA_BLACKSWAN_COMPLAINT", uuid, c.status); return c;
                }
                private ComplaintTargetRequest target(String alias, int seq) { ComplaintTargetRequest t = new ComplaintTargetRequest(); t.aliasName = alias; t.sequence = seq; return t; }
                private long countRecent(String hash, Instant cutoff) { return store.complaints.stream().filter(c -> hash.equals(c.reporterEidHash) && c.createTime != null && c.createTime.isAfter(cutoff)).count(); }
                private long distinctOpenL6With(List<UserDirectory.User> incoming) { Set<String> s = store.complaints.stream().filter(c -> "L6".equals(c.targetRoleCode) && !"CLOSED".equals(c.status) && !"SCREENING_FAILED".equals(c.status)).map(c -> c.targetEid).collect(Collectors.toSet()); incoming.stream().filter(u -> "L6".equals(u.role)).forEach(u -> s.add(u.eid)); return s.size(); }
                private void assertL6(RequestContext ctx) { if (!"L6".equals(ctx.roleCode)) throw ErrorCode.COMPLAINT_DUAL_SIGN_NOT_L6.toException(); }
                private void assertNotSelf(RequestContext ctx, String targetEid) { if (targetEid != null && targetEid.equalsIgnoreCase(ctx.eid)) throw ErrorCode.COMPLAINT_L6_SELF_SIGN_FORBIDDEN.toException(); }
            }

            public final class ReviewHolds {
                public ReviewHold create(RequestContext ctx, ReviewHoldCreateRequest r) {
                    if (r.targetEid == null || r.targetEid.isBlank()) throw ErrorCode.BLACKSWAN_DIM_PARAM_INVALID.toException("targetEid", "<empty>");
                    if (store.reviewHolds.stream().anyMatch(h -> r.targetEid.equals(h.targetEid) && "ACTIVE".equals(h.status))) throw ErrorCode.REVIEW_HOLD_ACTION_CONFLICT.toException("CREATE");
                    int days = r.holdWorkdays != null && r.holdWorkdays > 0 ? r.holdWorkdays : intParam("D9", "REVIEW_HOLD_WORKDAYS", 30);
                    ReviewHold h = new ReviewHold(); h.id = store.nextId(); h.targetEid = r.targetEid; h.complaintUuid = r.complaintUuid; h.holdStart = ctx.now; h.holdUntil = workdays.plus(ctx.now, days); h.blockedActions = r.blockedActions == null || r.blockedActions.isBlank() ? "PAYROLL_ADJUST,TRANSFER,TERMINATION,PERF_DOWN,DEMOTE" : r.blockedActions; h.status = "ACTIVE"; h.originalChairpersonEid = r.originalChairpersonEid; h.chairpersonForceSwitched = r.chairpersonForceSwitched == null ? 0 : r.chairpersonForceSwitched; store.reviewHolds.add(h); store.audit(ctx, "BLACKSWAN_REVIEW_HOLD_CREATE", "OA_BLACKSWAN_REVIEW_HOLD", String.valueOf(h.id), "OK"); return h;
                }
                public ReviewHold release(RequestContext ctx, long id) { ReviewHold h = store.reviewHolds.stream().filter(x -> x.id == id && "ACTIVE".equals(x.status)).findFirst().orElseThrow(() -> ErrorCode.REVIEW_HOLD_NOT_FOUND.toException(id)); h.status = "RELEASED"; h.releasedAt = ctx.now; h.releasedBy = ctx.userId; store.audit(ctx, "BLACKSWAN_REVIEW_HOLD_RELEASE", "OA_BLACKSWAN_REVIEW_HOLD", String.valueOf(id), "OK"); return h; }
                public List<ReviewHold> list(String status, String target) { return store.reviewHolds.stream().filter(h -> (status == null || status.isBlank() || status.equals(h.status)) && (target == null || target.isBlank() || target.equals(h.targetEid))).collect(Collectors.toList()); }
                public int autoRelease(Instant now) { int n = 0; for (ReviewHold h : store.reviewHolds) if ("ACTIVE".equals(h.status) && h.holdUntil != null && !h.holdUntil.isAfter(now)) { h.status = "AUTO_RELEASED"; h.releasedAt = now; h.releasedBy = "system"; n++; } return n; }
                public void assertWriteAllowed(String targetEidOrUserId, ReviewHoldAction action, Instant now) {
                    String eid = users.resolveEid(targetEidOrUserId);
                    Optional<ReviewHold> hold = store.reviewHolds.stream().filter(h -> eid.equals(h.targetEid) && "ACTIVE".equals(h.status) && h.holdUntil != null && h.holdUntil.isAfter(now)).findFirst();
                    if (hold.isPresent() && contains(hold.get().blockedActions, action.getCode())) throw ErrorCode.WHISTLEBLOWER_PROTECTION_HOLD.toException(eid, workdays.remaining(now, hold.get().holdUntil), action.getCode());
                    if (action.getWhistleblowerCode() != null && protectedReporter(targetEidOrUserId, now)) throw ErrorCode.WHISTLEBLOWER_RETALIATION_BLOCKED.toException();
                }
                private boolean protectedReporter(String idOrEid, Instant now) { String uid = users.resolveUserId(idOrEid); if (uid == null) return false; String hash = sha256(uid); Instant cut = now.minusSeconds(180L * 24L * 3600L); return store.complaints.stream().anyMatch(c -> hash.equals(c.reporterEidHash) && c.createTime != null && c.createTime.isAfter(cut) && !ComplaintScreeningResult.MALICIOUS.getCode().equals(c.screeningResult)); }
                private boolean contains(String csv, String code) { return csv != null && Arrays.stream(csv.split(",")).map(String::trim).anyMatch(code::equals); }
            }

            public final class Deadlocks {
                public DeadlockFingerprint report(RequestContext ctx, DeadlockReportRequest r) {
                    if (r.topicHash == null || r.topicHash.isBlank()) throw ErrorCode.BLACKSWAN_DIM_PARAM_INVALID.toException("topicHash", "blank");
                    DeadlockFingerprint fp = store.deadlocks.stream().filter(d -> r.topicHash.equals(d.topicHash)).findFirst().orElse(null);
                    if (fp == null) { fp = new DeadlockFingerprint(); fp.id = store.nextId(); fp.topicHash = r.topicHash; fp.nodeSet = normalize(r.nodeSet); fp.cumulativeCount = 1; fp.lastTriggeredAt = ctx.now; store.deadlocks.add(fp); }
                    else { fp.cumulativeCount++; fp.lastTriggeredAt = ctx.now; }
                    int threshold = intParam("D8", "DEADLOCK_THRESHOLD", 5);
                    if (fp.cumulativeCount >= threshold && (fp.triggeredAlertUuid == null || fp.triggeredAlertUuid.isBlank())) { Alert a = alerts.create(DimCode.D8, BlackswanSeverity.RED, null, null, "{\"topicHash\":\"" + fp.topicHash + "\",\"cumulativeCount\":" + fp.cumulativeCount + "}", 0, ctx.now); fp.triggeredAlertUuid = a.alertUuid; }
                    store.audit(ctx, "DEADLOCK_FINGERPRINT_COUNTED", "OA_BLACKSWAN_DEADLOCK_FP", fp.topicHash, "OK"); return fp;
                }
                public List<DeadlockFingerprint> page(String topicHash, Integer min) { return store.deadlocks.stream().filter(d -> (topicHash == null || topicHash.isBlank() || topicHash.equals(d.topicHash)) && (min == null || d.cumulativeCount >= min)).collect(Collectors.toList()); }
                public List<String> normalize(List<String> raw) { LinkedHashSet<String> set = new LinkedHashSet<>(); if (raw != null) for (String n : raw) { if (n == null || n.isBlank()) continue; String t = n.trim(); set.add(t.equals("L6_A") || t.equals("L6_B") || t.equals("L6_C") ? "L6" : t); } return new ArrayList<>(set); }
            }

            public final class Scans {
                public Map<String,Integer> all(RequestContext ctx) { Map<String,Integer> m = new LinkedHashMap<>(); m.put("D6", d6(ctx)); m.put("D7", d7(ctx)); m.put("D8", d8(ctx)); m.put("D9", d9(ctx)); return m; }
                public int d6(RequestContext ctx) { long distinct = store.complaints.stream().filter(c -> "L6".equals(c.targetRoleCode) && !"CLOSED".equals(c.status) && !"SCREENING_FAILED".equals(c.status)).map(c -> c.targetEid).distinct().count(); if (distinct < 3 || existsToday(DimCode.D6, null, ctx.now)) return 0; Alert a = alerts.create(DimCode.D6, BlackswanSeverity.RED, null, null, "{\"distinctL6\":" + distinct + "}", 1, ctx.now); a.status = BlackswanAlertStatus.ESCALATED_L6.getCode(); a.escalatedL6Time = ctx.now; return 1; }
                public int d7(RequestContext ctx) { int th = intParam("D7", "COMPLAINT_30D_THRESHOLD", 3); Instant cut = ctx.now.minusSeconds(30L * 24L * 3600L); Map<String,Long> by = store.complaints.stream().filter(c -> c.filedAt != null && c.filedAt.isAfter(cut)).collect(Collectors.groupingBy(c -> c.reporterEidHash, Collectors.counting())); int n = 0; for (Map.Entry<String,Long> e : by.entrySet()) if (e.getValue() >= th) { String p = e.getKey().substring(0, Math.min(10, e.getKey().length())); if (!existsToday(DimCode.D7, p, ctx.now)) { alerts.create(DimCode.D7, BlackswanSeverity.ORANGE, null, p, "{\"reporterHashPrefix\":\"" + p + "\"}", 0, ctx.now); n++; } } return n; }
                public int d8(RequestContext ctx) { int th = intParam("D8", "DEADLOCK_THRESHOLD", 5); int n = 0; for (DeadlockFingerprint fp : store.deadlocks) if (fp.cumulativeCount >= th && (fp.triggeredAlertUuid == null || fp.triggeredAlertUuid.isBlank())) { Alert a = alerts.create(DimCode.D8, BlackswanSeverity.RED, null, null, "{\"topicHash\":\"" + fp.topicHash + "\"}", 0, ctx.now); fp.triggeredAlertUuid = a.alertUuid; n++; } return n; }
                public int d9(RequestContext ctx) { int days = intParam("D9", "REVIEW_HOLD_WORKDAYS", 30); int n = 0; for (ReviewHold h : store.reviewHolds) if ("ACTIVE".equals(h.status) && h.holdUntil != null && h.holdUntil.isBefore(ctx.now) && !existsToday(DimCode.D9, h.targetEid, ctx.now)) { Alert a = alerts.create(DimCode.D9, BlackswanSeverity.RED, null, h.targetEid, "{\"targetEid\":\"" + h.targetEid + "\",\"workdays\":" + days + "}", 0, ctx.now); a.status = BlackswanAlertStatus.ESCALATED_L6.getCode(); a.escalatedL6Time = ctx.now; n++; } return n; }
                private boolean existsToday(DimCode dim, String target, Instant now) { Instant start = now.atZone(ZoneOffset.UTC).toLocalDate().atStartOfDay().toInstant(ZoneOffset.UTC); return store.alerts.stream().anyMatch(a -> dim.getCode().equals(a.dimCode) && (target == null || target.equals(a.targetEid)) && a.createTime != null && !a.createTime.isBefore(start)); }
            }

            public final class MetaDeadlock {
                public void check(RequestContext ctx, String targetEid, String method) { if (ctx == null || targetEid == null || !ctx.roleStartsWith("Y-L5B")) return; boolean locked = store.reviewHolds.stream().anyMatch(h -> targetEid.equals(h.targetEid) && "ACTIVE".equals(h.status) && h.chairpersonForceSwitched == 1); if (locked) { store.audit(ctx, "WATCHDOG_CHAIR_CONFLICT", "OA_BLACKSWAN_REVIEW_HOLD", targetEid, method); throw ErrorCode.WATCHDOG_CHAIR_CONFLICT.toException(); } }
            }

            public final class PeakMonths {
                public PeakMonth declare(RequestContext ctx, PeakMonthRequest r) { PeakMonth old = store.peakMonths.stream().filter(p -> r.orgId.equals(p.orgId) && p.peakYear == r.peakYear && p.peakMonth == r.peakMonth).findFirst().orElse(null); if (old != null) return old; PeakMonth p = new PeakMonth(); p.id = store.nextId(); p.orgId = r.orgId; p.peakYear = r.peakYear; p.peakMonth = r.peakMonth; p.declaredBy = ctx.userId; p.declaredAt = ctx.now; store.peakMonths.add(p); return p; }
                public List<PeakMonth> list(String orgId) { return store.peakMonths.stream().filter(p -> orgId == null || orgId.isBlank() || orgId.equals(p.orgId)).collect(Collectors.toList()); }
            }

            public final class Imperial {
                private final AtomicInteger seq = new AtomicInteger(0); private String day = "";
                public ImperialTakeover assign(RequestContext ctx, ImperialAssignRequest r) { requireL6(ctx); if (blank(r.agentEid) || blank(r.orgId) || blank(r.scopeJson) || blank(r.reason)) throw ErrorCode.COMMON_VALIDATION_ERROR.toException("imperial"); ImperialTakeover i = new ImperialTakeover(); i.id = store.nextId(); i.ticketNo = ticket(ctx); i.agentEid = r.agentEid; i.scopeJson = r.scopeJson; i.status = ImperialTakeoverStatus.ACTIVE.getCode(); i.orgId = r.orgId; i.reason = r.reason; i.createdBy = ctx.eid; i.approvedAt = ctx.now; i.createTime = ctx.now; store.imperialTakeovers.add(i); store.audit(ctx, "IMPERIAL_TAKEOVER_ASSIGN", "OA_IMPERIAL_TAKEOVER", String.valueOf(i.id), "OK"); return i; }
                public ImperialTakeover revoke(RequestContext ctx, ImperialRevokeRequest r) { requireL6(ctx); long id = Long.parseLong(r.id); ImperialTakeover i = store.imperialTakeovers.stream().filter(x -> x.id == id).findFirst().orElseThrow(() -> ErrorCode.IMPERIAL_TAKEOVER_NOT_FOUND.toException(r.id)); if (!ImperialTakeoverStatus.ACTIVE.getCode().equals(i.status)) throw ErrorCode.IMPERIAL_TAKEOVER_ALREADY_REVOKED.toException(i.status); i.status = ImperialTakeoverStatus.REVOKED.getCode(); i.revokedAt = ctx.now; i.revokeReason = r.reason; store.audit(ctx, "IMPERIAL_TAKEOVER_REVOKE", "OA_IMPERIAL_TAKEOVER", String.valueOf(i.id), "OK"); return i; }
                public List<ImperialTakeover> page(String org, String status) { return store.imperialTakeovers.stream().filter(i -> (blank(org) || org.equals(i.orgId)) && (blank(status) || status.equals(i.status))).collect(Collectors.toList()); }
                public ImperialTakeover activeByOrg(String org) { return store.imperialTakeovers.stream().filter(i -> org.equals(i.orgId) && ImperialTakeoverStatus.ACTIVE.getCode().equals(i.status)).findFirst().orElse(null); }
                private void requireL6(RequestContext ctx) { if (ctx == null || !"L6".equals(ctx.roleCode)) throw ErrorCode.IMPERIAL_TAKEOVER_L6_ONLY.toException(); }
                private synchronized String ticket(RequestContext ctx) { String d = DateTimeFormatter.ofPattern("yyyyMMdd").withZone(ZoneOffset.UTC).format(ctx.now); if (!d.equals(day)) { day = d; seq.set(0); } return "IMP-" + d + "-" + String.format("%04d", seq.incrementAndGet()); }
            }

            public final class Compliance {
                private final AtomicInteger seq = new AtomicInteger(0);
                public ComplianceInquiryTicket apply(RequestContext ctx, ComplianceInquiryApplyRequest r) { require(ctx); ComplianceInquiryTicket t = new ComplianceInquiryTicket(); t.id = store.nextId(); t.ticketNo = "CI-" + DateTimeFormatter.ofPattern("yyyyMMdd").withZone(ZoneOffset.UTC).format(ctx.now) + "-" + String.format("%04d", seq.incrementAndGet()); t.type = "COMPLIANCE_INQUIRY"; t.status = TicketStatus.PENDING.getCode(); t.subjectEid = r.subjectEid; t.fieldsCsv = "REAL_NAME"; t.reason = r.reason; t.purpose = r.purpose; t.applicantId = ctx.userId; t.applicantRole = ctx.roleCode; t.currentApproverId = "Z-L4C1"; t.createTime = ctx.now; store.complianceTickets.add(t); store.audit(ctx, "COMPLIANCE_INQUIRY_SUBMITTED", "OA_TICKET", String.valueOf(t.id), "OK"); return t; }
                public ComplianceInquiryTicket handle(RequestContext ctx, long id, ComplianceInquiryHandleRequest r) { require(ctx); ComplianceInquiryTicket t = store.complianceTickets.stream().filter(x -> x.id == id && "COMPLIANCE_INQUIRY".equals(x.type)).findFirst().orElseThrow(() -> ErrorCode.COMPLIANCE_INQUIRY_TICKET_REQUIRED.toException()); if (!TicketStatus.PENDING.getCode().equals(t.status)) throw ErrorCode.TICKET_STATUS_NOT_APPROVABLE.toException(t.status); if (r.action == ComplianceInquiryAction.COMPLETE) { t.status = TicketStatus.COMPLETED.getCode(); t.completedAt = ctx.now; } else t.status = TicketStatus.REJECTED.getCode(); t.handlerId = ctx.userId; t.comment = r.comment; store.audit(ctx, "COMPLIANCE_INQUIRY_HANDLED", "OA_TICKET", String.valueOf(t.id), t.status); return t; }
                public String realName(RequestContext ctx, String subjectEid) { if (!hasTicket(subjectEid, ctx.userId, ctx.now)) throw ErrorCode.COMPLIANCE_INQUIRY_TICKET_REQUIRED.toException(); String name = users.realName(subjectEid); if (name == null) throw ErrorCode.COMPLIANCE_INQUIRY_TICKET_REQUIRED.toException(); store.audit(ctx, "COMPLIANCE_INQUIRY_VIEWED", "OA_COMPLIANCE_IDENTITY", subjectEid, "OK"); return name; }
                public List<ComplianceInquiryTicket> pending() { return store.complianceTickets.stream().filter(t -> "COMPLIANCE_INQUIRY".equals(t.type) && TicketStatus.PENDING.getCode().equals(t.status)).collect(Collectors.toList()); }
                private void require(RequestContext ctx) { if (!"Z-L4C1".equals(ctx.roleCode) && !"L6".equals(ctx.roleCode)) throw ErrorCode.COMPLIANCE_INQUIRY_FORBIDDEN.toException(); }
                private boolean hasTicket(String subject, String user, Instant now) { return store.complianceTickets.stream().anyMatch(t -> subject.equals(t.subjectEid) && user.equals(t.applicantId) && TicketStatus.COMPLETED.getCode().equals(t.status) && t.completedAt != null && t.completedAt.plusSeconds(24L * 3600L).isAfter(now)); }
            }

            public final class MonthlyReports {
                public final class ReportEntry { public final String id, content; public ReportEntry(String id, String content) { this.id = id; this.content = content; } }
                public String build(List<ReportEntry> entries) { String prev = "HEAD"; StringBuilder out = new StringBuilder("head_anchor=HEAD\n"); for (ReportEntry e : entries) { String cur = sha256(prev + ":" + e.id + ":" + e.content); out.append(e.id).append('|').append(prev).append('|').append(cur).append('|').append(e.content).append('\n'); prev = cur; } out.append("tail_anchor=").append(prev).append('\n'); return out.toString(); }
                public List<ReportEntry> verify(String report) { String[] lines = report.split("\\R"); if (lines.length < 2 || !lines[0].equals("head_anchor=HEAD")) throw ErrorCode.MONTHLY_REPORT_TAIL_TRUNCATED.toException("head"); List<ReportEntry> out = new ArrayList<>(); String prev = "HEAD"; String tail = null; for (int i = 1; i < lines.length; i++) { String line = lines[i]; if (line.startsWith("tail_anchor=")) { tail = line.substring("tail_anchor=".length()); break; } String[] p = line.split("\\|", 4); if (p.length != 4 || !prev.equals(p[1])) throw ErrorCode.MONTHLY_REPORT_TAIL_TRUNCATED.toException("chain"); String cur = sha256(prev + ":" + p[0] + ":" + p[3]); if (!cur.equals(p[2])) throw ErrorCode.MONTHLY_REPORT_TAIL_TRUNCATED.toException("hash"); out.add(new ReportEntry(p[0], p[3])); prev = cur; } if (tail == null || !tail.equals(prev)) throw ErrorCode.MONTHLY_REPORT_TAIL_TRUNCATED.toException("tail"); return out; }
            }

            public final class Controllers {
                public final OaBlackswanController blackswan = new OaBlackswanController();
                public final OaBlackswanComplaintController complaint = new OaBlackswanComplaintController();
                public final OaBlackswanConfigController config = new OaBlackswanConfigController();
                public final OaBlackswanInternalController internal = new OaBlackswanInternalController();
                public final OaBlackswanDeadlockController deadlock = new OaBlackswanDeadlockController();
                public final OaBlackswanReviewHoldController reviewHold = new OaBlackswanReviewHoldController();
                public final OaBlackswanPeakMonthController peakMonth = new OaBlackswanPeakMonthController();
                public final OaImperialTakeoverController imperialController = new OaImperialTakeoverController();
                public final ComplianceInquiryController complianceController = new ComplianceInquiryController();
            }

            public final class OaBlackswanController { public Map<String,Object> dashboard(RequestContext c) { return alerts.dashboard(c.now); } public List<Alert> alerts(AlertPageQuery q) { return alerts.list(q); } public Alert alert(String id) { return alerts.get(id); } public Alert ack(RequestContext c, String id, AckRequest r) { return alerts.ack(c, id, r); } public Alert close(RequestContext c, String id, CloseRequest r) { return alerts.close(c, id, r); } }
            public final class OaBlackswanComplaintController { public Complaint submit(RequestContext c, ComplaintSubmitRequest r) { return complaints.submit(c, r); } public List<Complaint> list(String s) { return complaints.list(s); } public Complaint detail(String id) { return complaints.detail(id); } public Complaint screen(RequestContext c, String id, ComplaintScreenRequest r) { return complaints.screen(c, id, r); } public Complaint dualL6FirstSign(RequestContext c, String id, DualSignRequest r) { return complaints.firstSign(c, id, r); } public Complaint dualL6SecondSign(RequestContext c, String id, DualSignRequest r) { return complaints.secondSign(c, id, r); } }
            public final class OaBlackswanConfigController { public List<DimConfig> list(String d) { return configs.list(d); } public DimConfig save(RequestContext c, ConfigSaveRequest r) { return configs.save(c, r); } public DimConfig approve(RequestContext c, ConfigApproveRequest r) { return configs.approve(c, r); } }
            public final class OaBlackswanInternalController { public Map<String,Integer> scan(RequestContext c) { return scans.all(c); } public DeadlockFingerprint deadlockFingerprint(RequestContext c, DeadlockReportRequest r) { return deadlocks.report(c, r); } }
            public final class OaBlackswanDeadlockController { public List<DeadlockFingerprint> page(String h, Integer m) { return deadlocks.page(h, m); } }
            public final class OaBlackswanReviewHoldController { public ReviewHold create(RequestContext c, ReviewHoldCreateRequest r) { return reviewHolds.create(c, r); } public List<ReviewHold> list(String s, String e) { return reviewHolds.list(s, e); } public ReviewHold release(RequestContext c, long id) { return reviewHolds.release(c, id); } }
            public final class OaBlackswanPeakMonthController { public PeakMonth declare(RequestContext c, PeakMonthRequest r) { return peakMonths.declare(c, r); } public List<PeakMonth> list(String o) { return peakMonths.list(o); } }
            public final class OaImperialTakeoverController { public ImperialTakeover assign(RequestContext c, ImperialAssignRequest r) { return imperial.assign(c, r); } public ImperialTakeover revoke(RequestContext c, ImperialRevokeRequest r) { return imperial.revoke(c, r); } public List<ImperialTakeover> page(String o, String s) { return imperial.page(o, s); } }
            public final class ComplianceInquiryController { public ComplianceInquiryTicket apply(RequestContext c, ComplianceInquiryApplyRequest r) { return compliance.apply(c, r); } public ComplianceInquiryTicket handle(RequestContext c, long id, ComplianceInquiryHandleRequest r) { return compliance.handle(c, id, r); } public String viewRealName(RequestContext c, String e) { return compliance.realName(c, e); } public List<ComplianceInquiryTicket> pending() { return compliance.pending(); } }

            private int intParam(String dim, String key, int fallback) { String v = configs.value(dim, key); if (v == null || v.isBlank()) return fallback; try { return Integer.parseInt(v.trim()); } catch (NumberFormatException ex) { return fallback; } }
            private boolean blank(String s) { return s == null || s.isBlank(); }
        }
    ''')


def generate_test() -> None:
    write("FullWatchdogModuleTest.java", r'''
        package com.skills.pilot.oa.watchdog.full;

        import com.skills.pilot.oa.watchdog.full.api.*;
        import com.skills.pilot.oa.watchdog.full.dto.*;
        import com.skills.pilot.oa.watchdog.full.entity.*;
        import com.skills.pilot.oa.watchdog.full.model.*;
        import java.time.Instant;
        import java.util.*;

        public final class FullWatchdogModuleTest {
            private int passed;
            public static void main(String[] args) { FullWatchdogModuleTest t = new FullWatchdogModuleTest(); t.run(); System.out.println("WATCHDOG_FULL_MODULE_TESTS passed=" + t.passed); }
            private void run() {
                enumAndEndpointCoverage(); configPendingAndDirectApply(); complaintSubmitScreenAndTargets(); complaintL6DualSignHappyAndRejectPaths();
                complaintL6TimeoutAndExternalCommittee(); deadlockD8AndRadarScans(); reviewHoldProtectionAndMetaDeadlock(); peakMonthAlertDashboardAndIdempotency();
                imperialTakeoverFlow(); complianceInquiryFlow(); monthlyReportIntegrity();
            }
            private WatchdogFullModule m() { return new WatchdogFullModule().seedDefaultUsers(); }
            private RequestContext ctx(String uid, String eid, String role, Instant t) { return new RequestContext(uid, eid, role, "ORG-A", "123456", t); }
            private RequestContext reporter(Instant t) { return ctx("u-reporter","E-REPORTER","Y-L3",t); }
            private RequestContext zl5(Instant t) { return ctx("u-zl5","E-ZL5","Z-L5A1",t); }
            private RequestContext l6a(Instant t) { return ctx("u-l6a","E-L6-A","L6",t); }
            private RequestContext l6b(Instant t) { return ctx("u-l6b","E-L6-B","L6",t); }
            private RequestContext l6c(Instant t) { return ctx("u-l6c","E-L6-C","L6",t); }
            private RequestContext zl4(Instant t) { return ctx("u-zl4","E-ZL4","Z-L4C1",t); }
            private RequestContext yl5b(Instant t) { return ctx("u-yl5b","E-YL5B","Y-L5B",t); }

            private void enumAndEndpointCoverage() {
                ok(DimCode.of("D8") == DimCode.D8, "D8 supported"); ok(DimCode.of("D9") == DimCode.D9, "D9 supported"); ok(DimCode.of("F7-PIP") == DimCode.F7_PIP, "F7-PIP supported");
                WatchdogFullModule m = m(); ok(m.endpoints.routes().size() == 29, "route breadth"); ok(m.endpoints.contains("POST","/oa/compliance/inquiry/apply"), "compliance route"); ok(m.endpoints.contains("POST","/oa/governance/imperial/assign"), "imperial route");
            }
            private void configPendingAndDirectApply() {
                WatchdogFullModule m = m(); Instant t = Instant.parse("2026-07-28T00:00:00Z");
                ConfigSaveRequest s = new ConfigSaveRequest(); s.dimCode = "D8"; s.paramKey = "DEADLOCK_THRESHOLD"; s.pendingValue = "2"; s.changeReason = "tighten";
                DimConfig p = m.controllers.config.save(zl5(t), s); ok("2".equals(p.pendingValue), "pending written"); ok(m.configs.value("D8","DEADLOCK_THRESHOLD") == null, "pending not active");
                ConfigApproveRequest a = new ConfigApproveRequest(); a.dimCode = "D8"; a.paramKey = "DEADLOCK_THRESHOLD"; m.controllers.config.approve(zl5(t), a); ok("2".equals(m.configs.value("D8","DEADLOCK_THRESHOLD")), "approved");
                ConfigSaveRequest d = new ConfigSaveRequest(); d.dimCode = "D9"; d.paramKey = "REVIEW_HOLD_WORKDAYS"; d.pendingValue = "1"; d.changeReason = "direct"; ok("1".equals(m.controllers.config.save(l6a(t), d).paramValue), "L6 direct");
                ConfigSaveRequest bad = new ConfigSaveRequest(); bad.dimCode = "D10"; bad.paramKey = "X"; bad.pendingValue = "1"; bad.changeReason = "bad"; expect(ErrorCode.BLACKSWAN_DIM_NOT_FOUND, () -> m.controllers.config.save(zl5(t), bad), "bad dim");
            }
            private void complaintSubmitScreenAndTargets() {
                WatchdogFullModule m = m(); Instant t = Instant.parse("2026-07-28T01:00:00Z");
                Complaint c = m.controllers.complaint.submit(reporter(t), complaint("target", "a concrete complaint body that is long enough"));
                ok(c.contentText.contains("concrete"), "content text stored"); ok(c.contentRefId == null, "content ref unused"); ok(ComplaintStatus.SUBMITTED.getCode().equals(c.status), "submitted"); ok(m.store.complaintTargets.stream().filter(x -> x.complaintId == c.id).count() == 1, "target row");
                ComplaintScreenRequest sr = screen(1, 0); expect(ErrorCode.COMPLAINT_SCREEN_ROLE_DENIED, () -> m.controllers.complaint.screen(reporter(t), c.complaintUuid, sr), "screen role");
                ok(ComplaintStatus.FILED.getCode().equals(m.controllers.complaint.screen(zl5(t), c.complaintUuid, sr).status), "filed"); ok(m.store.reviewHolds.stream().anyMatch(h -> c.complaintUuid.equals(h.complaintUuid)), "review hold");
                Complaint c2 = m.controllers.complaint.submit(reporter(t.plusSeconds(1)), complaint("target", "another concrete body text")); expect(ErrorCode.COMPLAINT_SCREENING_FAILED, () -> m.controllers.complaint.screen(zl5(t), c2.complaintUuid, screen(0, 1)), "screen fail"); ok(ComplaintStatus.SCREENING_FAILED.getCode().equals(c2.status), "failed persisted");
                ComplaintSubmitRequest multi = complaint(null, "multi target complaint body with details"); multi.targets.add(target("target",1)); multi.targets.add(target("l6a",2)); Complaint c3 = m.controllers.complaint.submit(reporter(t), multi); ok(m.store.complaintTargets.stream().filter(x -> x.complaintId == c3.id).count() == 2, "multi target");
            }
            private void complaintL6DualSignHappyAndRejectPaths() {
                WatchdogFullModule m = m(); Instant t = Instant.parse("2026-07-28T02:00:00Z"); DualSignRequest ds = new DualSignRequest();
                Complaint c = m.controllers.complaint.submit(reporter(t), complaint("l6a", "complaint against one l6 with concrete body")); ok(ComplaintStatus.PENDING_DUAL_L6_SIGN.getCode().equals(c.status), "pending dual");
                expect(ErrorCode.COMPLAINT_L6_SELF_SIGN_FORBIDDEN, () -> m.controllers.complaint.dualL6FirstSign(l6a(t), c.complaintUuid, ds), "self sign");
                m.controllers.complaint.dualL6FirstSign(l6b(t), c.complaintUuid, ds); DualSignRequest yes = new DualSignRequest(); yes.accept = true;
                expect(ErrorCode.COMPLAINT_SAME_L6_DUAL_SIGN_FORBIDDEN, () -> m.controllers.complaint.dualL6SecondSign(l6b(t.plusSeconds(10)), c.complaintUuid, yes), "same signer"); m.controllers.complaint.dualL6SecondSign(l6c(t.plusSeconds(10)), c.complaintUuid, yes); ok(ComplaintStatus.L6_DUAL_SIGNED.getCode().equals(c.status), "signed");
                Complaint r = m.controllers.complaint.submit(reporter(t), complaint("l6a", "another complaint against one l6 concrete body")); m.controllers.complaint.dualL6FirstSign(l6b(t), r.complaintUuid, ds); DualSignRequest no = new DualSignRequest(); no.accept = false; m.controllers.complaint.dualL6SecondSign(l6c(t.plusSeconds(10)), r.complaintUuid, no); ok(ComplaintStatus.CLOSED_REJECTED.getCode().equals(r.status), "rejected");
            }
            private void complaintL6TimeoutAndExternalCommittee() {
                WatchdogFullModule m = m(); Instant t = Instant.parse("2026-07-28T03:00:00Z"); DualSignRequest ds = new DualSignRequest();
                Complaint c = m.controllers.complaint.submit(reporter(t), complaint("l6a", "timeout complaint against l6 concrete body")); m.controllers.complaint.dualL6FirstSign(l6b(t), c.complaintUuid, ds); DualSignRequest yes = new DualSignRequest(); yes.accept = true; expect(ErrorCode.COMPLAINT_DUAL_SIGN_TIMEOUT, () -> m.controllers.complaint.dualL6SecondSign(l6c(t.plusSeconds(73L*3600L)), c.complaintUuid, yes), "timeout"); ok(ComplaintStatus.EXTERNAL_COMMITTEE_TAKEOVER.getCode().equals(c.status), "external");
                m.controllers.complaint.submit(reporter(t), complaint("l6a","first open l6 complaint body")); m.controllers.complaint.submit(reporter(t), complaint("l6b","second open l6 complaint body")); ok(ComplaintStatus.EXTERNAL_COMMITTEE_TAKEOVER.getCode().equals(m.controllers.complaint.submit(reporter(t), complaint("l6c","third open l6 complaint body")).status), "three l6");
            }
            private void deadlockD8AndRadarScans() {
                WatchdogFullModule m = m(); Instant t = Instant.parse("2026-07-28T04:00:00Z"); ConfigSaveRequest s = new ConfigSaveRequest(); s.dimCode = "D8"; s.paramKey = "DEADLOCK_THRESHOLD"; s.pendingValue = "2"; s.changeReason = "test"; m.controllers.config.save(l6a(t), s);
                DeadlockReportRequest dr = new DeadlockReportRequest(); dr.topicHash = "hash-1"; dr.nodeSet.addAll(Arrays.asList("L6_A","L6_B","Z-L5A1")); DeadlockFingerprint fp = m.controllers.internal.deadlockFingerprint(zl5(t), dr); ok(fp.nodeSet.size() == 2 && fp.nodeSet.contains("L6"), "normalize");
                m.controllers.internal.deadlockFingerprint(zl5(t), dr); ok(fp.triggeredAlertUuid != null, "D8 trigger"); ok(m.store.redAlertPushes.size() == 1, "red outbox"); ok(m.scans.d8(zl5(t)) == 0, "D8 idempotent");
                seedThreeL6(m, t); ok(m.scans.d6(zl5(t.plusSeconds(10))) == 1, "D6"); ok(BlackswanAlertStatus.ESCALATED_L6.getCode().equals(m.store.alerts.stream().filter(a -> "D6".equals(a.dimCode)).findFirst().get().status), "D6 escalated");
                Complaint a = m.controllers.complaint.submit(reporter(t), complaint("target","d7 body one long")); Complaint b = m.controllers.complaint.submit(reporter(t), complaint("target","d7 body two long")); Complaint c = m.controllers.complaint.submit(reporter(t), complaint("target","d7 body three long")); a.filedAt=t; b.filedAt=t; c.filedAt=t; ok(m.scans.d7(zl5(t.plusSeconds(1))) == 1, "D7");
                ReviewHoldCreateRequest h = new ReviewHoldCreateRequest(); h.targetEid = "E-TARGET"; h.complaintUuid = "C-D9"; h.holdWorkdays = 1; ReviewHold rh = m.controllers.reviewHold.create(zl5(t.minusSeconds(3*24*3600L)), h); rh.holdUntil = t.minusSeconds(1); ok(m.scans.d9(zl5(t)) == 1, "D9"); ok(m.scans.d9(zl5(t.plusSeconds(30))) == 0, "D9 idempotent"); ok(BlackswanAlertStatus.ESCALATED_L6.getCode().equals(m.store.alerts.stream().filter(x -> "D9".equals(x.dimCode)).findFirst().get().status), "D9 escalated");
            }
            private void reviewHoldProtectionAndMetaDeadlock() {
                WatchdogFullModule m = m(); Instant t = Instant.parse("2026-07-28T05:00:00Z"); ReviewHoldCreateRequest h = new ReviewHoldCreateRequest(); h.targetEid = "E-TARGET"; ReviewHold created = m.controllers.reviewHold.create(zl5(t), h);
                expect(ErrorCode.REVIEW_HOLD_ACTION_CONFLICT, () -> m.controllers.reviewHold.create(zl5(t), h), "duplicate hold"); expect(ErrorCode.WHISTLEBLOWER_PROTECTION_HOLD, () -> m.reviewHolds.assertWriteAllowed("E-TARGET", ReviewHoldAction.TERMINATION, t), "hold blocks"); m.controllers.reviewHold.release(l6a(t), created.id); ok("RELEASED".equals(created.status), "released");
                Complaint c = m.controllers.complaint.submit(reporter(t), complaint("target","whistleblower protection body")); c.filedAt = t; expect(ErrorCode.WHISTLEBLOWER_RETALIATION_BLOCKED, () -> m.reviewHolds.assertWriteAllowed("u-reporter", ReviewHoldAction.PERF_DOWN, t.plusSeconds(1)), "reporter protected"); m.reviewHolds.assertWriteAllowed("u-reporter", ReviewHoldAction.TERMINATION, t.plusSeconds(1)); ok(true, "termination not whistleblower code");
                ReviewHoldCreateRequest meta = new ReviewHoldCreateRequest(); meta.targetEid = "E-TARGET"; meta.chairpersonForceSwitched = 1; m.controllers.reviewHold.create(zl5(t.plusSeconds(2)), meta); expect(ErrorCode.WATCHDOG_CHAIR_CONFLICT, () -> m.metaDeadlock.check(yl5b(t), "E-TARGET", "updatePerf"), "meta deadlock"); ok(m.reviewHolds.autoRelease(t.plusSeconds(100L*24*3600L)) >= 1, "auto release");
            }
            private void peakMonthAlertDashboardAndIdempotency() {
                WatchdogFullModule m = m(); Instant t = Instant.parse("2026-07-28T06:00:00Z"); PeakMonthRequest pm = new PeakMonthRequest(); pm.orgId="ORG-A"; pm.peakYear=2026; pm.peakMonth=7; ok(m.controllers.peakMonth.declare(zl5(t), pm).id > 0 && m.controllers.peakMonth.list("ORG-A").size() == 1, "peak");
                Alert a = m.alerts.create(DimCode.D1, BlackswanSeverity.YELLOW, "ORG-A", "E-TARGET", "{}", 0, t.minusSeconds(80*3600L)); AckRequest ar = new AckRequest(); ar.remark = "remark"; m.controllers.blackswan.ack(zl5(t), a.alertUuid, ar); expect(ErrorCode.ALERT_ALREADY_ACKED, () -> m.controllers.blackswan.ack(zl5(t), a.alertUuid, ar), "double ack"); CloseRequest cr = new CloseRequest(); cr.resolution = "RESOLVED"; cr.remark = "closed"; m.controllers.blackswan.close(zl5(t), a.alertUuid, cr); expect(ErrorCode.BLACKSWAN_ALERT_CLOSED, () -> m.controllers.blackswan.ack(zl5(t), a.alertUuid, ar), "closed ack"); ok(((Long)m.controllers.blackswan.dashboard(zl5(t)).get("totalAlertsThisMonth")) == 1L, "dash");
                m.idempotency.remember("k1", WatchdogFullModule.sha256("a")); m.idempotency.remember("k1", WatchdogFullModule.sha256("a")); expect(ErrorCode.IDEMPOTENCY_CONFLICT, () -> m.idempotency.remember("k1", WatchdogFullModule.sha256("b")), "idem");
            }
            private void imperialTakeoverFlow() {
                WatchdogFullModule m = m(); Instant t = Instant.parse("2026-07-28T07:00:00Z"); ImperialAssignRequest r = new ImperialAssignRequest(); r.agentEid="E-AGENT"; r.scopeJson="{}"; r.orgId="ORG-A"; r.reason="reason text has more than twenty chars"; ImperialTakeover it = m.controllers.imperialController.assign(l6a(t), r); ok(it.ticketNo.startsWith("IMP-20260728-"), "ticket"); ok(m.imperial.activeByOrg("ORG-A") != null, "active"); ImperialRevokeRequest rr = new ImperialRevokeRequest(); rr.id=String.valueOf(it.id); rr.reason="valid revoke reason"; m.controllers.imperialController.revoke(l6a(t), rr); ok(ImperialTakeoverStatus.REVOKED.getCode().equals(it.status), "revoked"); expect(ErrorCode.IMPERIAL_TAKEOVER_ALREADY_REVOKED, () -> m.controllers.imperialController.revoke(l6a(t), rr), "double revoke"); expect(ErrorCode.IMPERIAL_TAKEOVER_L6_ONLY, () -> m.controllers.imperialController.assign(zl5(t), r), "L6 only");
            }
            private void complianceInquiryFlow() {
                WatchdogFullModule m = m(); Instant t = Instant.parse("2026-07-28T08:00:00Z"); expect(ErrorCode.COMPLIANCE_INQUIRY_TICKET_REQUIRED, () -> m.controllers.complianceController.viewRealName(zl4(t), "E-TARGET"), "needs ticket"); ComplianceInquiryApplyRequest ar = new ComplianceInquiryApplyRequest(); ar.subjectEid="E-TARGET"; ar.reason="need real name for audit"; ar.purpose="AUDIT"; ComplianceInquiryTicket ticket = m.controllers.complianceController.apply(zl4(t), ar); ok(m.controllers.complianceController.pending().size()==1, "pending"); ComplianceInquiryHandleRequest hr = new ComplianceInquiryHandleRequest(); hr.action = ComplianceInquiryAction.COMPLETE; m.controllers.complianceController.handle(zl4(t.plusSeconds(60)), ticket.id, hr); ok("Target One".equals(m.controllers.complianceController.viewRealName(zl4(t.plusSeconds(120)), "E-TARGET")), "real name"); expect(ErrorCode.COMPLIANCE_INQUIRY_TICKET_REQUIRED, () -> m.controllers.complianceController.viewRealName(zl4(t.plusSeconds(25*3600L)), "E-TARGET"), "expired");
                ComplianceInquiryTicket rej = m.controllers.complianceController.apply(zl4(t), ar); ComplianceInquiryHandleRequest no = new ComplianceInquiryHandleRequest(); no.action = ComplianceInquiryAction.REJECT; m.controllers.complianceController.handle(zl4(t), rej.id, no); expect(ErrorCode.COMPLIANCE_INQUIRY_TICKET_REQUIRED, () -> m.controllers.complianceController.viewRealName(zl4(t), "E-L6-A"), "rejected");
            }
            private void monthlyReportIntegrity() {
                WatchdogFullModule m = m(); List<WatchdogFullModule.MonthlyReports.ReportEntry> e = Arrays.asList(m.monthlyReports.new ReportEntry("r1","alpha"), m.monthlyReports.new ReportEntry("r2","beta"), m.monthlyReports.new ReportEntry("r3","gamma")); String report = m.monthlyReports.build(e); ok(m.monthlyReports.verify(report).size()==3, "report valid"); String truncated = report.substring(0, report.lastIndexOf("r3|")); expect(ErrorCode.MONTHLY_REPORT_TAIL_TRUNCATED, () -> m.monthlyReports.verify(truncated), "tail truncation");
            }
            private void seedThreeL6(WatchdogFullModule m, Instant t) { m.controllers.complaint.submit(reporter(t), complaint("l6a","open l6 a complaint body")); m.controllers.complaint.submit(reporter(t), complaint("l6b","open l6 b complaint body")); m.controllers.complaint.submit(reporter(t), complaint("l6c","open l6 c complaint body")); }
            private ComplaintSubmitRequest complaint(String alias, String body) { ComplaintSubmitRequest r = new ComplaintSubmitRequest(); r.targetAliasName = alias; r.contentText = body; r.isAnonymousTemplate = 0; r.hasConcreteFacts = 1; return r; }
            private ComplaintScreenRequest screen(int facts, int anon) { ComplaintScreenRequest r = new ComplaintScreenRequest(); r.hasConcreteFacts = facts; r.isAnonymousTemplate = anon; r.remark = "remark"; return r; }
            private ComplaintTargetRequest target(String alias, int seq) { ComplaintTargetRequest r = new ComplaintTargetRequest(); r.aliasName = alias; r.sequence = seq; return r; }
            private void ok(boolean condition, String name) { if (!condition) throw new AssertionError(name); passed++; }
            private void expect(ErrorCode code, ThrowingRunnable fn, String name) { try { fn.run(); throw new AssertionError("expected " + code + ": " + name); } catch (ApiException ex) { if (ex.code() != code) throw new AssertionError("expected " + code + " got " + ex.code() + ": " + name); passed++; } }
            private interface ThrowingRunnable { void run(); }
        }
    ''', test=True)


def main() -> None:
    generate_api()
    generate_model()
    generate_data_classes()
    generate_core_module()
    generate_test()
    files = list((ROOT / "src").rglob("*.java"))
    print(f"generated_java={len(files)} root={ROOT}")


if __name__ == "__main__":
    main()
