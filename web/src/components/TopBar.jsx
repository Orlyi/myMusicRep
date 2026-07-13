import GoBack from "./GoBack.jsx";


export default function TopBar({from, path, title, children, is_show=false}){
    return(
        <div style={{width:'100%',height:'100%',display:'flex',justifyContent:'center',alignItems:'center'}}>
            <div style={{position:"fixed", left:"0"}}>
                {from!=="/login"&&path!=="/"&&!is_show ? <GoBack from={from} path={path} /> :""}

            </div>

            {
                children || <span style={{fontWeight:"bolder"}}>{title}</span>
            }
        </div>
    )
}