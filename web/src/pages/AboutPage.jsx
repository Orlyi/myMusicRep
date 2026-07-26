import { useNavigate } from "react-router-dom";
import { ChevronLeft } from "lucide-react";

export default function AboutPage() {
    const navigate = useNavigate();

    return (
        <div className="page" style={{ padding: "1em", display: "flex", flexDirection: "column", alignItems: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5em", marginBottom: "2em", width: "100%" }}>
                <ChevronLeft size={24} onClick={() => navigate(-1)} style={{ cursor: "pointer" }} />
                <span style={{ fontSize: "1.1em", fontWeight: 600 }}>关于我们</span>
            </div>

            {/* Logo */}
            <div style={{
                width: "20vw", height: "20vw", maxWidth: 100, maxHeight: 100,
                borderRadius: "20%", background: "#333",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "2.5em", color: "#fff", fontWeight: "bold", marginBottom: "1em",
            }}>
                ♪
            </div>

            <h2 style={{ margin: "0 0 0.2em", fontSize: "1.2em" }}>myMusic</h2>
            <p style={{ color: "#999", fontSize: "0.85em", margin: "0 0 2em", textAlign: "center" }}>
                一个在线音乐平台
            </p>

            <div style={{ width: "100%", maxWidth: 280, display: "flex", flexDirection: "column", gap: "0.8em" }}>
                <InfoRow label="版本" value="v1.0.0" />
                <InfoRow label="作者" value="Orly" />
                <InfoRow label="技术栈" value="React 19 + FastAPI" />
                <InfoRow label="数据库" value="MySQL + Redis" />
            </div>

            <p style={{ color: "#bbb", fontSize: "0.75em", marginTop: "auto", paddingBottom: "2em" }}>
                © 2026 myMusic
            </p>
        </div>
    );
}

function InfoRow({ label, value }) {
    return (
        <div style={{ display: "flex", justifyContent: "space-between", padding: "0.5em 0", borderBottom: "1px solid #f0f0f0" }}>
            <span style={{ color: "#666", fontSize: "0.9em" }}>{label}</span>
            <span style={{ fontSize: "0.9em" }}>{value}</span>
        </div>
    );
}
