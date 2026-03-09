import React, {useState} from 'react';
import {Link, useNavigate} from 'react-router-dom';

import {loginUser} from '../services/AuthService';

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [generalError, setGeneralError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear field error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});
    setGeneralError('');

    // Basic validation
    const validationErrors = {};
    if (!formData.username.trim()) {
      validationErrors.username = 'Username is required';
    }
    if (!formData.password) {
      validationErrors.password = 'Password is required';
    }

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      setLoading(false);
      return;
    }

    // Call API
    const result = await loginUser(formData);
    
    if (result.success) {
      // Redirect to dashboard on success
      navigate('/dashboard');
    } else {
      // Handle errors from backend
      if (result.errors) {
        // Backend validation errors
        const fieldErrors = {};
        Object.keys(result.errors).forEach(key => {
          if (key === 'detail' || key === 'general' || key === 'non_field_errors') {
            // Handle non-field errors
            const errorMsg = Array.isArray(result.errors[key]) 
              ? result.errors[key][0] 
              : result.errors[key];
            setGeneralError(errorMsg);
          } else {
            // Handle field-specific errors
            fieldErrors[key] = Array.isArray(result.errors[key]) 
              ? result.errors[key][0] 
              : result.errors[key];
          }
        });
        setErrors(fieldErrors);
        
        // If no specific field error and no general error set yet
        if (Object.keys(fieldErrors).length === 0 && !generalError) {
          setGeneralError('Invalid username or password');
        }
      }
    }
    
    setLoading(false);
  };

  return (
    <div className='min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8'>
      <div className='max-w-md w-full space-y-8'>
        <div>
          <h2 className='mt-6 text-center text-3xl font-extrabold text-gray-900'>
            Sign in to your account
          </h2>
        </div>
        
        {generalError && (
          <div className='rounded-md bg-red-50 p-4'>
            <div className='text-sm text-red-700'>
              {generalError}
            </div>
          </div>
        )}
        
        <form className='mt-8 space-y-6' onSubmit={handleSubmit}>
          <div className='rounded-md shadow-sm -space-y-px'>
            <div>
              <label htmlFor='username' className='sr-only'>
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border ${
                  errors.username ? 'border-red-300' : 'border-gray-300'
                } placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm`}
                placeholder="Username"
                value={formData.username}
                onChange={handleChange}
                disabled={loading}
              />
              {errors.username && (
                <p className='mt-1 text-sm text-red-600'>{errors.username}</p>
              )}
            </div>
            <div>
              <label htmlFor='password' className='sr-only'>
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border ${
                  errors.password ? 'border-red-300' : 'border-gray-300'
                } placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm`}
                placeholder="Password"
                value={formData.password}
                onChange={handleChange}
                disabled={loading}
              />
              {errors.password && (
                <p className='mt-1 text-sm text-red-600'>{errors.password}</p>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
        </form>

        <div className='text-center'>
          <p className='text-sm text-gray-600'>
            Don't have an account?{' '}
            <Link to='/register' className='font-medium text-indigo-600 hover:text-indigo-500'>
              Register
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;