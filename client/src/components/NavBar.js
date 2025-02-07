import React, { useState } from 'react';
import {
  AppBar,
  Box,
  Toolbar,
  IconButton,
  Typography,
  Menu,
  Container,
  Avatar,
  Button,
  Tooltip,
  MenuItem,
  useMediaQuery,
} from '@mui/material';
import { Menu as MenuIcon } from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { logout } from "../slices/accountSlice";
import LoginIcon from '@mui/icons-material/Login';

const pages = [
  { label: 'GREGoR', path: '/gregor' },
  { label: 'UDN', path: '/udn' },
  { label: 'MIA', path: '/mia' }
];

function NavBar() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const auth = useSelector((state) => state.account);
  const isMobile = useMediaQuery('(max-width:900px)');

  const [anchorElNav, setAnchorElNav] = useState(null);
  const [anchorElUser, setAnchorElUser] = useState(null);

  const handleOpenNavMenu = (event) => setAnchorElNav(event.currentTarget);
  const handleCloseNavMenu = () => setAnchorElNav(null);

  const handleOpenUserMenu = (event) => setAnchorElUser(event.currentTarget);
  const handleCloseUserMenu = () => setAnchorElUser(null);

  const handleLogout = () => {
    const token = auth.user.refresh_token
    handleCloseUserMenu()
    dispatch(logout({token}))
  };
  
  const handleProfileClick = () => {
    handleCloseUserMenu();
    navigate('/profile');
  };

  return (
    <AppBar position="static" className='navbar'>
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <Tooltip title="Home">
            <Typography
              variant="h6"
              noWrap
              component={Link}
              to="/"
              className="navbar-link"
            >
              UCI ICTS Dashboard
            </Typography>
          </Tooltip>
          {auth.isLoggedIn === true ?(
            <>{/* Mobile Menu */}
            {isMobile && (
              <Box sx={{ flexGrow: 1 }}>
                <IconButton
                  size="large"
                  aria-label="menu navigation"
                  onClick={handleOpenNavMenu}
                  color="inherit"
                >
                  <MenuIcon />
                </IconButton>
                <Menu
                  anchorEl={anchorElNav}
                  anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
                  transformOrigin={{ vertical: 'top', horizontal: 'left' }}
                  open={Boolean(anchorElNav)}
                  onClose={handleCloseNavMenu}
                >
                  {pages.map((page) => (
                    <MenuItem key={page.label} onClick={handleCloseNavMenu}>
                      <Typography textAlign="center">
                        <Link to={page.path} style={{ textDecoration: 'none', color: 'inherit' }}>
                          {page.label}
                        </Link>
                      </Typography>
                    </MenuItem>
                  ))}
                </Menu>
              </Box>
            )}
  
            {/* Desktop Menu */}
            <Box className="navbar-menu">
              {pages.map((page) => (
                <Button
                  key={page.label}
                  component={Link}
                  to={page.path}
                  onClick={handleCloseNavMenu}
                  className='navbar-link'
                >
                  {page.label}
                </Button>
              ))}
            </Box>
  
            {/* User Menu */}
            <Box sx={{ flexGrow: 0 }}>
              <Tooltip title="Profiel and settings">
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
                <MenuItem onClick={handleProfileClick}>Profile</MenuItem>
                <MenuItem onClick={handleCloseUserMenu}>Settings</MenuItem>
                <MenuItem onClick={handleLogout}>Logout</MenuItem>
              </Menu>
            </Box></>
            ) : (
            <>
              <Box className="navbar-right">
                <Tooltip title="Log In">
                  <IconButton                   
                    component={Link}
                    to={"/login"}
                    onClick={handleCloseNavMenu}
                    className='navbar-link'
                    >
                      <LoginIcon />
                      &nbsp;&nbsp;Log In
                  </IconButton>
                </Tooltip>
              </Box>
            </>
            )
          }
          
        </Toolbar>
      </Container>
    </AppBar>
  );
}

export default NavBar;
