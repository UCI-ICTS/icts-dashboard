import React from "react";
import { Home } from '@mui/icons-material';
import { Typography } from "@mui/material";
import { Link } from 'react-router-dom';

export default function HomeIcon() {
    return (
        <Typography
        variant="h6"
        noWrap
        component={Link}
        to="/"
        sx={{
          mr: 2,
          display: { xs: 'none', md: 'flex' },
          fontFamily: 'monospace',
          fontWeight: 700,
          letterSpacing: '.3rem',
          color: 'inherit',
          textDecoration: 'none',
        }}
      >
        <Home />
        PMGRC
      </Typography>
    )
}