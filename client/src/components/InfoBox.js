import React from "react";
import { Card, CardActionArea, CardContent, Typography } from "@mui/material"

export const InfoBox = ({ header, bodyText, linkTo }) => {
  const handleClick = (event) => {
    event.preventDefault(); // Prevent default navigation
    window.open(linkTo, "_blank", "noopener,noreferrer"); // Open in a new tab
  };

  return (
    <Card className="home-linkcard" elevation={1}>
      <CardActionArea 
        className="home-linkcard" 
        component="a" 
        href={linkTo} 
        onClick={handleClick}
      >
        <CardContent>
          <Typography className="home-intro-title">
            {header}
          </Typography>
          <Typography className="home-bullet">
            {bodyText}
            <br />
          </Typography>
        </CardContent>
      </CardActionArea>
    </Card>
  );
};
