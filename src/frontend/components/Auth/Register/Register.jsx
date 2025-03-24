import { useEffect } from "react";
import axios from "axios";
import { useNavigate } from 'react-router-dom';
import CryptoJS from "crypto-js";

import "./Register.css"

const URL = window.location.href.split(':');
const endpoint = "http:" + URL[1] + ":8000/addUser/";
export default function Register() {
  useEffect(() => {
    document.title = "Register";
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
    axios.post('http://127.0.0.1:8000/addUser', {
      firstName: formData.get("firstName"),
      lastName: formData.get("lastName"),
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
        <div className="row justify-content-center mt-4 mb-4">
          <input type="email" className="form-control" name="email" id="email" placeholder="placeholder@email.com" required />
          <div className="valid-feedback"></div>
          <div className="invalid-feedback">Please enter your email</div>
        </div>
        <div className="row justify-content-between mt-4 mb-4">
          <div className="col-5 removePadding">
            <input type="text" className="form-control" name="firstName" id="firstName" placeholder="First Name" required />
            <div className="valid-feedback"></div>
            <div className="invalid-feedback">
              Please enter your first name
            </div>
          </div>
          <div className="col-5 removePadding">
            <input type="text" className="form-control" name="lastName" id="lastName" placeholder="Last Name" required />
            <div className="valid-feedback"></div>
            <div className="invalid-feedback">
              Please enter your last name
            </div>
          </div>
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
        <div className="row justify-content-center mt-4 mb-4">
          <div className="input-group removePadding has-validation">
            <input type="password" className="form-control" name="verifyPassword" id="verifyPassword" placeholder="Verify Password" required />
            <span className="input-group-text togglePassword" name="toggleVerifyPassword" id="toggleVerifyPassword" onClick={togglePassword}>
              <i className="fa fa-eye"></i>
            </span>
            <div className="valid-feedback"></div>
            <div className="invalid-feedback">
              Please verify password
            </div>
          </div>
        </div>
        <div className="row justify-content-center mt-4 mb-4">
          <button type="submit" className="btn btn-success">Sign Up</button>
        </div>
      </form>
    </>
  )
}
