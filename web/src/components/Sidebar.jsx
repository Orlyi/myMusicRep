import './Sidebar.css'

export default function Sidebar({open, onClose}){
    return (
        <>
        {open&& (<div className= "overlay" onClick={onClose} />)}
        <div className={`sidebar ${open? "open": ""}`}></div>
        </>
    )
}