import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import {
  validateEmail,
  validatePassword,
  validateRequired,
} from '../../utils/validators';
import { AxiosError } from 'axios';

interface RegisterFormProps {
  onSuccess: () => void;
}

interface FormErrors {
  email?: string;
  password?: string;
  first_name?: string;
  last_name?: string;
  general?: string;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess }) => {
  const { register } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = (): boolean => {
    const newErrors: FormErrors = {};

    const emailError = validateEmail(email);
    if (emailError) newErrors.email = emailError;

    const passwordError = validatePassword(password);
    if (passwordError) newErrors.password = passwordError;

    const firstNameError = validateRequired(firstName, 'First name');
    if (firstNameError) newErrors.first_name = firstNameError;

    const lastNameError = validateRequired(lastName, 'Last name');
    if (lastNameError) newErrors.last_name = lastNameError;

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    setErrors({});

    try {
      await register({
        email,
        password,
        first_name: firstName,
        last_name: lastName,
      });
      onSuccess();
    } catch (error) {
      if (error instanceof AxiosError && error.response) {
        const detail = error.response.data?.detail;
        setErrors({
          general:
            typeof detail === 'string'
              ? detail
              : 'Registration failed. Please try again.',
        });
      } else {
        setErrors({ general: 'An unexpected error occurred. Please try again.' });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
      {errors.general && (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {errors.general}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Input
          label="First Name"
          type="text"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          error={errors.first_name}
          placeholder="John"
          autoComplete="given-name"
          required
        />

        <Input
          label="Last Name"
          type="text"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          error={errors.last_name}
          placeholder="Doe"
          autoComplete="family-name"
          required
        />
      </div>

      <Input
        label="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        error={errors.email}
        placeholder="you@example.com"
        autoComplete="email"
        required
      />

      <Input
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        error={errors.password}
        placeholder="At least 8 characters"
        helperText="Must contain uppercase, lowercase, and a number"
        autoComplete="new-password"
        required
      />

      <Button type="submit" isLoading={isSubmitting} className="w-full">
        Create Account
      </Button>
    </form>
  );
};