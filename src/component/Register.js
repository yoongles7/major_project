import React, {useState} from 'react';
import {Link, useNavigate} from 'react-router-dom';

import {registerUser} from '../services/AuthService';

const Register =
    () => {
      const navigate = useNavigate();
      const [formData, setFormData] = useState(
          {username: '', email: '', password: '', confirmPassword: ''});
      const [errors, setErrors] = useState({});
      const [loading, setLoading] = useState(false);
      const [generalError, setGeneralError] = useState('');

      const handleChange = (e) => {
        const {name, value} = e.target;
        setFormData(prev => ({...prev, [name]: value}));
        // Clear field error when user starts typing
        if (errors[name]) {
          setErrors(prev => ({...prev, [name]: null}));
        }
      };

      const validateForm = () => {
        const validationErrors = {};

        if (!formData.username.trim()) {
          validationErrors.username = 'Username is required';
        } else if (formData.username.length < 3) {
          validationErrors.username = 'Username must be at least 3 characters';
        }

        if (!formData.email.trim()) {
          validationErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
          validationErrors.email = 'Email is invalid';
        }

        if (!formData.password) {
          validationErrors.password = 'Password is required';
        } else if (formData.password.length < 6) {
          validationErrors.password = 'Password must be at least 6 characters';
        }

        if (!formData.confirmPassword) {
          validationErrors.confirmPassword = 'Please confirm your password';
        } else if (formData.password !== formData.confirmPassword) {
          validationErrors.confirmPassword = 'Passwords do not match';
        }

        return validationErrors;
      };

      const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setErrors({});
        setGeneralError('');

        // Client-side validation
        const validationErrors = validateForm();
        if (Object.keys(validationErrors).length > 0) {
          setErrors(validationErrors);
          setLoading(false);
          return;
        }

        // Call API
        const result = await registerUser(formData);

        if (result.success) {
          // Redirect to dashboard on success
          navigate('/dashboard');
        } else {
          // Handle errors from backend
          if (result.errors) {
            const fieldErrors = {};

            Object.keys(result.errors).forEach(key => {
              // Map backend field names to frontend field names
              if (key === 'password_confirmation') {
                fieldErrors.confirmPassword =
                    Array.isArray(result.errors[key]) ? result.errors[key][0] :
                                                        result.errors[key];
              } else if (
                  key === 'username' || key === 'email' || key === 'password') {
                fieldErrors[key] = Array.isArray(result.errors[key]) ?
                    result.errors[key][0] :
                    result.errors[key];
              } else if (key === 'non_field_errors' || key === 'detail') {
                setGeneralError(result.errors[key][0] || result.errors[key]);
              } else {
                // Any other errors as general
                setGeneralError(result.errors[key][0] || result.errors[key]);
              }
            });

            setErrors(fieldErrors);

            // If no specific field error and no general error set yet
            if (Object.keys(fieldErrors).length === 0 && !generalError) {
              setGeneralError('Registration failed. Please try again.');
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
            Create Account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Join NEPSE trading platform
          </p>
        </div>
        
        {generalError && (
          <div className="rounded-md bg-red-50 p-4">
            <div className="text-sm text-red-700">
              {generalError}
            </div>
          </div>
        )}
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            {/* Username Field */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Username
              </label>
              <input
  id = 'username'
  name = 'username'
  type = 'text'
  required
  className = {`mt-1 appearance-none relative block w-full px-3 py-2 border ${
      errors.username ?
          'border-red-300' :
          'border-gray-300'} placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm`} placeholder =
      'Choose a username'
                value={formData.username}
                onChange={handleChange}
                disabled={
    loading}
              />
              {errors.username && (
                <p className="mt-1 text-sm text-red-600">{errors.username}</p>
              )}
              < /div>

            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label >
    < input
id = 'email'
name = 'email'
type = 'email'
required
className = {`mt-1 appearance-none relative block w-full px-3 py-2 border ${
    errors.email ?
        'border-red-300' :
        'border-gray-300'} placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm`} placeholder =
    'Enter your email'
                value={formData.email}
                onChange={handleChange}
                disabled={loading}
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email}</p>
              )}
                </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label><
                    input
                id = 'password'
                name = 'password'
                type = 'password'
                required
                className = {`mt-1 appearance-none relative block w-full px-3 py-2 border ${
                    errors.password ?
                        'border-red-300' :
                        'border-gray-300'} placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm`} placeholder =
                    'Create a password'
                value={formData.password}
                onChange={handleChange}
                disabled={loading}
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password}</p>
              )
                }
                <p className = 'mt-1 text-xs text-gray-500'>Password must be at
                        least 6 characters</p>
              </div>
              
              {/* Confirm Password Field */}
              < div >
                    <label htmlFor = 'confirmPassword' className =
                         'block text-sm font-medium text-gray-700'>Confirm
                        Password<
                            /label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                className={`mt-1 appearance-none relative block w-full px-3 py-2 border ${
                  errors.confirmPassword ? 'border-red-300' : 'border-gray-300'
                } placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm`}
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={handleChange}
                disabled={loading}
              /> {errors.confirmPassword && (
                <p className='mt-1 text-sm text-red-600'>{errors.confirmPassword}</p>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating Account...' : 'Register'}
            </button>
          </div>
        </form>

        <div className='text-center'>
          <p className='text-sm text-gray-600'>
            Already have an account?{' '}
            <Link to='/login' className='font-medium text-indigo-600 hover:text-indigo-500'>
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;