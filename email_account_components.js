// src/components/EmailAccounts/AccountList.js
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondaryAction,
  Avatar,
  IconButton,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Chip,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Mail as MailIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { getEmailAccounts, deleteEmailAccount, syncEmailAccount } from '../../services/api';
import Loading from '../Common/Loading';
import ErrorMessage from '../Common/ErrorMessage';

const AccountList = () => {
  const navigate = useNavigate();
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [accountToDelete, setAccountToDelete] = useState(null);
  const [syncingAccount, setSyncingAccount] = useState(null);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await getEmailAccounts();
      setAccounts(response.data.accounts);
    } catch (err) {
      console.error('Error fetching accounts:', err);
      setError(
        err.response?.data?.message || 'An error occurred while fetching accounts'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleAddAccount = () => {
    navigate('/accounts/new');
  };

  const handleEditAccount = (accountId) => {
    navigate(`/accounts/${accountId}`);
  };

  const handleDeleteClick = (account) => {
    setAccountToDelete(account);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!accountToDelete) return;

    try {
      await deleteEmailAccount(accountToDelete.id);
      setAccounts(accounts.filter((a) => a.id !== accountToDelete.id));
      setDeleteDialogOpen(false);
      setAccountToDelete(null);
    } catch (err) {
      console.error('Error deleting account:', err);
      setError(
        err.response?.data?.message || 'An error occurred while deleting the account'
      );
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setAccountToDelete(null);
  };

  const handleSyncAccount = async (accountId) => {
    try {
      setSyncingAccount(accountId);
      await syncEmailAccount(accountId);
      // Optionally show a success message
    } catch (err) {
      console.error('Error syncing account:', err);
      setError(
        err.response?.data?.message || 'An error occurred while syncing the account'
      );
    } finally {
      setSyncingAccount(null);
    }
  };

  if (loading) {
    return <Loading message="Loading email accounts..." />;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5">Email Accounts</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddAccount}
        >
          Add Account
        </Button>
      </Box>

      <ErrorMessage message={error} onClose={() => setError('')} />

      <Paper sx={{ p: 0 }}>
        {accounts.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body1" gutterBottom>
              No email accounts found
            </Typography>
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={handleAddAccount}
              sx={{ mt: 2 }}
            >
              Add Your First Email Account
            </Button>
          </Box>
        ) : (
          <List>
            {accounts.map((account) => (
              <ListItem key={account.id} divider>
                <ListItemAvatar>
                  <Avatar>
                    <MailIcon />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={account.name}
                  secondary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {account.email}
                      {account.is_active ? (
                        <Chip
                          label="Active"
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      ) : (
                        <Chip
                          label="Inactive"
                          size="small"
                          color="error"
                          variant="outlined"
                        />
                      )}
                      <Chip
                        label={account.provider}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    aria-label="sync"
                    onClick={() => handleSyncAccount(account.id)}
                    disabled={syncingAccount === account.id}
                    sx={{ mr: 1 }}
                  >
                    <RefreshIcon />
                  </IconButton>
                  <IconButton
                    edge="end"
                    aria-label="edit"
                    onClick={() => handleEditAccount(account.id)}
                    sx={{ mr: 1 }}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    edge="end"
                    aria-label="delete"
                    onClick={() => handleDeleteClick(account)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        )}
      </Paper>

      {/* Delete confirmation dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">Delete Email Account</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Are you sure you want to delete the email account "
            {accountToDelete?.name}" ({accountToDelete?.email})? This action
            cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AccountList;

// src/components/EmailAccounts/AccountForm.js
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import {
  getEmailAccount,
  addEmailAccount,
  updateEmailAccount,
} from '../../services/api';
import Loading from '../Common/Loading';
import ErrorMessage from '../Common/ErrorMessage';

const AccountForm = () => {
  const navigate = useNavigate();
  const { accountId } = useParams();
  const isEditMode = !!accountId;

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    provider: '',
    is_active: true,
    credentials: {
      username: '',
      password: '',
      server: '',
      port: '',
      use_ssl: true,
    },
  });

  const [loading, setLoading] = useState(isEditMode);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [formErrors, setFormErrors] = useState({});

  useEffect(() => {
    if (isEditMode) {
      fetchAccount();
    }
  }, [accountId]);

  const fetchAccount = async () => {
    try {
      setLoading(true);
      const response = await getEmailAccount(accountId);
      
      // Parse credentials from JSON string
      const account = response.data;
      const credentials = JSON.parse(account.credentials);
      
      setFormData({
        name: account.name,
        email: account.email,
        provider: account.provider,
        is_active: account.is_active,
        credentials,
      });
    } catch (err) {
      console.error('Error fetching account:', err);
      setError(
        err.response?.data?.message || 'An error occurred while fetching the account'
      );
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.name.trim()) {
      errors.name = 'Account name is required';
    }
    
    if (!formData.email.trim()) {
      errors.email = 'Email address is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email address is invalid';
    }
    
    if (!formData.provider) {
      errors.provider = 'Provider is required';
    }
    
    // Validate credentials based on provider
    if (formData.provider === 'exchange') {
      if (!formData.credentials.username.trim()) {
        errors.username = 'Username is required';
      }
      
      if (!formData.credentials.password.trim()) {
        errors.password = 'Password is required';
      }
      
      if (!formData.credentials.server.trim()) {
        errors.server = 'Server is required';
      }
    } else if (formData.provider === 'gmail') {
      if (!formData.credentials.username.trim()) {
        errors.username = 'Username is required';
      }
      
      if (!formData.credentials.password.trim()) {
        errors.password = 'Password is required';
      }
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCredentialsChange = (e) => {
    const { name, value, type, checked } = e.target;
    const fieldValue = type === 'checkbox' ? checked : value;
    
    setFormData((prev) => ({
      ...prev,
      credentials: {
        ...prev.credentials,
        [name]: fieldValue,
      },
    }));
  };

  const handleSwitchChange = (e) => {
    const { name, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: checked,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    try {
      setSubmitting(true);
      setError('');
      
      if (isEditMode) {
        await updateEmailAccount(accountId, formData);
      } else {
        await addEmailAccount(formData);
      }
      
      navigate('/accounts');
    } catch (err) {
      console.error('Error saving account:', err);
      setError(
        err.response?.data?.message || 'An error occurred while saving the account'
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <Loading message="Loading account details..." />;
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        {isEditMode ? 'Edit Email Account' : 'Add Email Account'}
      </Typography>
      
      <ErrorMessage message={error} onClose={() => setError('')} />
      
      <Paper sx={{ p: 3 }}>
        <Box component="form" onSubmit={handleSubmit}>
          <Typography variant="h6" gutterBottom>
            Account Information
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              label="Account Name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              margin="normal"
              error={!!formErrors.name}
              helperText={formErrors.name}
              required
            />
            
            <TextField
              fullWidth
              label="Email Address"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              margin="normal"
              error={!!formErrors.email}
              helperText={formErrors.email}
              required
            />
            
            <FormControl
              fullWidth
              margin="normal"
              error={!!formErrors.provider}
              required
            >
              <InputLabel>Provider</InputLabel>
              <Select
                name="provider"
                value={formData.provider}
                onChange={handleChange}
                label="Provider"
              >
                <MenuItem value="">Select Provider</MenuItem>
                <MenuItem value="exchange">Exchange Online</MenuItem>
                <MenuItem value="gmail">Gmail</MenuItem>
              </Select>
              {formErrors.provider && (
                <FormHelperText>{formErrors.provider}</FormHelperText>
              )}
            </FormControl>
            
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_active}
                  onChange={handleSwitchChange}
                  name="is_active"
                  color="primary"
                />
              }
              label="Active"
              sx={{ mt: 2 }}
            />
          </Box>
          
          <Divider sx={{ my: 3 }} />
          
          <Typography variant="h6" gutterBottom>
            Credentials
          </Typography>
          
          {formData.provider === 'exchange' && (
            <Box>
              <Alert severity="info" sx={{ mb: 2 }}>
                For Exchange Online, you'll need to provide your email address,
                password, and server information.
              </Alert>
              
              <TextField
                fullWidth
                label="Username"
                name="username"
                value={formData.credentials.username}
                onChange={handleCredentialsChange}
                margin="normal"
                error={!!formErrors.username}
                helperText={formErrors.username}
                required
              />
              
              <TextField
                fullWidth
                label="Password"
                name="password"
                type="password"
                value={formData.credentials.password}
                onChange={handleCredentialsChange}
                margin="normal"
                error={!!formErrors.password}
                helperText={formErrors.password}
                required
              />
              
              <TextField
                fullWidth
                label="Server"
                name="server"
                value={formData.credentials.server}
                onChange={handleCredentialsChange}
                margin="normal"
                error={!!formErrors.server}
                helperText={formErrors.server}
                required
              />
              
              <TextField
                fullWidth
                label="Port"
                name="port"
                type="number"
                value={formData.credentials.port}
                onChange={handleCredentialsChange}
                margin="normal"
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.credentials.use_ssl}
                    onChange={handleCredentialsChange}
                    name="use_ssl"
                    color="primary"
                  />
                }
                label="Use SSL"
                sx={{ mt: 2 }}
              />
            </Box>
          )}
          
          {formData.provider === 'gmail' && (
            <Box>
              <Alert severity="info" sx={{ mb: 2 }}>
                For Gmail, you'll need to provide your email address and an app
                password. You can generate an app password in your Google
                Account settings.
              </Alert>
              
              <TextField
                fullWidth
                label="Username"
                name="username"
                value={formData.credentials.username}
                onChange={handleCredentialsChange}
                margin="normal"
                error={!!formErrors.username}
                helperText={formErrors.username}
                required
              />
              
              <TextField
                fullWidth
                label="App Password"
                name="password"
                type="password"
                value={formData.credentials.password}
                onChange={handleCredentialsChange}
                margin="normal"
                error={!!formErrors.password}
                helperText={formErrors.password}
                required
              />
            </Box>
          )}
          
          {!formData.provider && (
            <Alert severity="info">
              Please select a provider to see credential options.
            </Alert>
          )}
          
          <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
            <Button
              variant="outlined"
              onClick={() => navigate('/accounts')}
              disabled={submitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={submitting}
            >
              {submitting
                ? isEditMode
                  ? 'Saving...'
                  : 'Adding...'
                : isEditMode
                ? 'Save Changes'
                : 'Add Account'}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default AccountForm;

// src/components/User/UserProfile.js
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Divider,
  Grid,
} from '@mui/material';
import { getCurrentUser, updateCurrentUser } from '../../services/api';
import { updateUser } from '../../services/auth';
import Loading from '../Common/Loading';
import ErrorMessage from '../Common/ErrorMessage';

const UserProfile = () => {
  const [userData, setUserData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
  });
  
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formErrors, setFormErrors] = useState({});

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      setLoading(true);
      const response = await getCurrentUser();
      setUserData({
        username: response.data.username,
        email: response.data.email,
        first_name: response.data.first_name || '',
        last_name: response.data.last_name || '',
      });
    } catch (err) {
      console.error('Error fetching user data:', err);
      setError(
        err.response?.data?.message || 'An error occurred while fetching user data'
      );
    } finally {
      setLoading(false);
    }
  };

  const validateProfileForm = () => {
    const errors = {};
    
    if (!userData.email.trim()) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(userData.email)) {
      errors.email = 'Email address is invalid';
    }
    
    setFormErrors((prev) => ({ ...prev, ...errors }));
    return Object.keys(errors).length === 0;
  };

  const validatePasswordForm = () => {
    const errors = {};
    
    if (!passwordData.current_password.trim()) {
      errors.current_password = 'Current password is required';
    }
    
    if (!passwordData.new_password.trim()) {
      errors.new_password = 'New password is required';
    } else if (passwordData.new_password.length < 8) {
      errors.new_password = 'Password must be at least 8 characters';
    }
    
    if (!passwordData.confirm_password.trim()) {
      errors.confirm_password = 'Please confirm your password';
    } else if (passwordData.new_password !== passwordData.confirm_password) {
      errors.confirm_password = 'Passwords do not match';
    }
    
    setFormErrors((prev) => ({ ...prev, ...errors }));
    return Object.keys(errors).length === 0;
  };

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setUserData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateProfileForm()) {
      return;
    }
    
    try {
      setSubmitting(true);
      setError('');
      setSuccess('');
      
      const response = await updateCurrentUser({
        email: userData.email,
        first_name: userData.first_name,
        last_name: userData.last_name,
      });
      
      // Update user in local storage
      updateUser({
        email: userData.email,
        first_name: userData.first_name,
        last_name: userData.last_name,
      });
      
      setSuccess('Profile updated successfully');
    } catch (err) {
      console.error('Error updating profile:', err);
      setError(
        err.response?.data?.message || 'An error occurred while updating profile'
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    
    if (!validatePasswordForm()) {
      return;
    }
    
    try {
      setSubmitting(true);
      setError('');
      setSuccess('');
      
      await updateCurrentUser({
        password: passwordData.new_password,
        current_password: passwordData.current_password,
      });
      
      // Clear password fields
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
      
      setSuccess('Password updated successfully');
    } catch (err) {
      console.error('Error updating password:', err);
      setError(
        err.response?.data?.message || 'An error occurred while updating password'
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <Loading message="Loading profile..." />;
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        User Profile
      </Typography>
      
      <ErrorMessage message={error} onClose={() => setError('')} />
      
      {success && (
        <Box sx={{ mb: 2 }}>
          <Alert severity="success" onClose={() => setSuccess('')}>
            {success}
          </Alert>
        </Box>
      )}
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Profile Information
            </Typography>
            
            <Box component="form" onSubmit={handleProfileSubmit}>
              <TextField
                fullWidth
                label="Username"
                name="username"
                value={userData.username}
                margin="normal"
                disabled
                helperText="Username cannot be changed"
              />
              
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={userData.email}
                onChange={handleProfileChange}
                margin="normal"
                error={!!formErrors.email}
                helperText={formErrors.email}
                required
              />
              
              <TextField
                fullWidth
                label="First Name"
                name="first_name"
                value={userData.first_name}
                onChange={handleProfileChange}
                margin="normal"
              />
              
              <TextField
                fullWidth
                label="Last Name"
                name="last_name"
                value={userData.last_name}
                onChange={handleProfileChange}
                margin="normal"
              />
              
              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  type="submit"
                  variant="contained"
                  disabled={submitting}
                >
                  {submitting ? 'Saving...' : 'Save Changes'}
                </Button>
              </Box>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Change Password
            </Typography>
            
            <Box component="form" onSubmit={handlePasswordSubmit}>
              <TextField
                fullWidth
                label="Current Password"
                name="current_password"
                type="password"
                value={passwordData.current_password}
                onChange={handlePasswordChange}
                margin="normal"
                error={!!formErrors.current_password}
                helperText={formErrors.current_password}
                required
              />
              
              <TextField
                fullWidth
                label="New Password"
                name="new_password"
                type="password"
                value={passwordData.new_password}
                onChange={handlePasswordChange}
                margin="normal"
                error={!!formErrors.new_password}
                helperText={formErrors.new_password}
                required
              />
              
              <TextField
                fullWidth
                label="Confirm New Password"
                name="confirm_password"
                type="password"
                value={passwordData.confirm_password}
                onChange={handlePasswordChange}
                margin="normal"
                error={!!formErrors.confirm_password}
                helperText={formErrors.confirm_password}
                required
              />
              
              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  type="submit"
                  variant="contained"
                  disabled={submitting}
                >
                  {submitting ? 'Updating...' : 'Update Password'}
                </Button>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default UserProfile;
