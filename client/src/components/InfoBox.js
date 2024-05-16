import React from "react";
import { Card, CardActionArea, CardContent, Typography } from "@material-ui/core";
import { Link } from "react-router-dom";

export const InfoBox = ( {header, bodyText, linkTo}) => {
    return (
    <Card className="home-linkcard" elevation={1}>
      <CardActionArea className="home-linkcard" component={Link} to={linkTo}>
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
    )
}