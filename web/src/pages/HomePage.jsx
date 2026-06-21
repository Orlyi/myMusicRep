import {useEffect} from "react";
import client from "../api/client.js";

export default function HomePage(){
    useEffect(()=>
        {client.get('/health').then(res=> console.log('Success, return:', res)).catch(err=> console.log('Error, return:', err.message))
        }, []
    )

    return (
        <div className="page">
            <h1>HomePage</h1>
            <div>
            </div>
        </div>
    )
}