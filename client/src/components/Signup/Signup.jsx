import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./Signup.css";

function Signup({ email, password, handleEmailChange, handlePasswordChange }) {
    console.log(email, password);
    
    const navigate = useNavigate();
    
    const handleSubmit = async (event) => {
        event.preventDefault();
        try {
            const response = await axios.post(
                "http://localhost:8000/auth/register",
                { email, password },
                { headers: { "Content-Type": "application/json" } }
            );
            
            if (response.status !== 200 && response.status !== 201) {
                throw new Error("Registration failed");
            }
            
            console.log("Registration successful:", response.data);
            
            navigate("/login", { replace: true });
        } catch (error) {
            if (error.response) {
                console.error("Error during signup:", error.response.data);
            } else {
                console.error("Error during signup:", error.message);
            }
        }
    };
    
    return (
        <div className="signup-container">
            <div className="signup-card">
                <h2 className="signup-title">Create Account</h2>
                <p className="signup-subtitle">Join our community today</p>
                
                <form className="signup-form" onSubmit={handleSubmit}>
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
                            placeholder="Create a password"
                            required 
                        />
                    </div>
                    
                    <div className="form-footer">
                        <button type="submit" className="signup-button">
                            Create Account
                        </button>
                        <p className="signup-redirect">
                            Already have an account?
                            <span onClick={() => navigate("/login")}>Sign in</span>
                        </p>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default Signup;