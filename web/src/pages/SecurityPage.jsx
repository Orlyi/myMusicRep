import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { changePassword } from "../api/auth.js";
import { ChevronLeft } from "lucide-react";

export default function SecurityPage() {
    const navigate = useNavigate();
    const [oldPwd, setOldPwd] = useState("");
    const [newPwd, setNewPwd] = useState("");
    const [confirmPwd, setConfirmPwd] = useState("");
    const [msg, setMsg] = useState("");

    const handleSubmit = async () => {
        setMsg("");
        if (!oldPwd || !newPwd || !confirmPwd) {
            setMsg("请填写完整");
            return;
        }
        if (newPwd !== confirmPwd) {
            setMsg("两次新密码不一致");
            return;
        }
        if (newPwd.length < 6) {
            setMsg("密码至少6位");
            return;
        }
        try {
            const res = await changePassword({ old_password: oldPwd, new_password: newPwd });
            if (res.code === 0) {
                setMsg("密码修改成功");
                setOldPwd(""); setNewPwd(""); setConfirmPwd("");
            } else {
                setMsg(res.message || "修改失败");
            }
        } catch (err) {
            setMsg("修改失败");
        }
    };

    return (
        <div className="page" style={{ padding: "1em",flexDirection:"column" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5em", marginBottom: "1.5em",justifyContent:"center"  }}>
                <ChevronLeft size={24} onClick={() => navigate(-1)} style={{ cursor: "pointer",position:"fixed",left:"4vw" }} />
                <span style={{ fontSize: "1.1em", fontWeight: 600 }}>安全中心</span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "1em", maxWidth: 300 }}>
                <div>
                    <div style={{ fontSize: "0.85em", color: "#666", marginBottom: "0.3em" }}>原密码</div>
                    <input type="password" value={oldPwd} onChange={e => setOldPwd(e.target.value)}
                        style={{ border: "1px solid #ddd", borderRadius: 8, padding: "0.6em", fontSize: "0.9em", outline: "none", width: "100%", boxSizing: "border-box" }} />
                </div>
                <div>
                    <div style={{ fontSize: "0.85em", color: "#666", marginBottom: "0.3em" }}>新密码</div>
                    <input type="password" value={newPwd} onChange={e => setNewPwd(e.target.value)}
                        style={{ border: "1px solid #ddd", borderRadius: 8, padding: "0.6em", fontSize: "0.9em", outline: "none", width: "100%", boxSizing: "border-box" }} />
                </div>
                <div>
                    <div style={{ fontSize: "0.85em", color: "#666", marginBottom: "0.3em" }}>确认新密码</div>
                    <input type="password" value={confirmPwd} onChange={e => setConfirmPwd(e.target.value)}
                        style={{ border: "1px solid #ddd", borderRadius: 8, padding: "0.6em", fontSize: "0.9em", outline: "none", width: "100%", boxSizing: "border-box" }} />
                </div>
                <button onClick={handleSubmit}
                    style={{ background: "#333", color: "#fff", border: "none", borderRadius: "1.5em", padding: "0.6em 0", cursor: "pointer", fontSize: "0.9em" }}>
                    修改密码
                </button>
                {msg && <div style={{ fontSize: "0.85em", textAlign: "center" }}>{msg}</div>}
            </div>
        </div>
    );
}
