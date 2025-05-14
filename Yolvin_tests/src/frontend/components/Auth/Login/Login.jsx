import { useEffect } from "react";
import axios from "axios";
import { useNavigate } from 'react-router-dom';
import CryptoJS from "crypto-js";

const URL = window.location.href.split(':');
const endpoint = "http:" + URL[1] + ":8000/login/";
export default function Login() {
  useEffect(() => {
    document.title = "Login";
  }, []);

  const navigate = useNavigate();

  function togglePassword(event) {
    const type = event.target.offsetParent.firstChild.type;
    event.target.offsetParent.firstChild.type = type == "password" ? "text" : "password"
  }

  function onSubmit(event) {
    event.preventDefault();

    const form = event.target;
    if (!form.checkValidity()) {
      event.stopPropagation();
      form.classList.add('was-validated');
      return;
    }
    form.classList.add('was-validated');

    const formData = new FormData(form);
    const secretKey = "my-secret-key"; // should have environment variable instead of having it in the code
    const encryptedPassword = CryptoJS.AES.encrypt(formData.get("password"), secretKey).toString();

    axios.post(endpoint, {
      email: formData.get("email"),
      password: encryptedPassword,
    }).then((response) => {
      console.log(response);
      sessionStorage.setItem("token", "tempToken123abc");
      navigate("/");
    });
  }
  
  return (
    <>
      <form onSubmit={onSubmit} className="needs-validation" noValidate>
        <br />
        <br />
        <div className="row justify-content-center mt-4 mb-4">
          <input type="email" className="form-control" name="email" id="email" placeholder="placeholder@email.com" required />
          <div className="valid-feedback"></div>
          <div className="invalid-feedback">Please enter your email</div>
        </div>
        <div className="row justify-content-center mt-4 mb-4">
          <div className="input-group removePadding has-validation">
            <input type="password" className="form-control" name="password" id="password" placeholder="Password" required />
            <span className="input-group-text togglePassword" name="togglePassword" id="togglePassword" onClick={togglePassword}>
              <i className="fa fa-eye"></i>
            </span>
            <div className="valid-feedback"></div>
            <div className="invalid-feedback">
              Please enter password
            </div>
          </div>
        </div>
        <br />
        <div className="row justify-content-center mt-4 mb-4">
          <button type="submit" className="btn btn-success">Login</button>
        </div>
      </form>
    </>
  )
}
