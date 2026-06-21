import { useOutletContext} from "react-router-dom";
import {useEffect, useState} from "react";

export default function MessagesPage(){
    const {setHeaderContent}= useOutletContext()
    const [acting, setActing]= useState(0)
    useEffect(() => {
        setHeaderContent(
            <>
            <div className="top-nav-tab" onClick={()=>setActing(1)}><div className={`top-nav-tab-item ${acting=== 1? "larger_fontsize": ""}`}>私信</div><div className={`underline tab ${acting=== 1? "width_zero": ""}`}></div></div>
            <div className="top-nav-tab" onClick={()=>setActing(2)}><div className={`top-nav-tab-item ${acting=== 2? "larger_fontsize": ""}`}>点赞</div><div className={`underline tab ${acting=== 2? "width_zero": ""}`}></div></div>
            </>
        )
        return ()=>setHeaderContent(null)
    }, [acting, setHeaderContent]);

    return (
        <div className="page">
            <h1>消息</h1>
        </div>
    )
}