import React, { useState } from "react"
import {
  Avatar,
  Box,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
} from '@mui/material';
import { logout } from "../slices/accountSlice";
import { useSelector, useDispatch } from 'react-redux';
function UserMenu() {
  const auth = useSelector((state) => state.account);
  const dispatch = useDispatch();
  const handleOpenUserMenu = (event) => setAnchorElUser(event.currentTarget);
  const handleCloseUserMenu = () => setAnchorElUser(null);
  const [anchorElUser, setAnchorElUser] = useState(null);

  const handleLogout = () => {
    handleCloseUserMenu();
    if (auth.user && auth.user.refresh_token) {
      const token = auth.user.refresh_token;
      dispatch(logout({ token }));
    } else {
      console.error("No refresh token found");
    }
  };

  return (
    <Box sx={{ flexGrow: 0 }}>
    <Tooltip title="Open settings">
      <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
        <Avatar alt={auth?.name || 'User'} src={auth?.avatar || ''} />
      </IconButton>
    </Tooltip>
    <Menu
      anchorEl={anchorElUser}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      open={Boolean(anchorElUser)}
      onClose={handleCloseUserMenu}
    >
      <MenuItem onClick={handleCloseUserMenu}>Profile</MenuItem>
      <MenuItem onClick={handleCloseUserMenu}>Settings</MenuItem>
      <MenuItem onClick={handleLogout}>Logout</MenuItem>
    </Menu>
  </Box>
  );
}
export default UserMenu;