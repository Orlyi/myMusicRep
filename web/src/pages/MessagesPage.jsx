import { useOutletContext} from "react-router-dom";
import {useEffect, useState} from "react";
import { receivedMessage, listMessages, deleteMessageSoft } from "../api/messages.js";
import { Trash2, Send, UserRound, ChevronLeft } from "lucide-react";

export default function MessagesPage(){
    const {setHeaderContent}= useOutletContext()
    const [acting, setActing]= useState(1)
    const [received, setReceived] = useState([])
    const [sent, setSent] = useState([])
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        setHeaderContent(
            <>
            <div className="top-nav-tab" onClick={()=>setActing(1)}><div className={`top-nav-tab-item ${acting=== 1? "larger_fontsize": ""}`}>收到的</div><div className={`underline tab ${acting=== 1? "width_zero": ""}`}></div></div>
            <div className="top-nav-tab" onClick={()=>setActing(2)}><div className={`top-nav-tab-item ${acting=== 2? "larger_fontsize": ""}`}>已发送</div><div className={`underline tab ${acting=== 2? "width_zero": ""}`}></div></div>
            </>
        )
        return ()=>setHeaderContent(null)
    }, [acting, setHeaderContent]);

    const load = async () => {
        setLoading(true)
        try {
            if (acting === 1) {
                const res = await receivedMessage({ page: 1, page_size: 50 })
                setReceived(res.data?.items || [])
            } else {
                const res = await listMessages({ page: 1, page_size: 50 })
                setSent(res.data?.items || [])
            }
        } catch (err) {
            console.log("获取消息失败", err)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { load() }, [acting])

    const handleDelete = async (msg) => {
        try {
            await deleteMessageSoft(msg.message_id)
            if (acting === 1) setReceived(prev => prev.filter(m => m.message_id !== msg.message_id))
            else setSent(prev => prev.filter(m => m.message_id !== msg.message_id))
        } catch (err) {
            console.log("删除失败", err)
        }
    }

    const formatTime = (iso) => {
        try {
            const d = new Date(iso)
            const now = new Date()
            const diff = (now - d) / 1000
            if (diff < 60) return "刚刚"
            if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
            if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
            return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")}`
        } catch { return "" }
    }

    const items = acting === 1 ? received : sent

    return (
        <div className="page" style={{display:"flex",flexDirection:"column"}}>
            <div style={{flex:1,width:"100%",overflow:"auto",minHeight:0}}>
                {loading ? (
                    <p style={{textAlign:"center",color:"#999",padding:"2em"}}>加载中...</p>
                ) : items.length === 0 ? (
                    <p style={{textAlign:"center",color:"#999",padding:"3em"}}>
                        {acting === 1 ? "还没有收到消息" : "还没有发送消息"}
                    </p>
                ) : (
                    items.map((msg, i) => (
                        <div key={msg.message_id || i} style={{
                            display:"flex", alignItems:"flex-start", gap:"0.5em",
                            padding:"0.8em 0.8em", borderBottom:"1px solid #f0f0f0",
                        }}>
                            {/* 头像占位 */}
                            <div style={{
                                width:"2.5em", height:"2.5em", borderRadius:"50%",
                                background:"#e0e0e0", flexShrink:0,
                                display:"flex", alignItems:"center", justifyContent:"center",
                                color:"#999",
                            }}>
                                <UserRound size={16} />
                            </div>

                            <div style={{flex:1,minWidth:0}}>
                                <div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
                                    <span style={{fontSize:"0.85em",fontWeight:600}}>
                                        {msg.sender_name || msg.receiver_name || "未知"}
                                    </span>
                                    <div style={{display:"flex",alignItems:"center",gap:"0.4em"}}>
                                        <span style={{fontSize:"0.7em",color:"#aaa"}}>{formatTime(msg.sent_time)}</span>
                                        <Trash2 size={14} color="#ccc" style={{cursor:"pointer"}}
                                            onClick={() => handleDelete(msg)} />
                                    </div>
                                </div>
                                <div style={{fontSize:"0.85em",color:"#555",marginTop:"0.3em",
                                    wordBreak:"break-all", whiteSpace:"pre-wrap"}}>
                                    {msg.content}
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
            <div style={{height:"20vh",flexShrink:0}} />
        </div>
    )
}
