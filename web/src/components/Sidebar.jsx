import './Sidebar.css'
import useAuth from "../hooks/useAuth.js";

export default function Sidebar({open, onClose, children}){
    const {logout} = useAuth()
    return (
        <>
        {open && (<div className="overlay" onClick={onClose} />)}
        <div className={`sidebar ${open ? "open" : ""}`} >

            {children}
        </div>
        </>
    )
}