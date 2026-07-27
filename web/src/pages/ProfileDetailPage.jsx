import TopBar from "../components/TopBar.jsx";
import {useLocation, useNavigate} from "react-router-dom";
import {useEffect, useState} from "react";
import {getMyInfo, writeMyInfo} from "../api/users.js";
import {uploadAvatar} from "../api/auth.js";
import {ChevronLeft} from "lucide-react";
import {STATIC_BASE} from "../config.js";

export default function ProfileDetailPage(){
    const navigate = useNavigate();
    const [userInfo, setUserInfo] = useState(null);
    const [loading, setLoading] = useState(true);
    const [editing, setEditing] = useState(false);
    const [form, setForm] = useState({});
    const [saving, setSaving] = useState(false);
    const [msg, setMsg] = useState("");

    const fetchInfo = async () => {
        try {
            const res = await getMyInfo();
            setUserInfo(res.data);
            const d = res.data?.details || {};
            setForm({
                email: res.data?.user?.email || "",
                nick_name: d.nick_name || "",
                gender: d.gender || "其他",
                birthdate: d.birthdate || "",
                city: d.city || "",
                phone_number: d.phone_number || "",
            });
        } catch(err){
            console.log("获取用户信息失败", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchInfo(); }, []);

    const handleSave = async () => {
        setSaving(true);
        setMsg("");
        try {
            await writeMyInfo(form);
            setMsg(" 保存成功");
            setEditing(false);
            fetchInfo();
        } catch(err) {
            setMsg("保存失败");
        } finally {
            setSaving(false);
        }
    };

    const handleAvatarChange = async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        try {
            const res = await uploadAvatar(file);
            if (res.code === 0) {
                fetchInfo();
            }
        } catch(err) {
            console.log("上传头像失败", err);
        }
    };

    if(loading){
        return <div className="page" style={{padding:"1em"}}>加载中</div>;
    }

    const user = userInfo?.user;
    const details = userInfo?.details;

    return (
        <div className="page" style={{ display:"flex", flexDirection:"column"}}>
            <div style={{display:"flex", alignItems:"center", gap:"0.5em", marginBottom:"1em",justifyContent:"center" }}>
                <ChevronLeft size={24} onClick={() => navigate(-1)} style={{cursor:"pointer",position:"fixed",left:"4%",marginTop:"2vh",}} />
                <span style={{fontSize:"1.1em", fontWeight:600,marginTop:"2vh",}}>个人信息</span>
                <button onClick={() => editing ? handleSave() : setEditing(true)}
                    style={{
                        marginLeft:"auto", background: editing ? "#333" : "transparent",
                        color: editing ? "#fff" : "#333", border: editing ? "none" : "1px solid #333",marginTop:"2vh",
                        borderRadius:"1.5em", padding:"0.3em 0.8em", fontSize:"0.8em", cursor:"pointer",position:"fixed",right:"4%"
                    }}>
                    {editing ? (saving ? "保存中..." : "保存") : "编辑"}
                </button>
            </div>

            {/* 头像 */}
            <div style={{display:"flex", justifyContent:"center", marginBottom:"0", position:"relative"}}>
                <img src={user?.avatar_url ? `${STATIC_BASE}${user.avatar_url}` : ""}
                    alt="" style={{width:"20vw", height:"20vw", maxWidth:90, maxHeight:90, borderRadius:"50%", objectFit:"cover", background:"#eee"}} />
                {editing && (
                    <label style={{
                        position:"absolute", bottom:0, right:"30%", background:"#333", color:"#fff",
                        borderRadius:"50%", width:"1.5em", height:"1.5em", display:"flex", alignItems:"center", justifyContent:"center",
                        fontSize:"0.8em", cursor:"pointer",
                    }}>
                        ✎
                        <input type="file" accept="image/*" onChange={handleAvatarChange} style={{display:"none"}} />
                    </label>
                )}
            </div>

            {/* 表单 */}
            <div style={{display:"flex", flexDirection:"column", gap:"0.8em", maxWidth:350, margin:"0 auto", width:"100%",padding:"0 0.8em 0 0.8em",boxSizing:"border-box",}}>
                <Field label="用户名" value={user?.user_name || ""} />
                <Field label="邮箱">
                    {editing ? (
                        <input value={form.email} onChange={e => setForm({...form, email: e.target.value})}
                            style={inputStyle} placeholder="邮箱" />
                    ) : <span>{user?.email || "未设置"}</span>}
                </Field>
                <Field label="昵称">
                    {editing ? (
                        <input value={form.nick_name} onChange={e => setForm({...form, nick_name: e.target.value})}
                            style={inputStyle} placeholder="昵称" />
                    ) : <span>{details?.nick_name || "未设置"}</span>}
                </Field>
                <Field label="性别">
                    {editing ? (
                        <select value={form.gender} onChange={e => setForm({...form, gender: e.target.value})}
                            style={inputStyle}>
                            <option value="男">男</option>
                            <option value="女">女</option>
                            <option value="其他">其他</option>
                        </select>
                    ) : <span>{details?.gender || "未设置"}</span>}
                </Field>
                <Field label="生日">
                    {editing ? (
                        <input type="date" value={form.birthdate} onChange={e => setForm({...form, birthdate: e.target.value})}
                            style={inputStyle} />
                    ) : <span>{details?.birthdate || "未设置"}</span>}
                </Field>
                <Field label="手机">
                    {editing ? (
                        <input value={form.phone_number} onChange={e => setForm({...form, phone_number: e.target.value})}
                            style={inputStyle} placeholder="手机号" />
                    ) : <span>{details?.phone_number || "未设置"}</span>}
                </Field>
                <Field label="城市">
                    {editing ? (
                        <input value={form.city} onChange={e => setForm({...form, city: e.target.value})}
                            style={inputStyle} placeholder="城市" />
                    ) : <span>{details?.city || "未设置"}</span>}
                </Field>
                <Field label="注册天数" value={userInfo?.register_duration ? `${userInfo.register_duration} 天` : ""} />
            </div>

        </div>
    );
}

function Field({label, children, value}) {
    return (
        <div style={{display:"flex", justifyContent:"space-between", alignItems:"center", borderBottom:"1px solid #f0f0f0", padding:"0.5em 0"}}>
            <span style={{color:"#666", fontSize:"0.85em"}}>{label}</span>
            {children || <span style={{fontSize:"0.85em", color:"#333"}}>{value || ""}</span>}
        </div>
    );
}

const inputStyle = {
    border:"1px solid #ddd", borderRadius:6, padding:"0.4em", fontSize:"0.85em",
    outline:"none", width:"fit-content", maxWidth:"12em", textAlign:"right",
};
