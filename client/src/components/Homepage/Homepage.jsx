import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./Homepage.css";

const base_url = import.meta.env.VITE_BACKEND_URL;


function Homepage() {
    const [tasks, setTasks] = useState([]);
    const [newTask, setNewTask] = useState({
        title: "",
        description: "",
        scheduled_time: ""
    });
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState(null);
    const [editingTask, setEditingTask] = useState(null);
    
    const navigate = useNavigate();
    
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (!token) {
            navigate("/login");
            return;
        }
        
        fetchUserProfile(token);
        
        // Fetch tasks
        fetchTasks(token);
    }, [navigate]);
    
    const fetchUserProfile = async (token) => {
        try {
            const response = await axios.get(`${base_url}/users/me`, {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            setUser(response.data);
        } catch (error) {
            console.error("Error fetching user profile:", error);
            if (error.response && (error.response.status === 401 || error.response.status === 403)) {
                localStorage.removeItem("token");
                navigate("/login");
            }
        }
    };
    
    const fetchTasks = async (token) => {
        try {
            setLoading(true);
            const response = await axios.get(`${base_url}/tasks`, {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            setTasks(response.data);
        } catch (error) {
            console.error("Error fetching tasks:", error);
        } finally {
            setLoading(false);
        }
    };
    
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        if (editingTask) {
            setEditingTask(prev => ({
                ...prev,
                [name]: value
            }));
        } else {
            setNewTask(prev => ({
                ...prev,
                [name]: value
            }));
        }
    };
    
    const handleCreateTask = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem("token");
        if (!token) {
            navigate("/login");
            return;
        }
        
        try {
            // Format date properly for API
            const taskData = { ...newTask };
            
            // Make sure scheduled_time is in ISO format or null
            if (taskData.scheduled_time) {
                // If it's not a proper ISO string already, format it
                if (!taskData.scheduled_time.endsWith('Z') && !taskData.scheduled_time.includes('+')) {
                    taskData.scheduled_time = new Date(taskData.scheduled_time).toISOString();
                }
            } else {
                // If empty string, set to null to avoid validation errors
                taskData.scheduled_time = null;
            }
            
            console.log("Sending task data:", taskData);
            
            const response = await axios.post(
                `${base_url}/tasks`,
                taskData,
                {
                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json"
                    }
                }
            );
            
            console.log("Task created successfully:", response.data);
            
            setNewTask({
                title: "",
                description: "",
                scheduled_time: ""
            });
            
            fetchTasks(token);
        } catch (error) {
            console.error("Error creating task:", error);
            // Provide more detailed error information
            if (error.response) {
                console.error("Response data:", error.response.data);
                console.error("Response status:", error.response.status);
                
                // Show user-friendly error message
                alert(`Failed to create task: ${error.response.data.detail || 'Unknown error'}`);
            } else if (error.request) {
                console.error("No response received");
                alert("Server didn't respond. Please try again later.");
            } else {
                console.error("Error setting up request:", error.message);
                alert("Error preparing your request. Please try again.");
            }
        }
    };

    const handleUpdateTask = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem("token");
        if (!token || !editingTask) {
            return;
        }
        
        try {
            await axios.put(
                `${base_url}/tasks/${editingTask.id}`,
                editingTask,
                {
                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json"
                    }
                }
            );
            
            setEditingTask(null);
            fetchTasks(token);
        } catch (error) {
            console.error("Error updating task:", error);
        }
    };
    
    const handleDeleteTask = async (taskId) => {
        const token = localStorage.getItem("token");
        if (!token) {
            navigate("/login");
            return;
        }
        
        if (window.confirm("Are you sure you want to delete this task?")) {
            try {
                await axios.delete(`${base_url}/tasks/${taskId}`, {
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                });
                fetchTasks(token);
            } catch (error) {
                console.error("Error deleting task:", error);
            }
        }
    };
    
    const startEditing = (task) => {
        // Format the date for the datetime-local input
        const formattedTask = {
            ...task,
            scheduled_time: task.scheduled_time ? new Date(task.scheduled_time).toISOString().slice(0, 16) : ""
        };
        setEditingTask(formattedTask);
    };
    
    const cancelEditing = () => {
        setEditingTask(null);
    };
    
    const handleLogout = () => {
        localStorage.removeItem("token");
        navigate("/login");
    };
    
    const formatDateTime = (dateTimeStr) => {
        if (!dateTimeStr) return "No date";
        
        const date = new Date(dateTimeStr);
        return date.toLocaleString('en-IN', { 
            timeZone: 'Asia/Kolkata',
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        }) ;
    };
    
    return (
        <div className="homepage-container">
            <header className="homepage-header">
                <div className="header-content">
                    <h1>Task Manager</h1>
                    {user && (
                        <div className="user-info">
                            <span>Hello, {user.email}</span>
                            <button onClick={handleLogout} className="logout-button">Logout</button>
                        </div>
                    )}
                </div>
            </header>
            
            <main className="homepage-main">
                <section className="task-form-section">
                    <div className="form-container">
                        <h2>{editingTask ? "Update Task" : "Create New Task"}</h2>
                        <form onSubmit={editingTask ? handleUpdateTask : handleCreateTask}>
                            <div className="form-group">
                                <label htmlFor="title">Title</label>
                                <input
                                    id="title"
                                    type="text"
                                    name="title"
                                    value={editingTask ? editingTask.title : newTask.title}
                                    onChange={handleInputChange}
                                    placeholder="Task title"
                                    required
                                />
                            </div>
                            
                            <div className="form-group">
                                <label htmlFor="description">Description</label>
                                <textarea
                                    id="description"
                                    name="description"
                                    value={editingTask ? editingTask.description : newTask.description}
                                    onChange={handleInputChange}
                                    placeholder="Task description"
                                    rows="3"
                                />
                            </div>
                            
                            <div className="form-group">
                                <label htmlFor="scheduled_time">Scheduled Time</label>
                                <input
                                    id="scheduled_time"
                                    type="datetime-local"
                                    name="scheduled_time"
                                    value={editingTask ? editingTask.scheduled_time : newTask.scheduled_time}
                                    onChange={handleInputChange}
                                    
                                />
                            </div>
                            
                            <div className="form-actions">
                                <button type="submit" className="action-button primary-button">
                                    {editingTask ? "Update Task" : "Create Task"}
                                </button>
                                
                                {editingTask && (
                                    <button 
                                        type="button" 
                                        className="action-button secondary-button"
                                        onClick={cancelEditing}
                                    >
                                        Cancel
                                    </button>
                                )}
                            </div>
                        </form>
                    </div>
                </section>
                
                <section className="tasks-list-section">
                    <h2>Your Tasks</h2>
                    
                    {loading ? (
                        <div className="loading">Loading tasks...</div>
                    ) : tasks.length === 0 ? (
                        <div className="no-tasks">
                            <p>You don't have any tasks yet. Create one!</p>
                        </div>
                    ) : (
                        <div className="tasks-grid">
                            {tasks.map(task => (
                                <div key={task.id} className="task-card">
                                    <div className="task-header">
                                        <h3>{task.title}</h3>
                                        <div className="task-actions">
                                            <button 
                                                className="icon-button edit-button" 
                                                onClick={() => startEditing(task)}
                                                aria-label="Edit task"
                                            >
                                                Edit
                                            </button>
                                            <button 
                                                className="icon-button delete-button" 
                                                onClick={() => handleDeleteTask(task.id)}
                                                aria-label="Delete task"
                                            >
                                                Delete
                                            </button>
                                        </div>
                                    </div>
                                    <p className="task-description">{task.description}</p>
                                    <div className="task-time">
                                        <span className="time-label">Scheduled for:</span>
                                        <span className="time-value">{formatDateTime(task.scheduled_time)}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </section>
            </main>
            
            <footer className="homepage-footer">
                <p>&copy; {new Date().getFullYear()} Task Manager. All rights reserved.</p>
            </footer>
        </div>
    );
}

export default Homepage;