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
import { Link } from 'react-router-dom';
import HomeIcon  from "./HomeIcon"
import UserMenu from './UserMenu';
import { useDispatch } from 'react-redux';
import { setTableView } from '../slices/dataSlice';

const pages = [
  { label: 'About', path: '/about' },
  { label: 'GREGoR', path: '/gregor' },
  { label: 'UDN', path: '/udn' },
  { label: 'MIA', path: '/mia' }
];
const tables = [
  {name:"Participants", schema:"participants", identifier:"participants"},
  {name:"Family", schema:"family", identifier:"family"},
  {name:"Genetic Findings", schema:"genetic_findings", identifier:"genetic_findings"},
  {name:"Analyte", schema:"analyte", identifier:"analyte"}
]
function FormNavBar() {

  const isMobile = useMediaQuery('(max-width:900px)');

  const [anchorElNav, setAnchorElNav] = useState(null);
  const dispatch = useDispatch();
  const handleOpenNavMenu = (event) => setAnchorElNav(event.currentTarget);
  const handleCloseNavMenu = (table) => {
    setAnchorElNav(null)
    console.log("press", table)
    dispatch(setTableView(table));
  };
  
  return (
    <AppBar position="static">
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <HomeIcon />

          {/* Mobile Menu */}
            {isMobile && (
              <Box sx={{ flexGrow: 1 }}>
                <IconButton
                  size="large"
                  aria-label="menu navigation"
                  onClick={handleOpenNavMenu}
                  color="inherit"
                >
                  <MenuIcon />Menu
                </IconButton>
                <Menu
                  anchorEl={anchorElNav}
                  anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
                  transformOrigin={{ vertical: 'top', horizontal: 'left' }}
                  open={Boolean(anchorElNav)}
                  onClose={handleCloseNavMenu}
                >
                  <MenuItem key={"home"}>
                    <Typography textAlign="center">
                      Home
                    </Typography>
                  </MenuItem>
                  {tables.map((table) => (
                    <MenuItem key={table.schema} onClick={event => handleCloseNavMenu(table)}>
                      <Typography textAlign="center">
                        {table.name}
                      </Typography>
                    </MenuItem>
                  ))}
                </Menu>
              </Box>
            )}
  
            {/* Desktop Menu */}
            <Box sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' } }}>
              {tables.map((table) => (
                <Button
                  key={table.name}
                  onClick={event => handleCloseNavMenu(table)}
                  sx={{ my: 2, color: 'white', display: 'block' }}
                >
                  {table.name}
                </Button>
              ))}
            </Box>
          <UserMenu />
        </Toolbar>
      </Container>
    </AppBar>
  );
}

export default FormNavBar;
