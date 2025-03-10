import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./Login.css";

const base_url = import.meta.env.VITE_BACKEND_URL;

export default function Login({ email, password, handleEmailChange, handlePasswordChange }) {
    const navigate = useNavigate();
    
    const handleSubmit = async (event) => {
        event.preventDefault();
        try {
            console.log("Login attempt with:", { username: email });
            
            // Create form data
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);
            
            console.log("Request URL:", `${base_url}/auth/login`);
            console.log("Form data:", formData.toString());
            
            const response = await axios.post(
                `${base_url}/auth/login`, 
                formData,  // Pass the URLSearchParams object directly
                {
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                }
            );
            
            console.log("Login response:", response);
            
            if (response.status !== 200 && response.status !== 201) {
                throw new Error("Login failed");
            }
            
            localStorage.setItem("token", response.data.access_token);
            console.log("Successfully logged in:", response.data);
            
            navigate("/homepage", { replace: true });
        } catch (error) {
            if (error.response) {
                console.error("Error status:", error.response.status);
                console.error("Error headers:", error.response.headers);
                console.error("Error data:", error.response.data);
            } else if (error.request) {
                console.error("No response received:", error.request);
            } else {
                console.error("Error during login:", error.message);
            }
        }
    }
    
    return (
        <div className="login-container">
            <div className="login-card">
                <h2 className="login-title">Welcome Back</h2>
                <p className="login-subtitle">Sign in to continue to your account</p>
                
                <form className="login-form" onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input 
                            id="email"
                            type="email" 
                            value={email} 
                            onChange={(e) => handleEmailChange(e.target.value)} 
                            placeholder="Enter your email"
                            required 
                        />
                    </div>
                    
                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input 
                            id="password"
                            type="password"
                            value={password} 
                            onChange={(e) => handlePasswordChange(e.target.value)} 
                            placeholder="Enter your password"
                            required 
                        />
                    </div>
                    
                    <div className="form-footer">
                        <button type="submit" className="login-button">
                            Sign In
                        </button>
                        <p className="login-redirect">
                            Don't have an account? 
                            <span onClick={() => navigate("/")}>Sign up</span>
                        </p>
                    </div>
                </form>
            </div>
        </div>
    );
}