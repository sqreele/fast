'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface RegisterFormData {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  role: string;
  password: string;
  confirmPassword: string;
  property_ids: number[];
}

interface DebugLog {
  timestamp: string;
  type: 'info' | 'error' | 'warning' | 'success';
  message: string;
  data?: any;
}

export default function Register() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [properties, setProperties] = useState<Array<{id: number, name: string}>>([]);
  const [showDebug, setShowDebug] = useState(false);
  const [debugLogs, setDebugLogs] = useState<DebugLog[]>([]);
  const [networkStatus, setNetworkStatus] = useState({
    propertiesEndpoint: 'idle',
    registrationEndpoint: 'idle'
  });
  const [formData, setFormData] = useState<RegisterFormData>({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    role: 'TECHNICIAN',
    password: '',
    confirmPassword: '',
    property_ids: []
  });

  const roles = [
    { value: 'TECHNICIAN', label: 'Technician' },
    { value: 'SUPERVISOR', label: 'Supervisor' },
    { value: 'MANAGER', label: 'Manager' },
    { value: 'ADMIN', label: 'Admin' }
  ];

  // Debug logging function
  const addDebugLog = (type: DebugLog['type'], message: string, data?: any) => {
    const log: DebugLog = {
      timestamp: new Date().toISOString(),
      type,
      message,
      data
    };
    setDebugLogs(prev => [...prev, log]);
    console.log(`[DEBUG] ${type.toUpperCase()}: ${message}`, data || '');
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Debug form changes
    addDebugLog('info', `Form field changed: ${name}`, { value, fieldType: e.target.type });
    
    // Clear errors when user starts typing
    if (error) setError('');
  };

  const handlePropertyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const propertyId = parseInt(e.target.value);
    const isChecked = e.target.checked;
    
    setFormData(prev => ({
      ...prev,
      property_ids: isChecked 
        ? [...prev.property_ids, propertyId]
        : prev.property_ids.filter(id => id !== propertyId)
    }));

    addDebugLog('info', `Property selection changed`, { 
      propertyId, 
      isChecked, 
      currentSelection: isChecked 
        ? [...formData.property_ids, propertyId]
        : formData.property_ids.filter(id => id !== propertyId)
    });
  };

  // Fetch available properties on component mount
  useEffect(() => {
    const fetchProperties = async () => {
      try {
        addDebugLog('info', 'Fetching properties from API...');
        setNetworkStatus(prev => ({ ...prev, propertiesEndpoint: 'loading' }));
        
        const startTime = Date.now();
        console.log('Making API call to /api/v1/properties/public');
        const response = await fetch('/api/v1/properties/public');
        const endTime = Date.now();
        
        console.log('API response:', response.status, response.statusText);
        addDebugLog('info', `Properties API response received`, {
          status: response.status,
          statusText: response.statusText,
          responseTime: `${endTime - startTime}ms`
        });

        if (response.ok) {
          const data = await response.json();
          console.log('Properties data:', data);
          setProperties(data);
          addDebugLog('success', `Properties loaded successfully`, {
            count: data.length,
            properties: data.map((p: any) => ({ id: p.id, name: p.name }))
          });
          setNetworkStatus(prev => ({ ...prev, propertiesEndpoint: 'success' }));
        } else {
          const errorText = await response.text();
          console.error('Properties API error:', response.status, errorText);
          addDebugLog('error', `Properties API error`, {
            status: response.status,
            statusText: response.statusText,
            errorText
          });
          setNetworkStatus(prev => ({ ...prev, propertiesEndpoint: 'error' }));
        }
      } catch (error) {
        console.error('Error fetching properties:', error);
        addDebugLog('error', 'Error fetching properties', { error: error instanceof Error ? error.message : error });
        setNetworkStatus(prev => ({ ...prev, propertiesEndpoint: 'error' }));
      }
    };
    
    fetchProperties();
  }, []);

  const validateForm = (): boolean => {
    addDebugLog('info', 'Starting form validation...');
    
    const validationErrors: string[] = [];
    
    if (!formData.username.trim()) {
      validationErrors.push('Username is required');
    }
    if (!formData.email.trim()) {
      validationErrors.push('Email is required');
    }
    if (!formData.email.includes('@')) {
      validationErrors.push('Please enter a valid email address');
    }
    if (!formData.first_name.trim()) {
      validationErrors.push('First name is required');
    }
    if (!formData.last_name.trim()) {
      validationErrors.push('Last name is required');
    }
    if (!formData.password) {
      validationErrors.push('Password is required');
    }
    if (formData.password.length < 6) {
      validationErrors.push('Password must be at least 6 characters long');
    }
    if (formData.password !== formData.confirmPassword) {
      validationErrors.push('Passwords do not match');
    }

    if (validationErrors.length > 0) {
      addDebugLog('warning', 'Form validation failed', { errors: validationErrors });
      setError(validationErrors[0]);
      return false;
    }

    addDebugLog('success', 'Form validation passed');
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    addDebugLog('info', 'Form submission started');
    
    if (!validateForm()) return;
    
    setIsLoading(true);
    setError('');
    setNetworkStatus(prev => ({ ...prev, registrationEndpoint: 'loading' }));

    try {
      const registrationData = {
        username: formData.username.trim(),
        email: formData.email.trim(),
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        phone: formData.phone.trim(),
        role: formData.role,
        password: formData.password,
        is_active: true,
        property_ids: formData.property_ids
      };

      addDebugLog('info', 'Preparing registration data', {
        ...registrationData,
        password: '[HIDDEN]',
        property_ids: registrationData.property_ids
      });

      const startTime = Date.now();
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registrationData)
      });
      const endTime = Date.now();

      addDebugLog('info', 'Registration API response received', {
        status: response.status,
        statusText: response.statusText,
        responseTime: `${endTime - startTime}ms`,
        headers: Object.fromEntries(response.headers.entries())
      });

      const data = await response.json();
      addDebugLog('info', 'Registration response data', data);

      if (!response.ok) {
        const errorMessage = data.detail || data.message || `Registration failed: ${response.status}`;
        addDebugLog('error', 'Registration failed', {
          status: response.status,
          errorMessage,
          responseData: data
        });
        throw new Error(errorMessage);
      }

      addDebugLog('success', 'Registration successful', { responseData: data });
      setSuccess('Registration successful! Redirecting to login...');
      setNetworkStatus(prev => ({ ...prev, registrationEndpoint: 'success' }));
      
      setTimeout(() => {
        addDebugLog('info', 'Redirecting to login page');
        router.push('/signin?message=Registration successful, please sign in');
      }, 2000);

    } catch (error) {
      addDebugLog('error', 'Registration error caught', { 
        error: error instanceof Error ? error.message : error 
      });
      const errorMessage = error instanceof Error ? error.message : 'Registration failed. Please try again.';
      setError(errorMessage);
      setNetworkStatus(prev => ({ ...prev, registrationEndpoint: 'error' }));
    } finally {
      setIsLoading(false);
    }
  };

  const clearDebugLogs = () => {
    setDebugLogs([]);
    addDebugLog('info', 'Debug logs cleared');
  };

  const exportDebugLogs = () => {
    const debugData = {
      timestamp: new Date().toISOString(),
      formData: { ...formData, password: '[HIDDEN]', confirmPassword: '[HIDDEN]' },
      networkStatus,
      logs: debugLogs
    };
    
    const blob = new Blob([JSON.stringify(debugData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `registration-debug-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    addDebugLog('info', 'Debug logs exported');
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="mx-auto h-12 w-12 bg-green-100 rounded-full flex items-center justify-center">
              <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
            <h2 className="mt-4 text-2xl font-bold text-gray-900">Registration Successful!</h2>
            <p className="mt-2 text-gray-600">{success}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link href="/signin" className="font-medium text-indigo-600 hover:text-indigo-500">
              sign in to your existing account
            </Link>
          </p>
          
          {/* Debug Toggle */}
          <div className="mt-4 text-center">
            <button
              onClick={() => setShowDebug(!showDebug)}
              className="text-xs text-gray-500 hover:text-gray-700 underline"
            >
              {showDebug ? 'Hide Debug Panel' : 'Show Debug Panel'}
            </button>
          </div>
        </div>

        {/* Debug Panel */}
        {showDebug && (
          <div className="bg-gray-100 border border-gray-300 rounded-md p-4 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-semibold text-gray-700">Debug Panel</h3>
              <div className="space-x-2">
                <button
                  onClick={clearDebugLogs}
                  className="text-xs bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600"
                >
                  Clear Logs
                </button>
                <button
                  onClick={exportDebugLogs}
                  className="text-xs bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
                >
                  Export Logs
                </button>
              </div>
            </div>
            
            {/* Network Status */}
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-white p-2 rounded">
                <div className="font-medium">Properties API:</div>
                <div className={`inline-block px-1 rounded text-white ${
                  networkStatus.propertiesEndpoint === 'success' ? 'bg-green-500' :
                  networkStatus.propertiesEndpoint === 'error' ? 'bg-red-500' :
                  networkStatus.propertiesEndpoint === 'loading' ? 'bg-yellow-500' : 'bg-gray-500'
                }`}>
                  {networkStatus.propertiesEndpoint}
                </div>
              </div>
              <div className="bg-white p-2 rounded">
                <div className="font-medium">Registration API:</div>
                <div className={`inline-block px-1 rounded text-white ${
                  networkStatus.registrationEndpoint === 'success' ? 'bg-green-500' :
                  networkStatus.registrationEndpoint === 'error' ? 'bg-red-500' :
                  networkStatus.registrationEndpoint === 'loading' ? 'bg-yellow-500' : 'bg-gray-500'
                }`}>
                  {networkStatus.registrationEndpoint}
                </div>
              </div>
            </div>

            {/* Form Data Summary */}
            <div className="bg-white p-2 rounded text-xs">
              <div className="font-medium mb-1">Form Data:</div>
              <div className="space-y-1">
                <div>Username: {formData.username || '[empty]'}</div>
                <div>Email: {formData.email || '[empty]'}</div>
                <div>Name: {formData.first_name} {formData.last_name}</div>
                <div>Role: {formData.role}</div>
                <div>Properties: {formData.property_ids.length} selected</div>
              </div>
            </div>

            {/* Debug Logs */}
            <div className="bg-white p-2 rounded">
              <div className="font-medium mb-2 text-xs">Debug Logs ({debugLogs.length}):</div>
              <div className="max-h-32 overflow-y-auto space-y-1">
                {debugLogs.slice(-10).map((log, index) => (
                  <div key={index} className="text-xs border-l-2 pl-2" style={{
                    borderColor: 
                      log.type === 'error' ? '#ef4444' :
                      log.type === 'warning' ? '#f59e0b' :
                      log.type === 'success' ? '#10b981' : '#3b82f6'
                  }}>
                    <div className="font-mono text-gray-500">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </div>
                    <div className={`font-medium ${
                      log.type === 'error' ? 'text-red-600' :
                      log.type === 'warning' ? 'text-yellow-600' :
                      log.type === 'success' ? 'text-green-600' : 'text-blue-600'
                    }`}>
                      {log.message}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <p className="text-sm">{error}</p>
          </div>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Username *
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={formData.username}
                onChange={handleInputChange}
                disabled={isLoading}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Enter username"
              />
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email Address *
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleInputChange}
                disabled={isLoading}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Enter email address"
              />
            </div>

            {/* First Name */}
            <div>
              <label htmlFor="first_name" className="block text-sm font-medium text-gray-700">
                First Name *
              </label>
              <input
                id="first_name"
                name="first_name"
                type="text"
                required
                value={formData.first_name}
                onChange={handleInputChange}
                disabled={isLoading}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Enter first name"
              />
            </div>

            {/* Last Name */}
            <div>
              <label htmlFor="last_name" className="block text-sm font-medium text-gray-700">
                Last Name *
              </label>
              <input
                id="last_name"
                name="last_name"
                type="text"
                required
                value={formData.last_name}
                onChange={handleInputChange}
                disabled={isLoading}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Enter last name"
              />
            </div>

            {/* Phone */}
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                Phone Number
              </label>
              <input
                id="phone"
                name="phone"
                type="tel"
                value={formData.phone}
                onChange={handleInputChange}
                disabled={isLoading}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Enter phone number"
              />
            </div>

            {/* Role */}
            <div>
              <label htmlFor="role" className="block text-sm font-medium text-gray-700">
                Role *
              </label>
              <select
                id="role"
                name="role"
                required
                value={formData.role}
                onChange={handleInputChange}
                disabled={isLoading}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              >
                {roles.map((role) => (
                  <option key={role.value} value={role.value}>
                    {role.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password *
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleInputChange}
                disabled={isLoading}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Enter password"
              />
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                Confirm Password *
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                value={formData.confirmPassword}
                onChange={handleInputChange}
                disabled={isLoading}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Confirm password"
              />
            </div>

            {/* Property Access */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Property Access
              </label>
              {properties.length > 0 ? (
                <div className="space-y-2 max-h-32 overflow-y-auto border border-gray-300 rounded-md p-3">
                  {properties.map((property) => (
                    <div key={property.id} className="flex items-center">
                      <input
                        id={`property-${property.id}`}
                        name="property_ids"
                        type="checkbox"
                        value={property.id}
                        checked={formData.property_ids.includes(property.id)}
                        onChange={handlePropertyChange}
                        disabled={isLoading}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                      />
                      <label htmlFor={`property-${property.id}`} className="ml-2 block text-sm text-gray-900">
                        {property.name}
                      </label>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="border border-gray-300 rounded-md p-3 bg-gray-50">
                  <p className="text-sm text-gray-500">
                    {properties.length === 0 ? 'Loading properties...' : 'No properties available'}
                  </p>
                </div>
              )}
              <p className="mt-1 text-xs text-gray-500">
                Select properties this user should have access to
              </p>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating account...
                </>
              ) : (
                'Create account'
              )}
            </button>
          </div>

          <div className="text-center">
            <Link
              href="/"
              className="font-medium text-indigo-600 hover:text-indigo-500"
            >
              ← Back to home
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}