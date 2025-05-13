import { useEffect, useState } from "react";
import Login from "./Login/Login";
import Register from "./Register/Register";
import "./Auth.css"

export default function Auth() {
    const [authState, setAuthState] = useState("login");

    useEffect(() => {
        document.title = "Auth";
    }, []);

    function onAuthStateChange(newState) {
        setAuthState(newState)
    }

    return (
        <>
            <div className="container-fluid">
                <div className="row min-vh-100 justify-content-center align-content-center">
                    <div className="col-4"></div>
                    {/* Main Column */}
                    <div className="col-4">
                        <div className="row justify-content-center">
                            <div className="btn-group" role="group">
                                {/* Login Button */}
                                <input type="radio" className="btn-check" name="btnradio" id="loginBtnRadio" autoComplete="off" defaultChecked={true} onChange={() => onAuthStateChange("login")} />
                                <label className="btn btn-outline-success authButton" htmlFor="loginBtnRadio">Login</label>

                                {/* Register Button */}
                                <input type="radio" className="btn-check" name="btnradio" id="registerBtnRadio" autoComplete="off" onChange={() => onAuthStateChange("register")} />
                                <label className="btn btn-outline-success authButton" htmlFor="registerBtnRadio">Register</label>
                            </div>
                        </div>

                        {authState === "login" && <Login />}
                        {authState === "register" && <Register />}
                    </div>
                    <div className="col-4"></div>
                </div>
            </div>
        </>
    )
}
