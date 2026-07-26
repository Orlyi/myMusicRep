import {ChevronRight} from "lucide-react";
import {useNavigate} from "react-router-dom";
import "./SidebarItem.css"

export function SideItem({path, from, content, onClose}){
    const navigate=useNavigate()
    const goForward=() =>{
        onClose?.()
        from&&path ?navigate(path, {state:{from:from}}): navigate(path)
    }

    return (
        <div className="sidebar-item" onClick={goForward}>
            <div className="sidebar-item-font" >{content}</div><button style={{position:"absolute",right:0}}><ChevronRight /></button>
        </div>
    )
}

// 无右侧箭头的纯展示项
export function SideLabel({content}){
    return (
        <div className="sidebar-item" style={{cursor:"default"}}>
            <div className="sidebar-item-font">{content}</div>
        </div>
    )
}
